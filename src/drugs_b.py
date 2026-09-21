"""Drug records, part 2."""

from drugs_a import (rng, val, steps, flat, perkg, every, moa, path,
                     transporter, metabolite, absent, DRUGS)

# ---------------------------------------------------------------- 12
DRUGS["esomeprazole"] = {
    "drugName": "Esomeprazole",
    "synonyms": ["Nexium", "S-omeprazole"],
    "codes": {"atc": ["A02BC05"]},
    "srcs": ["merck", "ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Frequent heartburn", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(20, "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(20, "mg"), "maxDurationDays": 14,
             "notes": "OTC course, at least an hour before the first meal. Not for immediate relief — full effect takes 1-4 days. Repeat courses no more often than every 4 months without advice."},
        ]},
        {"name": "GERD / erosive oesophagitis", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([20, 40], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(40, "mg"), "maxDurationDays": 56,
             "notes": "Prescription dosing, 4-8 weeks for healing."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("proton-pump-inhibitor", note="Irreversible covalent binding to the gastric H+/K+-ATPase. Like aspirin and COX-1, the effect outlives the drug: a 1-1.5 hour half-life produces 24-hour acid suppression because new pumps must be synthesised."),
    ],
    "metabolismPathways": [
        path("cyp2c19", enzyme="CYP2C19", effect="substrate-and-inhibitor",
             note="Primary clearance route and also inhibited by it. Highly polymorphic: poor metabolisers reach much higher exposure."),
        path("cyp3a4", enzyme="CYP3A4", effect="substrate", note="Secondary route, to the sulphone."),
    ],
    "activeMetabolites": [
        metabolite("None", None, "inactive", None, "cyp2c19", "CYP2C19", None,
                   "Hydroxy and sulphone metabolites have no antisecretory activity."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "delayed-release",
         "halfLife": rng(1, 1.5, "h"), "bioavailability": rng(0.64, 0.9),
         "volumeOfDistribution": val(16, "L"), "proteinBinding": val(0.97),
         "timeToPeak": rng(1, 2, "h"), "durationOfAction": val(24, "h"),
         "notes": "Enteric-coated, so delayed-release rather than immediate. Bioavailability rises with repeated dosing as first-pass metabolism saturates. Duration of action is 24 h against a 1-1.5 h half-life — the mechanism, not the kinetics, sets the dosing interval."},
    ],
    "notes": "Two separate interaction mechanisms live here and should not be conflated: CYP2C19 inhibition (systemic) and gastric pH elevation (luminal). The pH effect is shared with famotidine and cimetidine; the enzyme effect is not.",
}

# ---------------------------------------------------------------- 13
DRUGS["famotidine"] = {
    "drugName": "Famotidine",
    "synonyms": ["Pepcid"],
    "codes": {"atc": ["A02BA03"]},
    "srcs": ["merck", "ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Heartburn / acid indigestion", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([10, 20], "mg")),
             "dosingInterval": every(720), "asNeeded": True,
             "maxDailyDose": val(40, "mg"), "maxDurationDays": 14,
             "notes": "OTC. May be taken 10-60 minutes before a meal expected to cause symptoms."},
        ]},
        {"name": "GERD / duodenal ulcer", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([20, 40], "mg")),
             "dosingInterval": every(720, 1440), "asNeeded": False,
             "maxDailyDose": val(80, "mg"), "maxDurationDays": 56},
        ]},
        {"name": "Renal impairment dose adjustment", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "renal-impairment", "route": "oral", "dose": flat(val(20, "mg")),
             "dosingInterval": every(1440, 2880), "asNeeded": False,
             "notes": "CrCl below 50 mL/min: halve the dose or double the interval. Because clearance is renal rather than hepatic, this is where famotidine needs attention — unlike cimetidine, whose problems are hepatic."},
        ]},
    ],
    "mechanismsOfAction": [moa("competitive-histamine-h2-receptor-antagonist")],
    "metabolismPathways": [
        path("renal-excretion-unchanged", fraction=rng(0.65, 0.7),
             note="Dominant route. Famotidine does NOT meaningfully inhibit any CYP enzyme — the single most useful fact about it in a polypharmacy database, and the reason it is the substitute of choice when cimetidine's inhibition is the problem."),
        path("cyp450-oxidation", fraction=val(0.3), note="Minor, to the inactive S-oxide."),
    ],
    "activeMetabolites": [
        metabolite("Famotidine S-oxide", None, "inactive", None, "cyp450-oxidation"),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(2.5, 3.5, "h"), "bioavailability": rng(0.4, 0.45),
         "volumeOfDistribution": rng(1.1, 1.4, "L/kg"), "proteinBinding": rng(0.15, 0.2),
         "timeToOnset": val(1, "h"), "durationOfAction": rng(10, 12, "h"),
         "timeToPeak": rng(1, 3, "h")},
    ],
    "notes": "Kept in this set as the deliberate control against cimetidine: same class, same indication, and almost none of the interactions. Any pair where cimetidine is flagged for enzyme inhibition and famotidine is screened clean is a real clinical substitution, not a data gap.",
}

# ---------------------------------------------------------------- 14
DRUGS["ibuprofen"] = {
    "drugName": "Ibuprofen",
    "synonyms": ["Advil", "Motrin"],
    "codes": {"atc": ["M01AE01"]},
    "srcs": ["merck", "ahfs", "dailymed", "statpearls"],
    "indications": [
        {"name": "Pain / fever", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([200, 400], "mg")),
             "dosingInterval": every(240, 360), "asNeeded": True,
             "maxDailyDose": val(1200, "mg"), "maxDurationDays": 10,
             "notes": "OTC ceiling. Do not exceed 1200 mg/day without medical advice."},
            {"population": "adult", "route": "oral", "dose": flat(steps([400, 600, 800], "mg")),
             "dosingInterval": every(360, 480), "asNeeded": False,
             "maxDailyDose": val(3200, "mg"),
             "notes": "Prescription dosing for inflammatory conditions."},
            {"population": "pediatric", "route": "oral", "dose": perkg(rng(5, 10, "mg/kg")),
             "dosingInterval": every(360, 480), "asNeeded": True,
             "maxDailyDose": val(40, "mg/kg")},
        ]},
    ],
    "mechanismsOfAction": [
        moa("cox-inhibition-peripheral", note="Reversible and competitive, which is exactly why it collides with aspirin: it occupies the COX-1 channel without acetylating it, and blocks aspirin from reaching the serine it needs to acetylate."),
        moa("cox-inhibition-central", "probable"),
    ],
    "metabolismPathways": [
        path("cyp2c9", enzyme="CYP2C9", effect="substrate", note="Primary."),
        path("cyp2c8", enzyme="CYP2C8", effect="substrate"),
        path("glucuronidation"),
    ],
    "activeMetabolites": [
        metabolite("None", None, "inactive", None, "cyp2c9", "CYP2C9", None,
                   "Hydroxy and carboxy metabolites are inactive."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(2, 4, "h"), "bioavailability": rng(0.8, 1.0),
         "volumeOfDistribution": val(0.15, "L/kg"), "proteinBinding": val(0.99),
         "timeToOnset": rng(30, 60, "min"), "durationOfAction": rng(4, 6, "h"),
         "timeToPeak": rng(1, 2, "h")},
    ],
}

# ---------------------------------------------------------------- 15
DRUGS["levocetirizine"] = {
    "drugName": "Levocetirizine",
    "synonyms": ["Xyzal", "levocetirizine dihydrochloride"],
    "codes": {"atc": ["R06AE09"]},
    "srcs": ["ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Allergic rhinitis / chronic idiopathic urticaria", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(5, "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(5, "mg"),
             "notes": "Once daily in the evening. Some people are controlled on 2.5 mg. Do not exceed 5 mg/day — unlike the first-generation agents, more is not better, it is only more sedating."},
            {"population": "renal-impairment", "route": "oral", "dose": flat(val(2.5, "mg")),
             "dosingInterval": every(1440, 2880), "asNeeded": False,
             "notes": "CrCl 50-80: 2.5 mg daily. CrCl 30-50: 2.5 mg every other day. CrCl 10-30: 2.5 mg twice weekly. Contraindicated below 10 or on haemodialysis. Renal clearance dominates, so this adjustment is the main dosing consideration."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("h1-receptor-blockade-inverse-agonism",
            note="Second-generation: the active R-enantiomer of cetirizine, with limited blood-brain barrier penetration. Less sedating than diphenhydramine, not non-sedating — roughly 6% of people report somnolence at 5 mg."),
    ],
    "metabolismPathways": [
        path("renal-excretion-unchanged", fraction=rng(0.85, 0.86),
             note="Under 14% is metabolised, and no single CYP dominates. This is a drug with essentially no metabolic interactions, and that absence is the point of recording the pathway explicitly."),
    ],
    "activeMetabolites": [
        metabolite("None", None, "inactive", None, "renal-excretion-unchanged", None, None,
                   "Barely metabolised; no active metabolite."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(8, 9, "h"), "bioavailability": val(1.0),
         "volumeOfDistribution": val(0.4, "L/kg"), "proteinBinding": rng(0.91, 0.92),
         "timeToOnset": val(1, "h"), "durationOfAction": val(24, "h"),
         "timeToPeak": rng(0.9, 1.5, "h")},
    ],
}

# ---------------------------------------------------------------- 16
DRUGS["loperamide"] = {
    "drugName": "Loperamide",
    "synonyms": ["Imodium", "Imodium A-D"],
    "codes": {"atc": ["A07DA03"]},
    "srcs": ["ahfs", "dailymed", "statpearls", "drugbank"],
    "indications": [
        {"name": "Acute diarrhoea", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(4, "mg")),
             "asNeeded": True, "maxDailyDose": val(8, "mg"), "maxDurationDays": 2,
             "notes": "OTC: 4 mg initially, then 2 mg after each subsequent loose stool. Hard ceiling 8 mg/day for self-treatment, 2 days maximum."},
            {"population": "adult", "route": "oral", "dose": flat(val(4, "mg")),
             "asNeeded": True, "maxDailyDose": val(16, "mg"),
             "notes": "Prescription ceiling, for chronic diarrhoea under supervision. 16 mg/day is the absolute maximum in any setting."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("mu-opioid-agonist-peripheral",
            note="Confined to the myenteric plexus by P-gp efflux at the blood-brain barrier. The confinement is the safety margin, and it is a transporter, not a property of the molecule."),
        moa("herg-potassium-channel-blockade", "established",
            "Off-target, and only reached at systemic exposures well above therapeutic. Blockade of hERG prolongs QT; Nav1.5 blockade widens QRS. This is why the FDA added a boxed warning and why anything that raises systemic loperamide exposure is a cardiac question rather than a GI one."),
    ],
    "metabolismPathways": [
        path("cyp3a4", enzyme="CYP3A4", effect="substrate",
             note="Major, via N-demethylation. Ketoconazole inhibited this by 90% in vitro."),
        path("cyp2c8", enzyme="CYP2C8", effect="substrate", note="Major. Quercetin inhibited by 40% in vitro."),
        path("cyp2b6", enzyme="CYP2B6", effect="substrate", note="Minor."),
        path("cyp2d6", enzyme="CYP2D6", effect="substrate", note="Minor."),
    ],
    "transporters": [
        transporter("p-glycoprotein", "substrate",
                    "The thing that keeps loperamide out of the brain. Inhibit it and CNS opioid effects appear; saturate it with a large dose and the same happens. Recorded here rather than under metabolism because it changes distribution, not clearance."),
    ],
    "activeMetabolites": [
        metabolite("N-desmethylloperamide", None, "inactive", "less-potent", "cyp3a4", "CYP3A4", None,
                   "The major metabolite and essentially inactive."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(9.1, 14.4, "h"), "bioavailability": val(0.004),
         "proteinBinding": val(0.97), "timeToPeak": val(5, "h"),
         "notes": "Bioavailability is roughly 0.4% — extraction in the gut wall plus heavy first pass. Almost no intact loperamide reaches the systemic circulation at label doses, which is the entire safety basis for OTC status. Capsules peak around 5 h, oral solution around 2.5 h."},
    ],
    "notes": "The only drug in this set where the safety margin depends on a transporter rather than on dose alone. Two independent things can dismantle it: a P-gp or CYP3A4/2C8 inhibitor, or a dose far above label. Cimetidine is in this database and does the first.",
}

# ---------------------------------------------------------------- 17
DRUGS["melatonin"] = {
    "drugName": "Melatonin",
    "synonyms": ["N-acetyl-5-methoxytryptamine"],
    "codes": {"atc": ["N05CH01"]},
    "srcs": ["ahfs", "statpearls", "drugbank"],
    "indications": [
        {"name": "Sleep onset difficulty / circadian rhythm disruption", "labelStatus": "supplement", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([0.5, 1, 3, 5], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": True,
             "maxDailyDose": val(5, "mg"),
             "notes": "30-60 minutes before the target bedtime. Dose-response is flat or inverted above roughly 3 mg — higher doses are not more effective and prolong next-morning grogginess. For circadian phase shifting, timing matters far more than dose and the effective dose is lower (0.5 mg)."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("mt1-mt2-agonist", note="MT1 suppresses the wake drive in the suprachiasmatic nucleus; MT2 shifts circadian phase. Melatonin is a timing signal rather than a sedative, and stacking it with true sedatives gives additive drowsiness without additive efficacy."),
    ],
    "metabolismPathways": [
        path("cyp1a2", enzyme="CYP1A2", effect="substrate", fraction=rng(0.9, 0.95),
             note="Dominant route, to 6-hydroxymelatonin. Extensive and highly variable first-pass metabolism here is why oral bioavailability is both low and unpredictable."),
        path("cyp2c19", enzyme="CYP2C19", effect="substrate", note="Minor."),
    ],
    "activeMetabolites": [
        metabolite("6-hydroxymelatonin", None, "inactive", "less-potent", "cyp1a2", "CYP1A2", None,
                   "Excreted as the sulphate conjugate; the standard urinary marker of melatonin production, but not itself active."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(20, 50, "min"), "bioavailability": rng(0.01, 0.37),
         "timeToPeak": rng(30, 60, "min"), "durationOfAction": rng(1, 2, "h"),
         "notes": "Bioavailability is the widest range in this database and is not a data quality problem — first-pass CYP1A2 metabolism genuinely varies more than tenfold between people. The very short half-life is why immediate-release melatonin helps sleep onset but not sleep maintenance."},
    ],
    "knownAbsences": [
        absent("codes.rxcui", "Marketed in the US as a dietary supplement rather than a drug, so there is no FDA-reviewed label and no assured content per unit. Assays have repeatedly found actual content differing substantially from the label. Dose fields here describe what is printed on the bottle, not what was verified in it.", status="not-applicable"),
    ],
    "notes": "labelStatus is `supplement`, a term added in 1.5. Typing it on-label would have implied an FDA-reviewed indication that does not exist; typing it off-label would have implied a prescription drug used outside its label. Neither is true.",
}

# ---------------------------------------------------------------- 18
DRUGS["naproxen"] = {
    "drugName": "Naproxen",
    "synonyms": ["Aleve", "Naprosyn", "naproxen sodium"],
    "codes": {"atc": ["M01AE02"]},
    "srcs": ["merck", "ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Pain / fever", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(220, "mg")),
             "dosingInterval": every(480, 720), "asNeeded": True,
             "maxDailyDose": val(660, "mg"), "maxDurationDays": 10,
             "notes": "OTC naproxen sodium. 220 mg sodium salt equals 200 mg naproxen base."},
        ]},
        {"name": "Rheumatoid arthritis / osteoarthritis / ankylosing spondylitis", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([250, 375, 500], "mg")),
             "dosingInterval": every(720, 720), "asNeeded": False,
             "maxDailyDose": val(1000, "mg"),
             "notes": "Prescription dosing, twice daily. Up to 1500 mg/day for limited periods."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("cox-inhibition-peripheral"),
        moa("cox-inhibition-central", "probable"),
    ],
    "metabolismPathways": [
        path("cyp2c9", enzyme="CYP2C9", effect="substrate", note="Primary, to 6-O-desmethylnaproxen."),
        path("cyp1a2", enzyme="CYP1A2", effect="substrate", note="Secondary."),
        path("glucuronidation"),
    ],
    "activeMetabolites": [
        metabolite("6-O-desmethylnaproxen", None, "inactive", "less-potent", "cyp2c9", "CYP2C9", None,
                   "No meaningful anti-inflammatory activity."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(12, 17, "h"), "bioavailability": val(0.95),
         "volumeOfDistribution": val(0.16, "L/kg"), "proteinBinding": val(0.99),
         "timeToOnset": val(1, "h"), "durationOfAction": rng(8, 12, "h"),
         "timeToPeak": rng(1, 4, "h"),
         "notes": "The long half-life is what sets naproxen apart from ibuprofen: 12-17 h versus 2-4 h, hence twice-daily dosing and a longer washout before any other NSAID."},
    ],
}

# ---------------------------------------------------------------- 19
DRUGS["propranolol"] = {
    "drugName": "Propranolol (immediate release)",
    "synonyms": ["Inderal"],
    "codes": {"atc": ["C07AA05"]},
    "srcs": ["merck", "ahfs", "dailymed", "statpearls"],
    "indications": [
        {"name": "Hypertension", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([40, 80, 120, 160], "mg")),
             "dosingInterval": every(360, 720), "asNeeded": False,
             "maxDailyDose": val(640, "mg"),
             "notes": "Start 40 mg twice daily. Usual maintenance 120-240 mg/day. The 640 mg ceiling is only reachable on a 6-hourly schedule; twice-daily dosing tops out at 320 mg/day."},
        ]},
        {"name": "Migraine prophylaxis", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([80, 160, 240], "mg")),
             "dosingInterval": every(480, 720), "asNeeded": False,
             "maxDailyDose": val(240, "mg"),
             "notes": "In divided doses. Prophylactic, not abortive — it does nothing for an attack in progress."},
        ]},
        {"name": "Performance / situational anxiety", "labelStatus": "off-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([10, 20, 40], "mg")),
             "asNeeded": True, "maxDailyDose": val(120, "mg"),
             "notes": "Genuinely off-label in the sense the term is meant for: an unapproved medical use with substantial clinical basis. Taken 30-60 minutes before the event; blunts the peripheral symptoms (tremor, tachycardia) rather than the anxiety itself."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("beta-adrenergic-antagonist-nonselective",
            note="Non-selective is the operative word for this database: blocking beta-2 removes the vasodilatory counterweight to alpha-1 vasoconstriction. Pair it with any alpha agonist and the result is unopposed alpha stimulation."),
    ],
    "metabolismPathways": [
        path("cyp2d6", enzyme="CYP2D6", effect="substrate", note="Primary, via 4-hydroxylation. Polymorphic."),
        path("cyp1a2", enzyme="CYP1A2", effect="substrate", note="Major, via side-chain oxidation."),
        path("cyp2c19", enzyme="CYP2C19", effect="substrate", note="Minor."),
        path("glucuronidation"),
    ],
    "activeMetabolites": [
        metabolite("4-hydroxypropranolol", "4-hydroxypropranolol", "therapeutic", "comparable", "cyp2d6", "CYP2D6", None,
                   "Equipotent as a beta-blocker but much shorter-lived. Formed on first pass, so it contributes after oral doses and not after intravenous ones."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(3, 6, "h"), "bioavailability": rng(0.25, 0.3),
         "volumeOfDistribution": val(4, "L/kg"), "proteinBinding": val(0.9),
         "timeToOnset": rng(1, 2, "h"), "durationOfAction": rng(6, 12, "h"),
         "timeToPeak": rng(1, 4, "h"),
         "notes": "Bioavailability is low and variable because of extensive first-pass metabolism — which means anything inhibiting CYP2D6 or CYP1A2 raises exposure disproportionately, not proportionately. Two of the four enzyme inhibitors in this database hit both."},
    ],
    "notes": "Abrupt discontinuation after regular use can precipitate rebound tachycardia, hypertension and angina. That is a stopping hazard rather than a drug interaction, and this schema has nowhere to put it.",
}

# ---------------------------------------------------------------- 20
DRUGS["pseudoephedrine-ir"] = {
    "drugName": "Pseudoephedrine (immediate release)",
    "synonyms": ["Sudafed", "PSE"],
    "codes": {"atc": ["R01BA02"]},
    "srcs": ["ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Nasal / eustachian tube congestion", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(val(60, "mg")),
             "dosingInterval": every(240, 360), "asNeeded": True,
             "maxDailyDose": val(240, "mg"), "maxDurationDays": 7,
             "notes": "Immediate-release tablets only, per the request. Sold behind the pharmacy counter in the US under the Combat Methamphetamine Epidemic Act, with purchase limits."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("alpha-adrenergic-agonist", note="Direct partial agonism at alpha-1; vasoconstriction of the nasal mucosa is the therapeutic effect."),
        moa("sympathomimetic-indirect", note="Displaces stored noradrenaline from presynaptic vesicles. This is the shared mechanism with amphetamine and the reason the two stack on blood pressure."),
    ],
    "metabolismPathways": [
        path("renal-excretion-unchanged", fraction=rng(0.55, 0.75),
             note="Dominant, and strongly urinary-pH-dependent in the same direction as amphetamine: alkaline urine raises exposure and prolongs half-life, acidic urine shortens it."),
        path("n-demethylation", fraction=rng(0.1, 0.2), note="Minor, to inactive norpseudoephedrine."),
    ],
    "activeMetabolites": [
        metabolite("None clinically relevant", None, "inactive", None, "n-demethylation", None, None,
                   "Largely excreted unchanged."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(3, 6, "h"), "bioavailability": rng(0.9, 1.0),
         "volumeOfDistribution": rng(2.6, 3.5, "L/kg"),
         "timeToOnset": rng(15, 30, "min"), "durationOfAction": rng(4, 6, "h"),
         "timeToPeak": rng(1, 3, "h"),
         "notes": "Half-life varies roughly twofold with urinary pH."},
    ],
}

# ---------------------------------------------------------------- 21
DRUGS["sertraline"] = {
    "drugName": "Sertraline",
    "synonyms": ["Zoloft"],
    "codes": {"atc": ["N06AB06"]},
    "srcs": ["merck", "ahfs", "dailymed", "statpearls"],
    "indications": [
        {"name": "Major depressive disorder", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([50, 100, 150, 200], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(200, "mg"),
             "notes": "Start 50 mg daily; titrate at intervals of at least one week. Antidepressant effect takes 2-6 weeks; the interaction risks below start on day one."},
        ]},
        {"name": "Panic disorder / OCD / PTSD / social anxiety disorder", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([25, 50, 100, 150, 200], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": False,
             "maxDailyDose": val(200, "mg"),
             "notes": "Panic and PTSD start lower, at 25 mg, because early activation is worse in anxiety disorders."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("serotonin-reuptake-inhibition"),
    ],
    "metabolismPathways": [
        path("cyp2b6", enzyme="CYP2B6", effect="substrate", note="Principal route for N-demethylation."),
        path("cyp2c19", enzyme="CYP2C19", effect="substrate-and-inhibitor", note="Contributes to clearance; weakly inhibited."),
        path("cyp2c9", enzyme="CYP2C9", effect="substrate-and-inhibitor", note="Weak inhibition."),
        path("cyp3a4", enzyme="CYP3A4", effect="substrate-and-inhibitor",
             note="Weak to moderate inhibition. Enough to matter for triazolam, which has almost no margin."),
        path("cyp2d6", enzyme="CYP2D6", effect="substrate-and-inhibitor",
             note="Dose-dependent moderate inhibition — clinically slight at 50 mg, substantial at 150-200 mg. This single property drives most of sertraline's interactions in this database."),
    ],
    "transporters": [
        transporter("p-glycoprotein", "inhibitor", "Weak. Relevant only where a P-gp substrate's safety depends on efflux, which in this set means loperamide."),
    ],
    "activeMetabolites": [
        metabolite("N-desmethylsertraline", "n-desmethylsertraline", "therapeutic", "less-potent", "cyp2b6", "CYP2B6", None,
                   "Roughly 20-fold less potent at SERT, so it contributes little to effect — but its half-life is 62-104 h against the parent's 26 h, so it dominates the washout period after stopping."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": val(26, "h"), "bioavailability": val(0.44),
         "volumeOfDistribution": val(20, "L/kg"), "proteinBinding": val(0.98),
         "timeToPeak": rng(4.5, 8.4, "h"), "durationOfAction": val(24, "h"),
         "notes": "Steady state takes about a week. Enzyme inhibition builds over that period and decays over a longer one, because the desmethyl metabolite persists — so a sertraline interaction does not switch off the day the drug is stopped."},
    ],
    "notes": "The interaction hub of this database on the pharmacodynamic side (serotonin) and one of two on the pharmacokinetic side (CYP2D6). Both effects scale with dose.",
}

# ---------------------------------------------------------------- 22
DRUGS["simethicone"] = {
    "drugName": "Simethicone",
    "synonyms": ["Gas-X", "activated dimethicone", "activated polymethylsiloxane"],
    "codes": {"atc": ["A03AX13"]},
    "srcs": ["ahfs", "dailymed", "drugbank"],
    "indications": [
        {"name": "Flatulence / functional gastric bloating", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([40, 80, 125, 180], "mg")),
             "asNeeded": True, "maxDailyDose": val(500, "mg"),
             "notes": "After meals and at bedtime. Chewable tablets must be chewed thoroughly — the mechanism is physical contact with gas bubbles."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("surface-tension-reduction", note="Lowers the surface tension of gas bubbles so they coalesce and pass. Entirely physical; no receptor, no enzyme, no absorption."),
    ],
    "metabolismPathways": [
        path("not-absorbed", fraction=val(1.0), note="Excreted unchanged in faeces."),
    ],
    "activeMetabolites": [
        metabolite("None", None, "inactive", None, None, None, None, "Not absorbed, so not metabolised."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "not-applicable",
         "bioavailability": val(0.0),
         "notes": "No systemic exposure."},
    ],
    "notes": "Screened clean against every other record in this database, and that is a finding rather than an omission. Simethicone is the control case that shows the difference between an empty interactions array and a populated interactionScreening array — without the latter you cannot tell 'inert' from 'nobody checked'.",
}

# ---------------------------------------------------------------- 23
DRUGS["temazepam"] = {
    "drugName": "Temazepam",
    "synonyms": ["Restoril"],
    "codes": {"atc": ["N05CD07"]},
    "srcs": ["merck", "ahfs", "dailymed", "drugbank"],
    "controlledSubstance": {"usSchedule": "IV"},
    "indications": [
        {"name": "Short-term treatment of insomnia", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([7.5, 15, 22.5, 30], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": True,
             "maxDailyDose": val(30, "mg"), "maxDurationDays": 35,
             "notes": "At bedtime, with 7-8 hours available for sleep. Labelled for short-term use, generally 7-10 days; reassess beyond 2-3 weeks."},
            {"population": "geriatric", "route": "oral", "dose": flat(steps([7.5, 15], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": True,
             "maxDailyDose": val(15, "mg"),
             "notes": "Start at 7.5 mg. Falls and next-day confusion are the limiting risks."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("gaba-a-positive-allosteric-modulation"),
    ],
    "metabolismPathways": [
        path("glucuronidation", fraction=rng(0.8, 0.9),
             note="Direct conjugation, with no CYP step. This is the single most useful fact about temazepam in a polypharmacy database: CYP inhibitors, including every one in this set, leave it untouched. Contrast triazolam, which is pure CYP3A4."),
        path("cyp3a4", enzyme="CYP3A4", effect="substrate", fraction=val(0.05),
             note="Trivial route, to oxazepam. Not enough to create a clinically meaningful 3A4 interaction."),
    ],
    "activeMetabolites": [
        metabolite("Oxazepam", "oxazepam", "therapeutic", "comparable", "cyp3a4", "CYP3A4", val(0.05),
                   "Minor by fraction, and itself glucuronidated. Does not materially extend the parent's duration."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(8, 15, "h"), "bioavailability": val(0.96),
         "volumeOfDistribution": rng(0.8, 1.0, "L/kg"), "proteinBinding": val(0.96),
         "timeToOnset": rng(30, 60, "min"), "durationOfAction": rng(6, 8, "h"),
         "timeToPeak": rng(1.2, 1.6, "h"),
         "notes": "Slow absorption relative to other hypnotics — the reason it is dosed 30 minutes or more before bed. The 8-15 h half-life is long enough that next-morning residual effect is common at 30 mg."},
        {"population": "geriatric", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(14, 25, "h"),
         "notes": "Glucuronidation is better preserved with age than CYP oxidation, so the increase is milder than for triazolam — but not absent."},
    ],
    "notes": "Schedule IV. Paired deliberately with triazolam: same class, same indication, and opposite metabolic profiles. Any interaction flagged for triazolam on CYP3A4 grounds and screened clean for temazepam is a real substitution.",
}

# ---------------------------------------------------------------- 24
DRUGS["triazolam"] = {
    "drugName": "Triazolam",
    "synonyms": ["Halcion"],
    "codes": {"atc": ["N05CD05"]},
    "srcs": ["merck", "ahfs", "dailymed", "drugbank"],
    "controlledSubstance": {"usSchedule": "IV"},
    "indications": [
        {"name": "Short-term treatment of insomnia", "labelStatus": "on-label", "dosageRegimens": [
            {"population": "adult", "route": "oral", "dose": flat(steps([0.125, 0.25, 0.5], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": True,
             "maxDailyDose": val(0.5, "mg"), "maxDurationDays": 21,
             "notes": "0.25 mg at bedtime is the usual dose. 0.5 mg only for exceptional non-responders. Labelled for 7-10 days; anterograde amnesia is dose-related and is the characteristic adverse effect."},
            {"population": "geriatric", "route": "oral", "dose": flat(steps([0.125, 0.25], "mg")),
             "dosingInterval": every(1440, 1440), "asNeeded": True,
             "maxDailyDose": val(0.25, "mg"),
             "notes": "Start 0.125 mg, do not exceed 0.25 mg."},
        ]},
    ],
    "mechanismsOfAction": [
        moa("gaba-a-positive-allosteric-modulation"),
    ],
    "metabolismPathways": [
        path("cyp3a4", enzyme="CYP3A4", effect="substrate", fraction=rng(0.9, 0.95),
             note="Almost exclusively. Triazolam is the textbook probe substrate for CYP3A4 because the effect size is enormous: ketoconazole raises its AUC more than twentyfold. Combined with a sub-milligram therapeutic dose, this leaves essentially no margin for a 3A4 inhibitor."),
    ],
    "activeMetabolites": [
        metabolite("alpha-hydroxytriazolam", "alpha-hydroxytriazolam", "therapeutic", "comparable", "cyp3a4", "CYP3A4", None,
                   "Pharmacologically active but rapidly glucuronidated, so it contributes little under normal conditions. When CYP3A4 is inhibited, parent accumulates and this route contributes even less."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(1.5, 5.5, "h"), "bioavailability": val(0.44),
         "volumeOfDistribution": rng(0.8, 1.8, "L/kg"), "proteinBinding": val(0.89),
         "timeToOnset": rng(15, 30, "min"), "durationOfAction": rng(3, 5, "h"),
         "timeToPeak": rng(1, 2, "h"),
         "notes": "The shortest half-life of the hypnotics here, which is its advantage (little next-morning residue) and its problem (early-morning rebound insomnia and rebound anxiety)."},
        {"population": "geriatric", "route": "oral", "absorptionModel": "immediate-release",
         "halfLife": rng(3, 9, "h"),
         "notes": "CYP3A4-dependent clearance falls with age, so exposure roughly doubles."},
    ],
    "notes": "Schedule IV. The narrowest therapeutic margin in this database, and the drug most sensitive to a CYP3A4 interaction.",
}
