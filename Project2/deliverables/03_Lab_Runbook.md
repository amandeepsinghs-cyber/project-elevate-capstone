# Task 3: AeroGlobal FlightOps Agent — Qwiklabs End-to-End Build Runbook

> **CRITICAL LAB RULES (READ BEFORE RUNNING ANY COMMAND):**
> 1. **Only the first lab attempt counts (`G1`).** Never click **"End Lab"** until your passing score (`>= 20 / 25` checks) is visible on the Qwiklabs ribbon.
> 2. **Lab Names Override SDD Names (`§5`).** Whenever the Qwiklabs instructions specify exact dataset names, table names, model IDs, agent names, or regions, **always use the lab's exact strings**.
> 3. **Trap #1 — Location Split (`404 NOT_FOUND` on Gemini):** Always set `GOOGLE_CLOUD_LOCATION="global"` and `GOOGLE_GENAI_USE_VERTEXAI="True"` for Gemini model inference, while keeping `DEPLOY_REGION` (`us-central1` or the lab's assigned region) for BigQuery, Cloud Run, and Agent Runtime deployments.
> 4. **Trap #2 — ADK Agent Naming (`ValueError`):** Every `Agent(name=...)` **must** be a valid Python identifier using **`snake_case` (underscores only, NEVER hyphens)**, and **never attach the same sub-agent instance to more than one parent agent** (use a factory function if needed).
> 5. **Trap #3 — Managed Agent Identity & OAuth IAM Gates (`401`/`403`):** Never hardcode API keys or service-account JSON keys. Use Managed Agent Identity (`agentidentity.googleapis.com` / SPIFFE `principal://...`) and grant the exact IAM roles (`roles/run.invoker`, `roles/bigquery.dataViewer`, `roles/bigquery.jobUser`, `roles/discoveryengine.viewer`, `roles/modelarmor.user`).
> 6. **Trap #4 — Subtask 25 Gateway/Security Teardown LAST (`G3`):** **DO NOT** run the final gateway/permission teardown step (Subtask 25) until Checks 1 through 24 have scored green on your Qwiklabs dashboard.

---

## Phase 0: Lab Startup, Repo Clone & Environment Variables

| Field | Content |
|---|---|
| **Goal** | Boot the lab VM, initialize `agy`, clone this private repo, and export split regional vs. global environment variables. |
| **Commands** | ```bash
# 1. Wait 2-4 minutes after lab start. If agy closes after 2s:
# sudo pkill -9 antigravity

# 2. Clone private repo into ~/project-elevate-agents (using Fine-Grained PAT)
git clone https://<YOUR_PAT>@github.com/<YOUR_GITHUB_USER>/project-elevate-agents.git ~/project-elevate-agents

# 3. Copy AGENTS.md into the active lab workspace so in-lab agy obeys all 4 trap rules
cp ~/project-elevate-agents/Project2/lab_blueprint/AGENTS.md ./AGENTS.md

# 4. Set split environment variables (TRAP #1 FIX)
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
export DEPLOY_REGION="us-central1"           # Override if lab specifies europe-west1 / etc.
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"        # MANDATORY for Gemini 3.x / PT inference
export GOOGLE_GENAI_USE_VERTEXAI="True"
export MODEL_ID="gemini-2.5-flash"           # Override with lab's exact model string (e.g. gemini-3.6-flash)
``` |
| **Verify** | `echo "Project=$PROJECT_ID (#$PROJECT_NUMBER) | Deploy=$DEPLOY_REGION | Inference=$GOOGLE_CLOUD_LOCATION | Vertex=$GOOGLE_GENAI_USE_VERTEXAI"` |
| **Expected Result** | Non-empty `PROJECT_ID` and `PROJECT_NUMBER`, `Deploy=us-central1`, `Inference=global`, `Vertex=True`. |
| **If It Fails** | Run `gcloud auth list` and `gcloud config set project <LAB_PROJECT_ID>` using the Qwiklabs student credentials. |

---

## Phase 1: Enable Required Google Cloud APIs

| Field | Content |
|---|---|
| **Goal** | Enable Vertex AI, BigQuery, Discovery Engine (Vertex AI Search), Model Armor, DLP/SDP, Cloud Run, Agent Registry, and Agent Identity APIs. |
| **Commands** | ```bash
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  discoveryengine.googleapis.com \
  modelarmor.googleapis.com \
  dlp.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudtasks.googleapis.com \
  pubsub.googleapis.com \
  logging.googleapis.com \
  cloudtrace.googleapis.com \
  agentregistry.googleapis.com \
  agentidentity.googleapis.com \
  --project="$PROJECT_ID"
``` |
| **Verify** | `gcloud services list --enabled --project="$PROJECT_ID" | grep -E "aiplatform|bigquery|discoveryengine|modelarmor|dlp|run"` |
| **Expected Result** | All core APIs listed as enabled. |
| **If It Fails** | If a preview API name (e.g. `agentregistry` or `agentidentity`) is not needed or differently named in the lab, enable the exact list in the lab instructions. |

---

## Phase 2: IAM Service Accounts & Managed Agent Identity (Trap #3 Fix)

| Field | Content |
|---|---|
| **Goal** | Configure least-privilege service accounts and SPIFFE/Agent Identity bindings without any hardcoded keys. |
| **Commands** | ```bash
export AGENT_SA_NAME="sa-flightops-agent"    # Use lab's exact SA name if specified
export AGENT_SA="${AGENT_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create "$AGENT_SA_NAME" \
  --display-name="AeroGlobal FlightOps Agent SA" \
  --project="$PROJECT_ID" || true

for ROLE in \
  roles/aiplatform.user \
  roles/bigquery.dataViewer \
  roles/bigquery.jobUser \
  roles/discoveryengine.viewer \
  roles/modelarmor.user \
  roles/dlp.user \
  roles/run.invoker \
  roles/logging.logWriter \
  roles/cloudtrace.agent; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${AGENT_SA}" \
    --role="$ROLE" \
    --quiet
done
``` |
| **Verify** | `gcloud projects get-iam-policy "$PROJECT_ID" --flatten="bindings[].members" --filter="bindings.members:serviceAccount:${AGENT_SA}" --format="value(bindings.role)"` |
| **Expected Result** | All required least-privilege roles bound to `${AGENT_SA}` (zero `roles/owner` or `roles/bigquery.admin` on the agent SA). |
| **If It Fails** | Check if the lab requires granting `roles/run.invoker` or `roles/bigquery.dataViewer` to a SPIFFE principal (`principal://...`); copy the exact principal URI from the lab prompt. |

---

## Phase 3: BigQuery Operational Dataset & Partitioned/Clustered Tables (`DATA-01..05`)

| Field | Content |
|---|---|
| **Goal** | Create the operational dataset and load/partition `flights`, `passengers`, `bookings`, `airports_hubs`, and `baggage_claims` (`scheduled_departure` partition, `flight_id, carrier_jurisdiction` cluster). |
| **Commands** | ```bash
export BQ_DATASET="aeroglobal_ops"           # Use lab's exact dataset name

bq --location="$DEPLOY_REGION" mk --dataset \
  --description="AeroGlobal FlightOps Operational Data" \
  "${PROJECT_ID}:${BQ_DATASET}" || true

# Create partitioned & clustered flights table (INC-882914 remediation[0])
bq query --use_legacy_sql=false --location="$DEPLOY_REGION" "
CREATE TABLE IF NOT EXISTS \`${PROJECT_ID}.${BQ_DATASET}.flights\` (
  flight_id STRING,
  scheduled_departure DATE,
  origin_iata STRING,
  destination_iata STRING,
  carrier_jurisdiction STRING,
  great_circle_km FLOAT64,
  actual_arrival_delay_minutes INT64,
  is_carrier_controllable BOOL,
  disruption_code STRING,
  weather_delay_minutes INT64,
  mechanical_delay_minutes INT64
)
PARTITION BY scheduled_departure
CLUSTER BY flight_id, carrier_jurisdiction;
"
``` |
| **Verify** | `bq show --format=prettyjson "${PROJECT_ID}:${BQ_DATASET}.flights" | grep -A 5 -E "timePartitioning|clustering"` |
| **Expected Result** | `field: "scheduled_departure"` under `timePartitioning` and `flight_id`, `carrier_jurisdiction` under `clustering`. |
| **If It Fails** | If CSV files are provided in the lab workspace (`flights.csv`, `passengers.csv`, `bookings.csv`, `airports_hubs.csv`), load them with `bq load --autodetect --source_format=CSV` into the partitioned table or create the partitioned table via `CREATE OR REPLACE TABLE ... PARTITION BY ... CLUSTER BY ... AS SELECT * FROM ...`. |

---

## Phase 4: Vertex AI Search Policy Grounding Store (`DATA-02`, `FR-17`)

| Field | Content |
|---|---|
| **Goal** | Upload active policy manuals (`v2024.4`, EU261 2025, 2025-Q1 Waiver, Hotel Directory) to GCS and index in Vertex AI Search with `500`-token chunks, `100`-token overlap, and `is_active=true` metadata. |
| **Commands** | ```bash
export POLICY_BUCKET="${PROJECT_ID}-flightops-policies"
gcloud storage buckets create "gs://${POLICY_BUCKET}" --location="$DEPLOY_REGION" || true

# Upload policy documents from the lab workspace (exclude archived 2022 CoC from active passenger scope or tag is_active=false)
# gcloud storage cp ./data/policies/* "gs://${POLICY_BUCKET}/"
``` |
| **Verify** | `gcloud storage ls "gs://${POLICY_BUCKET}/"` |
| **Expected Result** | Active policy documents uploaded and Vertex AI Search data store created with chunk size `500` and overlap `100`. |
| **If It Fails** | If the lab uses Gemini Enterprise EU region (`europe-west1`/`europe-west4`), switch the Vertex AI Search / Gemini Enterprise location to `eu` (`global` for US). |

---

## Phase 5: Model Armor & Sensitive Data Protection Guardrails (`NFR-27`, `FR-24`)

| Field | Content |
|---|---|
| **Goal** | Configure SDP inspect/de-identify templates (masking 16-digit PANs, CVVs, passports, names, PNRs) and Model Armor template blocking prompt injection, jailbreaks, and malicious URIs. |
| **Commands** | ```bash
export MA_TEMPLATE_ID="flightops-guardrail-template" # Use lab's exact template ID

# Create Model Armor template (adjust region/flags to match lab instructions)
gcloud model-armor templates create "$MA_TEMPLATE_ID" \
  --location="$DEPLOY_REGION" \
  --project="$PROJECT_ID" \
  --pi-and-jailbreak-filter-enforcement=ENABLED \
  --pi-and-jailbreak-filter-confidence-level=MEDIUM_AND_ABOVE \
  --malicious-uri-filter-enforcement=ENABLED || true
``` |
| **Verify** | `gcloud model-armor templates describe "$MA_TEMPLATE_ID" --location="$DEPLOY_REGION" --project="$PROJECT_ID"` |
| **Expected Result** | Template active with PI/jailbreak and SDP enforcement enabled. |
| **If It Fails** | Check if the lab requires `LOW_AND_ABOVE` or `HIGH` confidence or specific RAI thresholds, and update via `gcloud model-armor templates update`. |

---

## Phase 6: ADK Multi-Agent & Deterministic Calculators (`FR-01..17`, Trap #2 Fix)

| Field | Content |
|---|---|
| **Goal** | Implement the ADK agent hierarchy and deterministic tools (`compute_eu261_compensation`, `compute_dot_part260_refund`, `compute_baggage_liability`, `check_crew_fdp_alert`, `get_contracted_hotel_cap`, `check_escalation`) using `Project2/lab_blueprint/` as reference. |
| **Commands** | ```bash
# Run local verification script before deploying
python3 ~/project-elevate-agents/Project2/lab_blueprint/verify.py
``` |
| **Verify** | `python3 ~/project-elevate-agents/Project2/lab_blueprint/verify.py` |
| **Expected Result** | `ALL GOLDEN CHECKS PASSED`:<br>• `AG-102` (LHR->JFK, 5541 km, 318 min delay, APU fault) -> `EUR 600` (`carrier_controllable=True`)<br>• `AG-503` (LAX->HND, 38h bag delay, $2,850 claim, $75 fee, Exec Platinum) -> `1,288 SDR (~$1,710)` cap + `$75` fee refund + `escalate=True` (`claim > $2,500`)<br>• `AG-884` (ORD->DFW, 20 min remaining FDP) -> `alert=True` (`< 30 min`), hotel cap `ORD $140 / DFW $120`<br>• All agent names are valid Python `snake_case` identifiers with zero duplicate parent bindings. |
| **If It Fails** | Inspect the failing assertion in `verify.py` and align function names/signatures with the lab's exact instructions. |

---

## Phase 7: Evaluation (`adk eval` / Golden Dataset Gate `NFR-15`)

| Field | Content |
|---|---|
| **Goal** | Run trajectory and final-response evaluation against `eval_dataset.jsonl` (`>= 90%` intent routing & tool selection precision, `100%` golden statutory cases). |
| **Commands** | ```bash
# Run ADK evaluation against the lab's eval dataset
adk eval ./flightops_agent ./eval_dataset.jsonl
``` |
| **Verify** | Check `adk eval` summary output for `routing_precision >= 0.90` and `golden_accuracy == 1.00`. |
| **Expected Result** | Evaluation passes thresholds and writes results to the location expected by the lab grader. |
| **If It Fails** | Inspect failed trajectories: ensure tool docstrings and parameter type hints match the expected tool call arguments in `eval_dataset.jsonl`. |

---

## Phase 8: Deploy to Agent Runtime / Cloud Run & Register in Agent Registry

| Field | Content |
|---|---|
| **Goal** | Deploy the agent with GCP resource attribution labels (`env=prod`, `app=flightops-agent`, `tenant=aeroglobal`) and verify registration in Agent Registry. |
| **Commands** | ```bash
# Deploy using adk / agents-cli (or the lab's deploy script)
# Ensure GOOGLE_CLOUD_LOCATION="global" and GOOGLE_GENAI_USE_VERTEXAI="True" are passed in env_vars!
``` |
| **Verify** | Click **"Check my progress"** on Checks **1 through 24** in the Qwiklabs console and log each in `RUNLOG.md`. |
| **Expected Result** | Checks **1 through 24** turn green (`>= 20 / 25` already achieved). |
| **If It Fails** | Check Cloud Logging (`gcloud logging read "resource.type=cloud_run_revision OR resource.type=aiplatform.googleapis.com/ReasoningEngine" --limit=20`) for `404` (location split) or `403` (missing IAM role). |

---

## Phase 9: Subtask 25 — Gateway / Security Teardown (RUN LAST ONLY!)

| Field | Content |
|---|---|
| **Goal** | Execute the final security hardening / gateway teardown check **only after Checks 1–24 are green**. |
| **Commands** | ```bash
# STOP! Verify in Qwiklabs UI that Checks 1-24 are already scored green!
# Only then execute the Subtask 25 teardown command specified in the lab instructions.
``` |
| **Verify** | Confirm Check 25 turns green and total Qwiklabs score shows **`>= 20 / 25` (ideally `25 / 25`)** on the top-right lab ribbon before clicking **End Lab**. |
| **Expected Result** | `25 / 25` checks green; safe to click **End Lab**. |
| **If It Fails** | Do **not** click End Lab; re-verify the resource state required by Check 25. |
