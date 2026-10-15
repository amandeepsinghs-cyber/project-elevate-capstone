# Task 3 Qwiklabs Live Execution Checklist (`RUNLOG.md` — 25 / 25 Checkpoints)

- **Candidate:** Amandeep Singh
- **Project ID (`$PROJECT_ID`):** `_______________________`
- **Reasoning Engine ID (`$REASONING_ENGINE_ID`):** `_______________________`
- **Gemini Enterprise App ID (`$GEMINI_APP_ID`):** `_______________________`
- **Agent Registry ID (`$AGENT_REGISTRY_ID`):** `_______________________`

---

## Step 0: Clone Blueprint into `/workspace`
- [ ] Cloned repo and copied `Project2/lab_blueprint/*` into `/workspace/` (`aeroglobal_agent/`, `scripts/`, `AGENTS.md`)

## Task 1: Grounding Data & Metadata (`python3 /workspace/scripts/task1_grounding.py`)
- [ ] **AT ID 1 (Subtask 1):** BigQuery dataset `aeroglobal_aviation` (`US` multi-region) + 5 CSV tables loaded (`airports_hubs`, `baggage_incidents`, `bookings`, `flights`, `passengers`)
- [ ] **AT ID 2 (Subtask 2):** GCS bucket `gs://aeroglobal-policies-${PROJECT_ID}` (`us-central1`) + `aeroglobal-policies-store` datastore (`global`)
- [ ] **AT ID 3 (Subtask 3):** Table descriptions + all column descriptions populated in `aeroglobal_aviation`
- [ ] **AT ID 4 (Subtask 4):** `description` registered in datastore schema + `structData.description` populated on all 5 policy documents

## Task 2: Local ADK Agent on Port 8080 (`bash /workspace/scripts/task2_local_test.sh`)
- [ ] **AT ID 5 (Subtask 5):** `adk api_server --host 0.0.0.0 --port 8080 /workspace` listening on port 8080 (`HTTP 200` on `/docs`)
- [ ] **AT ID 6 (Subtask 6):** Local agent responds to conversational greeting
- [ ] **AT ID 7 (Subtask 7):** Local agent answers structured BigQuery query (`PAX-70418` -> `CORP-GOOGLE-901` & `256,409` miles)
- [ ] **AT ID 8 (Subtask 8):** Local agent answers unstructured policy query (`Rule 5.1` -> `$3,800` USD)
- [ ] **AT ID 9 (Subtask 9):** Local agent synthesizes multi-hop answer (`PAX-74972` / `AG-814` -> `€600` EU261 + `CORP-AMAZON-606`)

## Task 3: Deploy to Vertex AI Agent Runtime (`python3 /workspace/scripts/task3_deploy.py`)
- [ ] **AT ID 10 (Subtask 10):** Deployed `aeroglobal_agent` to Reasoning Engine (`us-central1`) + recorded in `/workspace/deployment_metadata.json`
- [ ] **AT ID 11 (Subtask 11):** Deployed agent responds to conversational greeting (`:streamQuery`)
- [ ] **AT ID 12 (Subtask 12):** Deployed agent answers unstructured policy query (`Rule 5.1` -> `$3,800` USD)
- [ ] **AT ID 13 (Subtask 13):** Deployed agent answers structured BigQuery query (`PAX-70418` -> `CORP-GOOGLE-901` & `256,409`)
- [ ] **AT ID 14 (Subtask 14):** Deployed agent synthesizes multi-hop answer (`PAX-74972` / `AG-814` -> `€600` + `CORP-AMAZON-606`)

## Task 4: Optimize & Harden the Agent (`python3 /workspace/scripts/task4_harden.py`)
- [ ] **AT ID 15 (Subtask 15):** Google GenAI `CachedContent` created in `global` on `gemini-3.8-flash` + Warm Run 2 latency verified
- [ ] **AT ID 16 (Subtask 16):** Least-privilege IAM enforced (`roles/bigquery.dataViewer` + `roles/bigquery.jobUser` only; write probe `PNR999901` count = `0`)
- [ ] **AT ID 17 (Subtask 17):** Semgrep SAST scan (`semgrep scan --config=/opt/security/rules.yaml --error /workspace/aeroglobal_agent/`) passes with `0 findings`
- [ ] **AT ID 18 (Subtask 18):** Red-Team Competitor Deflection probe (Delta / United) passed
- [ ] **AT ID 19 (Subtask 19):** Red-Team Persona Hijack & Humor probe (`ComedianBot`) passed
- [ ] **AT ID 20 (Subtask 20):** Red-Team Aviation Safety probe (swollen lithium-ion battery + solvent citing FAA/TSA/DOT/ICAO/IATA) passed

## Task 5: Enterprise Ready & Governance (`python3 /workspace/scripts/task5_govern.py setup` -> `cleanup`)
- [ ] **AT ID 21 (Subtask 21):** Created Gemini Enterprise App `aeroglobal-enterprise-app` (30-day trial accepted) + recorded ID in `/workspace/deployment_metadata.json`
- [ ] **AT ID 22 (Subtask 22):** Registered deployed Reasoning Engine with Gemini Enterprise (`v1alpha` assistant agents)
- [ ] **AT ID 23 (Subtask 23):** Recorded `agent_registry_id` from Google Cloud Agent Registry (`us-central1`) in `/workspace/deployment_metadata.json`
- [ ] **AT ID 24 (Subtask 24):** Created `aeroglobal-gateway` bound to Agent Registry + **clicked Check my progress for Subtask 24 BEFORE deleting**
- [ ] **AT ID 25 (Subtask 25):** Ran `python3 /workspace/scripts/task5_govern.py cleanup` to delete `aeroglobal-gateway` (`HTTP 404`) + clicked Check my progress for Subtask 25
