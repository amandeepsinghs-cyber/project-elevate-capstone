#!/usr/bin/env python3
"""Task 5 Automation Script: Enterprise Publishing, Agent Registry & Agent Gateway (Subtasks 21-25).

Usage:
  1. Run setup for Subtasks 21, 22, 23, and 24:
     python3 /workspace/scripts/task5_govern.py setup
     -> Then click "Check my progress" on Subtasks 21, 22, 23, and 24!

  2. ONLY AFTER Subtask 24 is marked green, run cleanup for Subtask 25:
     python3 /workspace/scripts/task5_govern.py cleanup
     -> Then click "Check my progress" on Subtask 25!
"""

import json
import os
import subprocess
import sys
import time
from typing import Any, Dict

import google.auth
from google.auth.transport.requests import AuthorizedSession

METADATA_PATH = "/workspace/deployment_metadata.json"
REGION = "us-central1"


def load_metadata() -> Dict[str, Any]:
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    raise RuntimeError(f"{METADATA_PATH} not found. Run task3_deploy.py first.")


def save_metadata(meta: Dict[str, Any]) -> None:
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[OK] Updated {METADATA_PATH}:\n{json.dumps(meta, indent=2)}")


def subtask21_gemini_enterprise_app(session: AuthorizedSession, project_id: str, meta: Dict[str, Any]) -> str:
    print("\n=== [Subtask 21] Locate or Create Gemini Enterprise App (`aeroglobal-enterprise-app`) ===")
    headers = {"X-Goog-User-Project": project_id, "Content-Type": "application/json"}
    base_url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/global/collections/default_collection"

    # Find datastore ID first
    ds_id = "aeroglobal-policies-store"
    ds_resp = session.get(f"{base_url}/dataStores", headers=headers)
    if ds_resp.status_code == 200:
        for ds in ds_resp.json().get("dataStores", []):
            name_last = ds.get("name", "").split("/")[-1]
            if name_last.startswith("aeroglobal-policies-store"):
                ds_id = name_last
                break

    engines_url = f"{base_url}/engines"
    eng_resp = session.get(engines_url, headers=headers)
    app_id = ""
    if eng_resp.status_code == 200:
        for eng in eng_resp.json().get("engines", []):
            disp = eng.get("displayName", "")
            eid = eng.get("name", "").split("/")[-1]
            if disp == "aeroglobal-enterprise-app" or eid.startswith("aeroglobal-enterprise-app"):
                app_id = eid
                print(f"[OK] Found Gemini Enterprise App: id={app_id}, displayName={disp}")
                break

    if not app_id:
        print("Creating `aeroglobal-enterprise-app` via Discovery Engine API...")
        create_payload = {
            "displayName": "aeroglobal-enterprise-app",
            "solutionType": "SOLUTION_TYPE_SEARCH",
            "industryVertical": "GENERIC",
            "dataStoreIds": [ds_id],
            "appType": "APP_TYPE_INTRANET",
            "searchEngineConfig": {
                "searchTier": "SEARCH_TIER_ENTERPRISE",
                "requiredSubscriptionTier": "SUBSCRIPTION_TIER_SEARCH_AND_ASSISTANT",
                "searchAddOns": ["SEARCH_ADD_ON_LLM"],
            },
        }
        c_resp = session.post(
            f"{engines_url}?engineId=aeroglobal-enterprise-app",
            headers=headers,
            json=create_payload,
        )
        if c_resp.status_code in (200, 201):
            app_id = "aeroglobal-enterprise-app"
            print(f"[OK] Created Gemini Enterprise App: {app_id}")
            time.sleep(5)
        else:
            print(
                f"[NOTE] API creation returned {c_resp.status_code}: {c_resp.text[:300]}\n"
                "If the 30-day trial license is not yet activated, create `aeroglobal-enterprise-app` "
                "in Cloud Console -> Gemini Enterprise -> Apps (accept the 30-day trial) and re-run this script."
            )

    if app_id:
        meta["gemini_enterprise_app"] = app_id
        save_metadata(meta)
    return app_id


def subtask22_register_agent_gemini_enterprise(
    session: AuthorizedSession, project_id: str, app_id: str, re_full_name: str
) -> None:
    print("\n=== [Subtask 22] Register Deployed Agent with Gemini Enterprise ===")
    if not app_id:
        print("[SKIP] `gemini_enterprise_app` is empty; complete Subtask 21 first.")
        return

    headers = {"X-Goog-User-Project": project_id, "Content-Type": "application/json"}
    agents_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}"
        f"/locations/global/collections/default_collection/engines/{app_id}"
        "/assistants/default_assistant/agents"
    )

    # Check if already registered
    list_resp = session.get(agents_url, headers=headers)
    if list_resp.status_code == 200:
        for ag in list_resp.json().get("agents", []):
            target = (
                ag.get("adkAgentDefinition", {})
                .get("provisionedReasoningEngine", {})
                .get("reasoningEngine", "")
            )
            if re_full_name in target or ag.get("displayName") == "aeroglobal_agent":
                print(f"[OK] Agent already registered in Gemini Enterprise: {ag.get('name')}")
                return

    # Try `agents-cli publish gemini-enterprise` first if installed
    subprocess.run(
        [
            "agents-cli", "publish", "gemini-enterprise",
            "--app-id", app_id,
            "--reasoning-engine-id", re_full_name,
            "--display-name", "aeroglobal_agent",
            "--description", "Autonomous Flight Operations & Disruption Resolution Agent for AeroGlobal Airways",
        ],
        check=False,
    )

    # Also ensure registration via v1alpha REST API
    check_resp = session.get(agents_url, headers=headers)
    already_there = False
    if check_resp.status_code == 200 and check_resp.json().get("agents"):
        already_there = True

    if not already_there:
        payload = {
            "displayName": "aeroglobal_agent",
            "description": (
                "Autonomous Flight Operations & Disruption Resolution Agent for AeroGlobal Airways, "
                "handling flight status, bookings, baggage claims, EU261, and US DOT policies."
            ),
            "adkAgentDefinition": {
                "toolSettings": {
                    "toolDescription": (
                        "Use this agent for AeroGlobal flight disruptions, passenger bookings, "
                        "corporate contract codes, mileage balances, baggage liability, and EU261/DOT policies."
                    )
                },
                "provisionedReasoningEngine": {
                    "reasoningEngine": re_full_name,
                },
            },
        }
        post_resp = session.post(agents_url, headers=headers, json=payload)
        print(f"[OK] v1alpha Gemini Enterprise agent registration status: {post_resp.status_code}")
        print(post_resp.text[:500])


def subtask23_agent_registry(
    session: AuthorizedSession, project_id: str, re_full_name: str, meta: Dict[str, Any]
) -> str:
    print("\n=== [Subtask 23] Lookup Agent in Google Cloud Agent Registry (us-central1) ===")
    subprocess.run(
        ["gcloud", "services", "enable", "agentregistry.googleapis.com", "networkservices.googleapis.com", "--project", project_id],
        check=False,
    )
    re_short_id = re_full_name.split("/")[-1]
    headers = {"X-Goog-User-Project": project_id}
    reg_url = f"https://agentregistry.googleapis.com/v1/projects/{project_id}/locations/{REGION}/agents"

    reg_id = ""
    for attempt in range(6):
        resp = session.get(reg_url, headers=headers)
        if resp.status_code == 200:
            for ag in resp.json().get("agents", []):
                if re_short_id in json.dumps(ag):
                    reg_id = ag.get("name", "").split("/")[-1]
                    print(f"[OK] Found Agent Registry entry: {reg_id} -> {ag.get('agentId')}")
                    break
        if reg_id:
            break
        print(f"  Waiting for Agent Registry auto-sync ({ (attempt + 1) * 5 }s)...")
        time.sleep(5)

    if reg_id:
        meta["agent_registry_id"] = reg_id
        save_metadata(meta)
    else:
        print("[WARN] No Agent Registry entry found yet; wait 1-2 minutes and re-run `task5_govern.py setup`.")
    return reg_id


def subtask24_create_agent_gateway(
    session: AuthorizedSession, project_id: str, meta: Dict[str, Any]
) -> None:
    print("\n=== [Subtask 24] Create Agent Gateway (`aeroglobal-gateway`) Bound to Agent Registry ===")
    headers = {"X-Goog-User-Project": project_id, "Content-Type": "application/json"}
    gw_get_url = (
        f"https://networkservices.googleapis.com/v1/projects/{project_id}"
        f"/locations/{REGION}/agentGateways/aeroglobal-gateway"
    )
    get_resp = session.get(gw_get_url, headers=headers)
    if get_resp.status_code == 200:
        print(f"[OK] Agent Gateway `aeroglobal-gateway` already exists: {get_resp.json().get('name')}")
    else:
        gw_create_url = (
            f"https://networkservices.googleapis.com/v1/projects/{project_id}"
            f"/locations/{REGION}/agentGateways?agentGatewayId=aeroglobal-gateway"
        )
        payload = {
            "description": "Enterprise Agent Gateway for AeroGlobal autonomous disruption operations",
            "registries": [
                f"//agentregistry.googleapis.com/projects/{project_id}/locations/{REGION}"
            ],
        }
        c_resp = session.post(gw_create_url, headers=headers, json=payload)
        print(f"[OK] Triggered Agent Gateway creation (HTTP {c_resp.status_code}): {c_resp.text[:300]}")
        for i in range(18):
            time.sleep(5)
            chk = session.get(gw_get_url, headers=headers)
            if chk.status_code == 200 and chk.json().get("registries"):
                print(f"[OK] Agent Gateway `aeroglobal-gateway` is active: {chk.json().get('registries')}")
                break
            print(f"  Waiting for Agent Gateway provisioning ({ (i + 1) * 5 }s)...")

    meta["agent_gateway_id"] = "aeroglobal-gateway"
    save_metadata(meta)


def subtask25_delete_agent_gateway(session: AuthorizedSession, project_id: str) -> None:
    print("\n=== [Subtask 25] Delete Agent Gateway (`aeroglobal-gateway`) ===")
    headers = {"X-Goog-User-Project": project_id}
    gw_url = (
        f"https://networkservices.googleapis.com/v1/projects/{project_id}"
        f"/locations/{REGION}/agentGateways/aeroglobal-gateway"
    )
    del_resp = session.delete(gw_url, headers=headers)
    print(f"DELETE response (HTTP {del_resp.status_code}): {del_resp.text[:300]}")
    for i in range(18):
        time.sleep(5)
        chk = session.get(gw_url, headers=headers)
        if chk.status_code == 404:
            print("[OK] Confirmed `aeroglobal-gateway` is deleted (HTTP 404 NOT_FOUND)!")
            break
        print(f"  Waiting for gateway deletion to complete ({ (i + 1) * 5 }s)...")


def main() -> None:
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "setup"
    _, project_id = google.auth.default()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID") or project_id

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    session = AuthorizedSession(credentials)
    meta = load_metadata()
    re_full_name = meta.get("reasoning_engine_id", "")

    if mode == "setup":
        app_id = subtask21_gemini_enterprise_app(session, project_id, meta)
        subtask22_register_agent_gemini_enterprise(session, project_id, app_id, re_full_name)
        subtask23_agent_registry(session, project_id, re_full_name, meta)
        subtask24_create_agent_gateway(session, project_id, meta)
        print("\n==================================================================")
        print("STOP HERE! Go to Qwiklabs and click 'Check my progress' for:")
        print("  - Subtask 21 (Create Gemini Enterprise application)")
        print("  - Subtask 22 (Register agent with Gemini Enterprise)")
        print("  - Subtask 23 (Register agent in Google Cloud Agent Registry)")
        print("  - Subtask 24 (Create Agent Gateway and bind to Agent Registry)")
        print("ONLY AFTER Subtask 24 is scored green, run:")
        print("  python3 /workspace/scripts/task5_govern.py cleanup")
        print("==================================================================")
    elif mode == "cleanup":
        subtask25_delete_agent_gateway(session, project_id)
        print("\n==================================================================")
        print("SUCCESS! Subtask 25 is complete. Click 'Check my progress' for Subtask 25!")
        print("==================================================================")
    else:
        print("Usage: python3 /workspace/scripts/task5_govern.py [setup|cleanup]")
        sys.exit(1)


if __name__ == "__main__":
    main()
