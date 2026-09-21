# Drug interaction dataset — schema 1.5.0

24 drug records, 11 active-metabolite records, 13 controlled vocabularies,
116 interaction findings and 171 explicit "screened, clean" entries covering
all 276 drug pairs.

```
drug-interaction-atlas.pdf   9-page visual atlas
figures/*.pdf                the same pages as individual files
index.json                   flat listing of every record
interaction-matrix.json      all 116 findings in one queryable file
drugs/*.json                 one record per drug (24)
metabolites/*.json           one record per active metabolite (11)
vocab/*.json                 controlled vocabularies (13)
src/                         generator, validator, visualiser
```

Everything outside `src/` is generated. Edit the Python modules in `src/`,
then run `bash src/rebuild.sh` (build, validate, visualise in order).

## The atlas

| Page | What it shows |
|---|---|
| Interaction matrix | All 276 pairs at once. Colour is the highest severity found; a number marks pairs with more than one distinct finding. Pale cells were screened and found clean — a recorded result, not an untested gap. Simethicone's row is entirely pale, which is the point of it. |
| Major interactions | All 36 major findings grouped by mechanism, with the reasoning for each. Two pages. |
| Metabolic routes | Drugs against enzymes, marked S (substrate), I (inhibitor) or S/I. Every pharmacokinetic interaction in the dataset is an I in one row meeting an S in the same column, so the grid makes them derivable rather than memorised. The two contrast pairs read straight off it. |
| Active metabolites | Parent to metabolite, with the forming pathway and fraction of dose, plus why each one earned a record of its own. |
| Pharmacokinetics | Half-life against duration of action and time to peak, log scale. Aspirin and esomeprazole are the two cases where the kinetics do not predict the duration at all. |
| Interaction hubs | The sedative cluster and the sertraline cluster drawn as graphs, which is where the density actually is. |

Sources: Merck Manual Professional, AHFS DI via Drugs.com, DailyMed labelling,
StatPearls, DrugBank. Every record carries its source list; nothing is cited
as "drive".

---

## What changed from 1.4

**Conventions that had drifted, now settled.**

*Enzyme naming.* `metabolism-pathways.json` said to put the enzyme in the
`enzyme` field and keep it out of the term, and acetaminophen followed that
(`cyp450-oxidation` + `enzyme: CYP2E1`) while every other record did the
opposite (`cyp2d6` as the term). Both forms existed in the vocabulary, so both
were legal and neither was queryable. Settled on the **specific-isoform term**,
with `enzyme` populated alongside for display. `cyp450-oxidation` is retained
and marked deprecated so 1.0 records still resolve. Acetaminophen migrated to
`cyp2e1`.

*Enzyme effects.* `effect.type` now carries `substrate`, `inhibitor`, `inducer`
or `substrate-and-inhibitor`, against the new `enzyme-effects` vocabulary. This
is what makes cimetidine and sertraline's interaction profiles derivable from
their records instead of hand-listed.

*Schema version.* All records on 1.5.0. Acetaminophen's stale `knownAbsence`
about time-to-peak is resolved — 1.4 added `timeToPeak`, so the value has a
home.

*Units.* Half-life in hours everywhere. Acetaminophen was in minutes.

**New vocabularies:** `transporters` (P-gp — not metabolism, and previously
unrecordable), `enzyme-effects`, `severity`, `evidence-levels`, `label-status`,
`metabolite-activity`. The last four were enum-valued fields with no vocabulary,
so nothing could check them.

**New terms:** `antidote` on interaction-types — the NAPQI record noted that
N-acetylcysteine had nowhere to go, and now it does. `pk-transporter`.
`pd-additive-cns-depression`, split out from `pd-synergism` because sedative
stacking is the most common serious pairing here and deserves its own query.
`non-medical` and `supplement` on label-status.

**Reciprocity.** Interactions are still written one-directionally, on whichever
drug comes later in `index.json`'s `canonicalOrder`. But they are now generated
from one pair table (`src/pairs.py`), so a pair cannot be recorded on one
record and missing from the other. `interaction-matrix.json` gives the
undirected view.

---

## Corrections to the uploaded records

| Record | Was | Now |
|---|---|---|
| `amphetamine-ir` | dose steps in `ug`, ceiling in `mg` | mg; thousandfold error |
| `ampheramine-xr` | misspelled id, referenced by 4 records | `amphetamine-xr`, old id in `supersedes` |
| `cimetidine` | `peakConcentration: 45–90 min` | `timeToPeak` |
| `cimetidine` | active metabolite `"s"`, activity `toxic` | stray keystroke; removed |
| `cimetidine` | referenced `cyp2d6` with no `metabolismPathways` | full pathway list |
| `diclofenac-tablets` | `cox-inhibition-central` | `cox-inhibition-peripheral` primary |
| `diclofenac-tablets` | `maxDurationDays: 200` | 10 |
| `diphenhydramine` | Vd 17 L/kg | 3–4 L/kg |
| `diphenhydramine` | `maxDurationDays: 1` | 14 (sleep), none (allergy) |
| `napqi` | absence filed under `field: codes`, prose about PK | `field: pharmacokinetics` |
| `napqi` | `route: oral`, `immediate-release` | removed |
| `acetaminophen` | AM404 `formedByPathway: hydrolysis`, pathway undeclared | declared |
| `acetaminophen` | `cannabinoid-am404` mechanism on the parent | moved to `am404` |
| `acetaminophen` | warfarin typed `pd-additive-toxicity` | out of scope here |
| all | sources titled "google", "drive" | real citations |

**`labelStatus` on the DXM recreational entry.** `off-label` means an
unapproved *medical* use. Typing non-medical use that way promotes it into
anything filtering for clinical indications — and that entry was the only
regimen in the whole set with neither a `maxDailyDose` nor a `dosingInterval`,
so nothing bounded it. 1.5 adds a distinct `non-medical` term for the
distinction. No non-medical regimen is carried forward; the clinically useful
content of that record, its interaction set, is retained in full.

---

## Validator

`src/validate.py` is built around the bugs that were actually present, on the
view that a validator earns its keep by catching real mistakes rather than easy
ones. Run against the original uploads it reports 12 errors and 4 warnings,
including:

- **Unit coherence, not just unit legality.** `ug` is a legal member of a closed
  units vocabulary, so nothing caught a 40 ug dose against a 40 mg ceiling. The
  check compares magnitudes after normalising.
- **Unreachable ceilings.** A `maxDailyDose` the stated interval cannot reach
  means the interval, the dose steps or the ceiling is wrong. This found seven
  errors in my own records, all of which were real.
- **Unbounded as-needed regimens** — no ceiling *and* no interval.
- **Field semantics** — a time value in `peakConcentration`.
- **Dangling references** — a metabolite formed by a pathway its parent does not
  declare; a `parentDrugIds` link the parent does not list back.
- **Pair coverage** — every pair must be a finding or an explicit screening entry.
- **Placeholder sources.**

---

## Reading the data

`interactionScreening` entries carry a `result`:

- `no-interaction-found` — checked, nothing there. Roughly 30 of these carry a
  `note` explaining *why* the pair is clean, because several are clinically
  useful negatives. Cimetidine + temazepam is the best example: temazepam is
  glucuronidated with no CYP step, so cimetidine's enzyme inhibition cannot
  touch it, while cimetidine + triazolam is a major interaction. That negative
  *is* the substitution.
- `covered-by-class-rule` — colestipol only. Its label rule is general (any oral
  drug 1 h before or 4 h after), so individually enumerating 23 pairs would
  imply precision that isn't there.

Deliberate contrast pairs built into the set: **cimetidine vs famotidine** (same
class, same indication, one is a pan-CYP inhibitor and the other inhibits
nothing) and **triazolam vs temazepam** (same class, same indication, pure
CYP3A4 vs pure glucuronidation). Where one is flagged and its twin is screened
clean, that is a real substitution rather than a data gap. **Simethicone** is
the inert control: clean against all 23, which is a finding and not an omission.

---

## Known limits

- `codes` holds ATC only. RxNorm and UNII identifiers are not populated —
  fabricating them would have been worse than leaving them out.
- Sources are cited at record level, not per-field. The uploaded acetaminophen
  and napqi records had per-entry `sourceIds`; that granularity is not
  reproduced across 35 records here.
- No pharmacogenomic dimension beyond the one `cyp2d6-poor-metabolizer` PK
  population on dextromethorphan.
- Propranolol's rebound-on-discontinuation hazard has nowhere to live. The
  schema models drug-drug pairs, not stopping risks. A `discontinuationRisks`
  field would fix it.
- Renal and hepatic dose adjustment appears as separate `dosageRegimens` where
  the label gives one, which is inconsistent — some records have it, some don't.
- **This is reference data assembled from tertiary sources. It is not a
  clinical decision tool and has not been reviewed by a pharmacist.**
