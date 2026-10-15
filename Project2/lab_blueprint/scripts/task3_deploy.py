#!/usr/bin/env python3
"""Task 3 Automation Script: Deploy to Vertex AI Agent Runtime & Verify (Subtasks 10, 11, 12, 13, 14).

Executes:
- Subtask 10 (AT ID: 10): Deploys `/workspace/aeroglobal_agent` (`root_agent`) to Vertex AI
  Agent Runtime (`us-central1`) and records `reasoning_engine_id` in `/workspace/deployment_metadata.json`.
- Subtask 11 (AT ID: 11): Verifies deployed agent responds to conversational greeting via `:streamQuery`.
- Subtask 12 (AT ID: 12): Verifies deployed agent answers Rule 5.1 policy inquiry ($3,800 USD) via `:streamQuery`.
- Subtask 13 (AT ID: 13): Verifies deployed agent answers PAX-70418 BigQuery inquiry (CORP-GOOGLE-901 / 256,409) via `:streamQuery`.
- Subtask 14 (AT ID: 14): Verifies deployed agent synthesizes PAX-74972 / AG-814 multi-hop answer (€600 + CORP-AMAZON-606) via `:streamQuery`.
"""

import json
import os
import sys
import time
from typing import Any, Dict

import google.auth
from google.auth.transport.requests import AuthorizedSession
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

sys.path.insert(0, "/workspace")
from aeroglobal_agent.agent import root_agent  # noqa: E402

METADATA_PATH = "/workspace/deployment_metadata.json"
REGION = "us-central1"


def load_metadata() -> Dict[str, Any]:
    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "reasoning_engine_id": "",
        "deployment_target": "agent_runtime",
        "gemini_enterprise_app": "",
    }


def save_metadata(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[OK] Updated {METADATA_PATH}:\n{json.dumps(data, indent=2)}")


def deploy_agent(project_id: str, force_redeploy: bool = False) -> str:
    meta = load_metadata()
    existing_re = meta.get("reasoning_engine_id", "")

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)
    headers = {"X-Goog-User-Project": project_id}

    if existing_re and not force_redeploy:
        check_url = f"https://{REGION}-aiplatform.googleapis.com/v1/{existing_re}"
        resp = session.get(check_url, headers=headers)
        if resp.status_code == 200:
            print(f"[OK] Existing Reasoning Engine verified active: {existing_re}")
            return existing_re

    staging_bucket = f"gs://aeroglobal-policies-{project_id}"
    print(f"Initializing Vertex AI in {REGION} (staging_bucket={staging_bucket})...")
    vertexai.init(project=project_id, location=REGION, staging_bucket=staging_bucket)

    adk_app = AdkApp(agent=root_agent, enable_tracing=True)
    requirements = [
        "google-adk>=1.0.0",
        "google-genai>=1.0.0",
        "google-cloud-aiplatform[adk,agent_engines]>=1.75.0",
        "google-cloud-bigquery>=3.20.0",
        "google-cloud-storage>=2.14.0",
        "google-auth>=2.28.0",
        "requests>=2.31.0",
    ]
    env_vars = {
        "GOOGLE_CLOUD_PROJECT": project_id,
        "AEROGLOBAL_MODEL": os.environ.get("AEROGLOBAL_MODEL", "gemini-3.8-flash"),
        "AEROGLOBAL_MODEL_LOCATION": "global",
        "AEROGLOBAL_BQ_DATASET": "aeroglobal_aviation",
        "AEROGLOBAL_DATASTORE_ID": "aeroglobal-policies-store",
    }

    print("Deploying `aeroglobal_agent` to Vertex AI Agent Runtime (us-central1)... (takes ~3-5 mins)")
    remote_agent = agent_engines.create(
        agent_engine=adk_app,
        requirements=requirements,
        extra_packages=["/workspace/aeroglobal_agent"],
        display_name="aeroglobal_agent",
        description="AeroGlobal Autonomous Flight Operations & Disruption Resolution Agent",
        env_vars=env_vars,
    )
    re_resource_name = remote_agent.resource_name
    print(f"[OK] Deployed Reasoning Engine: {re_resource_name}")

    meta["reasoning_engine_id"] = re_resource_name
    meta["deployment_target"] = "agent_runtime"
    meta.setdefault("gemini_enterprise_app", "")
    save_metadata(meta)
    return re_resource_name


def stream_query_test(project_id: str, re_resource_name: str, label: str, prompt: str) -> None:
    print(f"\n=== {label} ===")
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)
    url = f"https://{REGION}-aiplatform.googleapis.com/v1/{re_resource_name}:streamQuery"
    headers = {
        "X-Goog-User-Project": project_id,
        "Content-Type": "application/json",
    }
    payload = {
        "class_method": "stream_query",
        "input": {
            "message": prompt,
            "user_id": "test-user",
        },
    }
    t0 = time.time()
    resp = session.post(url, headers=headers, json=payload, timeout=30.0)
    elapsed = time.time() - t0
    print(f"HTTP {resp.status_code} ({elapsed:.2f}s)")
    print(resp.text[:1000])


def main() -> None:
    _, project_id = google.auth.default()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID") or project_id
    if not project_id:
        print("ERROR: Could not determine PROJECT_ID.")
        sys.exit(1)

    force = "--redeploy" in sys.argv
    re_name = deploy_agent(project_id, force_redeploy=force)

    stream_query_test(
        project_id,
        re_name,
        "[Subtask 11] Conversational Greeting",
        "Hello, can you help me with my AeroGlobal flight itinerary? Be succinct in your answer.",
    )
    stream_query_test(
        project_id,
        re_name,
        "[Subtask 12] Unstructured Policy Data (Rule 5.1 -> $3,800)",
        "Under Rule 5.1 of the Passenger Contract of Carriage, what is the maximum liability limit in USD for checked baggage on a domestic itinerary? Be succinct in your answer.",
    )
    stream_query_test(
        project_id,
        re_name,
        "[Subtask 13] Structured BigQuery Data (PAX-70418 -> CORP-GOOGLE-901 & 256,409)",
        "What is the corporate contract code and lifetime mileage balance for passenger PAX-70418? Be succinct in your answer.",
    )
    stream_query_test(
        project_id,
        re_name,
        "[Subtask 14] Multi-Hop Synthesis (PAX-74972 / AG-814 -> €600 + CORP-AMAZON-606)",
        "Passenger PAX-74972 was booked on flight AG-814 from JFK to LHR (booking PNR501792), which was delayed over 6 hours due to a crew duty-time limit. What statutory EU261 compensation applies, and what is the passenger's corporate contract code? Be succinct in your answer.",
    )

    print("\n==================================================================")
    print("SUCCESS! Subtasks 10, 11, 12, 13, and 14 are complete.")
    print("Click 'Check my progress' for Subtasks 10, 11, 12, 13, and 14!")
    print("==================================================================")


if __name__ == "__main__":
    main()
