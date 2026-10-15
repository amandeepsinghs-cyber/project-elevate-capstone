# Context and rules for agy (give this file to agy first)

You are helping me complete a timed, graded Qwiklabs lab. Follow these rules in every step.

## Authority and scope
1. **The lab's instructions are the specification.** Use the exact resource names, regions, models, file paths and parameters the lab gives. Never rename or "improve" them.
2. Work on **one lab task at a time**, in the order I give. Before running anything, show me the plan and the exact commands.
3. If the lab is silent on a design choice, prefer the defaults below, then ask me.

## Safety rules
4. **Never** run anything that deletes, tears down or disables a gateway, agent, runtime or project unless I explicitly say "run the teardown task now".
5. **Never** suggest ending the lab.
6. Never put secrets, keys or real personal data in code, prompts, logs or commit messages.
7. Do not push anything from this environment to any external repository.
8. Read-only access for the agent identity wherever the lab allows; least-privilege roles only.

## Defaults when the lab does not specify (from my Solution Design, Phase 1a)
- Deterministic code for any calculation, cap or entitlement; the model explains, never computes amounts.
- Guardrails on input and output (Model Armor where available); mask card numbers, CVVs, passport IDs, names and booking references.
- Answers cite the policy source and version; active policy version only.
- Escalate to a human above defined thresholds instead of acting autonomously.
- Per-turn limits on tool calls and tokens; structured tool errors; at most 2 self-corrections.
- Structured logs with trace and session IDs; no raw personal data in logs.

## Working style
- After each step, tell me how to verify it (command or console location) and which lab check it should turn green.
- If a command fails, show the full error and propose one fix at a time.
- Keep a running list of what we built (resource name, type, region) so I can log it in RUNLOG.md.
