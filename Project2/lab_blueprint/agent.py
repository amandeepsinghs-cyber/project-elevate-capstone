"""ADK Multi-Agent Hierarchy Blueprint for AeroGlobal FlightOps.

Encodes Cohort 20 Traps #1 and #2 Fixes:
- Global inference location (GOOGLE_CLOUD_LOCATION='global') set in config.py before ADK import
- Every Agent(name=...) uses strict snake_case (underscores only, NEVER hyphens)
- Factory functions instantiate fresh sub-agents so no agent instance is ever attached to two parents
"""

from typing import Any

from .config import MODEL_DEFAULT, MODEL_HIGH_STAKES, MODEL_ROUTER
from .tools import (
    check_crew_fdp_alert,
    check_escalation,
    compute_baggage_liability,
    compute_dot_part260_refund,
    compute_eu261_compensation,
    compute_right_to_care,
    evaluate_jurisdiction,
)

SYSTEM_INSTRUCTION_COORDINATOR = """You are the AeroGlobal Airways Autonomous Flight Operations & Regulatory Disruption Resolution Agent.
Follow these strict operational rules on every turn:
1. Classify the request as analytical operational data, policy lookup, or hybrid multi-hop reasoning.
2. NEVER invent or estimate financial compensation, baggage caps, hotel caps, or meal stipends. Always call the deterministic calculation tools (`evaluate_jurisdiction`, `compute_eu261_compensation`, `compute_dot_part260_refund`, `compute_baggage_liability`, `compute_right_to_care`, `check_crew_fdp_alert`, `check_escalation`).
3. Answer policy questions ONLY from the active Contract of Carriage v2024.4 ($3,800 domestic baggage cap), the 2025 EU261 Manual, the 2025-Q1 Weather Waiver Addendum, and the Partner Hotel Directory. Never cite the archived 2022 Contract of Carriage ($3,500 cap) for passenger or standard staff queries.
4. Technical defects (such as APU faults) and crew shortages are ALWAYS carrier-controllable under CJEU Wallentin-Hermann precedent, even when concurrent weather delays exist.
5. EU261 Right to Care (meals, contracted hotel lodging, airport transfers) is unconditional regardless of disruption cause.
6. Never include unmasked Credit Card PANs, CVVs, passport numbers, or raw PII in responses.
"""


def build_agent_Definitions() -> dict[str, dict[str, Any]]:
    """Returns canonical snake_case agent definitions (safe even if google-adk is not installed locally).

    When running inside the Qwiklabs VM with google-adk installed, `create_root_agent()`
    instantiates live `google.adk.agents.LlmAgent` objects from these definitions.
    """
    return {
        "ops_data_agent": {
            "name": "ops_data_agent",  # MUST use underscores, never hyphens
            "model": MODEL_DEFAULT,
            "description": (
                "Queries operational flight status, arrival delay minutes, great-circle distance, "
                "carrier controllability, baggage delay hours, and FAA Part 117 crew Flight Duty Period (FDP) margins."
            ),
            "tools": [check_crew_fdp_alert],
        },
        "policy_rag_agent": {
            "name": "policy_rag_agent",  # MUST use underscores, never hyphens
            "model": MODEL_DEFAULT,
            "description": (
                "Retrieves clauses from active AeroGlobal policy manuals (CoC v2024.4, EU261 2025 manual, "
                "2025-Q1 Weather Waiver Addendum, and Partner Hotel Directory) with version and clause citations."
            ),
            "tools": [compute_right_to_care],
        },
        "statutory_calculator_agent": {
            "name": "statutory_calculator_agent",  # MUST use underscores, never hyphens
            "model": MODEL_HIGH_STAKES,
            "description": (
                "Deterministically calculates EU261/UK261 compensation, US DOT Part 260 automatic refunds, "
                "Montreal Convention 1,288 SDR vs domestic $3,800 baggage liability caps, and human escalation triggers."
            ),
            "tools": [
                evaluate_jurisdiction,
                compute_eu261_compensation,
                compute_dot_part260_refund,
                compute_baggage_liability,
                compute_right_to_care,
                check_escalation,
            ],
        },
        "flight_ops_coordinator": {
            "name": "flight_ops_coordinator",  # MUST use underscores, never hyphens
            "model": MODEL_ROUTER,
            "description": (
                "Root 3-way intent router and coordinator for AeroGlobal FlightOps disruption resolution across "
                "operational data, active regulatory policy manuals, and deterministic statutory calculators."
            ),
        },
    }


def create_root_agent() -> Any:
    """Factory function that builds a fresh ADK LlmAgent tree (never reuses sub-agent instances)."""
    from google.adk.agents import LlmAgent  # Imported lazily for environments without google-adk

    defs = build_agent_Definitions()

    ops_agent = LlmAgent(
        name=defs["ops_data_agent"]["name"],
        model=defs["ops_data_agent"]["model"],
        description=defs["ops_data_agent"]["description"],
        instruction="Fetch operational flight, crew duty (Part 117), and baggage delay facts accurately using read-only tools.",
        tools=defs["ops_data_agent"]["tools"],
    )

    policy_agent = LlmAgent(
        name=defs["policy_rag_agent"]["name"],
        model=defs["policy_rag_agent"]["model"],
        description=defs["policy_rag_agent"]["description"],
        instruction="Retrieve and cite only active policy manuals (CoC v2024.4, EU261 2025, 2025-Q1 Waiver). Never use archived 2022 manuals.",
        tools=defs["policy_rag_agent"]["tools"],
    )

    calculator_agent = LlmAgent(
        name=defs["statutory_calculator_agent"]["name"],
        model=defs["statutory_calculator_agent"]["model"],
        description=defs["statutory_calculator_agent"]["description"],
        instruction=SYSTEM_INSTRUCTION_COORDINATOR,
        tools=defs["statutory_calculator_agent"]["tools"],
    )

    root_agent = LlmAgent(
        name=defs["flight_ops_coordinator"]["name"],
        model=MODEL_DEFAULT,
        description=defs["flight_ops_coordinator"]["description"],
        instruction=SYSTEM_INSTRUCTION_COORDINATOR,
        sub_agents=[ops_agent, policy_agent, calculator_agent],
        tools=[
            evaluate_jurisdiction,
            compute_eu261_compensation,
            compute_dot_part260_refund,
            compute_baggage_liability,
            compute_right_to_care,
            check_crew_fdp_alert,
            check_escalation,
        ],
    )
    return root_agent
