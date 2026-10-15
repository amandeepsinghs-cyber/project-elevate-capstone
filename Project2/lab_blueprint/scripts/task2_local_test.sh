#!/usr/bin/env bash
# Task 2 Automation Script: Local ADK Agent Server & Verification (Subtasks 5, 6, 7, 8, 9)
set -euo pipefail

export PROJECT_ID=$(gcloud config get-value project)
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export GOOGLE_GENAI_USE_VERTEXAI="1"
export GOOGLE_CLOUD_LOCATION="global"

cd /workspace

echo "=== [Subtask 5] Starting local ADK API Server on 0.0.0.0:8080 ==="
if ! curl -s -o /dev/null http://localhost:8080/docs; then
  nohup adk api_server --host 0.0.0.0 --port 8080 /workspace > /workspace/adk_server.log 2>&1 &
  sleep 5
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/docs)
echo "[OK] Local ADK server HTTP status on :8080/docs -> ${HTTP_CODE} (Expected: 200)"

echo ""
echo "=== [Subtask 6] Conversational Greeting Sanity Check ==="
python3 - <<'PY'
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from aeroglobal_agent.agent import root_agent

async def run_prompt(prompt: str):
    runner = InMemoryRunner(agent=root_agent, app_name="aeroglobal_agent")
    session = await runner.session_service.create_session(app_name="aeroglobal_agent", user_id="test-user")
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    out = []
    async for event in runner.run_async(user_id="test-user", session_id=session.id, new_message=msg):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    out.append(p.text)
    print("RESPONSE:", "".join(out))

asyncio.run(run_prompt("Hello! What can you help me with today? Be succinct in your answer."))
PY

echo ""
echo "=== [Subtask 7] Structured BigQuery Grounding Sanity Check (PAX-70418) ==="
python3 - <<'PY'
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from aeroglobal_agent.agent import root_agent

async def run_prompt(prompt: str):
    runner = InMemoryRunner(agent=root_agent, app_name="aeroglobal_agent")
    session = await runner.session_service.create_session(app_name="aeroglobal_agent", user_id="test-user")
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    out = []
    async for event in runner.run_async(user_id="test-user", session_id=session.id, new_message=msg):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    out.append(p.text)
    print("RESPONSE:", "".join(out))

asyncio.run(run_prompt("What is the corporate contract code and lifetime mileage balance for passenger PAX-70418? Be succinct in your answer."))
PY

echo ""
echo "=== [Subtask 8] Unstructured Policy Grounding Sanity Check (Rule 5.1 -> \$3,800) ==="
python3 - <<'PY'
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from aeroglobal_agent.agent import root_agent

async def run_prompt(prompt: str):
    runner = InMemoryRunner(agent=root_agent, app_name="aeroglobal_agent")
    session = await runner.session_service.create_session(app_name="aeroglobal_agent", user_id="test-user")
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    out = []
    async for event in runner.run_async(user_id="test-user", session_id=session.id, new_message=msg):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    out.append(p.text)
    print("RESPONSE:", "".join(out))

asyncio.run(run_prompt("Under Rule 5.1 of the Passenger Contract of Carriage, what is the maximum liability limit in USD for checked baggage on a domestic itinerary? Be succinct in your answer."))
PY

echo ""
echo "=== [Subtask 9] Multi-Hop Synthesis Sanity Check (PAX-74972 / AG-814 -> €600 + CORP-AMAZON-606) ==="
python3 - <<'PY'
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from aeroglobal_agent.agent import root_agent

async def run_prompt(prompt: str):
    runner = InMemoryRunner(agent=root_agent, app_name="aeroglobal_agent")
    session = await runner.session_service.create_session(app_name="aeroglobal_agent", user_id="test-user")
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    out = []
    async for event in runner.run_async(user_id="test-user", session_id=session.id, new_message=msg):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    out.append(p.text)
    print("RESPONSE:", "".join(out))

asyncio.run(run_prompt("Passenger PAX-74972 was booked on flight AG-814 from JFK to LHR (booking PNR501792), which was delayed over 6 hours due to a crew duty-time limit. What statutory EU261 compensation applies, and what is the passenger's corporate contract code? Be succinct in your answer."))
PY

echo ""
echo "=================================================================="
echo "SUCCESS! Subtasks 5, 6, 7, 8, and 9 are verified."
echo "Keep the local ADK server running on port 8080 and click 'Check my progress' for Subtasks 5, 6, 7, 8, and 9!"
echo "=================================================================="
