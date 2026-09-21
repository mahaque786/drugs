"""Drug records, part 1. See build.py for how these are assembled."""

# ---------- tiny constructors, so the data below stays readable ----------

def rng(lo, hi, unit=None):
    d = {"min": lo, "max": hi}
    if unit:
        d["unit"] = unit
    return d

def val(v, unit=None):
    d = {"value": v}
    if unit:
        d["unit"] = unit
    return d

def steps(xs, unit):
    return {"steps": xs, "unit": unit}

def flat(amount):
    return {"basis": "flat", "amount": amount}

def perkg(amount):
    return {"basis": "per-kg", "amount": amount}

def every(lo_min, hi_min=None):
    d = {"minMinutes": lo_min}
    if hi_min is not None:
        d["maxMinutes"] = hi_min
    return d

def moa(term, evidence="established", note=None):
    d = {"termId": term, "evidence": evidence}
    if note:
        d["note"] = note
    return d

def path(term, enzyme=None, effect=None, fraction=None, note=None):
    d = {"termId": term}
    if enzyme:
        d["enzyme"] = enzyme
    if effect:
        d["effect"] = {"type": effect}
    if fraction is not None:
        d["fractionOfDose"] = fraction
    if note:
        d["note"] = note
    return d

def transporter(term, effect, note=None):
    d = {"termId": term, "effect": {"type": effect}}
    if note:
        d["note"] = note
    return d

def metabolite(name, drug_id=None, activity="therapeutic", potency=None,
               pathway=None, enzyme=None, fraction=None, note=None):
    d = {"name": name}
    if drug_id:
        d["drugId"] = drug_id
    d["activity"] = activity
    if potency:
        d["potencyVsParent"] = potency
    if pathway:
        d["formedByPathway"] = pathway
    if enzyme:
        d["enzyme"] = enzyme
    if fraction is not None:
        d["fractionOfDose"] = fraction
    if note:
        d["note"] = note
    return d

def absent(field, note, status="not-reported"):
    return {"field": field, "status": status, "note": note}


DRUGS = {}

# ---------------------------------------------------------------- 1
DRUGS["acetaminophen"] = {
    "drugName": "Acetaminophen",
    "synonyms": ["Paracetamol", "APAP"],
    "codes": {"rxcui": "161", "unii": "362O9ITL9D", "atc": ["N02BE01"]},
    "srcs": ["merck", "ahfs", "statpearls"],
    "indications": [
        {"name": "Pain", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([325, 650], "mg")),
             "dosingInterval": every(240, 360), "asNeeded": True,
             "maxDailyDose": val(3900, "mg"), "maxDurationDays": 10,
             "notes": "Adults and adolescents at least 50 kg. OTC labelling in some markets caps the daily total below the prescription ceiling; confirm against the specific product label."},
            {"population": "adult", "route": "oral", "dose": flat(val(1000, "mg")),
             "dosingInterval": every(360, 480), "asNeeded": True,
             "maxDailyDose": val(4000, "mg"), "maxDurationDays": 10,
             "notes": "Adults and adolescents at least 50 kg."},
        ]},
        {"name": "Fever", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([325, 650], "mg")),
             "dosingInterval": every(240, 360), "asNeeded": True,
             "maxDailyDose": val(3900, "mg"), "maxDurationDays": 3},
            {"population": "pediatric", "route": "oral", "dose": perkg(rng(10, 15, "mg/kg")),
             "dosingInterval": every(240, 360), "asNeeded": True,
             "maxDailyDose": val(75, "mg/kg"),
             "notes": "Weight-based. Daily ceiling is the lesser of 75 mg/kg and the adult maximum."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("cox-inhibition-central", "proposed", "Reduced CNS prostaglandin synthesis follows from this rather than being a separate mechanism."),
        moa("serotonergic-descending-modulation", "proposed"),
        moa("trpv1-activation", "proposed"),
    ],
    "metabolismPathways": [
        path("glucuronidation", fraction=rng(0.5, 0.7), note="Major conjugation route in adults."),
        path("sulfate-conjugation", fraction=rng(0.25, 0.35)),
        path("cyp2e1", enzyme="CYP2E1", effect="substrate", fraction=rng(0.05, 0.1),
             note="Minor by fraction of dose, but the route that produces NAPQI and drives hepatotoxicity in overdose. Migrated from the generic cyp450-oxidation term in 1.5."),
        path("glutathione-conjugation", note="Detoxifies NAPQI. Saturable, which is why overdose behaves so differently from therapeutic dosing."),
        path("hydrolysis", fraction=val(0.01),
             note="Deacetylation to p-aminophenol, which is then conjugated with arachidonic acid to form AM404. Declared here in 1.5: the uploaded record listed AM404 as formedByPathway `hydrolysis` without the record declaring that pathway, so the metabolite pointed at a route the parent did not have."),
    ],
    "activeMetabolites": [
        metabolite("NAPQI", "napqi", "toxic", "more-potent", "cyp2e1", "CYP2E1", rng(0.05, 0.1),
                   "What belongs here is that this drug produces it, out of which pathway, and in what proportion. What NAPQI does, and how the body disposes of it, is on the napqi record."),
        metabolite("AM404", "am404", "therapeutic", "comparable", "hydrolysis", None, val(0.01),
                   "Formed by FAAH-mediated conjugation of the p-aminophenol deacetylation product with arachidonic acid, in brain and spinal cord rather than liver."),
    ],
    "pharmacokinetics": [
        {"population": "adult-healthy", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(2, 3, "h"), "bioavailability": rng(0.85, 0.98),
         "volumeOfDistribution": val(1, "L/kg"), "proteinBinding": rng(0.1, 0.25),
         "timeToPeak": rng(30, 60, "min"),
         "notes": "Half-life converted from minutes to hours in 1.5 so it sorts against every other record."},
    ],
    "knownAbsences": [
        absent("pharmacokinetics[0].timeToOnset", "Sources give time to peak plasma concentration, which is a different quantity and is now recorded in timeToPeak. Onset itself is checked and not stated."),
        absent("pharmacokinetics[0].durationOfAction", "Implied by the 4-6 hour dosing interval rather than stated as a measured quantity."),
    ],
    "notes": "Migrated from schema 1.0. Three changes worth knowing about: the CYP term moved from cyp450-oxidation to cyp2e1, half-life moved from minutes to hours, and the cannabinoid-am404 mechanism moved off this record onto am404, matching how NAPQI is already handled.",
}

# ---------------------------------------------------------------- 2
DRUGS["amphetamine-ir"] = {
    "drugName": "Dextroamphetamine/Amphetamine, immediate release",
    "synonyms": ["Adderall", "mixed amphetamine salts", "MAS IR"],
    "codes": {"atc": ["N06BA01"]},
    "srcs": ["dailymed", "ahfs", "statpearls", "drugbank"],
    "controlledSubstance": {"usSchedule": "II"},
    "indications": [
        {"name": "ADHD", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([5, 10, 15, 20, 25, 30, 35, 40], "mg")),
             "dosingInterval": every(240, 360), "asNeeded": False,
             "maxDailyDose": val(40, "mg"),
             "notes": "Start 5 mg once or twice daily; titrate in 5 mg weekly increments. Total daily dose is usually split into 2-3 administrations. Doses above 40 mg/day are rarely more effective."},
        ]},
        {"name": "Narcolepsy", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(rng(5, 60, "mg")),
             "asNeeded": False, "maxDailyDose": val(60, "mg"),
             "notes": "Given in divided doses, first on waking. Narcolepsy dosing runs higher than ADHD dosing."},
        ]},
    ],
    "mechanismsOfAction": [moa("nd-releaser"), moa("ndri")],
    "metabolismPathways": [
        path("cyp2d6", enzyme="CYP2D6", effect="substrate",
             note="Minor route (4-hydroxylation). Amphetamine clearance is dominated by renal excretion of unchanged drug, so CYP2D6 inhibitors matter less here than urinary pH does."),
        path("renal-excretion-unchanged", fraction=rng(0.3, 0.4),
             note="Strongly pH-dependent. Alkaline urine raises exposure substantially; acidic urine lowers it. This is the dominant pharmacokinetic lever on amphetamine and it is not a CYP effect."),
    ],
    "activeMetabolites": [
        metabolite("4-hydroxyamphetamine", "4-hydroxyamphetamine", "therapeutic", "less-potent", "cyp2d6", "CYP2D6"),
        metabolite("Norephedrine", None, "therapeutic", "less-potent", "cyp450-oxidation",
                   note="Formed by beta-hydroxylation. Weakly active; no separate record, since nothing in this set interacts through it."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(9, 14, "h"),
         "durationOfAction": rng(4, 6, "h"), "timeToPeak": rng(2, 3, "h"),
         "timeToOnset": rng(30, 60, "min"),
         "notes": "The half-life range spans the two enantiomers: d-amphetamine roughly 10 h, l-amphetamine roughly 13 h. Note that duration of clinical effect is far shorter than half-life, which is why this is dosed 2-3 times daily."},
    ],
    "notes": "Renamed from the uploaded record. The uploaded version had dose steps in `ug` with a maxDailyDose in `mg` — a thousandfold mismatch that no validator could catch, since both are legal terms in a closed units vocabulary. Steps are mg. validate.py now cross-checks dose units against the daily ceiling.",
}

# ---------------------------------------------------------------- 3
DRUGS["amphetamine-xr"] = {
    "drugName": "Dextroamphetamine/Amphetamine, extended release",
    "synonyms": ["Adderall XR", "MAS XR"],
    "codes": {"atc": ["N06BA01"]},
    "srcs": ["dailymed", "ahfs", "drugbank"],
    "controlledSubstance": {"usSchedule": "II"},
    "supersedes": ["ampheramine-xr"],
    "indications": [
        {"name": "ADHD", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([5, 10, 15, 20, 25, 30], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(30, "mg"),
             "notes": "Once daily in the morning. The adult label settles at 20 mg/day; 30 mg is the highest marketed capsule strength and is used in practice. Capsules may be opened onto applesauce but the beads must not be chewed."},
        ]},
    ],
    "mechanismsOfAction": [moa("nd-releaser"), moa("ndri")],
    "metabolismPathways": [
        path("cyp2d6", enzyme="CYP2D6", effect="substrate", note="Minor route, as for the IR form."),
        path("renal-excretion-unchanged", fraction=rng(0.3, 0.4),
             note="pH-dependent; see the IR record."),
    ],
    "activeMetabolites": [
        metabolite("4-hydroxyamphetamine", "4-hydroxyamphetamine", "therapeutic", "less-potent", "cyp2d6", "CYP2D6"),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "extended-release",
         "halfLife": rng(9, 14, "h"), "durationOfAction": rng(10, 12, "h"),
         "timeToPeak": val(7, "h"),
         "notes": "Elimination half-life is the same as the IR form — the drug is identical. Only the input rate differs, which is what stretches time-to-peak from ~3 h to ~7 h and duration from ~5 h to ~11 h. Bimodal bead release gives a second pulse around 4 h after the first."},
    ],
    "notes": "The uploaded id `ampheramine-xr` was a misspelling referenced by four other records. Corrected here to `amphetamine-xr`; `supersedes` carries the old id so existing references can be resolved rather than silently dropped.",
}

# ---------------------------------------------------------------- 4
DRUGS["aspirin"] = {
    "drugName": "Aspirin",
    "synonyms": ["Acetylsalicylic acid", "ASA"],
    "codes": {"atc": ["N02BA01", "B01AC06"]},
    "srcs": ["merck", "ahfs", "dailymed", "statpearls"],
    "indications": [
        {"name": "Pain / fever", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([325, 650], "mg")),
             "dosingInterval": every(240, 360), "asNeeded": True,
             "maxDailyDose": val(3900, "mg"), "maxDurationDays": 10,
             "notes": "The commonly quoted 4000 mg/day ceiling is not reachable on a q4h schedule at 650 mg; 3900 mg is the real bound, as for acetaminophen."},
        ]},
        {"name": "Antiplatelet / secondary cardiovascular prevention", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([81, 162, 325], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(325, "mg"),
             "notes": "81 mg daily is the usual maintenance dose. The antiplatelet effect is maximal at low dose and does not increase with analgesic dosing; bleeding risk does."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("cox-1-irreversible-acetylation", note="Acetylates serine-529 of platelet COX-1. Platelets cannot resynthesise the enzyme, so a single dose suppresses thromboxane for the platelet's 7-10 day lifespan. This is the whole basis of low-dose dosing and of the ibuprofen interaction."),
        moa("cox-inhibition-peripheral"),
    ],
    "metabolismPathways": [
        path("hydrolysis", note="Rapid esterase hydrolysis to salicylic acid, in gut wall, plasma and liver. Most of the systemic effect after the first pass is salicylate, not aspirin."),
        path("glycine-conjugation", note="Salicyluric acid formation. Saturable, which is why salicylate half-life stretches from ~3 h to 15-30 h as dose rises."),
        path("glucuronidation"),
    ],
    "activeMetabolites": [
        metabolite("Salicylic acid", "salicylic-acid", "mixed", "less-potent", "hydrolysis", None, val(1.0),
                   "Effectively the entire dose passes through it. Carries the analgesic and anti-inflammatory effect but NOT the irreversible antiplatelet effect, which belongs to intact aspirin."),
    ],
    "pharmacokinetics": [
        {"population": "adult-healthy", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(15, 20, "min"), "bioavailability": rng(0.5, 0.7),
         "volumeOfDistribution": val(0.15, "L/kg"),
         "timeToPeak": rng(30, 60, "min"), "durationOfAction": rng(4, 6, "h"),
         "notes": "The 15-20 minute half-life is intact aspirin only. Pharmacodynamic duration is decoupled from it in both directions: analgesia tracks salicylate, antiplatelet effect tracks platelet turnover and lasts days."},
    ],
    "notes": "A case where half-life is nearly useless on its own. Any consumer of this record that reasons from halfLife to duration will be wrong about aspirin three different ways.",
}

# ---------------------------------------------------------------- 5
DRUGS["caffeine"] = {
    "drugName": "Caffeine (oral tablets)",
    "synonyms": ["1,3,7-trimethylxanthine", "No-Doz", "Vivarin"],
    "codes": {"atc": ["N06BC01"]},
    "srcs": ["dailymed", "ahfs", "statpearls", "drugbank"],
    "indications": [
        {"name": "Restoration of mental alertness / fatigue", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([100, 200], "mg")),
             "dosingInterval": every(180, 240), "asNeeded": True,
             "maxDailyDose": val(400, "mg"),
             "notes": "Marketed as 100 mg and 200 mg tablets. The 400 mg/day ceiling is FDA general guidance for healthy adults from all sources combined, not a per-product label limit — dietary caffeine counts against it."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("adenosine-receptor-antagonist", note="Competitive antagonism at A1 and A2A. Alertness is disinhibition of adenosine's sleep-pressure signal, not stimulation — which is why caffeine opposes a hypnotic without reversing its sedation."),
    ],
    "metabolismPathways": [
        path("cyp1a2", enzyme="CYP1A2", effect="substrate", fraction=rng(0.9, 0.95),
             note="Almost the whole dose. CYP1A2 activity varies severalfold between people and is induced by tobacco smoke, so caffeine half-life is one of the most variable in common use."),
    ],
    "activeMetabolites": [
        metabolite("Paraxanthine", "paraxanthine", "therapeutic", "comparable", "cyp1a2", "CYP1A2", val(0.84),
                   "The dominant metabolite and a substantial share of the real-world effect."),
        metabolite("Theobromine", None, "therapeutic", "less-potent", "cyp1a2", "CYP1A2", val(0.12)),
        metabolite("Theophylline", None, "therapeutic", "more-potent", "cyp1a2", "CYP1A2", val(0.04)),
    ],
    "pharmacokinetics": [
        {"population": "adult-healthy", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(3, 7, "h"), "bioavailability": rng(0.99, 1.0),
         "volumeOfDistribution": val(0.6, "L/kg"),
         "timeToOnset": rng(15, 45, "min"), "timeToPeak": rng(30, 120, "min"),
         "durationOfAction": rng(3, 5, "h"),
         "notes": "Near-complete oral bioavailability and free CNS entry. Half-life roughly doubles in pregnancy and with oral contraceptives, and falls by about half in smokers."},
    ],
    "notes": "Worth holding against the hypnotics in this set: a 200 mg tablet at 4 pm still has roughly a quarter of its peak level in circulation at midnight.",
}

# ---------------------------------------------------------------- 6
DRUGS["cimetidine"] = {
    "drugName": "Cimetidine",
    "synonyms": ["Tagamet"],
    "codes": {"atc": ["A02BA01"]},
    "srcs": ["merck", "ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Heartburn / acid indigestion / sour stomach", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(200, "mg")),
             "dosingInterval": every(720), "asNeeded": True,
             "maxDailyDose": val(400, "mg"), "maxDurationDays": 14,
             "notes": "OTC strength. May be taken up to 30 minutes before a meal expected to cause symptoms."},
        ]},
        {"name": "Duodenal / gastric ulcer", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(800, "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(800, "mg"), "maxDurationDays": 56,
             "notes": "Prescription dosing, at bedtime. The alternative divided-dose regimen is 300 mg four times daily (1200 mg/day) or 400 mg twice daily; those are different regimens with different ceilings and should not share this one."},
        ]},
    ],
    "mechanismsOfAction": [moa("competitive-histamine-h2-receptor-antagonist")],
    "metabolismPathways": [
        path("renal-excretion-unchanged", fraction=rng(0.5, 0.75)),
        path("cyp1a2", enzyme="CYP1A2", effect="inhibitor",
             note="Moderate. Raises caffeine, melatonin and propranolol exposure."),
        path("cyp2c19", enzyme="CYP2C19", effect="inhibitor", note="Moderate."),
        path("cyp2d6", enzyme="CYP2D6", effect="inhibitor",
             note="Moderate. Raises dextromethorphan, propranolol and diphenhydramine exposure."),
        path("cyp3a4", enzyme="CYP3A4", effect="inhibitor",
             note="Weak to moderate, but enough to matter for a narrow-margin 3A4 substrate such as triazolam."),
    ],
    "activeMetabolites": [
        metabolite("Cimetidine sulfoxide", None, "inactive", None, "cyp450-oxidation", None, None,
                   "Recorded explicitly. The uploaded record listed an active metabolite named \"s\" with activity \"toxic\" — a stray keystroke. Cimetidine has no clinically relevant active metabolite."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": val(2, "h"), "bioavailability": rng(0.6, 0.7),
         "volumeOfDistribution": val(1, "L/kg"),
         "durationOfAction": rng(4, 6, "h"), "timeToPeak": rng(45, 90, "min"),
         "notes": "timeToPeak here holds the 45-90 minute value that the uploaded record filed under `peakConcentration` — a time in a field named for a concentration."},
    ],
    "notes": "The most interaction-prone drug in this set, and the reason it is worth pairing against famotidine in the same database: they do the same clinical job and have completely different interaction profiles. Every major cimetidine interaction below is enzyme inhibition, not H2 blockade.",
}

# ---------------------------------------------------------------- 7
DRUGS["colestipol"] = {
    "drugName": "Colestipol",
    "synonyms": ["Colestid"],
    "codes": {"atc": ["C10AC02"]},
    "srcs": ["ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Primary hypercholesterolaemia", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(rng(2, 16, "g")),
             "asNeeded": False, "maxDailyDose": val(16, "g"),
             "notes": "Tablets. Start 2 g once or twice daily; increase by 2 g at 1-2 month intervals. Swallow one tablet at a time, whole, with plenty of liquid."},
            {"population": "adult", "route": "oral", "dose": flat(rng(5, 30, "g")),
             "asNeeded": False, "maxDailyDose": val(30, "g"),
             "notes": "Granules for suspension, in 1-2 divided doses. Never administer the dry granules."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("bile-acid-sequestration", note="An anion-exchange resin. Its affinity is not selective for bile acids, which is the entire origin of its interaction profile: it binds other anionic drugs in the gut lumen indiscriminately."),
    ],
    "metabolismPathways": [
        path("not-absorbed", fraction=val(1.0),
             note="Nothing enters the circulation. Every colestipol interaction is therefore an absorption interaction and every one is solved by spacing rather than dose adjustment."),
    ],
    "activeMetabolites": [
        metabolite("None", None, "inactive", None, None, None, None, "Not absorbed, so not metabolised."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "not-applicable",
         "bioavailability": val(0.0),
         "notes": "No systemic pharmacokinetics exist. Recorded as a zero rather than left empty."},
    ],
    "knownAbsences": [
        absent("pharmacokinetics[0].halfLife", "Settled, not pending: an unabsorbed resin has no elimination half-life. Transit time through the gut is the analogous quantity and is not a PK parameter.", status="not-applicable"),
    ],
    "notes": "The label rule is general and is not captured by the pairwise interactions below: take any other oral medication at least 1 hour before, or 4 hours after, colestipol. Individually documented pairs are recorded as interactions; the rest of this database should be treated as covered by the general rule. Stopping colestipol in someone stabilised on a bound drug raises that drug's exposure — the interaction runs in both directions in time.",
}

# ---------------------------------------------------------------- 8
DRUGS["daridorexant"] = {
    "drugName": "Daridorexant",
    "synonyms": ["Quviviq", "ACT-541468", "nemorexant"],
    "codes": {"atc": ["N05CJ03"]},
    "srcs": ["dailymed", "ahfs", "drugbank"],
    "controlledSubstance": {"usSchedule": "IV"},
    "indications": [
        {"name": "Insomnia (sleep onset and/or sleep maintenance)", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([25, 50], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(50, "mg"),
             "notes": "Within 30 minutes of bedtime, with at least 7 hours remaining before the planned wake time. Taking with or soon after a large meal delays onset by about 1.3 hours."},
            {"population": "hepatic-impairment", "route": "oral", "dose": flat(val(25, "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(25, "mg"),
             "notes": "Moderate impairment (Child-Pugh 7-9). Not recommended in severe impairment (Child-Pugh 10 or above)."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("orexin-receptor-antagonist-dual", note="Blocks orexin-A and orexin-B signalling at OX1 and OX2, removing the wake-promoting drive rather than adding a sedative one. Mechanistically distinct from the GABA-A hypnotics in this set, though the practical result stacks with them."),
    ],
    "metabolismPathways": [
        path("cyp3a4", enzyme="CYP3A4", effect="substrate", fraction=val(0.89),
             note="89% of metabolic clearance. No other CYP contributes more than 3%. This makes daridorexant exposure almost entirely a function of 3A4 activity, so a 3A4 inhibitor is a dose change in disguise."),
    ],
    "activeMetabolites": [
        metabolite("None clinically relevant", None, "inactive", None, "cyp3a4", "CYP3A4", None,
                   "Extensively metabolised, but circulating metabolites do not contribute meaningfully to effect."),
    ],
    "pharmacokinetics": [
        {"population": "adult-healthy", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": val(8, "h"), "bioavailability": val(0.62),
         "volumeOfDistribution": val(31, "L"), "proteinBinding": val(0.997),
         "timeToPeak": rng(1, 2, "h"), "durationOfAction": val(8, "h"),
         "notes": "Volume of distribution is reported as an absolute 31 L rather than weight-normalised. No accumulation on repeat nightly dosing. Renal impairment, age, sex and body size do not meaningfully change exposure; hepatic impairment does."},
    ],
    "notes": "Schedule IV. The 7-hour rule is not a formality: next-morning driving impairment is dose-related and is the reason the label caps at 50 mg.",
}

# ---------------------------------------------------------------- 9
DRUGS["dextromethorphan"] = {
    "drugName": "Dextromethorphan",
    "synonyms": ["DXM", "DM"],
    "codes": {"atc": ["R05DA09"]},
    "srcs": ["ahfs", "dailymed", "statpearls", "drugbank"],
    "indications": [
        {"name": "Cough suppression", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(30, "mg")),
             "dosingInterval": every(360, 480), "asNeeded": True,
             "maxDailyDose": val(120, "mg"), "maxDurationDays": 7,
             "notes": "Immediate-release form. Extended-release polistirex is 60 mg every 12 hours, maximum 120 mg/day."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("noncompetitive-nmda-receptor-antagonist"),
        moa("sigma-1-agonist"),
        moa("serotonin-reuptake-inhibition", "probable",
            "Weak, but pharmacologically real and the basis of the serotonin syndrome risk with SSRIs. Recorded as a mechanism rather than only as an interaction note, so the risk is derivable rather than hard-coded."),
    ],
    "metabolismPathways": [
        path("cyp2d6", enzyme="CYP2D6", effect="substrate",
             note="Primary route, and highly polymorphic. Poor metabolisers reach several-fold higher parent exposure from a label dose; ultrarapid metabolisers may get little effect. Inhibiting 2D6 converts a normal metaboliser into a phenocopy of a poor one."),
        path("cyp3a4", enzyme="CYP3A4", effect="substrate", note="Minor route, to 3-methoxymorphinan."),
    ],
    "activeMetabolites": [
        metabolite("Dextrorphan", "dextrorphan", "therapeutic", "comparable", "cyp2d6", "CYP2D6", None,
                   "More potent than the parent at NMDA, less potent at sigma-1. Carries much of the effect in normal metabolisers."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(2, 4, "h"), "timeToOnset": rng(15, 30, "min"),
         "durationOfAction": rng(3, 6, "h"), "timeToPeak": val(2.5, "h"),
         "notes": "Applies to CYP2D6 extensive metabolisers."},
        {"population": "cyp2d6-poor-metabolizer", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(19, 45, "h"),
         "notes": "A different PK population, not a footnote on the first one. Parent half-life rises roughly tenfold and dextrorphan formation largely fails."},
    ],
    "notes": "The uploaded record carried a \"Recreational\" indication typed as off-label. off-label means an unapproved MEDICAL use; typing non-medical use that way promotes it into anything filtering for clinical indications. The 1.5 vocabulary adds a distinct `non-medical` term for that distinction, and no non-medical regimen is carried here — the clinically useful content of that entry is the interaction set below, which is retained in full.",
}

# ---------------------------------------------------------------- 10
DRUGS["diclofenac-tablets"] = {
    "drugName": "Diclofenac 50 mg tablets",
    "synonyms": ["Voltaren", "Cataflam"],
    "codes": {"atc": ["M01AB05"]},
    "srcs": ["merck", "ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Osteoarthritis", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(50, "mg")),
             "dosingInterval": every(480, 720), "asNeeded": False,
             "maxDailyDose": val(150, "mg"),
             "notes": "50 mg two or three times daily."},
        ]},
        {"name": "Rheumatoid arthritis", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(50, "mg")),
             "dosingInterval": every(360, 480), "asNeeded": False,
             "maxDailyDose": val(200, "mg"),
             "notes": "50 mg three or four times daily."},
        ]},
        {"name": "Acute migraine with or without aura", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(50, "mg")),
             "dosingInterval": every(600), "asNeeded": True,
             "maxDailyDose": val(100, "mg"), "maxDurationDays": 10,
             "notes": "The migraine indication belongs to the potassium oral solution (Cambia); the 50 mg tablet is used for this off the solution's evidence. Frequent use of any acute migraine drug risks medication-overuse headache — the uploaded record's maxDurationDays of 200 appears to be a placeholder, and 10 days per month is the usual practical ceiling."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("cox-inhibition-peripheral", note="Retyped in 1.5. The uploaded record used cox-inhibition-central, which is the acetaminophen term; for an NSAID the peripheral term is the primary one and leaving it central made diclofenac unfindable in any NSAID query."),
        moa("cox-inhibition-central", "probable", "Contributes, but secondary."),
    ],
    "metabolismPathways": [
        path("cyp2c9", enzyme="CYP2C9", effect="substrate", note="Primary route."),
        path("cyp2c8", enzyme="CYP2C8", effect="substrate", note="Secondary."),
        path("cyp3a4", enzyme="CYP3A4", effect="substrate", note="Minor."),
        path("glucuronidation"),
    ],
    "activeMetabolites": [
        metabolite("4'-hydroxydiclofenac", None, "inactive", "less-potent", "cyp2c9", "CYP2C9", None,
                   "The major metabolite. Some in vitro COX activity, but not enough to count as clinically active; recorded as inactive deliberately rather than omitted."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": val(2, "h"), "bioavailability": val(0.55),
         "volumeOfDistribution": val(1.3, "L/kg"), "proteinBinding": val(0.99),
         "durationOfAction": rng(6, 8, "h"), "timeToPeak": val(1, "h"),
         "notes": "Bioavailability around 55% because of substantial first-pass metabolism. Synovial fluid concentrations persist well past plasma, which is why effect outlasts the 2-hour half-life."},
    ],
}

# ---------------------------------------------------------------- 11
DRUGS["diphenhydramine"] = {
    "drugName": "Diphenhydramine",
    "synonyms": ["Benadryl", "DPH"],
    "codes": {"atc": ["R06AA02", "D04AA32"]},
    "srcs": ["merck", "ahfs", "dailymed", "statpearls"],
    "indications": [
        {"name": "Allergic rhinitis / urticaria / motion sickness", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([25, 50], "mg")),
             "dosingInterval": every(240, 360), "asNeeded": True,
             "maxDailyDose": val(300, "mg"),
             "notes": "OTC labels commonly cap at 300 mg/day; some prescription labels allow 400 mg/day."},
        ]},
        {"name": "Occasional sleeplessness", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(50, "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": True,
             "maxDailyDose": val(50, "mg"), "maxDurationDays": 14,
             "notes": "At bedtime. Tolerance to the sedative effect develops within days, which is why the OTC sleep label is short-term. The uploaded record's maxDurationDays of 1 was too short to be a real ceiling."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("h1-receptor-blockade-inverse-agonism",
            "established", "First-generation, so it crosses the blood-brain barrier freely — central H1 blockade is the sedation, and it is an unavoidable part of the same mechanism rather than a side effect of a separable one."),
    ],
    "metabolismPathways": [
        path("cyp2d6", enzyme="CYP2D6", effect="substrate-and-inhibitor",
             note="Both, and that matters. It is cleared by 2D6, so 2D6 inhibitors raise it; and it inhibits 2D6 itself, so it raises other 2D6 substrates. Two records in this set (dextromethorphan, propranolol) are on the receiving end."),
        path("cyp1a2", enzyme="CYP1A2", effect="substrate", note="Minor."),
        path("cyp2c9", enzyme="CYP2C9", effect="substrate", note="Minor."),
    ],
    "activeMetabolites": [
        metabolite("Nordiphenhydramine", "nordiphenhydramine", "therapeutic", "less-potent", "cyp2d6", "CYP2D6"),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(4, 9, "h"), "bioavailability": rng(0.4, 0.6),
         "volumeOfDistribution": rng(3, 4, "L/kg"), "proteinBinding": rng(0.98, 0.99),
         "timeToOnset": rng(15, 30, "min"), "durationOfAction": rng(4, 6, "h"),
         "timeToPeak": rng(2, 4, "h"),
         "notes": "Volume of distribution corrected in 1.5: the uploaded record held 17 L/kg, roughly five times the published value."},
        {"population": "geriatric", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(9, 18, "h"),
         "notes": "Clearance falls and half-life roughly doubles. Diphenhydramine appears on the Beers criteria for this reason: anticholinergic burden, falls, and next-day confusion."},
    ],
    "notes": "Sedating antihistamine, anticholinergic, and CYP2D6 inhibitor all at once. Most of its interaction entries below come from one of the latter two rather than from H1 blockade.",
}
