"""Pairwise interactions, as a single source of truth.

The uploaded records recorded interactions one-directionally: each new record
screened everything that existed before it, and positive findings were written
on the newer record pointing backward. That convention is kept — but it is now
derived rather than hand-maintained, so dextromethorphan knowing about
cimetidine while cimetidine knows nothing about dextromethorphan is a
presentation detail instead of a data integrity problem.

ORDER is the canonical record order. build.py places each finding on whichever
of the two drugs comes later in it, and generates screening entries for every
earlier pair with no finding.
"""

ORDER = [
    "acetaminophen", "amphetamine-ir", "amphetamine-xr", "aspirin", "caffeine",
    "cimetidine", "colestipol", "daridorexant", "dextromethorphan",
    "diclofenac-tablets", "diphenhydramine", "esomeprazole", "famotidine",
    "ibuprofen", "levocetirizine", "loperamide", "melatonin", "naproxen",
    "propranolol", "pseudoephedrine-ir", "sertraline", "simethicone",
    "temazepam", "triazolam",
]

SEDATIVES = ["daridorexant", "diphenhydramine", "levocetirizine", "melatonin",
             "temazepam", "triazolam"]
STIMULANTS = ["amphetamine-ir", "amphetamine-xr", "caffeine", "pseudoephedrine-ir"]
NSAIDS = ["aspirin", "diclofenac-tablets", "ibuprofen", "naproxen"]


def P(a, b, itype, severity, action, note, evidence="established"):
    return {"a": a, "b": b, "interactionType": itype, "severity": severity,
            "evidence": evidence, "suggestedAction": action, "note": note}


PAIRS = []

# ============================ CNS depressant stacking ============================
# The highest-frequency serious pairing in a set containing five sedatives.
_sed_pairs = [
    ("daridorexant", "diphenhydramine", "major"),
    ("daridorexant", "temazepam", "major"),
    ("daridorexant", "triazolam", "major"),
    ("daridorexant", "melatonin", "moderate"),
    ("daridorexant", "levocetirizine", "moderate"),
    ("diphenhydramine", "temazepam", "major"),
    ("diphenhydramine", "triazolam", "major"),
    ("diphenhydramine", "melatonin", "moderate"),
    ("diphenhydramine", "levocetirizine", "moderate"),
    ("levocetirizine", "temazepam", "moderate"),
    ("levocetirizine", "triazolam", "moderate"),
    ("levocetirizine", "melatonin", "moderate"),
    ("melatonin", "temazepam", "moderate"),
    ("melatonin", "triazolam", "moderate"),
    ("temazepam", "triazolam", "major"),
]
for a, b, sev in _sed_pairs:
    PAIRS.append(P(a, b, "pd-additive-cns-depression", sev,
        "Avoid combining. If both are genuinely needed, the sedative doses are not additive in benefit but are additive in impairment — reduce both, and do not drive or operate machinery the following morning.",
        "Additive sedation, psychomotor impairment and next-day residual effect. The mechanisms differ (GABA-A, H1, orexin, MT1/MT2) so the effect is not detected by any duplication check that reasons from drug class alone."))

# The three that are also duplication, not merely additive.
PAIRS.append(P("temazepam", "triazolam", "therapeutic-duplication", "major",
    "Do not combine. Two benzodiazepine hypnotics for one indication is a dosing error, not a strategy.",
    "Same class, same receptor site, same indication. Also recorded as additive CNS depression above; both entries are intentional, because a duplication check and a sedation check should each catch this."))
PAIRS.append(P("daridorexant", "temazepam", "therapeutic-duplication", "major",
    "Pick one hypnotic. If switching between them, stop one before starting the other rather than overlapping.",
    "Different mechanisms, same indication and same night."))
PAIRS.append(P("daridorexant", "triazolam", "therapeutic-duplication", "major",
    "Pick one hypnotic.",
    "Different mechanisms, same indication and same night."))
PAIRS.append(P("diphenhydramine", "levocetirizine", "therapeutic-duplication", "moderate",
    "Use one antihistamine. Adding diphenhydramine to a daily levocetirizine adds sedation and anticholinergic burden without adding antihistamine effect.",
    "Both are H1 antagonists. Receptor occupancy from levocetirizine at steady state is already near-maximal."))

# ============================ Stimulant stacking ============================
_stim_pairs = [
    ("amphetamine-ir", "caffeine", "moderate"),
    ("amphetamine-xr", "caffeine", "moderate"),
    ("amphetamine-ir", "pseudoephedrine-ir", "major"),
    ("amphetamine-xr", "pseudoephedrine-ir", "major"),
    ("caffeine", "pseudoephedrine-ir", "moderate"),
]
for a, b, sev in _stim_pairs:
    PAIRS.append(P(a, b, "pd-synergism", sev,
        "Additive cardiovascular load. Expect higher heart rate and blood pressure, more anxiety and worse sleep than either alone. Space them, reduce one, or drop the decongestant for a topical alternative.",
        "Additive sympathomimetic effect. Amphetamine and pseudoephedrine share the indirect noradrenaline-releasing mechanism; caffeine adds through adenosine antagonism. None of these is detected by a same-class duplication check."))

PAIRS.append(P("amphetamine-ir", "amphetamine-xr", "therapeutic-duplication", "moderate",
    "Count the total daily amphetamine dose across both records against a single ceiling, not against two. Deliberate layering — XR in the morning with a small IR dose in the afternoon — is a recognised regimen, but the combined total still applies.",
    "Same active drug, different release profile. Retyped from `minor` in the uploaded set: an overlap that doubles exposure is not minor merely because it was intended."))

# ============================ Stimulant vs sedative opposition ============================
for stim in STIMULANTS:
    for sed in ["daridorexant", "temazepam", "triazolam", "melatonin"]:
        if (stim, sed) == ("caffeine", "melatonin"):
            continue  # handled by a dedicated entry below that also carries the CYP1A2 effect
        sev = "moderate" if stim in ("caffeine", "amphetamine-ir", "amphetamine-xr") else "minor"
        PAIRS.append(P(stim, sed, "pd-antagonism", sev,
            "Separate by as many hours as possible. Taking a stimulant late and then a hypnotic to compensate produces a cycle where each dose justifies the next.",
            "Directly opposing effects on arousal. The stimulant does not shorten the hypnotic's duration, so the combination yields impaired sleep quality plus next-day residual sedation rather than cancelling out."))

PAIRS.append(P("amphetamine-ir", "diphenhydramine", "pd-antagonism", "moderate",
    "Expect reduced effect from both.",
    "Opposing effects on arousal and alertness."))
PAIRS.append(P("amphetamine-xr", "diphenhydramine", "pd-antagonism", "moderate",
    "Expect reduced effect from both.",
    "Opposing effects on arousal and alertness. Carried forward from the uploaded record."))

# ============================ Serotonergic ============================
for amp in ["amphetamine-ir", "amphetamine-xr"]:
    PAIRS.append(P(amp, "dextromethorphan", "pd-additive-toxicity", "moderate",
        "Monitor for serotonin syndrome: agitation, tremor, clonus, hyperreflexia, fever, diarrhoea. Onset is usually within hours of a dose change.",
        "Additive serotonergic activity. Amphetamine has some serotonin-releasing effect at higher doses; dextromethorphan is a weak serotonin reuptake inhibitor. Carried forward from the uploaded records."))
    PAIRS.append(P(amp, "sertraline", "pd-additive-toxicity", "major",
        "A recognised combination that is sometimes deliberately prescribed, but it needs a prescriber who knows about both. Do not add one to the other without that, and watch for serotonin syndrome for the first two weeks and after every dose increase.",
        "Additive serotonergic activity, plus additive cardiovascular effect. Sertraline also weakly inhibits CYP2D6, a minor amphetamine route."))

PAIRS.append(P("dextromethorphan", "sertraline", "pd-additive-toxicity", "major",
    "Avoid. If a cough suppressant is needed while on sertraline, use one without dextromethorphan — many combination cold products contain it unlabelled in the front-of-box name, so check the active ingredients panel.",
    "The clearest serotonin syndrome risk in this database, and it is a double hit: sertraline inhibits CYP2D6, which is dextromethorphan's main clearance route, so parent levels rise several-fold at the same time as serotonergic tone rises. Cases are well documented at ordinary OTC doses."))
PAIRS.append(P("dextromethorphan", "sertraline", "pk-metabolism", "major",
    "Treat a normal dextromethorphan dose as though it were several times larger.",
    "CYP2D6 inhibition by sertraline converts an extensive metaboliser into a functional poor metaboliser. Recorded separately from the pharmacodynamic entry because the two need different mitigations: one is solved by dose, the other is not."))
PAIRS.append(P("pseudoephedrine-ir", "sertraline", "pd-additive-toxicity", "moderate",
    "Watch for agitation, raised blood pressure and insomnia, particularly in the first weeks of sertraline.",
    "Weak additive serotonergic and sympathomimetic effect."))

# ============================ NSAID mesh ============================
for i, a in enumerate(NSAIDS):
    for b in NSAIDS[i + 1:]:
        PAIRS.append(P(a, b, "pd-additive-toxicity", "major",
            "Do not combine. Use one NSAID at a time. Acetaminophen is the analgesic that can be safely layered on top of an NSAID; another NSAID is not.",
            "Additive gastrointestinal, renal and cardiovascular toxicity with no additive analgesic benefit — the COX enzyme is already saturated by one agent at therapeutic dose. GI bleeding risk rises multiplicatively."))
        if a != "aspirin":
            PAIRS.append(P(a, b, "therapeutic-duplication", "major",
                "Same mechanism, same indication.",
                "Two COX inhibitors for one job."))

PAIRS.append(P("aspirin", "ibuprofen", "pd-antagonism", "major",
    "If both are truly required, take aspirin at least 30 minutes BEFORE ibuprofen, or at least 8 hours after it. Occasional ibuprofen is a smaller problem than daily ibuprofen; the antagonism needs repeated dosing to matter.",
    "Ibuprofen occupies the COX-1 channel reversibly and blocks aspirin from reaching serine-529, so aspirin cannot acetylate it. The cardioprotective effect of low-dose aspirin is lost while this continues. This is the reason aspirin's irreversible mechanism is recorded as its own term rather than as generic COX inhibition."))
PAIRS.append(P("aspirin", "naproxen", "pd-antagonism", "moderate",
    "Same timing rule as ibuprofen: aspirin first, at least 30 minutes ahead.",
    "The same competitive blockade of platelet COX-1 acetylation, demonstrated for naproxen though less extensively than for ibuprofen."))

for n in NSAIDS:
    PAIRS.append(P(n, "sertraline", "pd-additive-toxicity", "major",
        "Avoid regular combined use. If an NSAID is needed for more than a few days alongside an SSRI, gastroprotection with a PPI is the usual mitigation — esomeprazole and famotidine are both in this database for that reason.",
        "SSRIs deplete platelet serotonin and impair platelet aggregation; NSAIDs damage the mucosa and inhibit platelet COX-1. Combined, upper GI bleeding risk rises several-fold above either alone. One of the most under-recognised pairings in ordinary outpatient use."))
    PAIRS.append(P(n, "propranolol", "pd-antagonism", "moderate" if n != "aspirin" else "minor",
        "Monitor blood pressure if the NSAID is taken regularly. Occasional doses matter little.",
        "NSAIDs inhibit renal prostaglandin synthesis, causing sodium and fluid retention and blunting the antihypertensive effect of beta-blockers. Low-dose aspirin does this much less than full-dose NSAIDs."))

# ============================ CYP3A4 inhibition ============================
PAIRS.append(P("cimetidine", "triazolam", "pk-metabolism", "major",
    "Avoid. Famotidine is in this database precisely as the substitute: same class, same indication, no meaningful CYP inhibition. If cimetidine must continue, triazolam is the wrong hypnotic.",
    "Triazolam is cleared almost entirely by CYP3A4 and has a sub-milligram therapeutic dose, so it has essentially no margin. Cimetidine inhibits CYP3A4. Expect prolonged sedation, next-day impairment and anterograde amnesia."))
PAIRS.append(P("cimetidine", "daridorexant", "pk-metabolism", "major",
    "Avoid, or halve the daridorexant dose to 25 mg and do not exceed it. Famotidine is the straightforward substitute.",
    "89% of daridorexant's metabolic clearance is CYP3A4, so its exposure is close to a direct function of 3A4 activity. Next-morning driving impairment is the dose-related risk the label caps for."))
PAIRS.append(P("cimetidine", "loperamide", "pk-metabolism", "major",
    "Avoid. Do not exceed 8 mg of loperamide daily under any circumstances while on cimetidine.",
    "Loperamide's safety rests on almost none of it reaching the systemic circulation. Cimetidine inhibits CYP3A4 — one of its two clearance routes — raising systemic exposure toward the range where hERG blockade prolongs QT. The FDA boxed warning for loperamide is about exactly this scenario."))
PAIRS.append(P("sertraline", "triazolam", "pk-metabolism", "moderate",
    "Reduce the triazolam dose, or use temazepam instead — it is glucuronidated and untouched by CYP inhibition.",
    "Sertraline is a weak-to-moderate CYP3A4 inhibitor. Against most substrates this is unimportant; against triazolam, which has no margin, it is not."))
PAIRS.append(P("sertraline", "daridorexant", "pk-metabolism", "moderate",
    "Consider 25 mg daridorexant rather than 50 mg, particularly at sertraline doses of 150-200 mg.",
    "Weak CYP3A4 inhibition against a substrate that is 89% dependent on that enzyme."))
PAIRS.append(P("esomeprazole", "triazolam", "pk-metabolism", "minor",
    "No routine action; be aware if sedation seems stronger than expected.",
    "Weak CYP3A4 inhibition. Included for completeness — the clinically important PPI interaction is CYP2C19, which triazolam does not use."))
PAIRS.append(P("daridorexant", "esomeprazole", "pk-metabolism", "minor",
    "No routine action.",
    "Weak CYP3A4 inhibition against a 3A4-dependent substrate. Well below the effect size of cimetidine."))
PAIRS.append(P("daridorexant", "loperamide", "pk-metabolism", "minor",
    "No routine action; both compete for CYP3A4 rather than either inhibiting it.",
    "Substrate competition only."))

# ============================ CYP2D6 inhibition ============================
PAIRS.append(P("cimetidine", "dextromethorphan", "pk-metabolism", "moderate",
    "Expect stronger and longer-lasting effect from a normal dose. Reduce the dextromethorphan dose or space the two.",
    "CYP2D6 inhibition raises parent dextromethorphan and suppresses dextrorphan formation. Carried forward from the uploaded record."))
PAIRS.append(P("cimetidine", "propranolol", "pk-metabolism", "moderate",
    "Monitor heart rate and blood pressure; a dose reduction may be needed.",
    "Cimetidine inhibits both CYP1A2 and CYP2D6, propranolol's two main routes. Because propranolol's first-pass extraction is high, inhibiting it raises exposure disproportionately rather than proportionately — reported increases are around 50%."))
PAIRS.append(P("cimetidine", "diphenhydramine", "pk-metabolism", "moderate",
    "Expect more sedation and anticholinergic effect than usual from a standard dose.",
    "CYP2D6 inhibition raising diphenhydramine exposure."))
PAIRS.append(P("dextromethorphan", "diphenhydramine", "pk-metabolism", "moderate",
    "Common in multi-symptom cold products, where both appear in the same tablet. Check the active ingredients panel rather than the product name.",
    "Diphenhydramine is a CYP2D6 inhibitor as well as a substrate, so it raises dextromethorphan exposure while competing with it."))
PAIRS.append(P("diphenhydramine", "propranolol", "pk-metabolism", "moderate",
    "Monitor for bradycardia and hypotension with regular combined use.",
    "CYP2D6 inhibition by diphenhydramine raising propranolol exposure."))
PAIRS.append(P("propranolol", "sertraline", "pk-metabolism", "major",
    "Monitor heart rate and blood pressure closely, especially in the first weeks and after any sertraline increase. A propranolol dose reduction is often needed. Symptomatic bradycardia and heart block have been reported.",
    "Moderate CYP2D6 inhibition by sertraline against a high-extraction CYP2D6 substrate. The effect scales with sertraline dose — slight at 50 mg, substantial at 200 mg — which means the interaction can appear weeks after both drugs were started."))
PAIRS.append(P("diphenhydramine", "sertraline", "pk-metabolism", "moderate",
    "Expect more sedation than usual. Relevant if diphenhydramine is being used nightly for sleep.",
    "Mutual CYP2D6 inhibition plus additive CNS effect."))
PAIRS.append(P("dextromethorphan", "propranolol", "pk-metabolism", "minor",
    "No routine action.",
    "Competition for CYP2D6 rather than inhibition."))

# ============================ CYP1A2 ============================
PAIRS.append(P("caffeine", "cimetidine", "pk-metabolism", "moderate",
    "Expect a normal amount of caffeine to feel stronger and last considerably longer. Cut the dose, especially in the afternoon.",
    "CYP1A2 inhibition. Caffeine half-life rises by roughly 50-70%, so an evening cut-off that normally works stops working."))
PAIRS.append(P("cimetidine", "melatonin", "pk-metabolism", "moderate",
    "Expect a stronger and longer melatonin effect, including morning grogginess. A lower melatonin dose is the fix.",
    "CYP1A2 inhibition against a substrate whose first-pass metabolism is both dominant and variable."))
PAIRS.append(P("caffeine", "melatonin", "pd-antagonism", "moderate",
    "Separate by as many hours as possible; caffeine's half-life of 3-7 hours means an afternoon dose is still present at bedtime.",
    "Two interactions at once: direct opposition of adenosine-mediated sleep pressure, and competition for CYP1A2 that raises melatonin exposure. The pharmacodynamic effect dominates."))

# ============================ Gastric pH and absorption ============================
PAIRS.append(P("amphetamine-xr", "esomeprazole", "pk-absorption", "moderate",
    "Watch for an earlier, sharper onset and a shorter tail than usual. Adjusting timing works better than adjusting dose.",
    "Raised gastric pH accelerates release from the delayed-release bead fraction. The Adderall XR label documents a shortened time to peak with omeprazole. The IR form does not have this problem, because it has no pH-dependent coating."))
PAIRS.append(P("amphetamine-ir", "cimetidine", "pk-absorption", "moderate",
    "Monitor for stronger stimulant effect. Carried forward from the uploaded record.",
    "Raised gastric pH increases absorption of amphetamine, a weak base. Cimetidine's urinary alkalinising tendency additionally reduces renal excretion — the larger of the two effects."))
PAIRS.append(P("amphetamine-xr", "cimetidine", "pk-absorption", "moderate",
    "Monitor for stronger stimulant effect. Carried forward from the uploaded record.",
    "Raised gastric pH plus reduced renal clearance, as for the IR form."))
PAIRS.append(P("amphetamine-ir", "famotidine", "pk-absorption", "minor",
    "No routine action.",
    "Raised gastric pH, but without cimetidine's additional enzyme and renal effects. A deliberate contrast case."))
PAIRS.append(P("amphetamine-xr", "famotidine", "pk-absorption", "minor",
    "No routine action.",
    "Raised gastric pH affecting bead release, smaller in magnitude than with a PPI."))

# Acid suppressant duplication
PAIRS.append(P("cimetidine", "esomeprazole", "therapeutic-duplication", "moderate",
    "Use one. A PPI and an H2 blocker together is occasionally deliberate — an H2 blocker at night alongside a morning PPI for nocturnal breakthrough — but routine overlap adds no benefit.",
    "Both suppress gastric acid, by different mechanisms and to different degrees."))
PAIRS.append(P("cimetidine", "famotidine", "therapeutic-duplication", "moderate",
    "Use one. These are the same drug class.",
    "Two H2 antagonists."))
PAIRS.append(P("esomeprazole", "famotidine", "therapeutic-duplication", "moderate",
    "Use one, with the same nocturnal-breakthrough caveat as above.",
    "Overlapping acid suppression."))

# ============================ Colestipol binding ============================
PAIRS.append(P("colestipol", "propranolol", "pk-absorption", "major",
    "Take propranolol at least 1 hour before or 4 hours after colestipol, and keep the interval constant day to day.",
    "Specifically documented on the colestipol label: repeated colestipol doses before a propranolol dose reduced propranolol absorption. The reverse risk matters too — stopping colestipol without adjusting propranolol raises propranolol exposure."))
for d, sev in [("acetaminophen", "moderate"), ("aspirin", "moderate"),
               ("diclofenac-tablets", "moderate"), ("ibuprofen", "moderate"),
               ("naproxen", "moderate"), ("loperamide", "moderate"),
               ("levocetirizine", "moderate"), ("sertraline", "moderate"),
               ("famotidine", "moderate"), ("esomeprazole", "moderate")]:
    PAIRS.append(P("colestipol", d, "pk-absorption", sev,
        "Separate the doses: at least 1 hour before, or 4 hours after, colestipol.",
        "An anion-exchange resin binds anionic and other drugs non-selectively in the gut lumen, delaying or reducing absorption. Acidic drugs such as the NSAIDs bind particularly well. Solved entirely by spacing, since nothing is absorbed systemically."))

# ============================ Transporter and miscellaneous ============================
PAIRS.append(P("loperamide", "sertraline", "pk-transporter", "moderate",
    "Keep loperamide at or below 8 mg daily. Do not exceed the label dose while on sertraline.",
    "Sertraline weakly inhibits P-glycoprotein, the efflux pump that keeps loperamide out of the CNS, and weakly inhibits CYP3A4, one of its clearance routes. Neither is dramatic alone; both point the same direction."))
PAIRS.append(P("diphenhydramine", "loperamide", "pd-additive-toxicity", "moderate",
    "Watch for severe constipation. Avoid the combination in anyone with a history of ileus or bowel obstruction.",
    "Additive slowing of gut motility — anticholinergic plus opioid antimotility. Both also prolong QT at raised systemic exposure, so the pairing has a second, rarer mechanism of harm."))
PAIRS.append(P("cimetidine", "sertraline", "pk-metabolism", "moderate",
    "Monitor for increased sertraline side effects; a dose reduction may be appropriate.",
    "Cimetidine inhibits several of sertraline's clearance routes. Reported sertraline AUC increases are around 50%, which also amplifies sertraline's own inhibitory effects on CYP2D6 — so this interaction propagates into every other sertraline pair in this database."))
PAIRS.append(P("cimetidine", "diclofenac-tablets", "pd-additive-toxicity", "minor",
    "Monitor for GI symptoms. Carried forward from the uploaded record.",
    "Retyped in 1.5. The uploaded entry was `pk-absorption` but its own suggested action described GI toxicity, which is a pharmacodynamic concern. Cimetidine is also mildly gastroprotective, so the net direction here is genuinely uncertain."))
PAIRS.append(P("amphetamine-ir", "propranolol", "pd-antagonism", "moderate",
    "Monitor blood pressure. Watch for bradycardia with hypertension, which is the signature of unopposed alpha stimulation.",
    "Non-selective beta blockade removes the beta-2 vasodilatory counterweight while amphetamine drives alpha-mediated vasoconstriction. A cardioselective beta-blocker does not have this problem."))
PAIRS.append(P("amphetamine-xr", "propranolol", "pd-antagonism", "moderate",
    "As for the IR form, with a longer window of overlap each day.",
    "Unopposed alpha stimulation, sustained across the XR duration."))
PAIRS.append(P("propranolol", "pseudoephedrine-ir", "pd-antagonism", "major",
    "Avoid. Use a nasal steroid or saline rather than an oral decongestant while on propranolol. If a decongestant is unavoidable, a topical one has far less systemic effect.",
    "The textbook unopposed-alpha interaction: pseudoephedrine drives alpha-1 vasoconstriction while propranolol blocks the beta-2 vasodilation that would normally offset it. Hypertensive episodes with reflex bradycardia are documented, including in people whose blood pressure is otherwise well controlled."))
PAIRS.append(P("caffeine", "propranolol", "pd-antagonism", "minor",
    "No routine action.",
    "Caffeine modestly blunts the antihypertensive effect; propranolol modestly slows caffeine clearance through CYP1A2. Both effects are small and partly offsetting."))
PAIRS.append(P("aspirin", "cimetidine", "pd-antagonism", "minor",
    "No action needed; the direction of this one is protective.",
    "Recorded so the pair is not left looking unexamined. Acid suppression reduces aspirin-related mucosal injury."))

# ============================ Notable negatives ============================
# Screened, clean, and worth saying so — each of these is a substitution someone
# might actually make, or a trap someone might expect and not find.
NEGATIVES = [
    ("cimetidine", "temazepam",
     "Screened and clean, and this is the single most useful negative in the database. Temazepam is cleared by direct glucuronidation with no CYP step, so cimetidine's enzyme inhibition does not touch it. Where cimetidine plus triazolam is a major interaction, cimetidine plus temazepam is not one at all. Note that the additive-sedation concern is a separate matter and is recorded on its own."),
    ("famotidine", "triazolam",
     "Clean. The deliberate contrast to cimetidine plus triazolam: famotidine does not meaningfully inhibit CYP3A4, so it is the H2 blocker to use when a 3A4 substrate is on board."),
    ("famotidine", "daridorexant",
     "Clean, for the same reason as triazolam. Substituting famotidine for cimetidine resolves the major daridorexant interaction outright."),
    ("dextromethorphan", "famotidine",
     "Clean. Famotidine does not inhibit CYP2D6."),
    ("famotidine", "propranolol",
     "Clean. No CYP1A2 or CYP2D6 inhibition."),
    ("famotidine", "melatonin",
     "Clean. No CYP1A2 inhibition."),
    ("famotidine", "loperamide",
     "Clean. No CYP3A4 or P-gp inhibition, so none of the cimetidine cardiac concern applies."),
    ("famotidine", "sertraline",
     "Clean."),
    ("caffeine", "famotidine",
     "Clean."),
    ("levocetirizine", "cimetidine",
     "Clean. Levocetirizine is over 85% renally excreted unchanged and barely metabolised, so CYP inhibitors do not reach it."),
    ("levocetirizine", "sertraline",
     "Clean on pharmacokinetic grounds, for the same reason. Additive sedation is recorded separately."),
    ("levocetirizine", "esomeprazole",
     "Clean."),
    ("acetaminophen", "ibuprofen",
     "Clean, and worth stating positively: acetaminophen is the analgesic that can be layered on top of an NSAID, because the mechanisms and the toxicities do not overlap. Alternating the two is a recognised strategy."),
    ("acetaminophen", "naproxen", "Clean, as for ibuprofen."),
    ("acetaminophen", "diclofenac-tablets", "Clean, as for ibuprofen."),
    ("acetaminophen", "aspirin", "Clean. No additive hepatic or GI mechanism at therapeutic doses."),
    ("acetaminophen", "sertraline",
     "Clean. Notable because sertraline plus any NSAID is a major bleeding interaction and acetaminophen is not an NSAID — this is the substitution that resolves it."),
    ("esomeprazole", "ibuprofen",
     "Clean, and protective rather than harmful: a PPI is the standard mitigation for NSAID mucosal injury."),
    ("esomeprazole", "naproxen", "Clean and protective, as for ibuprofen."),
    ("esomeprazole", "diclofenac-tablets", "Clean and protective, as for ibuprofen."),
    ("famotidine", "ibuprofen", "Clean; partly protective, though less effective than a PPI."),
    ("temazepam", "esomeprazole",
     "Clean. Temazepam's glucuronidation route is untouched by CYP2C19 inhibition — the same property that protects it from cimetidine."),
    ("temazepam", "sertraline",
     "Clean pharmacokinetically: no CYP route to inhibit. Additive sedation is recorded separately."),
    ("melatonin", "sertraline",
     "Clean or near-clean. The dramatic melatonin interaction is with fluvoxamine, a strong CYP1A2 inhibitor; sertraline is not one."),
    ("caffeine", "sertraline", "Clean. Sertraline does not meaningfully inhibit CYP1A2."),
    ("colestipol", "simethicone",
     "Clean. Neither is absorbed; there is nothing for either to affect."),
    ("loperamide", "esomeprazole",
     "Clean. CYP2C19 is not a loperamide route."),
    ("aspirin", "esomeprazole",
     "Clean and protective — the standard pairing for aspirin-related GI risk."),
    ("acetaminophen", "amphetamine-ir", "Clean."),
    ("acetaminophen", "cimetidine",
     "Clean at therapeutic doses. Cimetidine's CYP inhibition includes weak CYP2E1 effects, which would if anything be mildly protective against NAPQI formation, but this is not a basis for any clinical action."),
]
