"""ADK Security, PII/PCI Redaction, and Anti-Loop Callbacks for AeroGlobal FlightOps.

Implements:
- NFR-27 / INC-883199: 16-digit PAN masking (XXXX-XXXX-XXXX-1234), CVV removal, passport/PNR tokenisation
- FR-24 / TEN-04: Prompt injection & system-override blocking (while allowing angry legitimate customers)
- NFR-09 / CON-02: SQL read-only and SELECT * blocking on tool arguments
- NFR-40 / NFR-43: Per-turn tool-call ceiling (<= 8 calls) and cycle detection (halt on 2nd identical call)
"""

import hashlib
import json
import re
from typing import Any, Optional

# Regex patterns for PII/PCI masking (NFR-27)
PAN_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
CVV_REGEX = re.compile(r"\b(?:CVV|CVC|CVV2|CSC)\s*[:=#]?\s*\d{3,4}\b", re.IGNORECASE)
PASSPORT_REGEX = re.compile(r"\b(?:passport(?:\s*(?:no|number|id|#))?\s*[:=#]?\s*)([A-Z0-9]{6,9})\b", re.IGNORECASE)
PNR_REGEX = re.compile(r"\b(?:PNR|confirmation(?:\s*code)?|locator)\s*[:=#]?\s*([A-Z0-9]{6})\b", re.IGNORECASE)

# High-confidence adversarial prompt injection signatures (FR-24)
# Note: legitimate angry customer phrases like "Ignore what the last agent told me, I demand my compensation"
# must NOT be blocked (GC-08 / TEN-04).
INJECTION_PATTERNS = [
    re.compile(r"system\s+override", re.IGNORECASE),
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|system)\s+instructions", re.IGNORECASE),
    re.compile(r"bypass\s+(?:security|guardrails|policy|validation)", re.IGNORECASE),
    re.compile(r"reveal\s+(?:your\s+)?system\s+prompt", re.IGNORECASE),
    re.compile(r"print\s+(?:your\s+)?(?:initial|system)\s+instructions", re.IGNORECASE),
    re.compile(r"issue\s+an?\s+immediate\s+\$\d+[,\d]*\s+cash\s+refund\s+without\s+verification", re.IGNORECASE),
]

FORBIDDEN_SQL_PATTERNS = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|MERGE)\b|SELECT\s+\*",
    re.IGNORECASE,
)


def mask_sensitive_text(text: str) -> str:
    """Masks 16-digit PANs to last 4 digits, strips CVVs, and tokenises passports/PNRs."""
    if not text:
        return text

    def _mask_pan(match: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) < 13 or len(digits) > 16:
            return match.group(0)
        return f"XXXX-XXXX-XXXX-{digits[-4:]}"

    sanitized = CVV_REGEX.sub("CVV:[REDACTED]", text)
    sanitized = PAN_REGEX.sub(_mask_pan, sanitized)
    sanitized = PASSPORT_REGEX.sub(r"passport:[PASSPORT_TOKEN]", sanitized)
    sanitized = PNR_REGEX.sub(r"PNR:[PNR_TOKEN]", sanitized)
    return sanitized


def is_adversarial_injection(text: str) -> tuple[bool, Optional[str]]:
    """Checks for high-confidence prompt injection while avoiding false refusals on angry customers (GC-08)."""
    if not text:
        return False, None
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True, pattern.pattern
    return False, None


def before_model_guardrail_callback(
    callback_context: Any,
    llm_request: Any,
) -> Optional[dict[str, Any]]:
    """ADK before_model_callback: screens for prompt injection and masks PII/PCI in place.

    Returns None to allow model execution, or a response dict to block/short-circuit.
    """
    state = getattr(callback_context, "state", {})
    contents = getattr(llm_request, "contents", []) or []

    for content in contents:
        parts = getattr(content, "parts", []) or []
        for part in parts:
            raw_text = getattr(part, "text", None)
            if isinstance(raw_text, str) and raw_text:
                blocked, matched_rule = is_adversarial_injection(raw_text)
                if blocked:
                    if isinstance(state, dict):
                        state["security_audit_event"] = {
                            "event": "SECURITY_BLOCK_PROMPT_INJECTION",
                            "rule": matched_rule,
                            "action": "REFUSED",
                        }
                    return {
                        "status": "BLOCKED",
                        "reason": "SECURITY_POLICY_VIOLATION",
                        "message": (
                            "Request refused: adversarial override or policy-manipulation attempt detected. "
                            "An immutable security audit event has been recorded."
                        ),
                    }
                # Mask PII/PCI before prompt reaches the model (NFR-27, CON-04)
                part.text = mask_sensitive_text(raw_text)
    return None


def before_tool_guardrail_callback(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
    max_tool_calls: int = 8,
) -> Optional[dict[str, Any]]:
    """ADK before_tool_callback: enforces read-only/bounded SQL, tool-call ceiling, and cycle detection.

     per ADK 2.0 contract (Core Guide §5 #17):
    - Return None to ALLOW normal tool execution.
    - Return a dict to BLOCK/SHORT-CIRCUIT the tool and return that dict to the LLM.
    """
    state = getattr(tool_context, "state", {})
    if not isinstance(state, dict):
        state = {}

    tool_name = getattr(tool, "name", getattr(tool, "__name__", str(tool)))
    canonical_args = json.dumps(args or {}, sort_keys=True, default=str)
    fingerprint = hashlib.sha256(f"{tool_name}:{canonical_args}".encode("utf-8")).hexdigest()

    # 1. Cycle detection (NFR-43: halt on 2nd identical tool call in same turn)
    seen_fingerprints: list[str] = list(state.get("turn_tool_fingerprints", []))
    if fingerprint in seen_fingerprints:
        return {
            "error": "CYCLE_DETECTED",
            "message": f"Halted repeated identical call to {tool_name} with identical arguments (NFR-43). Escalating to human.",
            "retryable": False,
        }
    seen_fingerprints.append(fingerprint)
    state["turn_tool_fingerprints"] = seen_fingerprints

    # 2. Tool-call ceiling per turn (NFR-40: <= 8 tool calls)
    step_count = int(state.get("turn_step_count", 0)) + 1
    state["turn_step_count"] = step_count
    if step_count > max_tool_calls:
        return {
            "error": "TOOL_CALL_CEILING_EXCEEDED",
            "message": f"Turn exceeded maximum of {max_tool_calls} tool calls (NFR-40). Halting and escalating.",
            "retryable": False,
        }

    # 3. Read-only & bounded SQL check (CON-02, NFR-09)
    for key, val in (args or {}).items():
        if isinstance(val, str) and ("sql" in key.lower() or "query" in key.lower()):
            if FORBIDDEN_SQL_PATTERNS.search(val):
                return {
                    "error": "UNSAFE_OR_UNBOUNDED_SQL",
                    "message": "Blocked query: write operations and SELECT * are prohibited (CON-02, NFR-09).",
                    "retryable": False,
                }

    return None
