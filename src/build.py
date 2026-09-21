#!/usr/bin/env python3
"""Emit the JSON dataset from the Python data modules.

Everything under /mnt/user-data/outputs is generated. Edit the modules in
src/, not the JSON, then re-run this.
"""
import json, os, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import drugs_b  # noqa: F401  (imports drugs_a and fills DRUGS)
from drugs_a import DRUGS
from metabolites import METABOLITES
from pairs import PAIRS, NEGATIVES, ORDER
from vocab import VOCAB

OUT = "/mnt/user-data/outputs"
SCHEMA_VERSION = "1.5.0"

SOURCE_TEMPLATES = {
    "merck":      ("Merck Manual Professional Edition", "{name} — Drug Information"),
    "ahfs":       ("Drugs.com / ASHP (AHFS DI)",        "{name} Monograph for Professionals"),
    "dailymed":   ("DailyMed, U.S. National Library of Medicine", "{name} — FDA label"),
    "statpearls": ("StatPearls, NCBI Bookshelf",        "{name}"),
    "drugbank":   ("DrugBank Online",                   "{name}"),
}

# ---------------------------------------------------------------- sources

def build_sources(rec_id, name, kinds):
    out = []
    for k in kinds:
        publisher, title_fmt = SOURCE_TEMPLATES[k]
        out.append({"id": f"{k}-{rec_id}", "title": title_fmt.format(name=name),
                    "publisher": publisher})
    return out

# ---------------------------------------------------------------- interactions

def place_pairs():
    """Put each finding on whichever drug comes later in ORDER."""
    rank = {d: i for i, d in enumerate(ORDER)}
    by_drug = collections.defaultdict(list)
    seen_pairs = collections.defaultdict(set)

    for p in PAIRS:
        a, b = p["a"], p["b"]
        if a not in rank or b not in rank:
            raise SystemExit(f"pair references unknown drug: {a} / {b}")
        later, earlier = (a, b) if rank[a] > rank[b] else (b, a)
        entry = {k: v for k, v in p.items() if k not in ("a", "b")}
        entry = {"interactingDrug": earlier, **entry}
        by_drug[later].append(entry)
        seen_pairs[later].add(earlier)

    for a, b, note in NEGATIVES:
        later, earlier = (a, b) if rank[a] > rank[b] else (b, a)
        seen_pairs[later].add(earlier)

    return by_drug, seen_pairs


def build_screening(drug_id, seen_pairs):
    """Every earlier drug is screened. Findings live in `interactions`;
    everything else is recorded here as an explicit clean result."""
    rank = {d: i for i, d in enumerate(ORDER)}
    notes = {(a if rank[a] > rank[b] else b, b if rank[a] > rank[b] else a): n
             for a, b, n in NEGATIVES}
    out = []
    for other in ORDER[:rank[drug_id]]:
        if other in seen_pairs.get(drug_id, set()):
            note = notes.get((drug_id, other))
            if note:
                out.append({"drugId": other, "result": "no-interaction-found", "note": note})
            # else: a positive finding exists in `interactions`; not repeated here
        else:
            entry = {"drugId": other, "result": "no-interaction-found"}
            if drug_id == "colestipol" or other == "colestipol":
                entry["result"] = "covered-by-class-rule"
                entry["note"] = "No individually documented pair. Colestipol's general labelling rule applies: give any other oral medication at least 1 hour before, or 4 hours after."
            out.append(entry)
    return out

# ---------------------------------------------------------------- assemble

FIELD_ORDER = [
    "schemaVersion", "id", "drugName", "synonyms", "recordType", "codes",
    "controlledSubstance", "parentDrugIds", "supersedes", "indications",
    "mechanismsOfAction", "metabolismPathways", "transporters",
    "activeMetabolites", "pharmacokinetics", "interactions",
    "interactionScreening", "knownAbsences", "sources", "notes",
]


def order_fields(rec):
    return {k: rec[k] for k in FIELD_ORDER if k in rec}


def assemble():
    by_drug, seen_pairs = place_pairs()
    records = {}

    for rec_id, raw in DRUGS.items():
        rec = dict(raw)
        kinds = rec.pop("srcs", [])
        rec["schemaVersion"] = SCHEMA_VERSION
        rec["id"] = rec_id
        rec["recordType"] = "drug"
        rec["sources"] = build_sources(rec_id, raw["drugName"], kinds)
        ints = by_drug.get(rec_id, [])
        if ints:
            rec.setdefault("interactions", [])
            rec["interactions"] = ints + rec.get("interactions", [])
        screening = build_screening(rec_id, seen_pairs)
        if screening:
            rec["interactionScreening"] = screening
        records[rec_id] = order_fields(rec)

    for rec_id, raw in METABOLITES.items():
        rec = dict(raw)
        kinds = rec.pop("srcs", [])
        rec["schemaVersion"] = SCHEMA_VERSION
        rec["id"] = rec_id
        rec["recordType"] = "metabolite"
        rec["sources"] = build_sources(rec_id, raw["drugName"], kinds)
        records[rec_id] = order_fields(rec)

    return records


def write(records):
    for name in ("drugs", "metabolites", "vocab"):
        os.makedirs(f"{OUT}/{name}", exist_ok=True)

    counts = collections.Counter()
    for rec_id, rec in records.items():
        sub = "drugs" if rec["recordType"] == "drug" else "metabolites"
        with open(f"{OUT}/{sub}/{rec_id}.json", "w") as f:
            json.dump(rec, f, indent=2, ensure_ascii=False)
            f.write("\n")
        counts[sub] += 1

    for name, v in VOCAB.items():
        with open(f"{OUT}/vocab/{name}.json", "w") as f:
            json.dump(v, f, indent=2, ensure_ascii=False)
            f.write("\n")
        counts["vocab"] += 1

    # A flat index, so a consumer does not have to open 35 files to list them.
    index = {
        "schemaVersion": SCHEMA_VERSION,
        "generated": "build.py",
        "canonicalOrder": ORDER,
        "drugs": sorted([
            {"id": r["id"], "drugName": r["drugName"],
             "file": f"drugs/{r['id']}.json",
             "interactionCount": len(r.get("interactions", [])),
             "activeMetabolites": [m["name"] for m in r.get("activeMetabolites", [])
                                   if m.get("activity") != "inactive"]}
            for r in records.values() if r["recordType"] == "drug"
        ], key=lambda d: d["id"]),
        "metabolites": sorted([
            {"id": r["id"], "drugName": r["drugName"],
             "file": f"metabolites/{r['id']}.json",
             "parentDrugIds": r.get("parentDrugIds", [])}
            for r in records.values() if r["recordType"] == "metabolite"
        ], key=lambda d: d["id"]),
        "vocabularies": sorted(f"vocab/{n}.json" for n in VOCAB),
    }
    with open(f"{OUT}/index.json", "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Flat interaction matrix: every finding, both directions, for querying.
    matrix = []
    for rec in records.values():
        for i in rec.get("interactions", []):
            matrix.append({
                "drugA": rec["id"], "drugB": i["interactingDrug"],
                "interactionType": i["interactionType"],
                "severity": i["severity"],
                "evidence": i.get("evidence", "established"),
                "suggestedAction": i.get("suggestedAction"),
                "note": i.get("note"),
            })
    matrix.sort(key=lambda m: ({"contraindicated": 0, "major": 1, "moderate": 2,
                                "minor": 3}[m["severity"]], m["drugA"], m["drugB"]))
    with open(f"{OUT}/interaction-matrix.json", "w") as f:
        json.dump({"schemaVersion": SCHEMA_VERSION,
                   "note": "Derived from the per-drug records by build.py. Each finding appears once, on the pair rather than on a direction. Do not edit by hand.",
                   "count": len(matrix), "interactions": matrix}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return counts, len(matrix)


if __name__ == "__main__":
    recs = assemble()
    counts, n_int = write(recs)
    sev = collections.Counter(
        i["severity"] for r in recs.values() for i in r.get("interactions", []))
    print(f"drugs={counts['drugs']}  metabolites={counts['metabolites']}  "
          f"vocab={counts['vocab']}")
    print(f"interaction findings={n_int}  " +
          "  ".join(f"{k}={v}" for k, v in sorted(sev.items())))
