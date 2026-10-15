# AGENTS.md — In-Lab Antigravity (`agy`) Coding Rules for AeroGlobal FlightOps

> **DROP THIS FILE INTO THE QWIKLABS WORKSPACE ROOT.**
> Every coding agent (`agy`, Claude, Gemini) operating in this workspace MUST follow these 6 non-negotiable rules.

## 1. Source of Truth: Lab Instructions Win
- Always use the **exact** resource names, dataset/table names, file paths, function names, model IDs, and IAM roles specified in the live Qwiklabs lab instructions.
- Only use default names from `lab_blueprint/` when the lab instructions do not specify a name.

## 2. Trap #1 Fix — Location Split (`global` Inference vs. Regional Deployment)
- **Never** set `GOOGLE_CLOUD_LOCATION="us-central1"` for Gemini model calls when using preview or Provisioned-Throughput-backed models (e.g., `gemini-3.6-flash` or `gemini-2.5-flash`), as regional endpoints throw `404 NOT_FOUND ... Publisher model`.
- Always set in `.env` and container environment variables:
  - `GOOGLE_GENAI_USE_VERTEXAI="True"`
  - `GOOGLE_CLOUD_LOCATION="global"` (for Gemini inference)
  - `DEPLOY_REGION="us-central1"` (or the lab's assigned region for BigQuery, Cloud Run, Model Armor, and Agent Runtime deployments)

## 3. Trap #2 Fix — ADK Agent Naming & Single-Parent Rule
- Every ADK agent's `name` parameter (`Agent(name=...)`, `LlmAgent(name=...)`, `SequentialAgent(name=...)`, `ParallelAgent(name=...)`, `LoopAgent(name=...)`) **MUST** be a valid Python identifier using **`snake_case` (underscores only, NEVER hyphens)**.
  - Correct: `name="flight_ops_coordinator"`, `name="ops_data_agent"`, `name="policy_rag_agent"`
  - Wrong: `name="flight-ops-coordinator"` (raises validation error and breaks multi-agent routing checks)
- **Never attach the same sub-agent object instance to more than one parent agent** (raises `ValueError: Agent already has a parent`). Always instantiate fresh sub-agents via factory functions if a sub-agent is used in multiple workflows.
- Every sub-agent must have a clear, specific `description` so the parent coordinator routes to it accurately (`>= 90%` routing precision).

## 4. Trap #3 Fix — Managed Agent Identity & Zero Hardcoded Keys
- **Never** hardcode API keys or service-account JSON key files (`NFR-17a`).
- Use Application Default Credentials (ADC), Managed Agent Identity (`agentidentity.googleapis.com`), and SPIFFE principals (`principal://...`).
- Ensure service accounts have explicit least-privilege IAM roles (`roles/aiplatform.user`, `roles/bigquery.dataViewer`, `roles/bigquery.jobUser`, `roles/discoveryengine.viewer`, `roles/modelarmor.user`, `roles/dlp.user`, `roles/run.invoker`).
- All SQL queries against BigQuery must be **read-only**, **date-bounded (`WHERE scheduled_departure = ...`)**, and **project explicit columns (NEVER `SELECT *`)**.

## 5. Domain & Golden-Case Invariants (`100%` Required on `NFR-15`)
1. **EU261 / UK261 (`AG-102` LHR->JFK, 5,541 km, 318 min arrival delay, APU fault):**
   - Technical defects (APU fault) and crew shortages are **always carrier-controllable (`is_carrier_controllable = True`)**, never extraordinary circumstances (*CJEU Wallentin-Hermann*), even if a minor weather delay (`30 min snow squall`) occurred.
   - Distance brackets: `<= 1,500 km` -> `EUR 250`; `1,501–3,500 km` -> `EUR 400`; `> 3,500 km` with `>= 4h (240 min)` arrival delay -> `EUR 600` (or `GBP 520` under UK261).
   - **Right to Care (`FR-32`):** Meals, contracted hotel lodging, and airport transfers are **unconditional** even during extraordinary weather delays.
2. **Montreal Convention & US DOT Part 260 (`AG-503` LAX->HND, 38h bag delay, `$2,850` claim, `$75` bag fee, Executive Platinum):**
   - International itinerary (`LAX->HND`) -> **Montreal Convention** applies (precedence over domestic DOT cap), capping baggage liability at **`1,288 SDR` (`~$1,710 USD`)** instead of the `$3,800` US domestic cap (`CoC v2024.4`; never quote the outdated `2022` `$3,500` figure).
   - Baggage delayed `> 12h` domestic or `> 15–30h` international -> automatic refund of the **`$75` ancillary baggage fee** under US DOT 14 CFR Part 260.
   - Claim `$2,850 > $2,500` (or Executive Platinum churn risk / medical emergency / high `fraud_dispute_risk_score`) -> **deterministic escalation to human review (`escalate = True`)**.
3. **FAA Part 117 Crew Duty & Contracted Hotel Caps (`AG-884` ORD->DFW, 20 min remaining FDP):**
   - Alert NOC dispatch whenever `remaining_fdp_minutes < 30`.
   - Contracted hotel nightly caps: **ORD = `$140/night`**, **DFW = `$120/night`**, **LHR = `EUR 150/night`**.
   - Meal stipends: **Executive Platinum = `$65/day`**, **General / other tiers = `$40/day`**.
4. **PII / PCI Redaction (`INC-883199`):**
   - Mask 16-digit PANs (`XXXX-XXXX-XXXX-1234`), strip CVVs completely, and redact/tokenise passport numbers, full names, and PNRs in prompts, responses, and logs.

## 6. Trap #4 Fix — STOP Before Subtask 25 (Gateway / Security Teardown)
- **HARD STOP GATE:** Complete Tasks/Checks **1 through 24** first and pause for the user to click *"Check my progress"* on Checks 1–24 in the Qwiklabs UI.
- **NEVER execute Task/Check 25 (Gateway or permission teardown) until the user explicitly confirms that Checks 1–24 have scored green.**
