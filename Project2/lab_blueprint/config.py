"""Environment & configuration blueprint for AeroGlobal FlightOps Agent.

Encodes Cohort 20 Trap #1 Fix:
- GOOGLE_CLOUD_LOCATION='global' and GOOGLE_GENAI_USE_VERTEXAI='True' for Gemini inference
- DEPLOY_REGION='us-central1' (or lab region) for BigQuery, Cloud Run, Model Armor, and Agent Engine
"""

import os

# 1. Force Vertex AI + Global inference endpoint before importing google.genai / ADK
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

PROJECT_ID: str = os.environ.get("GOOGLE_CLOUD_PROJECT", os.environ.get("PROJECT_ID", ""))
DEPLOY_REGION: str = os.environ.get("DEPLOY_REGION", "us-central1")
INFERENCE_LOCATION: str = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

# Model identifiers — override via environment variables if the lab specifies e.g. gemini-3.6-flash
MODEL_ROUTER: str = os.environ.get("MODEL_ROUTER", "gemini-2.5-flash-lite")
MODEL_DEFAULT: str = os.environ.get("MODEL_DEFAULT", "gemini-2.5-flash")
MODEL_HIGH_STAKES: str = os.environ.get("MODEL_HIGH_STAKES", "gemini-2.5-pro")

# BigQuery & Vertex AI Search settings
BQ_DATASET: str = os.environ.get("BQ_DATASET", "aeroglobal_ops")
VERTEX_SEARCH_DATA_STORE_ID: str = os.environ.get("VERTEX_SEARCH_DATA_STORE_ID", "flightops-policy-store")
MODEL_ARMOR_TEMPLATE_ID: str = os.environ.get("MODEL_ARMOR_TEMPLATE_ID", "flightops-guardrail-template")

# Execution & Cost Ceilings (NFR-40, NFR-41, NFR-42)
MAX_TOOL_CALLS_PER_TURN: int = int(os.environ.get("MAX_TOOL_CALLS_PER_TURN", "8"))
MAX_LLM_CALLS_PER_TURN: int = int(os.environ.get("MAX_LLM_CALLS_PER_TURN", "10"))
MAX_UNCACHED_TOKENS_PER_TURN: int = int(os.environ.get("MAX_UNCACHED_TOKENS_PER_TURN", "32000"))
TURN_TIMEOUT_SECONDS: int = int(os.environ.get("TURN_TIMEOUT_SECONDS", "20"))

# Resource Attribution Labels
RESOURCE_LABELS: dict[str, str] = {
    "env": os.environ.get("ENV", "prod"),
    "app": "flightops-agent",
    "tenant": "aeroglobal",
    "phase": "p1a",
}
