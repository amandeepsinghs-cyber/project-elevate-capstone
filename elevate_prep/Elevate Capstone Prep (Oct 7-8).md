# §Tab 1: Agentic AI & Security Assessment — Core Study Guide, Cheat Sheet & Reflexes

**⚠️ DISCLAIMER — UNOFFICIAL PERSONAL STUDY NOTES (PLEASE READ FIRST)**

* **Not an Official Study Guide:** This document is a personal, AI-assisted study compilation created by an individual candidate (`contributor`) for their own Capstone prep. It is **not** an official Project Elevate study guide, endorsed curriculum, or authoritative reference.  
* **Do Not Use as Your Only Resource:** Although notes have been cross-checked against course materials and current Google documentation, sections of this doc synthesize community trainers, peer-shared notes, and AI-generated practice questions that may contain errors, outdated details, or assumptions that differ from the live assessment.  
* **Always Use Official Sources as Your Source of Truth:** Rely primarily on the [**Capstone Portal (`go/elevate-capstone-reg`)**](https://sites.google.com/corp/google.com/elevateai/capstone), the [**Elevate Playbook (`go/elevate-playbook`)**](#), the [**Candidate FAQ (`go/elevate-capstone-faq`)**](#), the [**Elevate Knowledge Check – How to Prepare (`contributor`)**](#), the [**official slide decks (`go/elevate-slides`)**](#), the pre-loaded [**NotebookLM (`go/elevate-notebook`)**](#), and the [**Elevate Labs course (`go/elevate-labs`)**](https://explore.qwiklabs.com/course_templates/1738435).  
* **🤝 Pay It Forward — Contribute Back After Your Capstone:** If this guide helps you, please contribute back once you've finished your Capstone so future cohorts can learn: drop a doc comment or ping `contributor` with corrections to the study material (decks, public docs, course labs, tool setup) and general prep tips. **Never share Capstone questions, test details, scenario briefs or specifics, solution code, or debugging patches.** The Playbook treats that as an assessment integrity violation "escalated to leadership", and FAQ Q12 escalates deliberate sharing to "regional CE leadership and People Operations".

&nbsp;

&nbsp;

**🎯 POST-EXAM REALITY CHECK — WHAT YOU ACTUALLY NEED TO STUDY**

* **Focus 90%+ of Your Study Time on Part 1 (The 60-Minute Closed-Book Knowledge Check):** Part 1 requires **90% (27/30 correct)** in **60 minutes** on HackerRank Secure Mode (closed-book, browser focus monitored). Many questions test specific product behaviors and documentation details (especially **Model Armor**, **Agent Registry**, **Agent Identity & Gateway**, **Agent Skills**, **ADK 2.0**, **MCP/A2A/OTel**, **CodeMender**, and **Gemini Cost & Capacity**) that go beyond high-level slide bullets. **Section 1 below is the exact doc-verified study guide I wish I had used first.**  
* **Deprioritize the Hands-On Labs (Parts 2 & 3):** In practice, the Part 2 Troubleshooting Lab and Part 3 Hands-On Solutioning / Build are **painless and fully automatable** using the in-environment **`agy` (Antigravity 2.0)** CLI/IDE and AI tools (which are explicitly permitted in Part 2 \[in-environment `agy`\] and Part 3 \[CE-owned AI\]). Do **not** waste hours memorizing CLI flags or lab runbooks before your window—treat **Tabs 4 and 5** as optional, low-priority reference material.  
* **📄 Submit Markdown (`.md`), NOT PDFs, for Part 3A (RAISE Portal):** When uploading your Part 3A Discovery Document and Solution Design Document (SDD) to the RAISE portal, **always submit Markdown (`.md`) files—PDFs were not submitting properly** (multi-page PDFs fail parsing, throw `500 Internal Error` timeouts, or return empty evaluation reports).

&nbsp;

&nbsp;

**📌 OCT 6–8 OFFICIAL & LIVE WEEK 1 UPDATES (MUST-READ BEFORE STARTING)**

* **Official Part 1 Passing Bar & Timer Confirmed (Oct 6):** The [**Elevate Knowledge Check – How to Prepare (`contributor`)**](#) officially confirms Part 1 is **60 minutes, 30 questions, and requires 90% (27/30 correct) to pass** (`Module 0: ~15%`, `Module 1: ~20%`, `Module 2: ~30%`, `Module 3: ~35%`). It is strictly **closed-book** (no notes, Gemini Notebook, Gemini, or external AI assistants).  
* **HackerRank Secure Mode (No Webcam/Mic AI Proctor):** Part 1 runs in [**HackerRank Secure Mode**](https://support.hackerrank.com/articles/2545360734-secure-mode), which tracks browser tab switching, window focus loss, and copy/paste—there is **no webcam or microphone AI Proctor mode** (using Chrome Incognito is recommended). After submitting Part 1, the portal dashboard button still displays `"Start Now"`—that is expected as long as you received the HackerRank confirmation email.  
* **🚨 CRITICAL Part 3A Rule — Submit Markdown (`.md`), NOT PDFs (RAISE Portal):** In the RAISE portal (Part 3A Task 1 Discovery & Task 2 SDD), **always upload your deliverables as Markdown (`.md`) files—PDFs do not submit properly** (they fail evaluation, time out, or return empty reports). Evaluation takes \~10–25 minutes; `"Completed"` means evaluated (not a confirmed pass). Only **Attempt 1** returns a qualitative rubric scorecard; **Attempt 2** records your final submission without a scorecard.  
* **🚨 CRITICAL Lab Rule — DO NOT END LAB EARLY (`contributor`, Live Week 1 Support):** In both Qwiklabs / LfS labs (*Part 2: Cymbal Retail: AI Agent Security Troubleshooting Lab \[3hr, 90/100\]* and *Part 3B: Autonomous Flight Operations & Disruption Resolution Agent \[6hr, 20/25 tasks\]*), **NEVER click `"End Lab"` early**—only click `"End Lab"` after verifying your full passing score on the lab ribbon / Qwiklabs profile (ending early permanently terminates your single attempt).  
* **Live Week 1 LfS Lab Watchouts:**  
  * **Antigravity (`agy`) startup & login in LfS:** Wait **2–4 minutes** after lab start for Antigravity to come up; sign in using **"Business Account" / "Project ID"** with your `student-...` credentials / lab GCP Project ID (not standard Google OAuth); if Antigravity closes after 2 seconds, run `sudo pkill -9 antigravity` in the terminal.  
  * **Gemini Enterprise EU Region Filter:** If the Gemini Enterprise Apps table appears empty in a European lab (`europe-west1` / `europe-west4`), switch the console location filter from `global` to **`eu`**.  
* **Official NotebookLM Interactive Tutor Prompts (`contributor` Oct 6 Doc):** Copy-paste these 3 official prompts into [`go/elevate-notebook`](#) (replace `[...]` with a deck PDF name like `M1L2 context engineering.pdf` or `M2S2 Agent Governance.pdf`, or specific concepts):  
1. **Prompt 1 — The scenario generator:** `"Act as an expert technical examiner for the Elevate program. I am studying [insert topic, e.g., Agent Registry vs. MCP]. Based strictly on the course materials in this notebook, generate a difficult, scenario-based multiple-choice question. The scenario should describe a customer problem or an architectural decision. Do not give me the answer. Wait for me to reply with my choice, and then explain why I was right or wrong."`  
2. **Prompt 2 — The concept differentiator:** `"I am reviewing the Elevate course materials. I am having trouble understanding the practical difference between [concept A] and [concept B]. Based on the provided documents, explain the difference to me in a single paragraph, and then give me a real-world customer use case where I would choose one over the other."`  
3. **Prompt 3 — The troubleshooting drill:** `"Act as an Elevate examiner. Create a troubleshooting scenario involving [insert topic, e.g., context window exhaustion]. Describe the symptoms of the failure. Ask me to identify the root cause from 4 multiple-choice options. Wait for my answer before grading me."`

&nbsp;

## 

## 1\. Agentic AI & Security Assessment — Core Study Guide (Start Here)

*Covers Google Cloud agent tooling (ADK, Agent Skills, Agent Registry, Agent Identity and Gateway, MCP and A2A), Model Armor, CodeMender, and Gemini cost and capacity. Every fact has been checked against current Google documentation or the official specs.*

### How to use this guide

Each section opens with a short explanation of the topic, followed by a table of the facts most worth knowing and a note on common wrong answers. A good approach is to read a section, then cover the right-hand column of the table and try to recall each fact before moving on.

**Model Armor (section 1.7)** and **Agent Registry (section 1.4)** are the most heavily tested topics, so if time is short, start there, then **Skills (section 1.1)** and **ADK (section 1.2)**. The quiz is 60 minutes of single-choice questions, so there's roughly two minutes per question.

### Test-taking tips

* **Spot absolute-language traps:** Many wrong options give themselves away with absolute language: `"only,"` `"always,"` `"never,"` `"under any configuration,"` `"entirely."` The correct answer is usually the most specific, balanced option, and it often matches Google's documentation nearly word for word.  
* **Watch for swapped-definition traps:** Look out for options that correctly describe two things but attach each description to the wrong one (for example, **MCP and A2A**, or **basic and advanced Sensitive Data Protection**).  
* **Read every option to the end:** The distinguishing detail often comes last.  
* **Identify the product first on scenario questions:** Scenario questions (`"a customer has…"`) typically test one specific feature, so identify which product the scenario is about before reading the options.

&nbsp;

### 

### 1.1 Agent Skills (Antigravity / Agent Skills standard)

Skills are folders of instructions an agent loads only when they're relevant. The core idea is **progressive disclosure**: the agent always sees a short menu (each skill's name and description) and reads the full instructions only for the skill that matches the task. This is the fix for **"tool bloat,"** where loading hundreds of tools and rules into context makes the agent slower, costlier, and worse at picking the right one.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **What's loaded at the start**agent judges the skill relevant.&nbsp; | Only each skill's **name and description**. The full `SKILL.md` is read when the agent judges the skill relevant. |
| **Folder structure** | `SKILL.md` (required, with YAML frontmatter: **`description` required, `name` optional**) plus optional `scripts/`, `examples/`, and `resources/`. |
| **Project (workspace) skill location** | `<project-root>/.agents/skills/<skill>/` (older posts use `.agent/skills/`). |
| **Global skill location** | `~/.gemini/config/skills/` (works across Antigravity, the IDE, and the CLI). |
| **How a skill activates** | **Automatically** (the prompt's intent matches the description) or **explicitly with a slash command** (`/skill-name`). |
| **Problem skills solve** | **"Tool bloat"**: too many tools at once overwhelms the agent; skills load specialist knowledge only when needed. |

* **Watch out for:** Options claiming the full `SKILL.md` for every skill is loaded up front, that skills need a slash command to work at all, or that a skill folder can't contain anything but `SKILL.md`. The global path (`~/.gemini/...`) is the wrong answer when the question says `"project-specific."`

&nbsp;

### 

### 1.2 ADK (Agent Development Kit) fundamentals

ADK gives you two ways to orchestrate: **LLM agents**, where the model decides what happens next, and **workflow agents**, which follow fixed logic with no model making the routing decisions. Google's design guidance is to use the simplest thing that works: if the steps are predefined and no model needs to orchestrate them, a deterministic workflow is enough. ADK 2.0 adds graph-based workflows that mix several node types.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **`SequentialAgent` / `ParallelAgent` / `LoopAgent`** | **Workflow agents.** They run sub-agents using predefined logic (in order, concurrently, or repeated) **without consulting an AI model to orchestrate**. Sub-agents can still be LLM agents and can still call tools. |
| **Choosing a design pattern** | Predefined steps, no model needed to orchestrate → a **workflow pattern**. Use **agentic patterns** (coordinator, etc.) only when the model must decide the route. |
| **Function tools** | ADK builds the tool schema the model sees from the function's **name, docstring, parameters, type hints, and default values**. The docstring becomes the description; **parameters without defaults are required**. The model **never** sees the function body or `#` comments. |
| **ADK 2.0 graph node types** | **Functions, human input, Tools, and LLM capabilities (agents)**. **Join nodes** merge parallel branches. |
| **Passing data in a graph** | Nodes set state through an **`Event`'s `state` field**; downstream nodes can read it. **`output`** passes data **only to the next node**. |
| **`SessionService`** | Loads and saves `Session` objects (one conversation's state and event history) and applies **`state_delta`** from each event. Implementations: **`InMemorySessionService`, `DatabaseSessionService`, `VertexAiSessionService`**. |

* **Watch out for:** `"Every routing decision costs a model call"` (not for workflow agents). `"Graphs support only LLM nodes."` `"You must hand-write a JSON schema for every tool."` Made-up services such as `"TextEmbeddingService"` offered as `SessionService` implementations.

&nbsp;

### 

### 1.3 Agent quality: context, grounding, and evaluation

These questions test whether you can diagnose why an agent misbehaves and how you'd prove its work is trustworthy. When an agent gives a confident but generic answer about something company-specific, the fix is **grounding (RAG)**: retrieve the company's own content at query time and give it to the model. Passing tests isn't proof of good work; you also have to inspect how the agent got there.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **Generic answer instead of the company's definition** | **Retrieval-augmented generation (grounding):** fetch enterprise content at query time and supply it as context. Not temperature, per-question fine-tuning, or more tools. |
| **Context bloat from tool output** | **"Observation flooding"**: context fills with logs, file dumps, and stack traces rather than reasoning. |
| **Summarization drops a needed fact** | **"Context collapse"**: aggressive compression deletes something the task needs later (e.g., a config value read earlier). |
| **Trajectory evaluation** | Grades the **path** (reasoning and the sequence of tool calls, e.g., did it read the file before editing it?), not just the final output. |
| **Final-response evaluation** | Functional correctness, outcome grading, or LLM-as-judge on the final text. Necessary, but it misses `"right answer, wrong process."` |

* **Watch out for:** `"The only fix is a bigger context window."` `"Passing all tests is sufficient evidence."` Options that describe real but unrelated failure modes (architectural drift, PR slop, tool bloat) when the scenario describes something else.

&nbsp;

### 

### 1.4 Agent Registry *(Most Heavily Tested \#2)*

Agent Registry is Google Cloud's central catalog for agents, MCP servers, tools, and skills. It isn't a runtime and it isn't a model registry. Know how things get into it (automatically vs. manually), its resource model, its three goals, and the difference between a catalog name and an IAM identity.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **What it is** | `"A centralized catalog that lets you store, discover, and govern MCP servers, tools, standalone skills, and AI agents within Google Cloud."` |
| **Three goals** | **Accelerate development** (discovery and reuse); **simplify integration** (standardized MCP and A2A protocols); **support governance** (enforce security and boundaries across the agentic fleet). |
| **Registration** | **Automatic** for agents and servers on supported Google Cloud runtimes once the API is enabled. Everything else is added **manually** through the writable **`Service`** resource, then queried through the read-only **`Agent`, `McpServer`, and `Endpoint`** resources. |
| **A2A skills vs. standalone skills** | **A2A skills** are declarative metadata declared inline in an agent's Agent Card. **Standalone skills** are separate resources managed, versioned, and listed through the **`Skill`, `SkillRevision`, and `Publisher`** resources. |
| **Agent Identifier vs. Agent Principal** | **Identifier** \= logical `urn:agent:...` used for inventory and lookup (**not used in IAM bindings**). **Principal** \= `principal://...` IAM identity (SPIFFE/service account) used for **permissions and auditing**. |
| **Registry MCP server tools** | **`list_agents`** for enumerating agents by project and location; **`search_agents`** for keyword/prefix/natural-language discovery. **`search_mcp_servers`** covers MCP servers only. |

* **Watch out for:** `"All registration is manual."` `"Only MCP servers can be registered."` Mixing up which resources are writable (`Service`) vs. read-only (`Agent`, `McpServer`, `Endpoint`). Swapping identifier and principal.

&nbsp;

### 

### 1.5 Agent identity and Agent Gateway

Every agent gets its own cryptographic identity, and traffic to and from agents is governed by a managed gateway. The classic scenario mixes a Google Cloud resource with a third-party SaaS app, and you need to know which identity is used for each.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **Agent Identity** | Each agent gets a **SPIFFE-based identity with an X.509 certificate**, assigned by Google Cloud. It's not shared and can't be impersonated. |
| **Google Cloud resources (e.g., BigQuery)** | The agent uses **its own identity**, governed by IAM. |
| **Third-party SaaS on the user's behalf** | **User-delegated 3-legged OAuth** through the **Agent Identity auth manager**. The token is issued by the **SaaS OAuth server**. |
| **Agent Gateway** | A fully managed component that governs agent traffic (**ingress and egress**), enforces access policies, and integrates with **Model Armor** to inspect tool calls and responses. **No app code changes are needed.** |

* **Watch out for:** `"An agent never holds its own credential."` `"One combined credential for both calls."` `"Agent Gateway only handles egress"` or `"only billing."` `"Gateway replaces Agent Identity."`

&nbsp;

### 

### 1.6 Protocols: MCP, A2A, and OpenTelemetry

MCP and A2A are complementary layers. MCP connects one agent to its tools and data; A2A lets independent agents discover each other and collaborate as peers. Several questions test the exact technical details of A2A and the enterprise features Google layers on top of MCP.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **MCP vs. A2A** | **MCP** \= agent ↔ tools, APIs, and data sources. **A2A** \= agent ↔ agent (discovery and peer collaboration to delegate work). |
| **A2A core technologies** | **HTTP, JSON-RPC 2.0, and Server-Sent Events (SSE)**, reusing existing web standards. |
| **Agent Card location** | `https://{server_domain}/.well-known/agent-card.json`, following **RFC 8615** well-known URIs (older versions used `/.well-known/agent.json`). |
| **MCP Toolbox for Databases** | Open-source MCP server for databases. It handles **connection pooling, authentication (IAM), and observability**, so you can add tools to an agent in **under 10 lines of code**. |
| **Google-managed MCP servers** | Add **MCP discovery (via Agent Registry)**, **IAM and VPC Service Controls governance**, **spec-compliant auth**, **Model Armor scanning**, and **tracing/audit-log observability**. |
| **OpenTelemetry `gen_ai.*` attributes** | Make GenAI telemetry **mean the same thing** across libraries, languages, and providers, enabling consistent cross-vendor observability. |

* **Watch out for:** The swapped-definition option (A2A for tools, MCP for agents). Exotic stacks (WebSockets/GraphQL/WebRTC, MQTT). `"OTel only standardizes names, not meanings."`

&nbsp;

### 

### 1.7 Model Armor *(Most Heavily Tested \#1)*

Model Armor screens prompts and responses for prompt injection and jailbreaks, harmful content, sensitive data, and malicious URLs. It's the most heavily tested topic, so know the configuration knobs, the rollout best practice, the limits, and where it plugs in.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **Floor settings** | Minimum requirements for all templates at an **org, folder, or project level**. Teams can't create a template less strict than the floor. |
| **Confidence levels** | **`HIGH`** flags only high-likelihood violations (**fewest false positives**). **`LOW_AND_ABOVE`** flags low, medium, and high (**strictest**). |
| **Recommended rollout** | Start in **Inspect only**, tune with test data, production monitoring, and user feedback, then switch to **Inspect and block**. Prompt injection/jailbreak filter typically starts at **Medium** (**High** for apps like Gemini Enterprise). |
| **SDP basic vs. advanced** | **Basic** uses a fixed set of predefined (mostly US) infoTypes and **only flags**. **Advanced** uses your own **SDP inspect template (required)** and **de-identify template (optional)**, so you get custom detectors and **redaction or tokenization**. |
| **File size limit** | Files and text over **4 MB** are **skipped, not blocked**, and **skipped data isn't billed**. |
| **Where it runs** | **Any cloud or on-prem via its REST API**, not just Google Cloud. |
| **Integrations** | **Apigee, Agent Gateway, Gemini Enterprise, Google and Google Cloud MCP servers, Cloud networking (Service Extensions), Agent Platform, and LangChain**. |
| **Always-on filter** | **CSAM** is applied by default; the other RAI categories (**hate speech, harassment, sexually explicit, dangerous**) have adjustable thresholds. |

* **Watch out for:** `"Deploy straight to Inspect and Block."` `"Oversized files are compressed or split."` `"Basic config does de-identification"` (it's the reverse). `"Only works on Google Cloud."`

&nbsp;

### 

### 1.8 CodeMender and Google AI Threat Defense

CodeMender is Google DeepMind's code-security agent: it finds vulnerabilities, verifies they're exploitable, and generates patches that a developer reviews. It's the remediation engine inside Google AI Threat Defense.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **AI Threat Defense stages** | Four: **Prepare, Scan and Prioritize, Remediate, Monitor**. CodeMender's `"fix"` work is in **Remediate** (generating patches, testing, committing with approval). |
| **Existing SAST tools** | CodeMender can **import external findings** and go straight to **verify and fix**, leaving the existing scanner in place. |
| **CLI commands** | `cm find`, `cm verify`, `cm fix`, `cm report` (and **`cm report import`** for external findings). |
| **Supported languages** | **C/C++, Go, Java, Python, Ruby, Rust, and TypeScript**. |
| **Model** | Defaults to a **Gemini Flash** model. Override with the **`--model` flag** and a supported model identifier. |

* **Watch out for:** `"CodeMender can only act on its own findings."` `"Must route through Security Command Center."` `"Model can only be changed via a support ticket."`

&nbsp;

### 

### 1.9 Gemini cost and capacity

These questions are about running Gemini economically: caching, reserved capacity, and routing between model tiers.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **Cache creation billing** | Tokens used to create a cache are billed at the **standard input price** for **both implicit and explicit caching**. |
| **Explicit vs. implicit caching** | **Explicit caching** also charges **storage** based on how long the cache is kept (TTL); **implicit caching has no storage cost**. Cached reads get about a **90% discount** on 2.5+ models. |
| **Minimum tokens for caching** | Varies by model (e.g., **Gemini 2.5 Flash 2,048**; **Gemini 3.x Flash 4,096** on the current Gemini API page). |
| **Provisioned Throughput limits** | **Doesn't support batch prediction**, and **doesn't cover calls made by other Agent Platform products (e.g., Agent Search)** even with the same model. **It does support fine-tuned models.** |
| **Semantic routing** | Send simple queries to the cheap tier (**Flash-Lite**) and complex ones to **Pro**: lower total spend without hurting quality where it matters. |

* **Watch out for:** `"Cache creation is free"` or `"double price."` `"Implicit caching has the storage cost."` `"Provisioned Throughput covers batch."`

&nbsp;

### 

### 1.10 Gemini Enterprise connectors and BigQuery multimodal

Two smaller topics that can also come up.

&nbsp;

| Concept | What to remember |
| :---- | :---- |
| **Federated connector second sign-in** | **Not a misconfiguration.** Federated connectors query Microsoft live with the user's delegated permissions, so SharePoint enforces that user's current ACLs (no stale cached index). |
| **BigQuery `ObjectRef`** | A **`STRUCT`** of **`uri`, `version`, `authorizer`** (the Cloud resource connection BigQuery uses to reach the object), and **`details`** (managed metadata: content type, size, hash, updated). |

* **Watch out for:** `"Deploying Workforce Identity Federation removes the second sign-in."` `"ObjectRef caches the object's bytes"` or `"is a signed URL."`

&nbsp;

### 

### 1.11 Last-minute review (10-Minute Self-Test Before Opening HackerRank)

If you only have ten minutes, make sure you can answer these without looking:

&nbsp;

| \# | Rapid-Fire Self-Test Question | Answer |
| :---- | :---- | :---- |
| **1** | What does an agent load at the start for each skill, and where do project skills live? | Only each skill's **name and description** (from `SKILL.md` YAML frontmatter); project skills live at **`<project-root>/.agents/skills/<skill>/`** (global: `~/.gemini/config/skills/`). |
| **2** | What makes a workflow agent different from an LLM agent? | A **workflow agent** (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) runs sub-agents using **predefined deterministic logic without consulting an AI model to orchestrate** (no model call for routing). |
| **3** | What are Agent Registry's three goals, and which of its resources are writable versus read-only? | **Goals:** (1) Accelerate development, (2) Simplify integration, (3) Support governance. **Writable:** `Service`. **Read-only:** `Agent`, `McpServer`, `Endpoint` (plus `Skill`, `SkillRevision`, `Publisher` for standalone skills). |
| **4** | Which identity does an agent use for BigQuery versus a third-party SaaS app? | **BigQuery (GCP resource):** the agent's **own SPIFFE identity** (governed by IAM). **Third-party SaaS on user's behalf:** **user-delegated 3-legged OAuth** via Agent Identity auth manager (token issued by the SaaS OAuth server). |
| **5** | What's the Model Armor rollout sequence, and what happens to a file over 4 MB? | Start in **Inspect only**, tune with test data/monitoring/feedback, then switch to **Inspect and block**. Files/text over **4 MB** are **skipped, not blocked, and not billed**. |
| **6** | Which stage of AI Threat Defense does CodeMender's fix belong to? | **Remediate** (Stage 3 of `Prepare -> Scan and Prioritize -> Remediate -> Monitor`). |
| **7** | Who pays storage costs, explicit or implicit caching? | **Explicit caching** pays TTL storage costs; **implicit caching has no storage cost** (both pay standard input token price for cache creation). |
| **8** | Where is an A2A Agent Card hosted, and what three technologies is A2A built on? | Hosted at **`https://{server_domain}/.well-known/agent-card.json`** (RFC 8615; older versions used `/.well-known/agent.json`); built on **HTTP, JSON-RPC 2.0, and Server-Sent Events (SSE)**. |

&nbsp;

## 

## 2\. Document Navigation (9-Tab Study Architecture)

Use the Google Docs left-hand **Document Tabs** sidebar to jump directly to each section:

1. **Tab 1 — Core Study Guide, Cheat Sheet & Reflexes (This Tab — HIGHEST PRIORITY):** The **10-Section Core Study Guide** (above), confirmed exam rules, essential links, the **22 Rapid-Reflex Triggers**, and **Core Numbers/Formulas/Hierarchies** for Part 1\.  
2. **Tab 2 — Study Guide: M3 & M2 (65% of Exam — HIGH PRIORITY):** Complete slide \+ doc deep-dive into **Module 3 (35%)** (ADK 2.0 Graph Engine, Callbacks, State Scopes, Eval, Harness Engineering, MCP Toolbox, `ObjectRef`, OTel, FinOps) and **Module 2 (30%)** (AI Threat Defense, CodeMender, Model Armor, Agent Registry, Agent Identity & Gateway).  
3. **Tab 3 — Study Guide: M1 & M0 (35% of Exam — MEDIUM PRIORITY):** Complete slide \+ doc deep-dive into **Module 1 (20%)** (Agent Skills standard, Context Engineering, App Mod, MCP vs Function Calling, AWS Migration, **Gemini Enterprise Identity & Federated Connectors**) and **Module 0 (15%)** (WAF Pillars, `google-agents-cli`, Multi-Agent Topologies, Runtime Substrates).  
4. **Tab 4 — \[Low Priority / Optional Ref\] Part 2: Lab Troubleshooting:** *(Deprioritize — the live Part 2 Cymbal Retail lab is painless and fully automatable using in-environment `agy` pointed at `/workspace/triage/briefs/TICKET-<n>.md`.)* Kept as a reference for the 15 course labs (`CEPF125`–`CEPF141`).  
5. **Tab 5 — \[Low Priority / Optional Ref\] Part 3: WAF & Code Blueprints:** *(Deprioritize — Part 3 Tasks 1 & 2 on RAISE allow AI assistance \[upload `.md`, not `.pdf`\!\], and Task 3 is automatable with in-environment `agy`.)* Kept as a reference for SDD rubrics and ADK/Model Armor code templates.  
6. **Tab 6 — 54-Q Drill Bank (M0–M3):** All 54 community trainer questions with full options, winning answers, explanations, and 34 inline `⚠️ Deck / Qwiklabs Ground Truth Note` callouts wherever the trainer diverges from official sources.  
7. **Tab 7 — Gap-Fill: Deck-by-Deck (M0–M3):** Cited key facts from all 25 slide decks with "Likely exam angles" at the end of each module.  
8. **Tab 8 — Question Bank (Original, 120 MCQs \+ Live Quiz):** 120 original deck-cited MCQs weighted toward M2/M3, plus the 6-item in-deck Antigravity-vs-Jetski Live Quiz.  
9. **Tab 9 — Run-of-Show, Official Samples & Beyond-Elevate:** Confirmed logistics, the 3 official Playbook sample questions keyed, RAISE portal tips, weekly support rooms & recording links, and summaries of `go/geap-agentic-blueprint`, `go/authoring-agent-skills`, `go/codemender-faqs`, and `go/elevate26-apigee-ai`.

&nbsp;

## 

## 3\. Assessment Structure, Confirmed Passing Bars & AI Tool Rules

&nbsp;

| Component | Prep Priority | Platform & Format | Passing Bar | Proctoring, AI Policy & Post-Exam Reality |
| :---- | :---- | :---- | :---- | :---- |
| **Part 1: Knowledge Check** | **🔥 HIGHEST PRIORITY (Study Section 1 Above\!)** | **HackerRank Secure Mode** — 30 single-choice MCQs, **60-minute timer** (`M3: 35%`, `M2: 30%`, `M1: 20%`, `M0: 15%`) | **90% (27 / 30\)** *(Officially confirmed Oct 6\)* | **STRICTLY CLOSED-BOOK & BROWSER-FOCUS MONITORED.** HackerRank Secure Mode tracks tab switching, window focus loss, and copy/paste (**no webcam/mic AI Proctor mode**; Chrome Incognito recommended). No notes, Gemini, or external AI allowed. |
| **Part 2: Troubleshooting Challenge Lab** | **🟢 Low Prep Priority (Painless & Automatable)** | **Labs for Sales (LfS)** — *Cymbal Retail: AI Agent Security Troubleshooting Lab* (3-hr timer, 5 tickets `#201`–`#205`, real-time console scoring) | **90 / 100** *(In-lab console score)* | **IN-ENVIRONMENT `agy` ALLOWED.** Only in-environment tools (e.g., `agy`) are permitted. In practice, it is very straightforward: point `agy` at `/workspace/triage/briefs/TICKET-<n>.md` and verify each ticket check turns green before clicking End Lab. |
| **Part 3A: Discovery & Solution Design (Tasks 1 & 2\)** | **🟢 Low Prep Priority (AI-Assisted)** | **RAISE Portal** (launched via `"Start Now"` on dashboard) — Task 1 Discovery (\~90m est.) \+ Task 2 SDD (\~90m est.), up to 2 attempts each | *Evaluated post-window* | **AI-ASSISTED (CE-OWNED).** **Upload `.md` files, NOT `.pdf`** (large PDFs fail parsing). Keep table cells **≤25 words**, set a sharp read-only MVP cut line for Phase 1, and include JSON Schema/Pydantic tool contracts \+ GCP billing labels in the SDD. Attempt 1 gives rubric feedback (\~10–25 min); Attempt 2 is final. |
| **Part 3B: End-to-End Build (Task 3\)** | **🟢 Low Prep Priority (Painless & Automatable)** | **Labs for Sales (LfS)** — *Autonomous Flight Operations & Disruption Resolution Agent* (6-hr timer, 25 automated checks) | **20 / 25 checks** *(80% in-lab score)* | **AI-ASSISTED (CE-OWNED).** Fully automatable inside the lab VM using `agy` (stop before Subtask 25's gateway teardown check until checks 1–24 are scored). **NEVER click "End Lab" early\!** |

* **Window & Submission Rules:** All 3 parts unlock independently on your personal dashboard (`go/elevate-capstone-reg`) at the start of your 48-hour regional window and can be taken in **any order** (**1 attempt per part** during your window, except RAISE Tasks 1 & 2 which give 1 feedback attempt \+ 1 final attempt). After submitting Part 1 on HackerRank, the dashboard button still says `"Start Now"`—that is normal as long as you receive the HackerRank confirmation email. Official pass/fail results go to **you and your manager 3–4 days** after the window closes. Passed components are **banked permanently**; retakes run the weeks of **Nov 2** and **Nov 9, 2026**.

&nbsp;

## 

## 4\. Essential Links, Simulators & Live Support

* **Capstone Portal & Dashboard (`go/elevate-capstone-reg`):** [https\://sites.google.com/corp/google.com/elevateai/capstone](https://sites.google.com/corp/google.com/elevateai/capstone) | Alias: [http\://go/elevate26-capstone](http://go/elevate26-capstone)  
* **Official "Elevate Knowledge Check \- How to Prepare" Doc (`contributor`, Oct 6):** [https\://docs.google.com/document/d/1JR1Oqinl1egsgKdVgkOKc7voSxBz8X1phT\_bC4EjWno/edit?resourcekey=0-\_0WR51D2j\_inR3YG8\_otmQ\&tab=t.0](#) (confirms 60 min, 30 Qs, 90% \= 27/30 pass bar, and 3 NotebookLM tutor prompts)  
* **Elevate Prework & Prerequisites (`go/elevate-prework`):** [https\://sites.google.com/corp/google.com/elevateai/prework](https://sites.google.com/corp/google.com/elevateai/prework)  
* **Official HackerRank Sample Test (1-Q UI familiarization):** [https\://www\.hackerrank.com/test-v2/ag2jlphjijk/login](https://www.hackerrank.com/test-v2/ag2jlphjijk/login)  
* **Live Support Rooms:** Week 1 (Oct 5): [https\://chat.google.com/room/AAQA8MNN3Vk?cls=7](#) | Week 2 (Oct 12): [https\://chat.google.com/room/AAQACjbNBbU?cls=7](#) | Week 3 (Oct 19): [https\://chat.google.com/room/AAQADkONaq8?cls=7](#) | Week 4 (Oct 26): [https\://chat.google.com/room/AAQASZk5yKo?cls=7](#) | Emails: `elevate-capstone-contributor`, `ce-elevate-contributor`  
* **Elevate Playbook (`go/elevate-playbook`):** [https\://docs.google.com/document/d/1uTRgnKCS8YZVXUGGkVg236ZLb2m6UxzSRMB3ayfMvGA/edit?resourcekey=0-GSA3bc8DWck7N1KHMf\_Q-w](#)  
* **Candidate FAQ (`go/elevate-capstone-faq`):** [https\://docs.google.com/document/d/1aBwqigDRZY2oJlRH2m\_2z7OusNxudwT6cQf63Lgzm3M/edit?resourcekey=0-0CnaC\_3pFs4MA364xRwzcw](#)  
* **Official Slide Decks Folder (`go/elevate-slides`):** [https\://drive.google.com/drive/folders/1iAfEumf-CU5uzIboRTfc1DnthokVvfQ2](#)  
* **Elevate Labs Course (`go/elevate-labs`):** [https\://explore.qwiklabs.com/course\_templates/1738435](https://explore.qwiklabs.com/course_templates/1738435)  
* **Pre-Loaded Elevate NotebookLM (`go/elevate-notebook`):** [https\://notebook.google.com/notebook/e1f5a08c-3a7c-459b-982a-59866cada04c](#)  
* **Peer-Sourced Tips (`go/beyond-elevate-links` & `go/beyond-elevate`):** [https\://docs.google.com/document/d/1baAR52E5zdZxQl5iPEq8Tb6AgNNU7PPxf20ucXSsC54/edit?resourcekey=0-TRQdEhpwOLMTRPK9e0BunQ](#) | Deck: [https\://docs.google.com/presentation/d/1sytHU6HPQO9lV9fE6cPbR1HuXHJhUZ2KlF1RWCfYqlw/edit?resourcekey=0-92dEW0la-\_Wm0pJ9UuFNEw](#)  
* **Community Simulators & Study Guides:**  
  * **`go/capstone-study` (`contributor`, MCQ study app grounded on Elevate slides)** & **`go/elevate-studyguide` (`contributor`, speaker-notes study guide)**  
  * **`go/elevate-capstone-hub` / `go/capstone-tutorial` (`contributor`, 210-Q bank & 180-Q Part 1 simulator):** [https\://shuklaankur.users.x20web.corp.google.com/www/elevate-capstone-tutorial/index.html](#) *(⚠️ v2.7.0 bug: its 18 M2S1 questions copied from Tab 8 were imported with answer `A`; use Tab 8's answer key.)*  
  * **`go/elevate-capstone-prep` (`contributor` Hacker Lab: 60 MCQs, 28 flashcards):** [https\://lukedyer.users.x20web.corp.google.com/www/elevate-capstone-prep/index.html](#) | Daily micro-coach (`go/elevate-edge`): [https\://lukedyer.users.x20web.corp.google.com/www/elevate-edge/index.html](#)  
  * **`go/study-4-elevate` (`contributor`: 50 MCQs, 40 flashcards, 5 module guides):** [https\://tuliani.users.x20web.corp.google.com/www/elevate-study-companion/index.html](#)  
  * **`go/elevate-quiz` (`contributor` Zipline practice quiz):** [https\://serve-dot-zipline.googleplex.com/asset/316b6e2e-640c-57f8-9958-e4e29fda512d](#)  
  * **`go/elevate-visual-tutorial` (`contributor` visual & narrated courseware):** [https\://prerakmehta.users.x20web.corp.google.com/elevate.html](#)  
  * **`go/elevate-capstone-trainer` (`contributor`, unofficial 54-Q simulator, see Tab 6):** [https\://thibaulthenry.users.x20web.corp.google.com/elevate-capstone-trainer/index.html](#)  
  * **Cloud Run Live Coaches:** `go/elevate-capstone-live-coach` (`contributor`): [https\://elevate-capstone-coach-650360736162.us-central1.run.app](https://elevate-capstone-coach-650360736162.us-central1.run.app) | Elevate Coach (`contributor`): [https\://elevate-coach-763419985448.us-central1.run.app/](https://elevate-coach-763419985448.us-central1.run.app/) | Elevate Ready Reckoner (`contributor`): [https\://elevate-ready-reckoner-712758616004.us-central1.run.app](https://elevate-ready-reckoner-712758616004.us-central1.run.app)

&nbsp;

## 

## 5\. The 22 Rapid-Reflex Exam Triggers ("If the Exam Says X → Answer Y")

&nbsp;

| \# | Module & Topic | If the Exam Scenario Mentions... (Trigger) | Immediate Correct Answer / Fix | Source / Slide Ref |
| :---- | :---- | :---- | :---- | :---- |
| **1** | **M0 • ADK Function Tools** | LLM never calls your Python tool (`tools=[my_fn]`), or asks how ADK builds the tool schema | ADK builds the tool schema from the function's **name, docstring, parameters, type hints, and default values** (docstring \= description; **parameters without defaults are required**). The model **never** sees the function body or `#` comments, and you do not hand-write JSON schemas. | `Core Guide §1.2; M0L6 Slides 6–7` |
| **2** | **M0 • Multi-Agent Routing** | Parent Coordinator/Orchestrator agent fails to delegate tasks to a specialist sub-agent | Sub-agent is missing a clear, specific `name` and `description` in `Agent(name=..., description=...)`. Use **workflow patterns** (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) when steps are predefined (no model call to route); use **agentic patterns** (coordinator) only when the model must decide the route. | `Core Guide §1.2; M0L7 Slides 15–16, 25` |
| **3** | **M0 • Workflows & ADK 2.0 Graphs** | Need deterministic orchestration without paying an LLM call for routing, or mixing node types in an ADK 2.0 graph | **`SequentialAgent` / `ParallelAgent` / `LoopAgent`** run sub-agents via predefined logic without consulting an AI model to orchestrate. **ADK 2.0 graphs** support 4 node types (**Functions, human input, Tools, LLM capabilities**) \+ **Join nodes** to merge parallel branches. Nodes set state via an `Event`'s `state` field (readable downstream); `output` passes data **only to the next node**. | `Core Guide §1.2; M0L7 Slides 10–12, 25; M3L1 Slide 9` |
| **4** | **M0 • Runtimes** | Customer wants \$0 compute cost when the agent sits idle overnight / on weekends | Deploy on **Cloud Run** (serverless container that scales to zero, so you pay nothing while idle). You supply the session service yourself: `--agent_engine_id` reuses Agent Runtime's managed sessions (`VertexAiSessionService`), or you run `DatabaseSessionService`. | `M0L9 Slides 7, 10, 15; M3L1 Slide 13` |
| **5** | **M0 • Runtimes & SessionService** | Customer wants managed durable sessions & Memory Bank out-of-the-box with zero container/infra management | Deploy on **Agent Runtime** (`adk deploy agent_engine`) — auto-created managed sessions (`VertexAiSessionService`, which loads/saves `Session` objects and applies `state_delta` from each event; other real implementations are `InMemorySessionService` and `DatabaseSessionService`—watch out for fake `TextEmbeddingService`), memory, ADK tool auth, observability, and automatic Agent Registry registration. | `Core Guide §1.2; M0L9 Slides 7, 10, 13; M3L1 Slide 10` |
| **6** | **M0 • Runtimes** | Workload needs custom networking, self-hosted open-source models not available on Vertex AI, or full Kubernetes control | Deploy on **GKE** — full control, custom networking, open models. Cost of control: "you are the DevOps team" (you run the containers, networking, scaling, and session infra). | `M0L9 Slides 6–7, 15` |
| **7** | **M0 • Compliance** | When to use **Jetski** (`go/jetski`) vs **Antigravity 2.0** (`agy`) | **Jetski** \= exclusively internal productivity (google3, Buganizer/Critique, day-to-day CE toil). NEVER show it to customers or screen-share with it open. **Antigravity 2.0** (Desktop App & CLI, authenticated via Argolis) \= customer-facing demos, safe for screen sharing and external 3P codebases. | `M0L5 Slides 6–8` |
| **8** | **M1 • Agent Skills & Context** | What is loaded at startup for a skill, where do skills live, and what causes context failures? | **Skills (`SKILL.md`, YAML frontmatter: `description` required, `name` optional \+ optional `scripts/`, `examples/`, `resources/`):** Only **name and description** load at startup; full `SKILL.md` loads when relevant (or via `/skill-name`), solving **"tool bloat"**. Workspace path: **`<project-root>/.agents/skills/<skill>/`**; Global path: **`~/.gemini/config/skills/`**. **Context failures:** **Observation flooding** (tool logs/file dumps/stack traces filling context) vs **Context collapse** (summarization deleting a needed fact) vs **Generic company answers** (fix with **RAG grounding** at query time). | `Core Guide §§1.1, 1.3; M1L1 Slides 8, 11; M1L2 Slide 13` |
| **9** | **M1 • AWS Migration** | The 4 Phases of the Google Cloud Migration Framework (in exact order) & Lambda → Cloud Run advantage | **`1. Assess -> 2. Plan & Build -> 3. Migrate -> 4. Optimize`**. AWS Lambda maps to **Cloud Run**: container-based (any language/framework), **up to 60-min timeout vs Lambda's 15-min limit**, and a concurrent-request model vs Lambda's per-invocation model. | `M1L5 Slides 3, 17–18` |
| **10** | **M1 • GE Federated Connectors** | Users see a **second sign-in prompt** when querying Microsoft SharePoint via a Gemini Enterprise Federated Connector | **Not a misconfiguration\!** Federated connectors query Microsoft live with the user's delegated permissions so SharePoint enforces that user's current ACLs (no stale cached index). Deploying Workforce Identity Federation (WIF) does **not** remove the second sign-in. | `Core Guide §1.10; M1L6 Slides 6, 10, 16` |
| **11** | **M2 • Threat Vectors & CodeMender** | Distinguish **Indirect Prompt Injection** vs **Tool Poisoning**, and how **CodeMender** works with existing SAST tools | **Indirect Prompt Injection** \= malicious instructions inside content the agent reads. **Tool Poisoning** \= compromised MCP servers/tools returning malicious outputs. **CodeMender** operates in **Stage 3 (`Remediate`)** of `Prepare -> Scan and Prioritize -> Remediate -> Monitor`, supports **7 languages** (`C/C++, Go, Java, Python, Ruby, Rust, TypeScript`), defaults to **Gemini Flash** (override with `--model`), and can **import external SAST findings** (`cm report import`) to go straight to `cm verify` and `cm fix`. | `Core Guide §1.8; M2S1 Slides 44, 47–53; M2S2 Slide 5` |
| **12** | **M2 • Model Armor** | Model Armor **Floor Settings**, **Confidence Levels**, **Rollout Sequence**, **SDP Basic vs Advanced**, and **4 MB File Limit** | **Floor settings:** org, folder, or project minimum requirements (templates can't be less strict). **Confidence:** `HIGH` \= fewest false positives; `LOW_AND_ABOVE` \= strictest. **Rollout:** start in **Inspect only**, tune, then **Inspect and block** (PI/jailbreak starts at Medium, High for GE). **SDP:** Basic \= predefined US infoTypes, **only flags**; Advanced \= custom **inspect template (required)** \+ **de-identify template (optional)** for redaction/tokenization. **Over 4 MB:** **skipped, not blocked, and not billed**. Runs on **any cloud or on-prem via REST API**; **CSAM** is always on by default. | `Core Guide §1.7; M2S2 Slides 38–51` |
| **13** | **M2 • Agent Registry Goals & IDs** | What are **Agent Registry's 3 goals**, `urn:agent:...` vs `principal://...`, A2A vs standalone skills, and Registry MCP tools? | **3 Goals:** **Accelerate development** (discovery/reuse), **Simplify integration** (standardized MCP & A2A), **Support governance** (fleet boundaries). **Identifier** (`urn:agent:...`) \= logical catalog lookup (**not used in IAM**); **Principal** (`principal://...`) \= SPIFFE/SA IAM identity for permissions & auditing. **A2A skills** \= inline in Agent Card; **Standalone skills** \= `Skill`, `SkillRevision`, `Publisher` resources. **Registry MCP tools:** `list_agents`, `search_agents`, `search_mcp_servers` (MCP only). | `Core Guide §1.4; M2S2 Slides 15–20` |
| **14** | **M2 • Agent Registry Registration** | How does **Agent Registry** separate Write vs Read operations, and how do agents get registered? | **Automatic** for agents/servers on supported GCP runtimes (Agent Runtime, Workspace/GE, annotated GKE, Google remote MCP servers) once the API is enabled. Everything else (e.g., Cloud Run) is registered **manually** via the writable **`Service`** resource, then queried via read-only **`Agent`, `McpServer`, and `Endpoint`** resources. | `Core Guide §1.4; M2S2 Slides 15–16, 20` |
| **15** | **M2 • Agent Identity & Gateway** | Agent calls **BigQuery** (GCP) AND a **3P SaaS API** (e.g., Zendesk/ Jira) on the user's behalf, governed by **Agent Gateway** | Each agent gets an unshared **SPIFFE X.509 identity**. For **GCP resources (BigQuery)**, the agent uses **its own identity** (IAM). For **3P SaaS on the user's behalf**, it uses **user-delegated 3-legged OAuth** via the **Agent Identity auth manager** (token issued by the SaaS OAuth server). **Agent Gateway** governs **both ingress and egress**, enforces access policies, and integrates with **Model Armor** with **no app code changes**. | `Core Guide §1.5; M2S2 Slides 24–29` |
| **16** | **M3 • Protocols (MCP & A2A)** | Distinguish **MCP vs A2A**, A2A's **3 core technologies**, and the **Agent Card URI** | **MCP** \= agent ↔ tools, APIs, data sources. **A2A** \= agent ↔ agent (peer discovery & delegation), built on **HTTP, JSON-RPC 2.0, and Server-Sent Events (SSE)**. Agent Card URI: **`https://{server_domain}/.well-known/agent-card.json`** per **RFC 8615** (older versions/slides used `/.well-known/agent.json`). | `Core Guide §1.6; M3L1 Slides 31–32` |
| **17** | **M3 • ADK 2.0 Callbacks & State** | How does `before_tool_callback` ALLOW vs BLOCK a tool call, and how do state prefixes work? | Return **`None`** to **ALLOW** normal tool execution; return a **`dict`** to **BLOCK/SHORT-CIRCUIT** the tool and return that dict to the LLM. State scopes: unprefixed (current session), `user:` (across sessions for user), `app:` (global across users), `temp:` (cleared after invocation). | `M3L1 Slides 10, 14–19` |
| **18** | **M3 • Evaluation** | Why passing unit tests / final-response evaluation isn't enough \+ the 7 Coding Agent Eval Dimensions | **Final-response evaluation** checks only the output and misses `"right answer, wrong process"`; **Trajectory evaluation** grades the path (reasoning \+ sequence of tool calls, e.g., did it read the file before editing it?). In the 7 Coding Eval Dimensions: **Dim 1 \= Intent Satisfaction**, **Dim 7 \= Self-Repair Behaviour**. | `Core Guide §1.3; M3L2 Slides 15–16, 19, 23` |
| **19** | **M3 • Harness Eng** | Formula, Author, and Terminal Bench 2.0 empirical proof of **Harness Engineering** | **`Agent = Model + Harness`** (Vivek Trivedy, LangChain, Mar 2026; term coined by **Mitchell Hashimoto**, Feb 2026). On **Terminal Bench 2.0**, LangChain changed ONLY the harness (self-verification loops \+ better context injection) and the same model jumped from **\#30 (52.8%) to \#5 (66.5%) (+13.7 pts)**. | `M3L3 Slides 2–3, 5` |
| **20** | **M3 • BigQuery `ObjectRef` & MCP Toolbox** | What is inside a BigQuery **`ObjectRef`**, and what does **MCP Toolbox for Databases** handle? | **`ObjectRef`** is a `STRUCT` of **`uri`, `version`, `authorizer`** (the Cloud resource connection BigQuery uses to reach the object), and **`details`** (managed metadata: content type, size, hash, updated)—it does **not** cache bytes and is **not** a signed URL. **MCP Toolbox for Databases** is Google's open-source DB MCP server handling **connection pooling, IAM auth, and observability in under 10 lines of code**. | `Core Guide §§1.6, 1.10; M3L4 Slides 14, 20` |
| **21** | **M3 • OpenTelemetry** | What do **`gen_ai.*` attributes** standardize, and what is the 4-level OTel hierarchy from SMALLEST to LARGEST? | `gen_ai.*` attributes standardize **both names and meanings** across libraries, languages, and providers for cross-vendor observability. Hierarchy: **`1. SPAN`** (1 atomic call) `<` **`2. TRACE`** (1 turn) `<` **`3. SESSION`** (multi-turn conversation) `<` **`4. TASK`** (multi-agent workflow; proposed). | `Core Guide §1.6; M3L5 Slides 8–9` |
| **22** | **M3 • Gemini Cost & Capacity** | **Cache creation billing**, **Explicit vs Implicit storage cost**, **Min tokens**, and **Provisioned Throughput limits** | **Cache creation** is billed at the **standard input price** for **both** implicit and explicit caching. **Explicit caching** charges **TTL storage**; **implicit caching has no storage cost** (\~**90% read discount** on Gemini 2.5+). **Min tokens:** Gemini 2.5 Flash \= **2,048**; Gemini 3.x Flash \= **4,096**. **Provisioned Throughput** does **not** support batch prediction and does **not** cover calls from other Agent Platform products (e.g., Agent Search), though it **does** support fine-tuned models. | `Core Guide §1.9; M3L5 Slides 14–19` |

&nbsp;

## 

## 6\. Core Numbers, Formulas & Hierarchies to Memorize Cold

### 6.1 OpenTelemetry (OTel) 4-Level Hierarchy (Smallest → Largest) (`M3L5` Slides 8–10 & Core Guide §1.6)

* **1\. `SPAN` (Smallest):** A single atomic operation (1 agent invocation, 1 LLM call, or 1 tool call).  
* **2\. `TRACE`:** A single end-to-end user-to-agent turn (all spans for that turn; traces are trees, spans are the nodes).  
* **3\. `SESSION`:** A multi-turn conversation spanning multiple Traces.  
* **4\. `TASK` (Largest):** A background task/workflow orchestrating multiple agents, possibly spanning multiple sessions (proposed, not yet finalized).  
* **Vendor-Neutral OTel GenAI Semantic Attributes (`gen_ai.*`, M3L5 Slide 8):** Make GenAI telemetry **mean the same thing** (both names and semantic meanings) across libraries, languages, and providers (`gen_ai.agent.id`, `gen_ai.conversation.id`, `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.input.messages`, `gen_ai.output.messages`).

### 6.2 Gemini Cost, Caching & FinOps Tiers (`Core Guide §1.9` & `M3L5` Slides 14–19)

* **Context Caching Rules (High Exam Yield):**  
  * **Cache creation billing:** Billed at the **standard input token price** for **both implicit and explicit caching** (neither free nor double price).  
  * **Storage billing:** **Explicit caching** charges **storage based on TTL** (default 60 min); **implicit caching has no storage cost**.  
  * **Cached read discount:** \~**90% discount** on Gemini 2.5+ models (75% on Gemini 2.0).  
  * **Minimum token threshold:** Varies by model — **Gemini 2.5 Flash \= 2,048 tokens**; **Gemini 3.x Flash \= 4,096 tokens**.  
* **Provisioned Throughput (PT) Rules:**  
  * Reserved capacity with an SLA for steady-state baseline traffic; **supports fine-tuned models**.  
  * **Limits:** Does **NOT** support batch prediction, and does **NOT** cover calls made by other Agent Platform products (e.g., Agent Search) even when using the same model.  
* **5 Consumption Tiers (`M3L5` Slide 15):** `1. Provisioned Throughput` (reserved SLA baseline), `2. Standard PayGo` (default variable traffic & spillover), `3. Priority PayGo` (premium per-token for consistent burst performance), `4. Flex PayGo` (discounted latency-tolerant traffic), `5. Batch Inference` (**50% discount** for async workloads).  
* **Semantic Routing:** Route simple queries to **Flash-Lite** and complex queries to **Pro** (**`3x` cost gap** between Pro and Flash-Lite; routing 40% of traffic to Flash-Lite delivers substantial savings without hurting quality).

### 6.3 Harness Engineering Formula & 6 Landmark Proof Points (`M3L3`)

* **Core Formula:** `Agent = Model + Harness` (Vivek Trivedy, LangChain, March 2026; term **"Harness Engineering"** coined by **Mitchell Hashimoto**, Feb 2026).  
* **Evolution Timeline:** `Prompt Engineering (2022–23) -> Context Engineering (2024–25) -> Harness Engineering (2026)`.  
* **6 Landmark Teams / Proof Points (`M3L3` Slides 3–5, 12 — "Six teams. One discipline."):**  
1. **LangChain on Terminal Bench 2.0:** Same model jumped from **Rank \#30 (52.8%) to Rank \#5 (66.5%) (+13.7 points)** purely by changing the harness (self-verification loops \+ better context injection).  
2. **OpenAI \+ Codex:** 3 engineers, 5 months, \~1M lines of production code with **0 manually written lines** (engineers built the harness).  
3. **Anthropic 3-Agent Harness:** Planner \+ Generator \+ Evaluator built a polished 2D game engine in 6 hours vs. a non-functional 20-min solo prototype.  
4. **Google ADK Kotlin Port:** 4 engineers (3 EPE \+ 1 Cloud) generated **57,000+ LoC in 2 months** (125,000+ lines changed across the codebase) with **35% test coverage** (Slide 3; Slide 12 also states **\~35% of the codebase is tests**).  
5. **Claude Code (`M3L3` Slides 3, 5):** `CLAUDE.md` \= context & intent, `PreToolUse` hooks \= deterministic enforcement, MCP config \= tool extension (*"the most programmable harness surface available today"*).  
6. **Google Antigravity (`M3L3` Slides 3, 5):** *"One harness, four surfaces"* — `1. IDE`, `2. CLI (agy)`, `3. SDK`, `4. Agent Manager`.

### 6.4 Offensive AI Threat Metrics, CodeMender & Security Gates (`Core Guide §§1.7–1.8`, `M2S1` & `M2S2`)

* **4-Stage AI Threat Defense Framework (`M2S1` Slide 44):** **`01. Prepare -> 02. Scan and prioritize -> 03. Remediate -> 04. Monitor`** (**CodeMender's fix work is in `03. Remediate`**).  
* **CodeMender Essentials (`Core Guide §1.8` & `M2S1` Slides 47–53):**  
  * **Existing SAST integration:** Imports external findings (`cm report import`) and goes straight to **verify and fix**, leaving your existing scanner in place.  
  * **CLI commands:** `cm find`, `cm verify`, `cm fix`, `cm report`, `cm report import`.  
  * **7 Supported languages:** **C/C++, Go, Java, Python, Ruby, Rust, and TypeScript**.  
  * **Default model:** Defaults to a **Gemini Flash** model; override with `--model <identifier>`.  
* **Offensive AI Scale Numbers (`M2S1` Slides 18, 41–43):** **`10x` Faster Recon**, **`85%` CVE Coverage** (working PoC exploits from CVE descriptions), **`~0` Human Oversight**; **`1.6 Days`** Time-to-Exploit (down from **`1.3 Years`** in 2020), **`60,000+`** annual CVEs (**`3x`** growth), **`6 Hours`** post-"React 2 Shell" CVE, **`32%`** of intrusions from vulnerabilities, **`<30 seconds`** autonomous stage handoffs vs. **`20–70 days`** human remediation timelines.  
* **Secure Agentic TDD Lab (`M2S1` Slides 60–62):** `1. CONTEXT.md workspace rules` → `2. Custom Semgrep rule` → `3. Git pre-commit hook blocks an injected mock credential` → `4. Antigravity agent analyzes the error and self-corrects the code`.

### 6.5 Coding Agent Evaluation: 7 Dimensions & 8 Methods (`M3L2` & `Core Guide §1.3`)

* **7 Dimensions (`M3L2` Slide 15 — 2 groups \+ transversal safety layer):** **User-Facing (Outside):** `1. Intent Satisfaction` | `2. Functional Correctness` | `3. Visual / Behavioural` | `4. Cost & Efficiency` — **Internal (Inside):** `5. Code Quality & Conventions` | `6. Trajectory Quality` | `7. Self-Repair Behaviour` — plus **Safety & Responsible AI (transversal)**.  
* **8 Methods (`M3L2` Slides 20, 23, 25):** 1\) Standardised Benchmarks, 2\) Automated Functional Testing, 3\) Security & Safety Evaluation, 4\) LLM / Agent-as-Judge, 5\) Browser-Based Testing, 6\) **Trajectory Inspection** (grades the reasoning path and sequence of tool calls, e.g., did it read the file before editing it?), 7\) Human Review, 8\) Online Evaluation. **Observability is the prerequisite** for all evaluation (`M3L2` Slide 25).

### 6.6 Multi-Cloud & Lifecycle Sequences (`M0L3`, `M1L1`, `M1L2`, `M1L5`)

* **`google-agents-cli` 8 Stages (`M0L3` Slide 63):** `Spec -> Scaffold -> Build -> Orchestrate -> Evaluate -> Deploy -> Publish -> Observe`.  
* **4 Context Window Budget Segments (`M1L2` Slide 6):** `1. System Prompt` \+ `2. Tools & Retrieved Context` \+ `3. Conversation History` \+ `4. Free / Working Budget`.  
* **5 Skill Patterns (`M1L1` Slide 7):** `Informational` (context for an environment/task), `Tool Wrapper` (how to use an existing tool/CLI), `Generator` (content of a specific type/format), `Reviewer` (criteria to assess work), `Workflow` (repeatable multi-step sequence).  
* **4-Phase AWS to GCP Migration Framework (`M1L5` Slide 3):** `1. Assess -> 2. Plan & Build -> 3. Migrate -> 4. Optimize`.  
  * **Look-Alike `M1L5` Sequence Trap (`s3` vs `s22` vs `s26`):** Don't confuse the **4-Phase Migration Framework** (`Assess -> Plan & Build -> Migrate -> Optimize`, `s3`) with the **5-Step Migration Center Journey** (`Estimate -> Discover -> Assess -> Plan -> Migrate`, `s22`) or the **4-Step Sprint-Based Execution Cycle per Wave** (`Assess -> Plan -> Deploy -> Optimize`, `s26`).

&nbsp;