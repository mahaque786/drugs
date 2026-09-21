#!/usr/bin/env python3
"""Generate PDF visualisations from the emitted dataset."""
import json, glob, os, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

OUT = "/mnt/user-data/outputs"
FIG = f"{OUT}/figures"
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.edgecolor": "#3d3d3d", "axes.labelcolor": "#1a1a1a",
    "text.color": "#1a1a1a", "figure.facecolor": "white",
    "pdf.fonttype": 42,
})

INK, MUTED, RULE = "#1a1a1a", "#6b6b6b", "#c9c9c9"
SEV_COLOR = {"major": "#a8201a", "moderate": "#d97706",
             "minor": "#e8c547", "clean": "#f2f4f2",
             "class-rule": "#d7e3ef", "none": "#ffffff"}
SEV_RANK = {"major": 3, "moderate": 2, "minor": 1}

# ---------------------------------------------------------------- load
recs = {}
for p in glob.glob(f"{OUT}/drugs/*.json") + glob.glob(f"{OUT}/metabolites/*.json"):
    r = json.load(open(p)); recs[r["id"]] = r
index = json.load(open(f"{OUT}/index.json"))
ORDER = index["canonicalOrder"]
matrix = json.load(open(f"{OUT}/interaction-matrix.json"))["interactions"]

SHORT = {
    "acetaminophen": "Acetaminophen", "amphetamine-ir": "Amphetamine IR",
    "amphetamine-xr": "Amphetamine XR", "aspirin": "Aspirin", "caffeine": "Caffeine",
    "cimetidine": "Cimetidine", "colestipol": "Colestipol",
    "daridorexant": "Daridorexant", "dextromethorphan": "Dextromethorphan",
    "diclofenac-tablets": "Diclofenac", "diphenhydramine": "Diphenhydramine",
    "esomeprazole": "Esomeprazole", "famotidine": "Famotidine",
    "ibuprofen": "Ibuprofen", "levocetirizine": "Levocetirizine",
    "loperamide": "Loperamide", "melatonin": "Melatonin", "naproxen": "Naproxen",
    "propranolol": "Propranolol", "pseudoephedrine-ir": "Pseudoephedrine",
    "sertraline": "Sertraline", "simethicone": "Simethicone",
    "temazepam": "Temazepam", "triazolam": "Triazolam",
}

def header(fig, title, subtitle=None):
    h = fig.get_size_inches()[1]
    gap = 0.30 / h                      # constant physical spacing, not fractional
    top = 1 - 0.42 / h
    fig.text(0.055, top, title, fontsize=15, weight="bold", color=INK, va="top")
    y = top - gap
    if subtitle:
        fig.text(0.055, y, subtitle, fontsize=8.5, color=MUTED, va="top",
                 linespacing=1.5)
        y -= gap * 0.62 * subtitle.count("\n") + gap * 0.55
    fig.add_artist(plt.Line2D([0.055, 0.945], [y, y], color=RULE, lw=0.8))
    return y

def footer(fig, text):
    fig.text(0.055, 0.028, text, fontsize=6.8, color=MUTED, style="italic")

pages = []

# ================================================================ 1 cover
def page_cover():
    fig = plt.figure(figsize=(11, 8.5))
    fig.text(0.5, 0.80, "Drug Interaction Dataset", ha="center", fontsize=30,
             weight="bold", color=INK)
    fig.text(0.5, 0.745, "24 drugs  ·  11 active metabolites  ·  schema 1.5.0",
             ha="center", fontsize=12, color=MUTED)
    fig.add_artist(plt.Line2D([0.28, 0.72], [0.705, 0.705], color=RULE, lw=1))

    sev = collections.Counter(i["severity"] for i in matrix)
    itype = collections.Counter(i["interactionType"] for i in matrix)
    n_scr = sum(len(r.get("interactionScreening", [])) for r in recs.values())
    n_meta = sum(1 for r in recs.values() if r["recordType"] == "metabolite")

    stats = [
        ("Drug records", "24"), ("Active metabolite records", str(n_meta)),
        ("Controlled vocabularies", "13"),
        ("Drug pairs (24 choose 2)", "276"),
        ("Interaction findings", str(len(matrix))),
        ("   major", str(sev["major"])), ("   moderate", str(sev["moderate"])),
        ("   minor", str(sev["minor"])),
        ("Explicit screening entries", str(n_scr)),
        ("Pair coverage", "100%"),
    ]
    y = 0.615
    for label, v in stats:
        ind = 0.06 if label.startswith("   ") else 0.0
        fig.text(0.30 + ind, y, label.strip(), fontsize=9.5,
                 color=MUTED if ind else INK)
        fig.text(0.70, y, v, fontsize=9.5, ha="right",
                 color=MUTED if ind else INK,
                 weight="normal" if ind else "bold")
        y -= 0.0335

    fig.text(0.5, 0.225, "Sources: Merck Manual Professional · AHFS DI (Drugs.com) · DailyMed\n"
             "StatPearls (NCBI) · DrugBank", ha="center", fontsize=8, color=MUTED)
    fig.text(0.5, 0.135,
             "Reference data assembled from tertiary sources.\n"
             "Not a clinical decision tool. Not reviewed by a pharmacist.",
             ha="center", fontsize=8.5, color="#a8201a", weight="bold")
    return fig

# ================================================================ 2 matrix
def page_matrix():
    n = len(ORDER)
    idx = {d: i for i, d in enumerate(ORDER)}
    grid = np.full((n, n), "none", dtype=object)
    counts = np.zeros((n, n), dtype=int)

    for d in ORDER:
        for s in recs[d].get("interactionScreening", []):
            if s["drugId"] in idx:
                v = "class-rule" if s.get("result") == "covered-by-class-rule" else "clean"
                grid[idx[d]][idx[s["drugId"]]] = v
                grid[idx[s["drugId"]]][idx[d]] = v
    for i in matrix:
        if i["drugA"] not in idx or i["drugB"] not in idx:
            continue
        a, b = idx[i["drugA"]], idx[i["drugB"]]
        cur = grid[a][b]
        if cur not in SEV_RANK or SEV_RANK[i["severity"]] > SEV_RANK[cur]:
            grid[a][b] = grid[b][a] = i["severity"]
        counts[a][b] += 1; counts[b][a] += 1

    fig = plt.figure(figsize=(11, 10.4))
    header(fig, "Interaction matrix",
           "All 276 pairs. Colour is the highest severity found; a number marks pairs with more than one "
           "distinct finding.\nPale cells were screened and found clean — a recorded result, not an untested gap.")
    ax = fig.add_axes([0.235, 0.155, 0.70, 0.715])

    for r in range(n):
        for c in range(n):
            if r == c:
                ax.add_patch(Rectangle((c, n - 1 - r), 1, 1, facecolor="#e6e6e6",
                                       edgecolor="white", lw=0.6)); continue
            ax.add_patch(Rectangle((c, n - 1 - r), 1, 1,
                                   facecolor=SEV_COLOR[grid[r][c]],
                                   edgecolor="white", lw=0.6))
            if counts[r][c] > 1:
                ax.text(c + .5, n - 1 - r + .5, str(counts[r][c]), ha="center",
                        va="center", fontsize=6, color="white", weight="bold")

    ax.set_xlim(0, n); ax.set_ylim(0, n); ax.set_aspect("equal")
    ax.set_xticks(np.arange(n) + .5); ax.set_yticks(np.arange(n) + .5)
    ax.set_xticklabels([SHORT[d] for d in ORDER], rotation=90, fontsize=7)
    ax.set_yticklabels([SHORT[d] for d in reversed(ORDER)], fontsize=7)
    ax.tick_params(length=0)
    for sp in ax.spines.values(): sp.set_visible(False)

    lx = 0.235
    for lab, key in [("Major", "major"), ("Moderate", "moderate"), ("Minor", "minor"),
                     ("Screened clean", "clean"), ("Class rule", "class-rule")]:
        fig.patches.append(Rectangle((lx, 0.884), 0.016, 0.014, facecolor=SEV_COLOR[key],
                                     edgecolor="#b0b0b0", lw=0.5,
                                     transform=fig.transFigure, figure=fig))
        fig.text(lx + 0.021, 0.8885, lab, fontsize=7.5, va="center", color=INK)
        lx += 0.105 + 0.032 * (len(lab) > 8)
    footer(fig, "Symmetric. The stored records write each finding once, on whichever drug comes later in canonical order.")
    return fig

# ================================================================ 3 major table
def pages_major():
    majors = [i for i in matrix if i["severity"] == "major" and i["drugA"] in SHORT]
    groups = collections.OrderedDict([
        ("Serotonergic and CYP2D6 - the sertraline cluster", []),
        ("NSAID stacking and bleeding risk", []),
        ("Sedative stacking", []),
        ("CYP3A4 inhibition", []),
        ("Sympathomimetic and unopposed alpha", []),
        ("Absorption", []),
    ])
    for i in majors:
        pair = {i["drugA"], i["drugB"]}
        t = i["interactionType"]
        if "sertraline" in pair and t in ("pd-additive-toxicity", "pk-metabolism"):
            k = "Serotonergic and CYP2D6 - the sertraline cluster"
        elif pair <= {"aspirin", "ibuprofen", "naproxen", "diclofenac-tablets"}:
            k = "NSAID stacking and bleeding risk"
        elif t == "pd-additive-cns-depression" or (t == "therapeutic-duplication" and
             pair <= {"temazepam", "triazolam", "daridorexant", "diphenhydramine"}):
            k = "Sedative stacking"
        elif t == "pk-metabolism":
            k = "CYP3A4 inhibition"
        elif t == "pk-absorption":
            k = "Absorption"
        else:
            k = "Sympathomimetic and unopposed alpha"
        groups[k].append(i)

    TYPE_LABEL = {"pd-additive-toxicity": "additive toxicity",
                  "pd-additive-cns-depression": "additive CNS depression",
                  "pd-antagonism": "antagonism", "pd-synergism": "synergism",
                  "pk-metabolism": "metabolism", "pk-absorption": "absorption",
                  "pk-transporter": "transporter",
                  "therapeutic-duplication": "duplication"}

    def wrap(txt, width=112):
        out, line = [], ""
        for w in txt.split():
            if len(line) + len(w) + 1 > width:
                out.append(line); line = w
            else:
                line = (line + " " + w).strip()
        out.append(line)
        return out

    # Lay out as a stream of blocks, then break into pages when the cursor runs low.
    blocks = []
    for gname, items in groups.items():
        if not items: continue
        blocks.append(("head", gname, None))
        for i in items:
            blocks.append(("item", i, wrap(i["note"])))

    out_pages, cursor, fig, ax = [], None, None, None
    BOTTOM, TOP = 0.055, None

    def new_page(first):
        nonlocal fig, ax, cursor
        fig = plt.figure(figsize=(11, 8.5))
        y0 = header(fig, "Major interactions" + ("" if first else " (continued)"),
            f"{len(majors)} drug-drug findings graded major, grouped by mechanism. Severity grades the "
            "consequence;\ncertainty is recorded separately as evidence. Suggested actions are in the records."
            if first else "Continued from the previous page.")
        cursor = y0 - 0.045
        ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        footer(fig, "Full suggested actions are in each drug record and in interaction-matrix.json.")
        out_pages.append(fig)

    new_page(True)
    pending_head = None
    for kind, payload, extra in blocks:
        if kind == "head":
            pending_head = payload
            continue
        need = 0.0175 + 0.0132 * len(extra) + 0.010
        if pending_head:
            need += 0.040
        if cursor - need < BOTTOM:
            new_page(False)
            if pending_head is None:
                pending_head = None
        if pending_head:
            ax.text(0.055, cursor, pending_head.upper(), fontsize=8,
                    weight="bold", color="#a8201a")
            cursor -= 0.009
            ax.plot([0.055, 0.945], [cursor, cursor], color="#e2cfce", lw=0.8)
            cursor -= 0.0225
            pending_head = None
        i = payload
        a, b = SHORT.get(i["drugA"], i["drugA"]), SHORT.get(i["drugB"], i["drugB"])
        ax.text(0.055, cursor, f"{a}  +  {b}", fontsize=8.6, weight="bold", color=INK)
        ax.text(0.945, cursor, TYPE_LABEL.get(i["interactionType"], i["interactionType"]),
                fontsize=7.2, color=MUTED, ha="right", style="italic")
        cursor -= 0.0175
        for ln in extra:
            ax.text(0.068, cursor, ln, fontsize=7.1, color="#454545")
            cursor -= 0.0132
        cursor -= 0.010
    return out_pages

# ================================================================ 4 enzyme grid
def page_enzymes():
    enz = ["cyp1a2", "cyp2b6", "cyp2c8", "cyp2c9", "cyp2c19", "cyp2d6", "cyp2e1",
           "cyp3a4", "glucuronidation", "hydrolysis", "renal-excretion-unchanged",
           "not-absorbed"]
    label = {"cyp1a2": "1A2", "cyp2b6": "2B6", "cyp2c8": "2C8", "cyp2c9": "2C9",
             "cyp2c19": "2C19", "cyp2d6": "2D6", "cyp2e1": "2E1", "cyp3a4": "3A4",
             "glucuronidation": "Glucuronidation", "hydrolysis": "Hydrolysis",
             "renal-excretion-unchanged": "Renal, unchanged",
             "not-absorbed": "Unabsorbed"}
    fig = plt.figure(figsize=(11, 9.6))
    header(fig, "Metabolic routes and enzyme effects",
           "S = substrate (cleared by it)   ·   I = inhibitor (raises other substrates)   ·   S/I = both.\n"
           "Every pharmacokinetic interaction in the dataset is an I in one row meeting an S in the same column.")
    ax = fig.add_axes([0.235, 0.135, 0.685, 0.685])
    n, m = len(ORDER), len(enz)

    for r, d in enumerate(ORDER):
        rowmap = {}
        for p in recs[d].get("metabolismPathways", []):
            rowmap[p["termId"]] = p.get("effect", {}).get("type", "substrate")
        for c, e in enumerate(enz):
            yy = n - 1 - r
            eff = rowmap.get(e)
            if eff is None:
                ax.add_patch(Rectangle((c, yy), 1, 1, facecolor="#fafafa",
                                       edgecolor="white", lw=0.7)); continue
            if eff == "inhibitor": fc, tx, tc = "#a8201a", "I", "white"
            elif eff == "substrate-and-inhibitor": fc, tx, tc = "#d97706", "S/I", "white"
            elif eff == "inducer": fc, tx, tc = "#7d5ba6", "IND", "white"
            else: fc, tx, tc = "#cfdae6", "S", "#1a3348"
            ax.add_patch(Rectangle((c, yy), 1, 1, facecolor=fc, edgecolor="white", lw=0.7))
            ax.text(c + .5, yy + .5, tx, ha="center", va="center",
                    fontsize=6.6 if len(tx) > 1 else 7.4, color=tc, weight="bold")

    ax.add_patch(Rectangle((0, 0), m, n, fill=False, edgecolor="#d5d5d5", lw=0.8))
    ax.plot([8, 8], [-0.75, n], color="#9a9a9a", lw=1.1, clip_on=False)
    ax.set_xlim(0, m); ax.set_ylim(0, n)
    ax.set_xticks(np.arange(m) + .5); ax.set_yticks(np.arange(n) + .5)
    ax.set_xticklabels([label[e] for e in enz], rotation=52, ha="left", fontsize=7.2)
    ax.xaxis.set_ticks_position("top")
    ax.set_yticklabels([SHORT[d] for d in reversed(ORDER)], fontsize=7.5)
    ax.tick_params(length=0)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.text(4, -1.15, "cytochrome P450", fontsize=7, color=MUTED,
            style="italic", ha="center")
    ax.text(10, -1.15, "phase II and non-metabolic", fontsize=7, color=MUTED,
            style="italic", ha="center")

    fig.text(0.055, 0.075,
        "Read the two contrast pairs off this grid. Cimetidine carries four I marks; famotidine carries none — same drug class,\n"
        "same indication. Triazolam is a single S under 3A4 with no alternative route; temazepam sits under glucuronidation, which\n"
        "no inhibitor in this set touches. That is why cimetidine + triazolam is major and cimetidine + temazepam is nothing at all.",
        fontsize=7.4, color="#454545")
    return fig

# ================================================================ 5 metabolites
def page_metabolites():
    fig = plt.figure(figsize=(11, 8.5))
    header(fig, "Active metabolites",
           "Metabolites get their own record when something is true of them that is not true of the parent: "
           "their own mechanism,\ntheir own disposal route, their own half-life, or their own interactions.")
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    tree = [
        ("Acetaminophen", [("NAPQI", "CYP2E1, 5-10%", "toxic"),
                           ("AM404", "hydrolysis, ~1%", "therapeutic")]),
        ("Aspirin", [("Salicylic acid", "hydrolysis, ~100%", "mixed")]),
        ("Caffeine", [("Paraxanthine", "CYP1A2, 84%", "therapeutic")]),
        ("Dextromethorphan", [("Dextrorphan", "CYP2D6", "therapeutic")]),
        ("Amphetamine IR / XR", [("4-hydroxyamphetamine", "CYP2D6", "therapeutic")]),
        ("Diphenhydramine", [("Nordiphenhydramine", "CYP2D6", "therapeutic")]),
        ("Propranolol", [("4-hydroxypropranolol", "CYP2D6, first pass", "therapeutic")]),
        ("Sertraline", [("N-desmethylsertraline", "CYP2B6", "therapeutic")]),
        ("Temazepam", [("Oxazepam", "CYP3A4, ~5%", "therapeutic")]),
        ("Triazolam", [("alpha-hydroxytriazolam", "CYP3A4", "therapeutic")]),
    ]
    ACT = {"toxic": "#a8201a", "therapeutic": "#2d6a4f", "mixed": "#d97706"}
    y = 0.845
    for parent, kids in tree:
        ax.add_patch(FancyBboxPatch((0.055, y - 0.019), 0.215, 0.032,
                     boxstyle="round,pad=0.004,rounding_size=0.006",
                     facecolor="#eef1f4", edgecolor="#b8c4ce", lw=0.8))
        ax.text(0.1625, y - 0.0035, parent, fontsize=8.6, ha="center",
                va="center", weight="bold", color=INK)
        for j, (name, route, act) in enumerate(kids):
            ky = y - j * 0.041
            ax.add_patch(FancyArrowPatch((0.272, y - 0.003), (0.405, ky - 0.003),
                         arrowstyle="-|>", mutation_scale=9, color="#9aa7b1", lw=0.9,
                         connectionstyle="arc3,rad=0" if len(kids) == 1 else "arc3,rad=0.12"))
            ax.text(0.338, (y + ky) / 2 + 0.008, route, fontsize=6.4, color=MUTED,
                    ha="center", style="italic")
            ax.add_patch(FancyBboxPatch((0.408, ky - 0.019), 0.255, 0.032,
                         boxstyle="round,pad=0.004,rounding_size=0.006",
                         facecolor="white", edgecolor=ACT[act], lw=1.1))
            ax.text(0.42, ky - 0.003, name, fontsize=8.2, va="center", color=INK)
            ax.text(0.671, ky - 0.003, {"therapeutic": "active", "toxic": "TOXIC",
                    "mixed": "mixed"}[act], fontsize=6.9, va="center",
                    color=ACT[act], weight="bold")
        y -= 0.041 * len(kids) + 0.0305

    ax.plot([0.737, 0.737], [0.16, 0.855], color=RULE, lw=0.8)
    ax.text(0.762, 0.845, "WHY THESE HAVE THEIR OWN RECORDS", fontsize=7.3,
            weight="bold", color=MUTED)
    notes = [
        ("NAPQI", "Its own mechanism (protein arylation) and its own\nantidote. Too reactive to have plasma PK at all —\nrecorded as a settled absence, not a pending one."),
        ("Salicylic acid", "Carries almost all of aspirin's systemic activity.\nSaturable elimination, so its half-life runs 2-3 h\nat low dose and 15-30 h at high dose."),
        ("Dextrorphan", "A CYP2D6 inhibitor raises the parent and suppresses\nthis at the same time. Effects redistribute between\ntwo different receptor profiles rather than adding up."),
        ("N-desmethylsertraline", "Only 1/20 as potent, but a 62-104 h half-life against\nthe parent's 26 h. It governs the washout, which is\nwhy sertraline interactions outlast the last dose."),
        ("Paraxanthine", "84% of a caffeine dose passes through it at\ncomparable potency. Much of what is experienced\nas caffeine is really this."),
    ]
    ny = 0.805
    for name, body in notes:
        ax.text(0.762, ny, name, fontsize=8, weight="bold", color=INK); ny -= 0.021
        for ln in body.split("\n"):
            ax.text(0.762, ny, ln, fontsize=6.9, color="#454545"); ny -= 0.0148
        ny -= 0.017
    footer(fig, "Inactive metabolites are recorded on the parent with activity 'inactive' — a finding, not an empty array.")
    return fig

# ================================================================ 6 PK
def page_pk():
    def hours(v):
        if not v: return None
        u = v.get("unit", "h"); f = {"min": 1/60, "h": 1, "d": 24}.get(u, 1)
        if "value" in v: return (v["value"]*f, v["value"]*f)
        return (v.get("min", 0)*f, v.get("max", 0)*f)

    rows = []
    for d in ORDER:
        pk = recs[d].get("pharmacokinetics", [])
        if not pk: continue
        p = pk[0]
        hl, doa, tp = hours(p.get("halfLife")), hours(p.get("durationOfAction")), hours(p.get("timeToPeak"))
        if hl: rows.append((SHORT[d], hl, doa, tp))
    rows.sort(key=lambda r: r[1][0])

    fig = plt.figure(figsize=(11, 8.9))
    header(fig, "Pharmacokinetics at a glance",
           "Elimination half-life (bar) against duration of clinical effect (line) and time to peak (dot). "
           "Log scale.\nWhere the two disagree, the mechanism rather than the kinetics is setting the dosing interval.")
    ax = fig.add_axes([0.20, 0.155, 0.745, 0.675])
    for i, (name, hl, doa, tp) in enumerate(rows):
        y = len(rows) - 1 - i
        lo, hi = max(hl[0], 0.08), max(hl[1], 0.1)
        if hi <= lo * 1.001:            # point value: give it visible width
            lo, hi = lo * 0.93, hi * 1.07
        ax.barh(y, hi - lo, left=lo, height=0.52, color="#cfdae6",
                edgecolor="#8fa6ba", lw=0.7, zorder=2)
        if doa:
            d0, d1 = max(doa[0], .08), max(doa[1], .1)
            if d1 <= d0 * 1.001:        # point value: give it visible width
                d0, d1 = d0 * 0.94, d1 * 1.06
            ax.plot([d0, d1], [y - 0.30, y - 0.30], color="#a8201a", lw=2.1,
                    solid_capstyle="round", zorder=3)
        if tp:
            ax.plot([(tp[0] + tp[1]) / 2], [y + 0.02], "o", ms=3.6,
                    color="#2d6a4f", zorder=4)
    ax.set_xscale("log")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=7.8)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_xlim(0.08, 130)
    ax.set_xticks([0.25, 0.5, 1, 2, 4, 8, 12, 24, 48, 96])
    ax.set_xticklabels(["15 min", "30 min", "1 h", "2 h", "4 h", "8 h", "12 h",
                        "24 h", "48 h", "96 h"], fontsize=7)
    ax.set_xlabel("time (log scale)", fontsize=8, color=MUTED)
    ax.grid(axis="x", color="#ededed", lw=0.7, zorder=0)
    ax.tick_params(length=0)
    for sp in ["top", "right", "left"]: ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(RULE)

    lx = 0.20
    for color, lab, kind in [("#cfdae6", "elimination half-life", "bar"),
                             ("#a8201a", "duration of action", "line"),
                             ("#2d6a4f", "time to peak", "dot")]:
        if kind == "bar":
            fig.patches.append(Rectangle((lx, 0.8555), 0.02, 0.011, facecolor=color,
                               edgecolor="#8fa6ba", lw=0.6, transform=fig.transFigure, figure=fig))
        elif kind == "line":
            fig.add_artist(plt.Line2D([lx, lx + 0.02], [0.861, 0.861], color=color, lw=2.1))
        else:
            fig.add_artist(plt.Line2D([lx + 0.01], [0.861], marker="o", ms=3.6, color=color))
        fig.text(lx + 0.026, 0.8608, lab, fontsize=7.4, va="center", color=INK)
        lx += 0.175
    fig.text(0.055, 0.045,
        "Aspirin is the clearest case where half-life misleads: 15-20 minutes for intact drug, 4-6 hours of analgesia carried by salicylate,\n"
        "and 7-10 days of antiplatelet effect set by platelet turnover. Esomeprazole is the same story — a 1 h half-life, 24 h of acid\n"
        "suppression, because it binds the pump covalently. Neither is derivable from the kinetics.",
        fontsize=7.4, color="#454545")
    return fig

# ================================================================ 7 clusters
def page_clusters():
    fig = plt.figure(figsize=(11, 8.5))
    header(fig, "The two interaction hubs",
           "Where findings concentrate. Neither cluster is caught by a duplication check that reasons from drug class.")
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    def cluster(cx, cy, r, nodes, edges, title, sub, color):
        ax.text(cx, cy + r + 0.115, title, fontsize=10.5, weight="bold",
                ha="center", color=INK)
        ax.text(cx, cy + r + 0.083, sub, fontsize=7.4, ha="center", color=MUTED)
        pos = {}
        for i, nm in enumerate(nodes):
            a = np.pi / 2 - 2 * np.pi * i / len(nodes)
            pos[nm] = (cx + r * np.cos(a) * 1.08, cy + r * np.sin(a))
        for a, b, sev in edges:
            ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]],
                    color=SEV_COLOR[sev], lw=2.0 if sev == "major" else 1.0,
                    alpha=0.75 if sev == "major" else 0.45, zorder=1,
                    solid_capstyle="round")
        for nm, (x, y) in pos.items():
            w = 0.0093 * len(nm) + 0.017
            ax.add_patch(FancyBboxPatch((x - w/2, y - 0.017), w, 0.032,
                         boxstyle="round,pad=0.003,rounding_size=0.007",
                         facecolor="white", edgecolor=color, lw=1.3, zorder=3))
            ax.text(x, y - 0.001, nm, fontsize=6.9, ha="center", va="center",
                    zorder=4, color=INK, weight="bold")

    sed = ["Diphenhydramine", "Levocetirizine", "Melatonin", "Temazepam",
           "Triazolam", "Daridorexant"]
    sed_e = [("Diphenhydramine", "Temazepam", "major"),
             ("Diphenhydramine", "Triazolam", "major"),
             ("Diphenhydramine", "Daridorexant", "major"),
             ("Diphenhydramine", "Melatonin", "moderate"),
             ("Diphenhydramine", "Levocetirizine", "moderate"),
             ("Levocetirizine", "Temazepam", "moderate"),
             ("Levocetirizine", "Triazolam", "moderate"),
             ("Levocetirizine", "Melatonin", "moderate"),
             ("Levocetirizine", "Daridorexant", "moderate"),
             ("Melatonin", "Temazepam", "moderate"),
             ("Melatonin", "Triazolam", "moderate"),
             ("Melatonin", "Daridorexant", "moderate"),
             ("Temazepam", "Triazolam", "major"),
             ("Temazepam", "Daridorexant", "major"),
             ("Triazolam", "Daridorexant", "major")]
    cluster(0.262, 0.585, 0.125, sed, sed_e, "Sedative stacking",
            "15 pairs, 6 of them major", "#7d5ba6")

    ser = ["Sertraline", "Dextromethorphan", "Amphetamine IR", "Amphetamine XR",
           "Propranolol", "Ibuprofen", "Naproxen", "Aspirin"]
    ser_e = [("Sertraline", "Dextromethorphan", "major"),
             ("Sertraline", "Amphetamine IR", "major"),
             ("Sertraline", "Amphetamine XR", "major"),
             ("Sertraline", "Propranolol", "major"),
             ("Sertraline", "Ibuprofen", "major"),
             ("Sertraline", "Naproxen", "major"),
             ("Sertraline", "Aspirin", "major"),
             ("Dextromethorphan", "Amphetamine IR", "moderate"),
             ("Dextromethorphan", "Amphetamine XR", "moderate"),
             ("Ibuprofen", "Naproxen", "major"),
             ("Ibuprofen", "Aspirin", "major"),
             ("Naproxen", "Aspirin", "major")]
    cluster(0.722, 0.585, 0.125, ser, ser_e, "Sertraline as hub",
            "major against 7 of the other 23 records", "#a8201a")

    ax.plot([0.055, 0.945], [0.335, 0.335], color=RULE, lw=0.8)
    blocks = [
        ("Five sedatives, four mechanisms",
         "GABA-A (temazepam, triazolam), H1 (diphenhydramine,\n"
         "levocetirizine), orexin (daridorexant) and MT1/MT2\n"
         "(melatonin). Because the mechanisms differ, no class-based\n"
         "duplication check flags any of these fifteen pairs — but the\n"
         "impairment is additive regardless of mechanism."),
        ("One property, most of the findings",
         "Moderate CYP2D6 inhibition explains sertraline against\n"
         "dextromethorphan and propranolol; platelet serotonin\n"
         "depletion explains it against all four NSAIDs. Both scale\n"
         "with sertraline dose, so the interaction can surface weeks\n"
         "after both drugs were started without anything changing."),
        ("What the data says to do",
         "Acetaminophen is screened clean against sertraline and\n"
         "against every NSAID — the substitution that resolves the\n"
         "bleeding cluster. Famotidine is clean where cimetidine is\n"
         "major, and temazepam clean where triazolam is major.\n"
         "The negatives carry as much of the answer as the positives."),
    ]
    for i, (h, body) in enumerate(blocks):
        x = 0.055 + i * 0.3
        ax.text(x, 0.295, h, fontsize=8.4, weight="bold", color=INK)
        yy = 0.269
        for ln in body.split("\n"):
            ax.text(x, yy, ln, fontsize=7.1, color="#454545"); yy -= 0.0165
    return fig

pages.append(page_cover())
pages.append(page_matrix())
major_pages = pages_major()
pages.extend(major_pages)
pages.append(page_enzymes())
pages.append(page_metabolites())
pages.append(page_pk())
pages.append(page_clusters())

names = (["00-cover", "01-interaction-matrix"]
         + [f"02-major-interactions-{i+1}" for i in range(len(major_pages))]
         + ["03-enzyme-routes", "04-active-metabolites", "05-pharmacokinetics",
            "06-interaction-hubs"])
for fig, nm in zip(pages, names):
    fig.savefig(f"{FIG}/{nm}.pdf", format="pdf")

with PdfPages(f"{OUT}/drug-interaction-atlas.pdf") as pdf:
    for fig in pages:
        pdf.savefig(fig)
    d = pdf.infodict()
    d["Title"] = "Drug Interaction Dataset — Visual Atlas"
    d["Subject"] = "24 drugs, 11 active metabolites, 116 interaction findings, schema 1.5.0"
    d["Creator"] = "build from src/"
for fig in pages: plt.close(fig)
print(f"wrote {len(pages)}-page atlas + {len(names)} individual figures")
