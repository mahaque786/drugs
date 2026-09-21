#!/usr/bin/env python3
"""Validate the emitted dataset.

Written around the bugs actually present in the uploaded records, on the
principle that a validator earns its keep by catching the mistakes that were
really made rather than the ones that are easy to check.

  ERROR   will produce wrong answers downstream
  WARN    suspicious; may be deliberate
"""
import json, glob, os, sys, collections

OUT = os.environ.get("DRUGDB", "/mnt/user-data/outputs")

MASS = {"ug": 1e-3, "mg": 1.0, "g": 1e3}
TIME = {"min": 1 / 60, "h": 1.0, "d": 24.0}

errors, warns = [], []
def err(rec, msg): errors.append(f"[{rec}] {msg}")
def warn(rec, msg): warns.append(f"[{rec}] {msg}")


def load():
    recs = {}
    for p in glob.glob(f"{OUT}/drugs/*.json") + glob.glob(f"{OUT}/metabolites/*.json"):
        with open(p) as f:
            r = json.load(f)
        recs[r["id"]] = r
    vocab = {}
    for p in glob.glob(f"{OUT}/vocab/*.json"):
        with open(p) as f:
            v = json.load(f)
        vocab[v["name"]] = {t["id"] for t in v["terms"]}
        vocab[v["name"] + "__closed"] = v.get("closed", False)
    return recs, vocab


def amounts(dose):
    """Every numeric magnitude in a dose amount, with its unit."""
    a = dose.get("amount", {})
    u = a.get("unit")
    vals = []
    if "value" in a: vals.append(a["value"])
    if "min" in a: vals.append(a["min"])
    if "max" in a: vals.append(a["max"])
    vals += a.get("steps", [])
    return vals, u


def check_dose_units(rid, rec):
    """The uploaded amphetamine-ir record had steps in `ug` and a daily maximum
    in `mg` — a thousandfold error that passed every schema check, because both
    terms are legal members of a closed units vocabulary. Unit legality is not
    unit coherence."""
    for ind in rec.get("indications", []):
        for reg in ind.get("dosageRegimens", []):
            vals, unit = amounts(reg.get("dose", {}))
            mx = reg.get("maxDailyDose")
            if not vals or not unit or not mx:
                continue
            mu = mx.get("unit")
            if unit in MASS and mu in MASS:
                biggest = max(vals) * MASS[unit]
                ceiling = mx["value"] * MASS[mu]
                if biggest > ceiling:
                    err(rid, f"single dose {max(vals)}{unit} exceeds maxDailyDose "
                             f"{mx['value']}{mu} ({ind['name']})")
                elif ceiling / biggest > 100:
                    err(rid, f"maxDailyDose {mx['value']}{mu} is {ceiling/biggest:.0f}x the "
                             f"largest single dose {max(vals)}{unit} — unit mismatch? ({ind['name']})")
            elif unit in MASS and mu not in MASS:
                warn(rid, f"dose unit {unit} and maxDailyDose unit {mu} are different kinds")


def check_interval_vs_max(rid, rec):
    """Dose x maximum administrations per day should not exceed the stated ceiling."""
    for ind in rec.get("indications", []):
        for reg in ind.get("dosageRegimens", []):
            iv = reg.get("dosingInterval", {})
            mx = reg.get("maxDailyDose")
            vals, unit = amounts(reg.get("dose", {}))
            if not (iv.get("minMinutes") and mx and vals and unit in MASS):
                continue
            if mx.get("unit") not in MASS:
                continue
            per_day = 1440 / iv["minMinutes"]
            reachable = max(vals) * MASS[unit] * per_day
            ceiling = mx["value"] * MASS[mx["unit"]]
            # A ceiling BELOW interval x dose is normal and intended: that is what
            # a daily maximum is for. A ceiling the interval cannot reach is not.
            if reachable < ceiling * 0.98:
                err(rid, f"maxDailyDose {mx['value']}{mx['unit']} is unreachable: "
                         f"{max(vals)}{unit} every {iv['minMinutes']}min tops out at "
                         f"{reachable:.4g}mg/day ({ind['name']})")


def check_open_ended(rid, rec):
    """An as-needed regimen with neither a daily ceiling nor a minimum interval
    is unbounded. The uploaded set had three."""
    for ind in rec.get("indications", []):
        for reg in ind.get("dosageRegimens", []):
            if not reg.get("asNeeded"):
                continue
            if not reg.get("maxDailyDose") and not reg.get("dosingInterval"):
                err(rid, f"as-needed regimen with no maxDailyDose and no dosingInterval "
                         f"({ind['name']}) — nothing bounds total daily exposure")
            elif not reg.get("maxDailyDose"):
                warn(rid, f"as-needed regimen with no maxDailyDose ({ind['name']})")


def check_field_semantics(rid, rec):
    """The uploaded cimetidine record held 45-90 min in `peakConcentration`:
    a time in a field named for a concentration."""
    for pk in rec.get("pharmacokinetics", []):
        for field, value in pk.items():
            if not isinstance(value, dict):
                continue
            unit = value.get("unit")
            if field in ("halfLife", "timeToOnset", "timeToPeak", "durationOfAction"):
                if unit and unit not in TIME:
                    err(rid, f"pharmacokinetics.{field} has unit {unit}, expected a time")
            if field == "peakConcentration" and unit in TIME:
                err(rid, f"pharmacokinetics.peakConcentration holds a time ({unit}) "
                         f"— should this be timeToPeak?")
        for f in ("bioavailability", "proteinBinding"):
            v = pk.get(f)
            if isinstance(v, dict):
                for k in ("value", "min", "max"):
                    if k in v and not (0 <= v[k] <= 1):
                        err(rid, f"pharmacokinetics.{f}.{k} = {v[k]}, expected a fraction 0-1")
        for f, lo, hi in [("volumeOfDistribution", 0.05, 25)]:
            v = pk.get(f)
            if isinstance(v, dict) and v.get("unit") == "L/kg":
                for k in ("value", "min", "max"):
                    if k in v and not (lo <= v[k] <= hi):
                        warn(rid, f"pharmacokinetics.{f}.{k} = {v[k]} L/kg is outside "
                                  f"the plausible {lo}-{hi} range")
        for f in ("halfLife", "timeToPeak", "durationOfAction", "timeToOnset"):
            v = pk.get(f)
            if isinstance(v, dict) and "min" in v and "max" in v and v["min"] > v["max"]:
                err(rid, f"pharmacokinetics.{f} has min > max")


def check_vocab(rid, rec, vocab):
    def chk(term, vname, where):
        terms = vocab.get(vname)
        if terms is None:
            return
        if term not in terms:
            (err if vocab.get(vname + "__closed") else warn)(
                rid, f"{where}: '{term}' is not in the {vname} vocabulary")

    for m in rec.get("mechanismsOfAction", []):
        chk(m["termId"], "mechanisms", "mechanismsOfAction")
        chk(m.get("evidence", "established"), "evidence-levels", "mechanismsOfAction.evidence")
    for p in rec.get("metabolismPathways", []):
        chk(p["termId"], "metabolism-pathways", "metabolismPathways")
        if "effect" in p:
            chk(p["effect"]["type"], "enzyme-effects", "metabolismPathways.effect")
    for t in rec.get("transporters", []):
        chk(t["termId"], "transporters", "transporters")
        chk(t["effect"]["type"], "enzyme-effects", "transporters.effect")
    for i in rec.get("interactions", []):
        chk(i["interactionType"], "interaction-types", "interactions")
        chk(i["severity"], "severity", "interactions.severity")
        chk(i.get("evidence", "established"), "evidence-levels", "interactions.evidence")
    for m in rec.get("activeMetabolites", []):
        chk(m["activity"], "metabolite-activity", "activeMetabolites.activity")
        if m.get("formedByPathway"):
            chk(m["formedByPathway"], "metabolism-pathways", "activeMetabolites.formedByPathway")
    for ind in rec.get("indications", []):
        chk(ind["labelStatus"], "label-status", "indications.labelStatus")
        for reg in ind.get("dosageRegimens", []):
            chk(reg["population"], "populations", "dosageRegimens.population")
            chk(reg["route"], "routes", "dosageRegimens.route")
            _, u = amounts(reg.get("dose", {}))
            if u: chk(u, "units", "dose.amount.unit")
    for pk in rec.get("pharmacokinetics", []):
        chk(pk["population"], "populations", "pharmacokinetics.population")
        if pk.get("route"): chk(pk["route"], "routes", "pharmacokinetics.route")
        if pk.get("absorptionModel"):
            chk(pk["absorptionModel"], "release-types", "pharmacokinetics.absorptionModel")


def check_refs(recs):
    ids = set(recs)
    for rid, rec in recs.items():
        for m in rec.get("activeMetabolites", []):
            if m.get("drugId") and m["drugId"] not in ids:
                err(rid, f"activeMetabolites references unknown record '{m['drugId']}'")
            if m.get("drugId") and m.get("formedByPathway"):
                declared = {p["termId"] for p in rec.get("metabolismPathways", [])}
                if m["formedByPathway"] not in declared:
                    warn(rid, f"metabolite '{m['name']}' is formed by "
                              f"'{m['formedByPathway']}', which this record does not declare "
                              f"in metabolismPathways")
        for p in rec.get("parentDrugIds", []):
            if p not in ids:
                err(rid, f"parentDrugIds references unknown record '{p}'")
            elif rid not in [m.get("drugId") for m in recs[p].get("activeMetabolites", [])]:
                warn(rid, f"claims '{p}' as parent, but that record does not list it back")
        seen = set()
        for i in rec.get("interactions", []):
            d = i["interactingDrug"]
            if d not in ids and not i.get("external") and " " not in d:
                warn(rid, f"interaction references unknown record '{d}' "
                          f"(add \"external\": true if this is deliberate)")
            key = (d, i["interactionType"])
            if key in seen:
                err(rid, f"duplicate interaction entry: {d} / {i['interactionType']}")
            seen.add(key)
        for s in rec.get("interactionScreening", []):
            if s["drugId"] not in ids:
                err(rid, f"screening references unknown record '{s['drugId']}'")


def check_coverage(recs):
    """Every drug pair must be either a finding or an explicit screening entry."""
    with open(f"{OUT}/index.json") as f:
        order = json.load(f)["canonicalOrder"]
    rank = {d: i for i, d in enumerate(order)}
    missing = []
    for rid in order:
        rec = recs[rid]
        covered = {i["interactingDrug"] for i in rec.get("interactions", [])}
        covered |= {s["drugId"] for s in rec.get("interactionScreening", [])}
        for other in order[:rank[rid]]:
            if other not in covered:
                missing.append(f"{rid} x {other}")
    if missing:
        err("coverage", f"{len(missing)} pair(s) neither screened nor flagged: "
                        + ", ".join(missing[:6]) + ("..." if len(missing) > 6 else ""))
    return len(order) * (len(order) - 1) // 2


def check_sources(recs):
    for rid, rec in recs.items():
        srcs = rec.get("sources", [])
        if not srcs:
            err(rid, "no sources")
        for s in srcs:
            if not s.get("publisher") or len(s.get("title", "")) < 4:
                err(rid, f"source '{s.get('id')}' has no real publisher or title "
                         f"(the uploaded set had sources titled 'google' and 'drive')")


if __name__ == "__main__":
    recs, vocab = load()
    for rid, rec in recs.items():
        check_dose_units(rid, rec)
        check_interval_vs_max(rid, rec)
        check_open_ended(rid, rec)
        check_field_semantics(rid, rec)
        check_vocab(rid, rec, vocab)
    check_refs(recs)
    check_sources(recs)
    total_pairs = check_coverage(recs)

    n_int = sum(len(r.get("interactions", [])) for r in recs.values())
    n_scr = sum(len(r.get("interactionScreening", [])) for r in recs.values())
    print(f"{len(recs)} records, {n_int} interaction findings, "
          f"{n_scr} explicit screening entries, {total_pairs} drug pairs total")
    for w in warns: print("WARN  " + w)
    for e in errors: print("ERROR " + e)
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s)")
    sys.exit(1 if errors else 0)
