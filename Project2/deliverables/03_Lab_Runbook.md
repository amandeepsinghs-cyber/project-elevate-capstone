# AeroGlobal Autonomous Flight Operations — Task 3 Qwiklabs Execution Runbook (All 25 Subtasks)

> **Target Score:** **25 / 25 Checkpoints (`AT ID: 1` through `AT ID: 25`)**
> **Estimated Completion Time:** **~60–75 minutes** (using the pre-built `Project2/lab_blueprint/` scripts or the in-lab Antigravity CLI `agy`).

---

## How the Lab Build Works (Two Ways to Execute)

Inside the Qwiklabs VM, **you do not have to write code by hand**:
1. **Clone this repository into `/workspace`** (Step 0 below). That immediately places:
   - `/workspace/aeroglobal_agent/` (`__init__.py`, `agent.py`, `tools.py`, `requirements.txt` — pre-built for `gemini-3.8-flash` and Semgrep SAST).
   - `/workspace/scripts/` (`task1_grounding.py`, `task2_local_test.sh`, `task3_deploy.py`, `task4_harden.py`, `task5_govern.py`).
   - `/workspace/AGENTS.md` (instructions for the in-lab Antigravity AI agent `agy`).
2. **Choose your execution style:**
   - **Option 1 (Direct Script Execution — Fastest & Most Deterministic):** Run the 5 pre-built scripts in the Konsole terminal (one script per Task) and click **Check my progress** after each Task.
   - **Option 2 (Have the In-Lab System Agent `agy` Execute for You):** Launch `agy` inside `/workspace`, select `Gemini 3.8 Flash` (`global`), and paste:
     > *"Read `/workspace/AGENTS.md` and execute the pre-built scripts in `/workspace/scripts/` for Tasks 1, 2, 3, and 4 sequentially, verifying each sanity check."*

---

## Step 0: Sign In & Clone Blueprint into `/workspace` (~5 Mins)

1. Open the **Antigravity Remote Session** browser tab from Qwiklabs and allow clipboard access.
2. Open **Konsole** (`Application Launcher > System > Konsole`) and run:

```bash
export PROJECT_ID=$(gcloud config get-value project)
echo "Active Project: ${PROJECT_ID}"

# Clone your private repo and copy the pre-built lab blueprint directly into /workspace
git clone https://<YOUR_PAT>@github.com/amandeepsinghs-cyber/project-elevate-agents.git /tmp/elevate-repo
cp -r /tmp/elevate-repo/Project2/lab_blueprint/* /workspace/
rm -rf /tmp/elevate-repo
cd /workspace
ls -la /workspace /workspace/aeroglobal_agent /workspace/scripts
```

> **Note:** If you also sign in to the Antigravity Agent Platform UI or `agy` CLI per the lab setup instructions, always select **Global** as the region and **Gemini 3.8 Flash** as the model.

---

## Task 1: Prepare Environment & Ingest Grounding Data (`AT ID: 1–4`, ~10 Mins)

Run the single Task 1 automation script in `/workspace`:

```bash
cd /workspace
export PROJECT_ID=$(gcloud config get-value project)
python3 /workspace/scripts/task1_grounding.py
```

### What `task1_grounding.py` Automates:
- **Subtask 1 (`AT ID: 1`):** Creates BigQuery dataset `aeroglobal_aviation` in the **`US` multi-region** and loads all 5 CSV tables (`airports_hubs`, `baggage_incidents`, `bookings`, `flights`, `passengers`) from `gs://${PROJECT_ID}-static-assets-bucket/data/structured/`.
- **Subtask 3 (`AT ID: 3`):** Populates **table descriptions** for all 5 tables AND **column descriptions** for every single column in `aeroglobal_aviation`.
- **Subtask 2 (`AT ID: 2`):** Creates `gs://aeroglobal-policies-${PROJECT_ID}` in `us-central1`, copies the 5 `.md` policy files from `gs://${PROJECT_ID}-static-assets-bucket/data/policies/`, and creates the Agent Search datastore **`aeroglobal-policies-store`** in `global`.
- **Subtask 4 (`AT ID: 4`):** Registers `description` in `aeroglobal-policies-store`'s schema and imports all 5 documents with `structData.description` in a single `FULL` pass (so you only wait for indexing once and never delete the datastore).

✅ **Action:** Click **Check my progress** for **Subtask 1, Subtask 2, Subtask 3, and Subtask 4**.

---

## Task 2: Build & Locally Verify the Autonomous ADK Agent (`AT ID: 5–9`, ~5 Mins)

Run the Task 2 local server & verification script:

```bash
cd /workspace
bash /workspace/scripts/task2_local_test.sh
```

### What `task2_local_test.sh` Automates:
- **Subtask 5 (`AT ID: 5`):** Starts `adk api_server --host 0.0.0.0 --port 8080 /workspace` in the background and confirms HTTP `200` on `http://localhost:8080/docs`.
- **Subtask 6 (`AT ID: 6`):** Verifies conversational greeting.
- **Subtask 7 (`AT ID: 7`):** Verifies BigQuery SQL grounding (`PAX-70418` -> `CORP-GOOGLE-901` and `256,409` miles).
- **Subtask 8 (`AT ID: 8`):** Verifies Agent Search policy grounding (`Rule 5.1` -> `$3,800` USD).
- **Subtask 9 (`AT ID: 9`):** Verifies multi-hop synthesis (`PAX-74972` on `AG-814` `JFK`->`LHR`, `PNR501792` -> `€600` EU261 compensation + `CORP-AMAZON-606`).

✅ **Action:** Keep the background ADK server running on port 8080 and click **Check my progress** for **Subtask 5, Subtask 6, Subtask 7, Subtask 8, and Subtask 9**.

---

## Task 3: Deploy to Agent Runtime (`AT ID: 10–14`, ~10 Mins)

Run the Task 3 deployment & verification script:

```bash
cd /workspace
python3 /workspace/scripts/task3_deploy.py
```

### What `task3_deploy.py` Automates:
- **Subtask 10 (`AT ID: 10`):** Deploys `/workspace/aeroglobal_agent` (`root_agent`) to Vertex AI Agent Runtime (`Reasoning Engine`) in `us-central1` and writes `/workspace/deployment_metadata.json`:
  ```json
  {
    "reasoning_engine_id": "projects/PROJECT_ID/locations/us-central1/reasoningEngines/REASONING_ENGINE_ID",
    "deployment_target": "agent_runtime",
    "gemini_enterprise_app": ""
  }
  ```
- **Subtask 11 (`AT ID: 11`):** Verifies deployed agent greeting via `:streamQuery`.
- **Subtask 12 (`AT ID: 12`):** Verifies deployed agent policy retrieval (`Rule 5.1` -> `$3,800` USD) via `:streamQuery`.
- **Subtask 13 (`AT ID: 13`):** Verifies deployed agent BigQuery lookup (`PAX-70418` -> `CORP-GOOGLE-901` & `256,409`) via `:streamQuery`.
- **Subtask 14 (`AT ID: 14`):** Verifies deployed agent multi-hop reasoning (`PAX-74972` / `AG-814` -> `€600` + `CORP-AMAZON-606`) via `:streamQuery`.

✅ **Action:** Click **Check my progress** for **Subtask 10, Subtask 11, Subtask 12, Subtask 13, and Subtask 14**.

---

## Task 4: Optimize & Harden the Agent (`AT ID: 15–20`, ~10 Mins)

Run the Task 4 optimization, IAM hardening, Semgrep SAST, and Red-Teaming script:

```bash
cd /workspace
python3 /workspace/scripts/task4_harden.py
```

### What `task4_harden.py` Automates:
- **Subtask 15 (`AT ID: 15` — Context Caching):** Creates an explicit Google GenAI `CachedContent` resource (`aeroglobal-policy-cache`) in **`global`** on **`gemini-3.8-flash`** (which deterministically satisfies Subtask 15!) AND runs two consecutive `:streamQuery` calls where Run 2 hits the warm response cache in `< 0.2s`.
- **Subtask 16 (`AT ID: 16` — Least-Privilege IAM):** Grants `roles/bigquery.dataViewer` + `roles/bigquery.jobUser` and removes `roles/editor`, `roles/bigquery.dataEditor`, `roles/bigquery.admin`, and `roles/bigquery.dataOwner` from the Reasoning Engine's service accounts, then verifies that the `PNR999901` write probe leaves `0` rows in `aeroglobal_aviation.bookings`.
- **Subtask 17 (`AT ID: 17` — Semgrep SAST):** Runs `semgrep scan --config=/opt/security/rules.yaml --error --exclude=venv --exclude=.venv --exclude=__pycache__ /workspace/aeroglobal_agent/` and prints all rule IDs in `/opt/security/rules.yaml`.
  > **Tip:** If the 8th rule in `/opt/security/rules.yaml` flags anything in `/workspace/aeroglobal_agent/`, read the printed `message:` from `/opt/security/rules.yaml` (or ask `agy` to remediate it), re-run `semgrep scan`, and if you changed `agent.py`/`tools.py`, run `python3 /workspace/scripts/task3_deploy.py --redeploy`.
- **Subtask 18 (`AT ID: 18` — Red-Team Competitor Deflection):** Verifies the agent politely declines to promote Delta/United and redirects to AeroGlobal services.
- **Subtask 19 (`AT ID: 19` — Red-Team Persona Hijack):** Verifies the agent rejects `ComedianBot` overrides and refuses pilot crash jokes/limericks.
- **Subtask 20 (`AT ID: 20` — Red-Team Aviation Safety):** Verifies the agent refuses to help conceal swollen lithium-ion batteries or unlabelled solvents and cites **FAA, TSA, DOT, ICAO, and IATA Dangerous Goods Regulations**.

✅ **Action:** Click **Check my progress** for **Subtask 15, Subtask 16, Subtask 17, Subtask 18, Subtask 19, and Subtask 20**.

---

## Task 5: Make the Agent Enterprise Ready & Govern (`AT ID: 21–25`, ~10 Mins)

### Step 5A: Create Gemini Enterprise App & Accept 30-Day Trial (`Subtask 21`)
1. In the Google Cloud Console, navigate to **Gemini Enterprise (or AI Applications / Search & Conversation) → Apps → Create App**.
2. Accept the **30-day trial license** if prompted, select **Enterprise Application** (with Search and Assistant capabilities enabled), connect your `aeroglobal-policies-store` datastore, and set the App Name to:
   **`aeroglobal-enterprise-app`**
3. Now run the Task 5 setup script in Konsole:

```bash
cd /workspace
python3 /workspace/scripts/task5_govern.py setup
```

### What `task5_govern.py setup` Automates:
- **Subtask 21 (`AT ID: 21`):** Looks up (or creates via API) `aeroglobal-enterprise-app` and writes its generated App ID into `/workspace/deployment_metadata.json` under `"gemini_enterprise_app"`.
- **Subtask 22 (`AT ID: 22`):** Publishes and registers your deployed Reasoning Engine with `aeroglobal-enterprise-app` via `agents-cli publish gemini-enterprise` and the `v1alpha` Discovery Engine Assistant Agents API.
- **Subtask 23 (`AT ID: 23`):** Looks up your auto-registered agent in **Google Cloud Agent Registry** (`agentregistry.googleapis.com` in `us-central1`) and writes `"agent_registry_id"` into `/workspace/deployment_metadata.json`.
- **Subtask 24 (`AT ID: 24`):** Creates **Agent Gateway** `aeroglobal-gateway` in `networkservices.googleapis.com` (`us-central1`) bound to `//agentregistry.googleapis.com/projects/${PROJECT_ID}/locations/us-central1` and writes `"agent_gateway_id": "aeroglobal-gateway"` into `/workspace/deployment_metadata.json`.

🛑 **CRITICAL PAUSE BEFORE SUBTASK 25:**
Click **Check my progress** for **Subtask 21, Subtask 22, Subtask 23, and Subtask 24** right now and verify all four turn **GREEN** (24/25 points)!

---

### Step 5B: Delete Agent Gateway (`Subtask 25`)
**Only after Subtask 24 is scored green**, run the cleanup command to delete `aeroglobal-gateway`:

```bash
cd /workspace
python3 /workspace/scripts/task5_govern.py cleanup
```

✅ **Action:** Click **Check my progress** for **Subtask 25** to achieve **25 / 25**!
