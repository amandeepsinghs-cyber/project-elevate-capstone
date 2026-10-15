# Task 3 Lab Runbook: End-to-End Build (Qwiklabs / Labs for Sales)

**Rule zero: the lab's own instructions and checks are the authority.** This runbook is the process around them. Where the lab names a resource, region, model, file or path, use the lab's value, even if the SDD says otherwise.

Sources are tagged **[O]** official (go/elevate-capstone-faq, go/elevate-playbook, Agentic Learning Guide) or **[P]** peer notes, which you verify in the lab.

## 1. Facts that shape the plan

| Fact | Source |
|---|---|
| Only the first lab attempt is scored; ending and restarting does not count | [O] FAQ Q5, Playbook Sec. 4 |
| Finish every task before clicking End Lab; never End Lab before the passing score shows | [O] FAQ Q5; [P] vikesht@ |
| AI-assisted work allowed; you must validate outputs and own them | [O] Agentic Learning Guide Sec. 2 |
| Environment is monitored against prompt injection, reverse engineering and "unauthorized automated solutions" | [O] Agentic Learning Guide Sec. 3 |
| Graded on technical accuracy, Well-Architected soundness and working code, not prose | [O] Agentic Learning Guide Sec. 3 |
| ~6-hour timer; ~25 automated checks; pass reported as 20/25 (another note says 90%) | [P] amudivedu@, josephz@ |
| Aim to finish in ~4 hours; leave buffer | [P] josephz@ |
| `agy` (Antigravity) is in the lab VM; wait 2-4 min after start; sign in as "Business Account" / "Project ID" with the `student-...` credentials; if it closes after ~2 s run `sudo pkill -9 antigravity` | [P] amudivedu@ |
| Run the gateway-teardown check last, only after checks 1-24 have scored | [P] amudivedu@ |
| EU lab: if Gemini Enterprise apps look empty, switch the console location filter from `global` to `eu` | [P] amudivedu@ |
| Stuck: stay in the lab; ask in #elevate-capstone-support; use "Escalate Issue" for sandbox crashes | [O] Playbook Sec. 5; [P] |
| Lab credentials arrive the day before the window opens | [O] launch announcement |

## 2. Before lab day (T-1)

- [ ] Ask in #elevate-capstone-support: "May I clone my own private repo (process notes and my SDD, no lab content) inside the Part 3 lab VM?" Use the fallback in Sec. 6 if the answer is no or unclear.
- [ ] Push `Project2/lab_kit/` (after you approve the file list).
- [ ] Create the read-only access you will use (Sec. 6). Do not create long-lived tokens.
- [ ] Re-read `AGY_CONTEXT.md`; it is the first thing you give `agy`.
- [ ] Block 6 uninterrupted hours; have the support chat open in another tab.

## 3. Lab-day timeline

| Time | Step | Done when |
|---|---|---|
| 0:00 | Start Lab; open the console with the `student-...` credentials; note project ID and region in `RUNLOG.md` | IDs logged |
| 0:05 | Wait for `agy`; sign in (Business Account / Project ID) | `agy` responds |
| 0:10 | Get context in: clone the kit (Sec. 6) or upload it; give `agy` `AGY_CONTEXT.md` | `agy` repeats the rules back |
| 0:15 | **Read every lab task before building.** Fill the check map (Sec. 4): task, check, expected resource or output | All 25 rows filled |
| 0:30 | Build task by task (Sec. 5 loop), in lab order unless a task depends on a later one | Each check green |
| ~3:30 | Re-verify every check; fix any red ones (except teardown) | Checks 1-24 green |
| ~3:45 | Run the gateway-teardown task last, if the lab has one | Check 25 green |
| ~4:00 | Confirm the passing score on the lab ribbon or profile; only then End Lab | Score >= pass bar |

## 4. Check map (fill in at 0:15)

| # | Lab task / check | Resource or output expected | SDD component (if any) | Status |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| ... | | | | |
| 24 | | | | |
| 25 | Gateway teardown (if present): run last | | | |

## 5. Per-task loop (repeat for each task)

1. **Read** the task text twice; copy exact names into the check map.
2. **Plan with `agy`:** ask for the plan and the exact commands; check them against the task text before running.
3. **Run** one step at a time; read every error in full.
4. **Verify** the lab check turns green. If the lab has a "Check my progress" button, use it; do not move on while red unless the task is blocked.
5. **Log** the commands and the result in `RUNLOG.md`.
6. **If stuck > 15 minutes:** skip to the next independent task, note it in the log, and return later. If a platform fault, post in #elevate-capstone-support without leaving the lab.

## 6. Getting the kit into the lab

**Option A: read-only deploy key (preferred; no reusable secret leaves your laptop).**

```bash
ssh-keygen -t ed25519 -N "" -f ~/.ssh/lab_key -C "lab-readonly"
cat ~/.ssh/lab_key.pub      # add in GitHub repo Settings > Deploy keys, read-only
GIT_SSH_COMMAND="ssh -i ~/.ssh/lab_key -o StrictHostKeyChecking=accept-new" \
  git clone --depth 1 --filter=blob:none --sparse git@github.com:amandeepsinghs-cyber/project-elevate-agents.git
cd project-elevate-agents && git sparse-checkout set Project2/lab_kit
```
Delete the deploy key in GitHub after the lab.

**Option B: fine-grained token.** Read-only, this repo only, 1-day expiry; clone over HTTPS; run `history -c` afterwards; revoke after the lab.

**Fallback: upload.** Use the Upload button in the lab VM or Cloud Shell to copy the `lab_kit` files from your laptop (about a minute, no credentials).

**Never push anything from the lab back to GitHub.** Lab code and lab content stay in the lab.

## 7. Guardrails

- The lab names override the SDD. The SDD (Phase 1a tags) only fills gaps where the lab is silent.
- Do not paste prebuilt solution scripts for the lab; build with `agy` from the lab's tasks and validate each step (integrity rule, Sec. 1).
- Never put secrets or real PII in code, prompts or logs.
- Never click End Lab until the passing score is visible.
