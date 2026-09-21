"""Metabolite records. Same schema, recordType `metabolite`, no indications.

A metabolite gets its own record when something is true of it that is not true
of its parent: its own mechanism, its own disposal route, its own half-life, or
its own interactions. Metabolites that are merely the parent's exhaust are
listed in the parent's activeMetabolites array and stop there.
"""

from drugs_a import rng, val, moa, path, transporter, absent

METABOLITES = {}

METABOLITES["napqi"] = {
    "drugName": "NAPQI",
    "synonyms": ["N-acetyl-p-benzoquinone imine"],
    "parentDrugIds": ["acetaminophen"],
    "srcs": ["statpearls", "ahfs"],
    "mechanismsOfAction": [
        moa("protein-arylation", note="Covalent binding to cysteine residues on hepatocyte protein, mitochondrial protein included. The oxidative stress and centrilobular necrosis that follow are consequences of this rather than separate mechanisms."),
    ],
    "metabolismPathways": [
        path("glutathione-conjugation", note="At therapeutic doses effectively all of it is conjugated with glutathione and excreted as cysteine and mercapturate conjugates. The pathway is saturable, which is why overdose behaves so differently from therapeutic dosing: once hepatic glutathione is depleted, what is left arylates protein instead."),
    ],
    "interactions": [
        {"interactingDrug": "n-acetylcysteine", "external": True, "interactionType": "antidote", "severity": "major",
         "evidence": "established",
         "suggestedAction": "Not a pairing to avoid — the reason acetaminophen overdose is survivable. Effectiveness is time-critical, approaching complete within 8 hours of ingestion and falling steeply after that.",
         "note": "N-acetylcysteine replenishes the glutathione this pathway consumes. Recorded properly in 1.5: the interaction-types vocabulary previously had no `antidote` term, so this sat as prose on this record's notes field."},
    ],
    "knownAbsences": [
        absent("pharmacokinetics", "No plasma pharmacokinetics are reported: NAPQI is too reactive and too short-lived to be measured that way, and exposure is inferred from the parent dose and from glutathione depletion instead. This absence is settled, not pending.", status="not-applicable"),
        absent("codes.rxcui", "A reactive intermediate, not a marketed substance. No RxNorm concept exists.", status="not-applicable"),
    ],
    "notes": "Corrected in 1.5: the uploaded record filed the 'no plasma PK' absence under `field: codes`, where the pointer and the prose disagreed. It also carried a pharmacokinetics entry with route `oral` and absorptionModel `immediate-release` for a substance nobody administers — shape filled in for its own sake. Both removed.",
}

METABOLITES["am404"] = {
    "drugName": "AM404",
    "synonyms": ["N-arachidonoylphenolamine"],
    "parentDrugIds": ["acetaminophen"],
    "srcs": ["statpearls", "drugbank"],
    "mechanismsOfAction": [
        moa("cannabinoid-am404", "proposed",
            "Anandamide reuptake inhibition and CB1 activity. Moved here from the acetaminophen record in 1.5, following the precedent NAPQI already set: a metabolite's mechanism belongs on the metabolite, with the parent carrying only the link and the fraction of dose."),
        moa("trpv1-activation", "proposed", "Shared with the parent compound."),
    ],
    "metabolismPathways": [
        path("hydrolysis", note="Formed rather than cleared by this route: p-aminophenol, itself a deacetylation product of acetaminophen, is conjugated with arachidonic acid by fatty acid amide hydrolase. The formation happens in brain and spinal cord, not liver, which is why AM404 is a central story and NAPQI is a hepatic one."),
    ],
    "knownAbsences": [
        absent("pharmacokinetics", "No human plasma pharmacokinetics reported. Formation is local to CNS tissue and the quantities involved are below routine assay. The mechanism's evidence level stays `proposed` largely for this reason."),
    ],
    "notes": "Expanded from a stub that contained only an id, a parent link, and a source titled 'google'. The mechanism it now carries was previously duplicated on the acetaminophen record.",
}

METABOLITES["dextrorphan"] = {
    "drugName": "Dextrorphan",
    "synonyms": ["DXO"],
    "parentDrugIds": ["dextromethorphan"],
    "srcs": ["ahfs", "statpearls", "drugbank"],
    "mechanismsOfAction": [
        moa("noncompetitive-nmda-receptor-antagonist", note="More potent at NMDA than the parent."),
        moa("sigma-1-agonist", "probable", "Weaker than the parent here — the two compounds are not interchangeable pharmacologically, they are complementary."),
    ],
    "metabolismPathways": [
        path("glucuronidation", note="Primary clearance, then renal excretion."),
        path("cyp3a4", enzyme="CYP3A4", effect="substrate", note="Minor, to 3-hydroxymorphinan."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "halfLife": rng(3, 6, "h"),
         "notes": "Formed on first pass, so dextrorphan exposure after an oral dose substantially exceeds parent exposure in CYP2D6 extensive metabolisers and collapses in poor metabolisers."},
    ],
    "notes": "The reason a CYP2D6 inhibitor does two things at once to dextromethorphan: raises the parent and suppresses this. Effects do not simply add up, they redistribute between two compounds with different receptor profiles.",
}

METABOLITES["salicylic-acid"] = {
    "drugName": "Salicylic acid",
    "synonyms": ["salicylate"],
    "parentDrugIds": ["aspirin"],
    "srcs": ["ahfs", "statpearls", "drugbank"],
    "mechanismsOfAction": [
        moa("cox-inhibition-peripheral", note="Reversible and weak. Carries aspirin's analgesic and anti-inflammatory effect but NOT the irreversible antiplatelet effect, which requires intact aspirin."),
    ],
    "metabolismPathways": [
        path("glycine-conjugation", note="To salicyluric acid. Saturable at analgesic doses, which converts salicylate elimination from first-order to zero-order — the reason salicylate half-life stretches from about 3 hours at low dose to 15-30 hours at high dose, and the reason aspirin overdose escalates non-linearly."),
        path("glucuronidation", note="Also saturable."),
        path("renal-excretion-unchanged", note="pH-dependent: alkalinisation of urine markedly increases excretion, which is the basis of urinary alkalinisation in salicylate poisoning."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "halfLife": rng(2, 3, "h"),
         "notes": "At low analgesic doses only. Rises to 15-30 h at anti-inflammatory and toxic doses as conjugation saturates. A single half-life figure for salicylate is meaningless without the dose attached."},
    ],
    "notes": "Where almost all of aspirin's systemic activity actually lives, and the reason aspirin's own 15-20 minute half-life is so misleading.",
}

METABOLITES["n-desmethylsertraline"] = {
    "drugName": "N-desmethylsertraline",
    "synonyms": ["desmethylsertraline"],
    "parentDrugIds": ["sertraline"],
    "srcs": ["ahfs", "dailymed", "drugbank"],
    "mechanismsOfAction": [
        moa("serotonin-reuptake-inhibition", note="Roughly 20-fold less potent than sertraline at SERT. Contributes little to therapeutic effect."),
    ],
    "metabolismPathways": [
        path("cyp3a4", enzyme="CYP3A4", effect="substrate"),
        path("glucuronidation"),
    ],
    "pharmacokinetics": [
        {"population": "adult", "halfLife": rng(62, 104, "h"),
         "notes": "Two to four times the parent's half-life. Clinically this is a washout fact rather than an efficacy fact: it takes roughly 2-3 weeks after stopping sertraline for this to clear, which is part of why the serotonin-syndrome interactions on the parent record do not end at the last dose."},
    ],
}

METABOLITES["4-hydroxypropranolol"] = {
    "drugName": "4-hydroxypropranolol",
    "parentDrugIds": ["propranolol"],
    "srcs": ["ahfs", "drugbank"],
    "mechanismsOfAction": [
        moa("beta-adrenergic-antagonist-nonselective", note="Roughly equipotent with the parent."),
    ],
    "metabolismPathways": [path("glucuronidation")],
    "pharmacokinetics": [
        {"population": "adult", "halfLife": rng(2, 3, "h"),
         "notes": "Shorter-lived than the parent. Formed on first pass, so it contributes to effect after oral dosing and not after intravenous dosing — the reason oral and IV propranolol are not simply dose-equivalent."},
    ],
}

METABOLITES["paraxanthine"] = {
    "drugName": "Paraxanthine",
    "synonyms": ["1,7-dimethylxanthine"],
    "parentDrugIds": ["caffeine"],
    "srcs": ["statpearls", "drugbank"],
    "mechanismsOfAction": [
        moa("adenosine-receptor-antagonist", note="Comparable potency to caffeine. Around 84% of a caffeine dose passes through here, so a large share of what people experience as caffeine is really this."),
    ],
    "metabolismPathways": [
        path("cyp1a2", enzyme="CYP1A2", effect="substrate"),
        path("n-acetylation", note="NAT2-dependent, and NAT2 is polymorphic — a second source of between-person variability on top of CYP1A2."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "halfLife": rng(3, 4, "h")},
    ],
}

METABOLITES["4-hydroxyamphetamine"] = {
    "drugName": "4-hydroxyamphetamine",
    "parentDrugIds": ["amphetamine-ir", "amphetamine-xr"],
    "srcs": ["drugbank", "statpearls"],
    "mechanismsOfAction": [
        moa("nd-releaser", "probable", "Less potent than the parent and less CNS-penetrant, so its contribution to clinical effect is small."),
    ],
    "metabolismPathways": [
        path("sulfate-conjugation"),
        path("renal-excretion-unchanged"),
    ],
    "knownAbsences": [
        absent("pharmacokinetics", "Not separately characterised in routine sources; amphetamine PK is reported for the parent enantiomers."),
    ],
}

METABOLITES["nordiphenhydramine"] = {
    "drugName": "Nordiphenhydramine",
    "synonyms": ["desmethyldiphenhydramine"],
    "parentDrugIds": ["diphenhydramine"],
    "srcs": ["drugbank"],
    "mechanismsOfAction": [
        moa("h1-receptor-blockade-inverse-agonism", "probable", "Weakly active; further demethylation yields inactive products."),
    ],
    "metabolismPathways": [path("cyp2d6", enzyme="CYP2D6", effect="substrate")],
    "knownAbsences": [
        absent("pharmacokinetics", "Not separately characterised in the sources used here."),
    ],
}

METABOLITES["oxazepam"] = {
    "drugName": "Oxazepam",
    "parentDrugIds": ["temazepam"],
    "srcs": ["ahfs", "drugbank"],
    "mechanismsOfAction": [moa("gaba-a-positive-allosteric-modulation")],
    "metabolismPathways": [
        path("glucuronidation", note="Direct conjugation, no CYP step — the same property as its parent. Oxazepam is itself a marketed benzodiazepine elsewhere; here it appears only as a minor temazepam metabolite."),
    ],
    "pharmacokinetics": [
        {"population": "adult", "halfLife": rng(5, 15, "h")},
    ],
    "notes": "A metabolite that is also a drug in its own right. Recorded here as a metabolite only, since no record in this database is dosing it.",
}

METABOLITES["alpha-hydroxytriazolam"] = {
    "drugName": "alpha-hydroxytriazolam",
    "parentDrugIds": ["triazolam"],
    "srcs": ["ahfs", "drugbank"],
    "mechanismsOfAction": [
        moa("gaba-a-positive-allosteric-modulation", "probable",
            "Pharmacologically active but rapidly conjugated, so circulating levels stay low and its contribution is minor."),
    ],
    "metabolismPathways": [path("glucuronidation")],
    "knownAbsences": [
        absent("pharmacokinetics", "Half-life not separately established; clearance is rapid enough that it is generally treated as a transient."),
    ],
}
