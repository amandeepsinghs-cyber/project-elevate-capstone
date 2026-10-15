# ELEVATE Context Constitution — AeroGlobal FlightOps Agent

> **v2.0 · 2026-10-14.** These are the working rules for every document in this engagement. Engagement facts and deliverables are in `AEROGLOBAL_FLIGHTOPS_CONTEXT_v2.md`. If a request conflicts with these rules, flag it before proceeding.

## 1. Source hierarchy
1. **Customer facts** come only from the 11 files in `discovery_package/` (verified originals). `context1.md` is a portal brief, not a customer artifact.
2. **Engagement rules** come from `AEROGLOBAL_FLIGHTOPS_CONTEXT_v2.md`, the portal briefs and the two official templates.
3. **Deliverables** in `deliverables/` must trace every fact to level 1.

Contradictions between artifacts are never resolved silently. Each is logged with both quotes and a recommended default.

## 2. Templates are strict
Use the exact section numbers, titles, order and table columns of the official templates. Never add, remove or rename sections. Extra material goes only in the template's own appendix (Discovery §15.2). The SDD has no appendix, so nothing is added to it.

## 3. Integrity
- **Facts** are cited. **Assumptions** go in the Assumptions Register with a validation action. **Recommendations** are labelled "Recommended".
- No invented numbers. Customer sizing figures are labelled *unvalidated* (A04b says they "have not been validated").
- Quotes are verbatim (they may be trimmed with "…").
- The Discovery Document separates **customer facts** from **engineering hypotheses**. Google Cloud product names may appear **only** in clearly labelled *"Recommended (CE hypothesis, validated in SDD)"* content: §15.2, design-impact cells and engineered acceptance criteria. They are never presented as customer requirements. *(Amended 2026-10-14 after the RAISE attempt-1 scorecard penalised the absence of service, model and store mapping.)*
- Any number we propose (not stated by the customer) needs an Assumptions-register entry.

## 4. Artifact IDs & citation format
| ID | File | Locator |
|---|---|---|
| A00 | `00_Customer_Narrative_Brief.md` | `§section` |
| A01 | `01_Artifact1_Executive_Operational_Call_Transcript.md` | `@hh:mm:ss` |
| A02 | `02_Artifact2_Technical_Security_Architecture_Review.md` | `@hh:mm:ss` |
| I-914 | `03_INC-882914_ord_part117_crew_timeout.yaml` | YAML key |
| I-042 | `03_INC-883042_lhr_jfk_eu261_apu_violation.yaml` | YAML key |
| I-199 | `03_INC-883199_infosec_dlp_pii_pan_leak.yaml` | YAML key |
| I-250 | `03_INC-883250_lax_hnd_montreal_baggage_dispute.yaml` | YAML key |
| A04 | `04_Artifact4_Functional_Whiteboard.jpg` | block label |
| A04b | `04b_Artifact4_Companion_Sizing_Sheet.md` | table row |
| A05 | `05_Artifact5_Serving_Architecture_Performance_Call.md` | `@hh:mm:ss` |
| A06 | `06_Artifact6_AgentOps_Observability_Call.md` | `@hh:mm:ss` |

## 5. Requirement IDs & quality bar
- IDs: `FR-` functional, `NFR-` non-functional, `CON-` constraint, `DATA-` data/integration, `STK-` stakeholder, `TEN-` tension, `CFL-` conflict, `Q-` question, `ASM-` assumption, `RSK-` risk, `DS-` data source, `ADR-` decision, `GC-` golden test case. IDs are never reused.
- Each requirement is **one testable "shall" statement** with measurable acceptance criteria, ≥ 1 cited source, a priority and a justification.

## 6. Prioritization: MoSCoW from an Evidence-Weighted Score (EWS)
EWS = **3R + 2I + 1V + 2S + 1D** (each factor 0–3, max 27):
R regulatory exposure · I incident/financial impact · V volume/blast radius · S stakeholder mandate (3 = veto holder) · D dependency enabler.

| MoSCoW | Rule |
|---|---|
| Must | EWS ≥ 18, **or** a hard gate (statutory obligation R ≥ 2 with a cited regulation, or an explicit veto-holder condition S = 3) |
| Should | 12–17 |
| Could | 6–11 |
| Won't (now) | < 6 or explicitly out of scope |

**Phase 1 cut line:** read-only, internal-staff MVP = all Musts + read-only Shoulds + anything they depend on. Write actions and consumer channels go to Phase 2.

## 7. Formatting
- Table cells ≤ 25 words; Mermaid only for diagrams; single `.md` per submission; Pyramid style (answer first).
- SDD components are tagged **[Built in lab]** or **[Production only]** inline.

## 8. Task 3 lab rules
One phase at a time from `deliverables/03_Lab_Runbook.md`; log each in `RUNLOG.md`; lab names override the SDD; gateway teardown only after checks 1–24 have scored; **never End Lab before the passing score shows**.

## 9. Confidentiality & change control
The repo is private. Scenario materials and solution code are never shared. No git commit or push without explicit user approval.
