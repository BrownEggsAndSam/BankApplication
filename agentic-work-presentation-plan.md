# From AI Buzzwords to Better Work

## Presentation blueprint for a nontechnical business audience

**Recommended subtitle:** How agents, skills, and harnesses can reduce rework, bridge technical gaps, and scale data-governance expertise

**Recommended length:** 45 minutes total: 40 minutes of content and 5 minutes for discussion

**Primary audience:** Business-facing data-governance associates, stewards, product owners, and leaders who understand the work but do not consider themselves technical

---

## 1. Executive direction

This presentation should not try to teach Python, PowerShell, HTML, databases, or AI architecture. Its job is to help a business audience recognize where agentic work fits into an ordinary workday.

The central idea is:

> Business users do not need to become software developers. They need to become effective designers, reviewers, and owners of agent-enabled work.

The presentation should bridge three gaps:

1. **The language gap:** Enterprise initiatives are discussed through terms such as agents, personas, data quality, metrics, and automation, but employees do not know what those terms mean for their own work.
2. **The execution gap:** Business teams know the rules and desired outcomes, while technical teams need clear requirements, examples, and acceptance criteria.
3. **The adoption gap:** People may see impressive demonstrations without knowing what they are allowed to try, who will support them, or how an experiment becomes an approved capability.

The four case studies should prove that agents can help close these gaps while the business owner remains accountable for context, judgment, and approval.

### The one-sentence promise to the audience

> By the end of this session, you will be able to identify one part of your work that an agent could help with, describe the skill it would need, and recognize the controls required to use it safely.

### What the audience should leave understanding

- What an **agent**, **skill**, and **harness** mean in plain language.
- Why an agent is more useful than a one-time chatbot response when work involves several steps or tools.
- How business knowledge becomes the rules and examples that make an agent useful.
- How to recognize good candidates for agent assistance.
- Why AI output still requires human judgment and verification.
- What support path exists if they want to test an idea after the presentation.

---

## 2. Recommended title options

### Recommended

**From AI Buzzwords to Better Work**  
*Thinking Agentically in Data Governance*

This title starts with the audience's frustration and promises a practical outcome.

### Alternatives

- **You Do Not Need to Be a Developer to Work Agentically**
- **Agents at Work: Turning Governance Expertise into Repeatable Workflows**
- **From Business Knowledge to Agent-Enabled Work**
- **Where Does an Agent Fit in My Workday?**

Avoid titles that sound like a technical architecture review or imply that people will be replaced.

---

## 3. Narrative spine

The presentation should feel like one story rather than four unrelated demonstrations.

### Act 1 — The problem

The enterprise is moving quickly, but many business users hear initiative names and AI terminology without seeing a connection to their daily work. At the same time, poorly directed AI can produce "workslop": polished-looking output that creates more verification and cleanup for someone else.

### Act 2 — The mental model

Introduce only three concepts:

| Concept | Plain-language definition | Workplace analogy |
| --- | --- | --- |
| **Agent** | An AI worker that can pursue a goal across several steps and use approved tools, while remaining under human oversight. | A capable analyst |
| **Skill** | Reusable instructions, rules, examples, and domain knowledge for performing one kind of task well. | The analyst's playbook or SOP |
| **Harness** | The controlled workspace that gives the agent its tools, context, permissions, limits, and review points. | The analyst's workstation, access, and guardrails |

The audience does not need deeper architecture for the main presentation. If the organization uses slightly different definitions, adjust the labels while preserving this mental model.

### Act 3 — Proof through familiar work

Use four case studies spanning email triage, requirement translation, live-data analysis, and rationalization. Every case follows the same structure:

1. The business problem.
2. What the agent is asked to accomplish.
3. The skill or domain knowledge it needs.
4. The tools and boundaries supplied by the harness.
5. The human review point.
6. The resulting business value.

### Act 4 — Safe adoption

End with a realistic adoption loop:

> **Find a small task → sandbox it → verify the result → tune it → package what works → reuse it → scale only with approval**

The closing message is not “race to put AI into production.” It is:

> **Prototype quickly. Productionize deliberately. Learn faster than the problem changes.**

---

## 4. Forty-five-minute run of show

| Time | Section | Purpose |
| --- | --- | --- |
| 0:00–0:03 | Opening and audience hook | Make the topic about their workday, not AI theory. |
| 0:03–0:06 | Buzzwords versus useful work | Name the current disconnect and introduce workslop. |
| 0:06–0:12 | Agent, skill, and harness | Give the audience one durable mental model. |
| 0:12–0:14 | The agentic workflow | Show where the human remains involved. |
| 0:14–0:19 | Case 1: Outlook to governed draft | Demonstrate orchestration and routing. |
| 0:19–0:24 | Case 2: EDG Scorecard prototype | Demonstrate requirement translation and iteration. |
| 0:24–0:29 | Case 3: Database comparison | Demonstrate grounded, reproducible analysis. |
| 0:29–0:34 | Case 4: Rationalization skill | Demonstrate reusable domain expertise. |
| 0:34–0:36 | What all four cases share | Reinforce the transferable pattern. |
| 0:36–0:39 | Safe experimentation | Explain controls without turning the session into compliance training. |
| 0:39–0:40 | Call to action and support path | Give the audience one concrete next step. |
| 0:40–0:45 | Questions and discussion | Ask participants to name candidate workflows. |

If questions are expected throughout, reserve only three minutes at the end and enforce a strict five-minute maximum for each case study.

---

## 5. Slide-by-slide plan

### Slide 1 — From AI Buzzwords to Better Work

**Time:** 1 minute

**Purpose:** Establish that the session is practical and designed for nontechnical business users.

**On-slide message:**

> How agents, skills, and harnesses can reduce rework and scale our governance expertise

**Suggested visual:** A bridge connecting “business expertise” to “repeatable, governed execution.” Do not open with a robot image or a wall of enterprise initiative logos.

**Speaker cue:**

> “This is not a coding lesson. It is a way to recognize where an agent could help in the work you already understand better than anyone else.”

---

### Slide 2 — Where Does an Agent Fit in My Tuesday Morning?

**Time:** 2 minutes

**Purpose:** Translate the topic from enterprise strategy to ordinary work.

**On-slide examples:**

- Finding and interpreting the right email.
- Turning a business need into a technical story.
- Comparing information across systems.
- Applying the same rationalization rules repeatedly.

**Suggested visual:** A simple workday with four recurring friction points. Keep the examples recognizable and avoid product architecture.

**Speaker cue:**

> “The useful question is not, ‘What can AI do?’ The useful question is, ‘Where am I repeatedly spending time finding context, translating intent, comparing information, or applying the same rules?’”

---

### Slide 3 — AI Can Remove Busywork—or Create More of It

**Time:** 3 minutes

**Purpose:** Address AI slop early and establish credibility.

**Define workslop:** AI-generated work that appears complete but lacks the context, validation, or ownership needed to be useful, shifting the cleanup burden to another person.

**On-slide contrast:**

| Workslop | Useful agent-enabled work |
| --- | --- |
| Vague request | Clear outcome and context |
| Polished but ungrounded answer | Output based on approved sources |
| No acceptance criteria | Defined tests for “good” |
| Forwarded without review | Human verifies and owns the result |

**Key line:**

> AI does not remove accountability. It moves more of our effort from first-draft creation to direction, judgment, and verification.

Use “workslop” on the slide if that fits the culture; keep “AI slop” as an informal speaker phrase rather than the formal heading.

---

### Slide 4 — The Role of the Business Expert Is Changing

**Time:** 2 minutes

**Purpose:** Remove the fear that technical syntax is the price of admission.

**On-slide message:**

> You do not have to write every line of code. You do have to define the outcome, provide the rules, recognize a bad result, and approve what happens next.

**Four responsibilities:**

- **Direct:** State the outcome and relevant context.
- **Teach:** Supply business rules, examples, and exceptions.
- **Verify:** Check facts, logic, and edge cases.
- **Own:** Approve the final action or escalate uncertainty.

**Important nuance:** A script generated from a plain-English request is still code. The easier creation method does not remove the need for safe execution and technical review when consequences are meaningful.

---

### Slide 5 — Three Concepts Are Enough to Get Started

**Time:** 4 minutes

**Purpose:** Explain agent, skill, and harness using one recurring analogy.

**Suggested visual:** Three connected cards:

1. **Agent = capable analyst** — reasons through the assignment.
2. **Skill = playbook** — describes how this organization performs the task.
3. **Harness = controlled workstation** — supplies approved tools, data, permissions, and checkpoints.

**Example:**

> A general agent may know how to compare two lists. A rationalization skill teaches it our matching criteria, exception rules, and desired output. The harness determines which systems it may read, which actions it may take, and where a person must approve the result.

**Optional clarification:** A chatbot generally answers a prompt. An agent can carry a goal through multiple steps, use tools, evaluate intermediate results, and return a completed draft or analysis.

---

### Slide 6 — What Agentic Work Actually Looks Like

**Time:** 2 minutes

**Purpose:** Show the common workflow and human checkpoints before the examples.

**Suggested flow:**

> Business goal → Approved context → Agent applies a skill → Approved tool or system → Draft/analysis → Human verifies → Human sends, changes, or deploys

**Place a human checkpoint in three locations:**

- **Before:** Is the request, data, and access appropriate?
- **During:** Does the logic and evidence make sense?
- **After:** Should this output be sent, changed, or used for a decision?

This slide becomes the reference point for all four cases.

---

### Slides 7–8 — Case 1: From Outlook Email to a Governed Draft

**Time:** 5 minutes total

#### Business problem

Relevant requests arrive through email. The user must find the message, infer its intent, identify the correct governance domain, locate the relevant guidance, and draft a response. Much of the time is spent switching contexts rather than making the final decision.

#### Proposed workflow

> Approved Outlook folder/sender filter → PowerShell retrieves the message → Agent extracts intent → Routes to the appropriate Ask Genie persona or domain skill → ICR/EDQ guidance is applied → Draft response is produced → Human reviews and sends

#### Agent, skill, and harness

| Element | In this case |
| --- | --- |
| Agent | Coordinates the steps and creates the draft. |
| Skill | Email interpretation, domain routing, and response-drafting rules. |
| Harness | Approved Outlook access, PowerShell or another approved connector, Ask Genie/domain access, sender restrictions, and no automatic sending. |

#### What to show

Use a sanitized, staged example rather than a live inbox:

1. A sample email from an approved sender.
2. A small annotated image of the filter or script—not a full code walkthrough.
3. The identified domain and source used.
4. The draft response with the human review checkpoint highlighted.

#### Business value to describe

- Less time searching and switching systems.
- More consistent routing to ICR, EDQ, or another governance domain.
- Faster first drafts grounded in the correct guidance.
- Human ownership retained because the agent does not send the message.

#### Measures to collect later

- Average handling time before and after.
- Routing accuracy.
- Percentage of the draft changed before sending.
- Number of systems manually opened per request.

#### Boundary to state clearly

The demonstration does not establish that all users may connect an agent to Outlook or run PowerShell locally. Access, data handling, and execution must follow the approved enterprise path.

**Transition:**

> “That example starts with an incoming request. The next starts with an idea that is still too ambiguous for a technical team to build.”

---

### Slides 9–10 — Case 2: From EDG Scorecard Requirement to Shared Prototype

**Time:** 5 minutes total

#### Business problem

A business owner knows what the EDG Scorecard should accomplish but may describe it through scattered rules, exceptions, screenshots, and examples. The technical team receives an incomplete story, asks follow-up questions, and may build something different from what the business envisioned.

#### Proposed workflow

> Raw business explanation → Agent identifies ambiguity and asks questions → Requirement is converted into user stories, rules, and acceptance criteria → Agent creates a disposable prototype → Business owner reviews it → Prompt and prototype are tuned → Validated package is handed to the technical team

#### What to show

Use three screenshots with large numbered callouts:

1. **The original prompt:** imperfect and conversational.
2. **The agent's clarification/tuning loop:** what was wrong or incomplete and how you corrected it.
3. **The prototype and requirements package:** what the technical team can now react to.

Avoid presenting the first output as magic. The most important part is the revision trail showing your judgment.

#### Agent, skill, and harness

| Element | In this case |
| --- | --- |
| Agent | Converts the need into structured requirements and a prototype. |
| Skill | Requirement elicitation, user-story formatting, scorecard logic, and acceptance-criteria generation. |
| Harness | Approved coding/prototyping environment, supplied examples, test data, and clear separation from production. |

#### Core lesson

> The prototype is a communication artifact, not a production application.

Its value is that business and technology can point to the same visible behavior before significant development begins.

#### Measures to collect later

- Number of requirement clarification cycles.
- Time from idea to an agreed story.
- Defects caused by misunderstood requirements.
- Percentage of acceptance criteria retained in implementation.

**Transition:**

> “The first two cases help us find and translate work. The third asks the agent to help investigate a live business question using approved data.”

---

### Slides 11–12 — Case 3: Comparing What Is in the Database with What Producers Vend

**Time:** 5 minutes total

#### Business problem

During the database issue or modernization effort, the technical team needs the business team to verify what actually exists in the database versus what producers are vending. Manually gathering and comparing the information is slow, and the result can become stale or difficult to reproduce.

#### Proposed workflow

> Plain-language business question → Agent creates a query/analysis plan → Approved read-only PostgreSQL call retrieves current information → Results are compared with producer-vended records → Differences and exceptions are summarized → Domain owner verifies the findings

Potential examples include Collibra datasets, glossary entries, or another work-domain object. Use one narrow example in the presentation rather than discussing every possible object.

#### Agent, skill, and harness

| Element | In this case |
| --- | --- |
| Agent | Plans the analysis, invokes the approved read-only query, and explains discrepancies. |
| Skill | Knowledge of schemas, object definitions, comparison logic, and how to present exceptions. |
| Harness | Read-only database connection, approved credentials handling, query limits, auditability, and no write/delete privileges. |

#### What to show

1. The business question in plain language.
2. A simple “database versus producer” comparison table.
3. One discrepancy and the evidence supporting it.
4. The human validation step before the result is treated as a finding.

Do not make SQL the centerpiece. If code is shown, annotate only the one or two lines that demonstrate scope and read-only behavior.

#### Measures to collect later

- Time required to perform a reconciliation.
- Number of records or exceptions reviewed.
- Reproducibility of the query and comparison.
- False-positive rate after domain review.

#### Boundary to state clearly

The agent should not receive unrestricted credentials, improvise against unknown production structures, or alter the database. Generated queries must be scoped, reviewable, and executed only through an approved read-only path.

**Transition:**

> “This worked because the agent had access to a specific analysis method. The final example shows how that method can become a reusable business capability instead of a one-off conversation.”

---

### Slides 13–14 — Case 4: Rationalization as a Reusable Skill

**Time:** 5 minutes total

#### Business problem

Rationalization work is repeated across Knowledge Explorer, Collibra, spreadsheets, and other sources. The business team repeatedly applies similar matching logic, definitions, exception rules, and review decisions. When that knowledge stays in individual heads or one-time prompts, the work is hard to scale and inconsistent.

#### Proposed workflow

> Approved source records → Rationalization skill applies documented rules → Potential duplicates or conflicts are scored → Exceptions are placed in a review queue → Steward decides retain/merge/retire/escalate → Decision and rationale are recorded

#### What becomes the skill

- The definition of a potential match.
- Normalization and comparison rules.
- Thresholds or confidence bands.
- Known exceptions and protected terms.
- Required evidence.
- Allowed recommendations.
- Output format and reviewer instructions.

#### What the harness supplies

- Approved access to source systems or exported data.
- Limits on which domains and records may be processed.
- Versioned rules and examples.
- A review queue rather than automatic destructive action.
- Audit records showing the recommendation, evidence, and decision.

#### Core lesson

> A successful prompt helps once. A well-designed skill helps repeatedly. A controlled harness makes that skill usable by more people.

#### Measures to collect later

- Time per rationalization batch.
- Reviewer agreement with recommendations.
- False-match and missed-match rates.
- Backlog reduction.
- Consistency across reviewers or domains.

#### Boundary to state clearly

The agent may identify and explain candidates. A steward or authorized owner should make consequential merge, retire, or deletion decisions.

---

### Slide 15 — Four Different Cases, One Repeatable Pattern

**Time:** 2 minutes

**Purpose:** Prevent the audience from treating the examples as solutions only you can use.

| Pattern | Email | Scorecard | Database comparison | Rationalization |
| --- | --- | --- | --- | --- |
| Trigger | Incoming request | Business need | Investigation question | Record batch/backlog |
| Skill | Route and draft | Clarify and prototype | Query and reconcile | Normalize and compare |
| Tool | Outlook/Ask Genie | Prototyping environment | Read-only PostgreSQL | Approved sources/review queue |
| Human checkpoint | Review before send | Validate requirements | Confirm findings | Approve disposition |
| Output | Draft response | Story + prototype | Evidence-backed exceptions | Reviewed recommendations |

**Key question to ask the audience:**

> “Which column looks most like a task you perform today?”

---

### Slide 16 — Experiment Safely: Not Every Task Has the Same Risk

**Time:** 3 minutes

**Purpose:** Give practical guardrails without making the session feel prohibitive.

| Starting zone | Examples | Minimum expectation |
| --- | --- | --- |
| **Green: good first experiments** | Format requirements, summarize user-provided nonsensitive text, create a prototype with dummy data, draft a checklist. | Review the output; do not treat it as automatically correct. |
| **Yellow: controlled experiments** | Read internal email, query an internal database, generate or execute scripts, analyze sensitive internal content. | Approved environment, least-privilege access, data controls, testing, human verification, and technical escalation path. |
| **Red: do not improvise** | Auto-send communications, write/delete production data, execute an unreviewed script, upload restricted data to an unauthorized tool, deploy without an owner. | Formal approval and established production controls; often the action should remain prohibited for an experiment. |

**Important language:**

Do not say that the risks “are not that big.” Say:

> “The risks are manageable when we match the controls to the consequence of the task.”

**Three nonnegotiables:**

1. Use only approved tools and data access.
2. Keep the human accountable for consequential decisions and external actions.
3. Escalate when you cannot explain what a script, query, or result is doing.

---

### Slide 17 — What Happens After This Presentation?

**Time:** 1 minute

**Purpose:** Prevent enthusiasm from turning into an unsupported flood of requests.

**Recommended call to action:**

> Choose one repetitive, low-risk task that takes 30–90 minutes, occurs at least twice a month, has a recognizable “good” result, and still allows a human to approve the outcome.

Ask participants to capture it using the Agent Opportunity Canvas in the appendix.

**The slide must also name the real support path:**

- Where to submit an idea.
- Who confirms whether the tool and data access are allowed.
- Where sandboxing occurs.
- Who helps package a successful experiment into a reusable skill.
- Who owns and supports it if it scales.

Do not present this call to action until Asta, Shiba, Lisa, or the appropriate sponsors confirm the operating model.

---

### Slide 18 — Our Expertise Must Shape the Agents

**Time:** 5 minutes including discussion

**Closing message:**

> Other teams can build governance technology, but our team understands the criteria, exceptions, and decisions that make governance work. If we participate early, our expertise becomes part of the capability. If we wait, others may encode those decisions without the domain owners.

**Final challenge:**

> “What is one piece of work you would teach a new analyst to do—and what would have to be true before you trusted an agent to help with it?”

Use responses to transition into questions and surface candidate workflows.

---

## 6. Demonstration strategy

The presentation will be stronger if each case is shown as a short story rather than a live technical walkthrough.

### Recommended demonstration format

For each case, use the same five-frame structure:

1. **Before:** What takes time or creates confusion today?
2. **Request:** What outcome did you give the agent?
3. **Work:** What skill and approved tool did it use?
4. **Review:** Where did you correct, verify, or approve the result?
5. **After:** What useful artifact was produced?

### Live versus recorded

- Prefer staged screenshots or a 60–90 second recording for Outlook and database examples. This avoids sensitive data exposure, connection failures, and unpredictable response time.
- A short live interaction can work for the EDG Scorecard prototype if the prompt and output are stable.
- Always retain backup screenshots of the expected result.
- Never use a live production inbox, credentials, confidential records, or unrestricted database connection on screen.

### How much code to show

Show enough to make the enabling mechanism real, but not enough to turn the session into code review.

- One small, annotated PowerShell excerpt is sufficient.
- One small, annotated read-only query is sufficient.
- Put full scripts, query details, and architecture in the appendix.
- Make the business input, output, and human checkpoint larger than the code.

> Do not make the code the proof. Make the improved workflow the proof.

---

## 7. Asset checklist

### Foundation slides

- A bridge visual: business expertise → controlled agentic workflow → validated outcome.
- Three-card visual for Agent, Skill, and Harness.
- One end-to-end flow with human checkpoints.
- Workslop versus useful-work comparison.

### Case 1 assets

- Sanitized sample email.
- Screenshot of sender/folder filter.
- Small PowerShell or connector excerpt.
- Domain-routing result.
- Draft response with “human reviews before send” callout.

### Case 2 assets

- Original conversational prompt.
- Agent's clarifying questions.
- One before/after prompt comparison.
- EDG Scorecard prototype screenshot.
- User story and two or three acceptance criteria.

### Case 3 assets

- One plain-language investigation question.
- Sanitized read-only query excerpt.
- Database-versus-vended comparison table.
- One discrepancy with supporting evidence.
- Human validation note.

### Case 4 assets

- Small sample of raw rationalization candidates.
- Example rule set.
- Recommendation/review queue.
- Steward decision and rationale.

### Closing assets

- Green/yellow/red risk table.
- Agent Opportunity Canvas.
- Confirmed intake and support path.

---

## 8. Leadership decisions required before the session

Talk with Asta and Shiba, and confirm sponsorship or direction from Lisa as appropriate. The objective is to avoid creating demand without a supported next step.

### Questions to resolve

1. **What is the intended outcome?** Is this education only, an invitation to experiment, or the launch of an adoption program?
2. **Which tools are approved?** Can the audience use a local agent, enterprise agent workspace, PowerShell, Python, HTML prototypes, Outlook access, or database connectors?
3. **Where can experimentation occur?** Is there an approved sandbox, test data, and provisioning process?
4. **What data is allowed?** Which classifications may be used, and what must be sanitized for the presentation?
5. **Who provisions access?** If 15 teams request agents or workspaces afterward, who handles intake and prioritization?
6. **Who provides technical review?** Where does a business user go when they cannot explain a generated script, query, or result?
7. **Who owns reusable skills?** Who approves, versions, maintains, and retires skills such as rationalization?
8. **How does this connect to Ask Genie?** Are local integrations with ICR, EDQ, or other personas supported, planned, or only conceptual?
9. **What actions must remain human-only?** Sending communications, database changes, record dispositions, and production deployment should be explicit.
10. **What is the approved call to action?** Idea submission, office hours, pilot cohort, or no immediate action?

### Recommended operating model to propose

If no model exists, propose a small pilot rather than open-ended enablement:

1. Collect candidate workflows through a one-page canvas.
2. Select three low-risk, high-frequency use cases.
3. Run a two- to four-week sandbox with named business and technical owners.
4. Measure baseline time, result quality, and reviewer effort.
5. Package only the successful patterns into approved, reusable skills.
6. Decide whether to scale, revise, or stop each pilot.

---

## 9. Agent Opportunity Canvas

Use this as an appendix slide or one-page handout.

| Field | Question |
| --- | --- |
| Task | What recurring work do you want help with? |
| Trigger | What starts the work—an email, request, file, schedule, or question? |
| Frequency and effort | How often does it happen, and how much time does it take? |
| Inputs | What information is needed, and how sensitive is it? |
| Rules | What steps, business definitions, and exceptions do you apply? |
| Tools | Which systems must be read or used? |
| Output | What useful artifact or recommendation should be produced? |
| Human checkpoint | What must a person verify or approve? |
| Failure impact | What could go wrong, and how serious would it be? |
| Success measure | How will you know the workflow is faster, better, or more consistent? |

### Good first-use-case test

A candidate is promising when most answers are “yes”:

- Is it repetitive?
- Is the input available in a consistent form?
- Can a subject-matter expert explain the rules?
- Is a good output recognizable?
- Can the first version use dummy or low-risk data?
- Can a human review the result before any consequential action?
- Would saving 15–30 minutes each time create meaningful value?

---

## 10. How to talk about tokens and experimentation

The transcript's instinct is useful: people learn by trying, and early exploration can feel inefficient. The presentation should refine the message so it does not sound like token consumption is the goal.

### Recommended framing

> “At first, experimentation is broad because we are learning what the agent needs. As patterns emerge, we stop repeating the same context and package the successful instructions, examples, and controls into reusable skills.”

### Practical optimization sequence

1. Start with a narrow task and a clear outcome.
2. Provide the relevant context rather than an entire history.
3. Give one or two examples of a good result.
4. State constraints and acceptance criteria.
5. Correct the result and record why.
6. Save the repeatable instructions as a skill.
7. Reuse the skill through an approved harness.

Tokens are an experimental budget, not a measure of productivity. The goal is fewer repeated explanations, better outputs, and shorter review cycles.

---

## 11. Phrasing to strengthen or avoid

| Avoid | Use instead |
| --- | --- |
| “AI is a race to get the product out first.” | “The advantage comes from learning quickly and converting what works into a reliable capability.” |
| “The risks aren't that big.” | “The risks are manageable when controls match the consequence of the task.” |
| “The agent does the work for me.” | “The agent handles repeatable steps while I provide context, judgment, and approval.” |
| “You do not need technical people anymore.” | “Business users can prototype and communicate more effectively, while technical expertise remains essential for safe integration and production.” |
| “Just run the script the agent creates.” | “Understand its purpose, test it in an approved sandbox, and seek technical review when the effect is unclear.” |
| “We are behind.” | “We have an opportunity to ensure our governance expertise shapes these capabilities early.” |
| “Use all your tokens.” | “Use experimentation to discover reusable patterns, then make those patterns more efficient.” |

---

## 12. Suggested opening and closing scripts

### Opening: approximately 60 seconds

> “We hear a lot about agents, enterprise AI initiatives, data-quality agents, personas, and automation. But for many business users, the unanswered question is much simpler: where does any of this fit in my actual workday? I am not here to teach Python or turn everyone into a developer. I want to show how the expertise you already have can guide an agent through repeatable work—and how an agent, a skill, and a controlled workspace can help us find context, translate requirements, analyze information, and apply governance rules more consistently.”

### Transition into the cases

> “Rather than stay at the buzzword level, I will use four pieces of work our teams already recognize. For each one, watch for the same three elements: the agent doing the steps, the skill carrying our business knowledge, and the harness controlling the tools and boundaries.”

### Closing: approximately 75 seconds

> “The goal is not to automate every decision, and it is not to push unverified output into production. The goal is to remove avoidable effort while preserving the judgment that makes our governance work credible. Our team knows the criteria, exceptions, and context that these systems need. That means we should help shape the capabilities, not wait for someone else to encode our work for us. Start with one narrow, repetitive, low-risk task. Sandbox it, verify it, tune it, and package what works. Prototype quickly, but productionize deliberately.”

---

## 13. Deck design guidance

### Visual direction

- Use a 16:9 layout with a calm enterprise palette: navy, off-white, teal, and amber for caution.
- Use one idea per slide and large type; avoid paragraphs on the projected deck.
- Keep detailed explanations in speaker notes and the appendix.
- Use the same visual template for all four cases.
- Place a small footer on each case slide: **Agent | Skill | Harness | Human checkpoint**.
- Use arrows, annotated screenshots, and before/after comparisons instead of decorative AI imagery.
- Give every screenshot a short caption and two or three numbered callouts.

### Density targets

- Headline: one complete takeaway, not just a topic label.
- Main-slide text: ideally fewer than 35 words, excluding a small table.
- Screenshot labels: three callouts maximum.
- Code: no more than 8–12 visible lines in the main deck.
- Appendix: full scripts, definitions, architecture, and detailed controls.

### Recommended case-study layout

**Left side:** Today's friction  
**Center:** Agent-enabled flow  
**Right side:** Human checkpoint and useful output  
**Bottom strip:** Potential measure of value

---

## 14. Appendix plan

Keep technical depth available without forcing it into the core story.

1. Full terminology glossary.
2. Agent versus chatbot comparison.
3. Full Outlook/PowerShell flow and approved-access assumptions.
4. EDG Scorecard prompt evolution and acceptance criteria.
5. Database schema/query assumptions and read-only controls.
6. Rationalization rule template.
7. Green/yellow/red activity examples.
8. Agent Opportunity Canvas.
9. Proposed intake and pilot process.
10. Sources, owners, and dates for enterprise initiative references.

---

## 15. Items to confirm from the transcript before building the deck

Speech-to-text appears to have altered several internal terms. Confirm the official spelling and meaning before placing them on slides:

- “Asian cube” — confirm the intended enterprise initiative or product name.
- “BRP metrics” and “BRP agents” — confirm whether the acronym is BRP, BPR, or another program.
- “AS Genie” — confirm whether the official name is **Ask Genie** and whether ICR/EDQ are personas, agents, skills, or domains.
- “DB mod” — confirm the formal project or incident name.
- “DTCE” — confirm whether this should be **DGCE** or another platform.
- “post-scress” — use **PostgreSQL** if that is the intended database.
- “Calibra” — use **Collibra** if referring to the data-governance platform.
- “Plato's algorithm” — confirm the example and the point it is intended to illustrate.

Also confirm which of the four examples are already working demonstrations versus proposed future-state workflows. Label them honestly as **working today**, **prototype**, or **concept**.

---

## 16. Final build checklist

### Content

- [ ] The opening is about daily work, not AI history.
- [ ] Agent, skill, and harness are defined once in plain language.
- [ ] Workslop is addressed before the demonstrations.
- [ ] Each case names the problem, skill, harness, human checkpoint, and value.
- [ ] Prototypes are clearly separated from production capabilities.
- [ ] Claims are measured or presented as metrics to collect—not invented savings.
- [ ] The support path after the presentation is real and named.

### Safety and accuracy

- [ ] All screenshots and sample data are sanitized.
- [ ] Enterprise names and acronyms are verified.
- [ ] Outlook, Ask Genie, and database access assumptions are confirmed.
- [ ] No live credential, production write access, or auto-send capability is shown.
- [ ] Full scripts and queries receive the appropriate technical review.
- [ ] A backup exists for every live demonstration.

### Delivery

- [ ] Rehearsal reaches Slide 16 by minute 36.
- [ ] Every case can be shortened to three minutes if needed.
- [ ] The speaker can explain all four cases without reading code.
- [ ] The final question invites one concrete workflow from the audience.
- [ ] Asta, Shiba, Lisa, or the correct sponsors approve the call to action.

---

## Final recommendation

Build the presentation around one memorable idea:

> **The agent supplies adaptable execution. The skill carries our expertise. The harness makes the work controlled and reusable. The human remains accountable.**

If every slide reinforces some part of that sentence, the audience will leave with a practical mental model rather than another list of AI buzzwords.
