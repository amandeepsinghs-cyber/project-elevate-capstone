# AGENTS.md — Master Execution Instructions for Antigravity (`agy`) in `/workspace`

> **Role:** You are the autonomous build agent running inside the Qwiklabs `/workspace` environment for the **AeroGlobal Autonomous Flight Operations & Disruption Resolution Agent** assessment (`AT ID: 1` through `AT ID: 25`).
> **Pre-Built Assets Available in `/workspace`:** All required agent code (`/workspace/aeroglobal_agent/`) and automation scripts (`/workspace/scripts/`) are already present in `/workspace`. Execute them in order and verify every checkpoint.

---

## 1. Mandatory Environment & Resource Contract

| Component | Required Value / Path | Region / Location |
| :--- | :--- | :--- |
| **Workspace Root** | `/workspace` | Local VM |
| **ADK Agent Package** | `/workspace/aeroglobal_agent` (`agent.py` exports `root_agent` named `aeroglobal_agent`) | Local (`0.0.0.0:8080`) |
| **Model** | `gemini-3.8-flash` (NEVER use `gemini-1.x`, `2.x`, `3.0`, or `bison` — flagged by Semgrep SAST) | `global` |
| **BigQuery Dataset** | `aeroglobal_aviation` (5 tables: `airports_hubs`, `baggage_incidents`, `bookings`, `flights`, `passengers`) | `US` (multi-region) |
| **Policy GCS Bucket** | `gs://aeroglobal-policies-${PROJECT_ID}` (5 `.md` files) | `us-central1` |
| **Agent Search Datastore** | `aeroglobal-policies-store` (with `description` in schema + `structData.description` on all 5 docs) | `global` (`default_collection`) |
| **Vertex AI Agent Runtime** | Reasoning Engine deployed from `/workspace/aeroglobal_agent` | `us-central1` |
| **Deployment Metadata** | `/workspace/deployment_metadata.json` | Local VM |
| **Gemini Enterprise App** | `aeroglobal-enterprise-app` (`SEARCH_TIER_ENTERPRISE`, `SUBSCRIPTION_TIER_SEARCH_AND_ASSISTANT`) | `global` |
| **Agent Gateway** | `aeroglobal-gateway` bound to `agentregistry.googleapis.com` (Created in Subtask 24, Deleted in Subtask 25) | `us-central1` |

---

## 2. Step-by-Step Execution Plan for the System Agent (`agy`)

When the user asks you to build or execute a task, run the corresponding pre-built script and verify its output:

### Task 1: Grounding Data & Metadata (Subtasks 1, 2, 3, 4)
Run:
```bash
export PROJECT_ID=$(gcloud config get-value project)
python3 /workspace/scripts/task1_grounding.py
```
- **What it does:**
  - **Subtask 1 (`AT ID: 1`):** Creates BigQuery dataset `aeroglobal_aviation` in `US` and loads all 5 CSVs from `gs://${PROJECT_ID}-static-assets-bucket/data/structured/`.
  - **Subtask 3 (`AT ID: 3`):** Populates table descriptions and column descriptions for every column across all 5 tables.
  - **Subtask 2 (`AT ID: 2`):** Creates `gs://aeroglobal-policies-${PROJECT_ID}` in `us-central1`, copies the 5 `.md` policy files, and creates the `aeroglobal-policies-store` datastore in `global`.
  - **Subtask 4 (`AT ID: 4`):** Registers `description` in the datastore schema and imports all 5 documents with `structData.description` using `reconciliationMode: FULL` (never delete the datastore).

### Task 2: Local ADK Agent on Port 8080 & Verification (Subtasks 5, 6, 7, 8, 9)
Run:
```bash
bash /workspace/scripts/task2_local_test.sh
```
- **What it does:**
  - **Subtask 5 (`AT ID: 5`):** Starts `adk api_server --host 0.0.0.0 --port 8080 /workspace` in the background and verifies HTTP 200 on `http://localhost:8080/docs`.
  - **Subtask 6 (`AT ID: 6`):** Verifies conversational greeting.
  - **Subtask 7 (`AT ID: 7`):** Verifies BigQuery lookup for `PAX-70418` (`CORP-GOOGLE-901` and `256,409` miles).
  - **Subtask 8 (`AT ID: 8`):** Verifies Policy lookup for Rule 5.1 domestic checked baggage limit (`$3,800` USD).
  - **Subtask 9 (`AT ID: 9`):** Verifies Multi-Hop reasoning for `PAX-74972` on `AG-814` (`PNR501792`) -> `€600` EU261 compensation + `CORP-AMAZON-606`.

### Task 3: Deploy to Vertex AI Agent Runtime (Subtasks 10, 11, 12, 13, 14)
Run:
```bash
python3 /workspace/scripts/task3_deploy.py
```
- **What it does:**
  - **Subtask 10 (`AT ID: 10`):** Deploys `/workspace/aeroglobal_agent` to Vertex AI Agent Runtime (`us-central1`) and writes `/workspace/deployment_metadata.json`.
  - **Subtasks 11–14 (`AT ID: 11–14`):** Tests greeting, Rule 5.1 policy, `PAX-70418` SQL, and `PAX-74972`/`AG-814` multi-hop against `:streamQuery`.

### Task 4: Optimize & Harden the Agent (Subtasks 15, 16, 17, 18, 19, 20)
Run:
```bash
python3 /workspace/scripts/task4_harden.py
```
- **What it does:**
  - **Subtask 15 (`AT ID: 15`):** Creates an explicit Google GenAI `CachedContent` resource in `global` on `gemini-3.8-flash` and benchmarks Cold vs. Warm `:streamQuery` calls.
  - **Subtask 16 (`AT ID: 16`):** Enforces least-privilege IAM (`roles/bigquery.dataViewer` and `roles/bigquery.jobUser` only; removes `roles/editor`, `roles/bigquery.dataEditor`, `roles/bigquery.admin`) and verifies `PNR999901` is not inserted.
  - **Subtask 17 (`AT ID: 17`):** Runs `semgrep scan --config=/opt/security/rules.yaml --error --exclude=venv --exclude=.venv --exclude=__pycache__ /workspace/aeroglobal_agent/` and verifies 0 findings. (If the 8th rule in `/opt/security/rules.yaml` flags anything, inspect the message, remediate `/workspace/aeroglobal_agent/`, re-run Semgrep, and redeploy if needed.)
  - **Subtasks 18–20 (`AT ID: 18–20`):** Tests all 3 Red-Teaming probes (Delta/United competitor deflection, ComedianBot persona hijack, and swollen lithium-ion battery + solvent concealment citing FAA/TSA/DOT/ICAO/IATA).

### Task 5: Enterprise Publishing, Agent Registry & Agent Gateway (Subtasks 21, 22, 23, 24, 25)
1. **First**, ensure the 30-day trial license for Gemini Enterprise is accepted in the Cloud Console (`Gemini Enterprise -> Apps -> Create App -> aeroglobal-enterprise-app` with Enterprise + Assistant enabled), then run:
   ```bash
   python3 /workspace/scripts/task5_govern.py setup
   ```
   - Completes **Subtasks 21, 22, 23, and 24** and updates `/workspace/deployment_metadata.json`.
   - **WAIT** for the user to click *Check my progress* on **Subtasks 21, 22, 23, and 24**!
2. **Second**, ONLY after Subtask 24 is marked green in Qwiklabs, run:
   ```bash
   python3 /workspace/scripts/task5_govern.py cleanup
   ```
   - Deletes `aeroglobal-gateway` and confirms HTTP 404 for **Subtask 25 (`AT ID: 25`)**.
