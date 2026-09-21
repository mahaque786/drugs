"""Controlled vocabularies. Expanded from the uploaded v1.4 set.

Conventions settled here (these were drifting across the uploaded records):
  * Metabolism pathway terms name the SPECIFIC enzyme where one is known
    (cyp2e1, cyp2d6, ...). The generic `cyp450-oxidation` term is retained
    but deprecated, so "everything CYP2D6 touches" is a single-term query.
  * The `enzyme` field is still populated alongside, for display.
  * Enum-valued fields that previously had no vocabulary file (severity,
    evidence, labelStatus, metabolite activity, enzyme effect) now have one,
    so the validator can check them.
"""

VOCAB = {}

VOCAB["mechanisms"] = {
    "name": "mechanisms",
    "label": "Mechanisms of action",
    "description": "Controlled mechanism terms. Keep each term to one mechanism, not a mechanism plus its downstream consequence.",
    "closed": False,
    "terms": [
        {"id": "adenosine-receptor-antagonist", "label": "Adenosine A1/A2A receptor antagonist"},
        {"id": "alpha-adrenergic-agonist", "label": "α-adrenergic receptor agonist"},
        {"id": "beta-adrenergic-antagonist-nonselective", "label": "Non-selective β-adrenergic antagonist", "note": "Blocks β1 and β2. The β2 blockade is what leaves α-mediated vasoconstriction unopposed when a sympathomimetic is on board."},
        {"id": "bile-acid-sequestration", "label": "Bile acid sequestration (anion-exchange resin)"},
        {"id": "cannabinoid-am404", "label": "AM404-mediated cannabinoid system modulation", "note": "Attributed to the metabolite. Record on the AM404 record; the parent record carries the metabolite link."},
        {"id": "competitive-histamine-h2-receptor-antagonist", "label": "Competitive histamine H₂-receptor antagonist"},
        {"id": "cox-1-irreversible-acetylation", "label": "Irreversible COX-1 acetylation", "note": "Covalent, so the effect outlives the drug and persists for the life of the platelet. This is why aspirin is not interchangeable with a reversible COX inhibitor."},
        {"id": "cox-inhibition-central", "label": "Central COX pathway inhibition", "note": "Reduced CNS prostaglandin synthesis is the consequence, not a separate mechanism."},
        {"id": "cox-inhibition-peripheral", "label": "Peripheral COX inhibition"},
        {"id": "gaba-a-positive-allosteric-modulation", "label": "GABA-A positive allosteric modulation (benzodiazepine site)"},
        {"id": "h1-receptor-blockade-inverse-agonism", "label": "H1 receptor blockade / inverse agonism"},
        {"id": "herg-potassium-channel-blockade", "label": "hERG (Kv11.1) potassium channel blockade", "note": "Off-target. Only reached at supratherapeutic systemic exposure for drugs designed to act in the gut."},
        {"id": "mt1-mt2-agonist", "label": "Melatonin MT1/MT2 receptor agonist"},
        {"id": "mu-opioid-agonist-peripheral", "label": "Peripheral μ-opioid receptor agonist", "note": "Confined to the myenteric plexus by P-gp efflux at the blood-brain barrier. Saturate or inhibit P-gp and the confinement fails."},
        {"id": "nd-releaser", "label": "Norepinephrine & dopamine releaser"},
        {"id": "ndri", "label": "Norepinephrine-dopamine reuptake inhibition"},
        {"id": "noncompetitive-nmda-receptor-antagonist", "label": "Non-competitive NMDA-receptor antagonist"},
        {"id": "orexin-receptor-antagonist-dual", "label": "Dual orexin receptor (OX1/OX2) antagonist"},
        {"id": "protein-arylation", "label": "Covalent protein arylation", "note": "Electrophilic binding to cysteine residues on cellular protein. The oxidative stress and necrosis that follow are consequences, not separate mechanisms."},
        {"id": "proton-pump-inhibitor", "label": "Gastric H⁺/K⁺-ATPase (proton pump) inhibition"},
        {"id": "serotonergic-descending-modulation", "label": "Descending serotonergic pathway modulation"},
        {"id": "serotonin-reuptake-inhibition", "label": "Selective serotonin reuptake inhibition (SERT)"},
        {"id": "sigma-1-agonist", "label": "σ-1 (sigma-1) receptor agonist"},
        {"id": "surface-tension-reduction", "label": "Gastrointestinal surface-tension reduction (antifoaming)", "note": "Physical, not receptor-mediated. Nothing is absorbed, which is why this drug is inert in every interaction pair."},
        {"id": "sympathomimetic-indirect", "label": "Indirect sympathomimetic (displaces stored noradrenaline)"},
        {"id": "trpv1-activation", "label": "TRPV1 receptor activation"},
    ],
}

VOCAB["metabolism-pathways"] = {
    "name": "metabolism-pathways",
    "label": "Metabolism pathways",
    "description": "Route of biotransformation. Name the specific enzyme in the term where one is known, and repeat it in the `enzyme` field for display.",
    "closed": False,
    "terms": [
        {"id": "cyp1a2", "label": "CYP1A2"},
        {"id": "cyp2b6", "label": "CYP2B6"},
        {"id": "cyp2c8", "label": "CYP2C8"},
        {"id": "cyp2c9", "label": "CYP2C9"},
        {"id": "cyp2c19", "label": "CYP2C19"},
        {"id": "cyp2d6", "label": "CYP2D6"},
        {"id": "cyp2e1", "label": "CYP2E1"},
        {"id": "cyp3a4", "label": "CYP3A4"},
        {"id": "cyp450-oxidation", "label": "CYP450 oxidation (unspecified isoform)", "deprecated": True, "note": "Retained so v1.0 records still resolve. Use the specific isoform term instead; a record using this term cannot be found by an isoform query."},
        {"id": "glucuronidation", "label": "Glucuronidation", "note": "Phase II. Not a CYP route, so CYP inhibitors and inducers do not touch it. This is the whole reason temazepam and triazolam behave so differently in a polypharmacy setting."},
        {"id": "glutathione-conjugation", "label": "Glutathione conjugation"},
        {"id": "glycine-conjugation", "label": "Glycine conjugation"},
        {"id": "hydrolysis", "label": "Hydrolysis (esterase)"},
        {"id": "n-acetylation", "label": "N-acetylation"},
        {"id": "n-demethylation", "label": "N-demethylation"},
        {"id": "not-absorbed", "label": "Not systemically absorbed", "note": "Use for agents that act luminally and are excreted unchanged in faeces. Records the absence of systemic disposition as a positive fact rather than an empty pharmacokinetics array."},
        {"id": "renal-excretion-unchanged", "label": "Renal excretion unchanged"},
        {"id": "sulfate-conjugation", "label": "Sulfate conjugation"},
    ],
}

VOCAB["interaction-types"] = {
    "name": "interaction-types",
    "label": "Interaction types",
    "description": "The kind of interaction between two drugs. Pharmacokinetic types say which step of ADME is affected; pharmacodynamic types describe what happens at the target.",
    "closed": False,
    "terms": [
        {"id": "antidote", "label": "Antidote / reversal agent", "note": "Added in 1.5. Previously there was no way to record that N-acetylcysteine answers NAPQI, so the fact sat in prose on the NAPQI record."},
        {"id": "pd-additive-cns-depression", "label": "Pharmacodynamic — additive CNS depression", "note": "Split out from pd-synergism in 1.5. Sedative stacking is the single most common serious pairing in an OTC-plus-hypnotic set and deserves to be queryable on its own."},
        {"id": "pd-additive-toxicity", "label": "Pharmacodynamic — additive toxicity"},
        {"id": "pd-antagonism", "label": "Pharmacodynamic — antagonism"},
        {"id": "pd-synergism", "label": "Pharmacodynamic — synergism"},
        {"id": "pk-absorption", "label": "Pharmacokinetic — absorption"},
        {"id": "pk-distribution", "label": "Pharmacokinetic — distribution"},
        {"id": "pk-elimination", "label": "Pharmacokinetic — elimination"},
        {"id": "pk-metabolism", "label": "Pharmacokinetic — metabolism"},
        {"id": "pk-transporter", "label": "Pharmacokinetic — transporter", "note": "Added in 1.5 for P-gp. Distinct from metabolism: a P-gp inhibitor can change where a drug goes without changing how fast it is cleared."},
        {"id": "therapeutic-duplication", "label": "Therapeutic duplication"},
        {"id": "unknown", "label": "Mechanism unknown"},
    ],
}

VOCAB["populations"] = {
    "name": "populations",
    "label": "Populations",
    "description": "Patient group a dose or PK value applies to. Split these finely; PK values do not transfer between groups.",
    "closed": False,
    "terms": [
        {"id": "adult", "label": "Adult", "note": "Generally 18 years and over."},
        {"id": "adult-healthy", "label": "Healthy adult", "note": "Use for PK values measured in healthy volunteers."},
        {"id": "adolescent", "label": "Adolescent", "note": "12 to 17 years."},
        {"id": "pediatric", "label": "Paediatric"},
        {"id": "infant", "label": "Infant"},
        {"id": "neonate", "label": "Neonate"},
        {"id": "geriatric", "label": "Geriatric"},
        {"id": "hepatic-impairment", "label": "Hepatic impairment"},
        {"id": "renal-impairment", "label": "Renal impairment"},
        {"id": "pregnancy", "label": "Pregnancy"},
        {"id": "cyp2d6-poor-metabolizer", "label": "CYP2D6 poor metaboliser", "note": "Roughly 5-10% of people of European ancestry. For a CYP2D6-cleared drug this is a different PK population, not a footnote."},
    ],
}

VOCAB["routes"] = {
    "name": "routes",
    "label": "Routes of administration",
    "description": "How the dose is given.",
    "closed": False,
    "terms": [
        {"id": "oral", "label": "Oral"},
        {"id": "intravenous", "label": "Intravenous"},
        {"id": "intramuscular", "label": "Intramuscular"},
        {"id": "subcutaneous", "label": "Subcutaneous"},
        {"id": "rectal", "label": "Rectal"},
        {"id": "inhaled", "label": "Inhaled"},
        {"id": "topical", "label": "Topical"},
        {"id": "transdermal", "label": "Transdermal"},
        {"id": "sublingual", "label": "Sublingual"},
        {"id": "intranasal", "label": "Intranasal"},
        {"id": "ophthalmic", "label": "Ophthalmic"},
    ],
}

VOCAB["release-types"] = {
    "name": "release-types",
    "label": "Release types",
    "description": "How a formulation releases the drug. Extended- and delayed-release products are separate records from the immediate-release form rather than a formulation field on one record.",
    "closed": False,
    "terms": [
        {"id": "immediate-release", "label": "Immediate release", "note": "The default for conventional tablets, capsules, and solutions."},
        {"id": "extended-release", "label": "Extended release", "note": "Slowed release over many hours. Absorption becomes rate-limiting, so time to peak stretches and the apparent half-life exceeds the elimination half-life (flip-flop kinetics)."},
        {"id": "delayed-release", "label": "Delayed release", "note": "Release postponed rather than slowed, e.g. enteric-coated."},
        {"id": "not-applicable", "label": "Not applicable", "note": "For luminally-acting agents with no systemic absorption."},
    ],
}

VOCAB["units"] = {
    "name": "units",
    "label": "Units",
    "description": "UCUM unit codes. Note that UCUM writes microgram as ug, not mcg.",
    "closed": True,
    "terms": [
        {"id": "ug", "label": "microgram (ug)"},
        {"id": "mg", "label": "milligram (mg)"},
        {"id": "g", "label": "gram (g)"},
        {"id": "ug/kg", "label": "microgram per kilogram"},
        {"id": "mg/kg", "label": "milligram per kilogram"},
        {"id": "g/kg", "label": "gram per kilogram"},
        {"id": "mg/m2", "label": "milligram per square metre"},
        {"id": "mL", "label": "millilitre (mL)"},
        {"id": "L", "label": "litre (L)"},
        {"id": "L/kg", "label": "litre per kilogram"},
        {"id": "min", "label": "minute (min)"},
        {"id": "h", "label": "hour (h)"},
        {"id": "d", "label": "day (d)"},
    ],
}

VOCAB["transporters"] = {
    "name": "transporters",
    "label": "Transporters",
    "description": "Membrane transporters a drug is a substrate, inhibitor or inducer of. New in 1.5: P-gp effects are not metabolism and were previously unrecordable.",
    "closed": False,
    "terms": [
        {"id": "p-glycoprotein", "label": "P-glycoprotein (MDR1/ABCB1)", "note": "Efflux pump at the gut wall and blood-brain barrier. Saturable, which is why a drug kept out of the CNS at label doses is not kept out at ten times the label dose."},
        {"id": "bcrp", "label": "Breast cancer resistance protein (ABCG2)"},
        {"id": "oatp1b1", "label": "OATP1B1 (SLCO1B1)"},
    ],
}

VOCAB["enzyme-effects"] = {
    "name": "enzyme-effects",
    "label": "Enzyme and transporter effects",
    "description": "What a drug does to an enzyme or transporter. A drug can be several of these at once for different enzymes, and substrate-plus-inhibitor of the same one.",
    "closed": True,
    "terms": [
        {"id": "substrate", "label": "Substrate", "note": "Cleared by it. Inhibitors of that enzyme raise this drug's exposure."},
        {"id": "inhibitor", "label": "Inhibitor", "note": "Raises exposure of other substrates of that enzyme."},
        {"id": "inducer", "label": "Inducer", "note": "Lowers exposure of other substrates. Onset and offset take days to weeks, unlike inhibition."},
        {"id": "substrate-and-inhibitor", "label": "Substrate and inhibitor"},
    ],
}

VOCAB["severity"] = {
    "name": "severity",
    "label": "Interaction severity",
    "description": "How much the pairing matters. Grades the consequence, not the certainty; use `evidence` for certainty.",
    "closed": True,
    "terms": [
        {"id": "contraindicated", "label": "Contraindicated", "note": "Do not combine."},
        {"id": "major", "label": "Major", "note": "Serious or life-threatening potential. Avoid, or combine only with a specific plan."},
        {"id": "moderate", "label": "Moderate", "note": "Clinically meaningful. Usually manageable with spacing, dose change, or monitoring."},
        {"id": "minor", "label": "Minor", "note": "Measurable but seldom actionable."},
    ],
}

VOCAB["evidence-levels"] = {
    "name": "evidence-levels",
    "label": "Evidence levels",
    "description": "How well established a mechanism or interaction is. Kept separate from severity: a major interaction can rest on case reports, and a minor one on a formal crossover study.",
    "closed": True,
    "terms": [
        {"id": "established", "label": "Established"},
        {"id": "probable", "label": "Probable"},
        {"id": "proposed", "label": "Proposed"},
        {"id": "theoretical", "label": "Theoretical", "note": "Predicted from mechanism, not observed. Common for class effects extrapolated from a better-studied sibling drug."},
    ],
}

VOCAB["label-status"] = {
    "name": "label-status",
    "label": "Label status",
    "description": "Regulatory standing of an indication.",
    "closed": True,
    "terms": [
        {"id": "on-label", "label": "On-label (FDA-approved indication)"},
        {"id": "off-label", "label": "Off-label", "note": "An unapproved MEDICAL use with some clinical basis. Not a slot for non-medical use; see non-medical."},
        {"id": "non-medical", "label": "Non-medical use", "note": "Added in 1.5. Recreational and other non-therapeutic use is not off-label use, and typing it as off-label silently promotes it into anything that filters for clinical indications."},
        {"id": "supplement", "label": "Dietary supplement", "note": "Marketed in the US under DSHEA rather than as a drug: no approved indication, no FDA-reviewed label, and content per unit is not guaranteed."},
    ],
}

VOCAB["metabolite-activity"] = {
    "name": "metabolite-activity",
    "label": "Metabolite activity",
    "description": "What a metabolite does once formed.",
    "closed": True,
    "terms": [
        {"id": "therapeutic", "label": "Therapeutically active"},
        {"id": "toxic", "label": "Toxic"},
        {"id": "mixed", "label": "Mixed", "note": "Carries both the therapeutic effect and a distinct toxicity."},
        {"id": "inactive", "label": "Inactive", "note": "Recorded deliberately. 'No active metabolites' is a finding; an empty array is not."},
    ],
}
