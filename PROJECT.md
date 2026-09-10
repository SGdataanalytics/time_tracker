# time_tracker

## Table of contents

- [Project purpose](#project-purpose)
- [Current development context](#current-development-context)
- [Main application goals](#main-application-goals)
- [Natural-language interpretation](#natural-language-interpretation)
- [Activity categorization](#activity-categorization)
- [Data storage](#data-storage)
- [Statistics](#statistics)
- [Business outcomes and later analysis](#business-outcomes-and-later-analysis)
- [Development phases](#development-phases)
- [Local AI direction](#local-ai-direction)
- [Security and deployment direction](#security-and-deployment-direction)
- [Architecture principles](#architecture-principles)
- [AI-assisted development workflow](#ai-assisted-development-workflow)
- [Learning requirement](#learning-requirement)
- [Cline permissions philosophy](#cline-permissions-philosophy)
- [Current status](#current-status)
- [Open design decisions](#open-design-decisions)

---

## Project purpose

`time_tracker` is a personal time-tracking and business-insight web application.

The goal is to make time registration as frictionless as possible, especially from a mobile browser.

The long-term idea is that the user can speak a short sentence such as:

> "I spent 45 minutes working on LinkedIn this morning."

or:

> "Yesterday I spent two hours working on the time tracker app."

The application should convert this input into structured time-tracking and business data.

Voice input is an important future feature, but it is **not** required for version 0.1.

---

## Current development context

- Operating system: Ubuntu 24.04 LTS
- Project path: `/home/sg/projects/time_tracker`
- Development environment: VS Code using Remote SSH from a Windows PC
- Primary language: Python
- Web framework: Flask
- Python virtual environment: `.venv`
- AI coding agent: Cline
- Current Cline model provider: Anthropic API
- Current model: Claude Sonnet
- Planned local AI environment: Ollama + Qwen

The project should remain beginner-friendly, easy to understand, and easy to maintain.

The user is learning Python, VS Code, Linux, server administration, and AI-assisted development while building the project.

Important technical decisions should therefore be explained clearly rather than implemented as unexplained complexity.

## Main application goals

### 1. Mobile-friendly web interface

The application should primarily be usable from a mobile browser.

The interface should make it possible to create a time entry with very little friction.

Version 0.1 can have a very simple interface.

### 2. Structured entry and text input

Version 0.1 focuses on **manual structured time entry**: simple form fields for date, duration, category, subcategory, and a description.

A simple free-text input field may also exist already in Phase 1 for convenience, but advanced natural-language interpretation of that free text is not required until Phase 2.

Eventually, both manually entered text and speech transcription should pass through the same interpretation pipeline.

Conceptually:

```
text input
→ interpretation
→ structured time entry
→ categorization
→ storage
```

Later:

```
voice
→ Whisper
→ text
→ same interpretation pipeline
```

### 3. Voice input

Voice input is planned for a later version (Phase 3).

The user should eventually be able to speak a time entry from a mobile browser.

Speech should be converted to text using Whisper or a Whisper-compatible solution.

Possible future architecture:

```
mobile browser
→ audio
→ Ubuntu server
→ Whisper / speech-to-text
→ text interpretation
→ structured time entry
```

Local speech processing on the Ubuntu server may be preferable later for privacy and local processing.

**Do not implement Whisper in the first milestone.**

---

## Natural-language interpretation

The application should eventually extract structured information from natural-language input.

Relevant information includes:

- activity
- category
- subcategory
- date (a normalized, concrete calendar date)
- duration
- optional start time
- optional end time
- original text or transcription

### Handling relative dates

Expressions such as "today", "yesterday", "Monday", or "last Tuesday" are relative or informal date references.

These should be **interpreted and normalized into a concrete date** (e.g. `2026-09-08`) before storage. The relative expression itself is not stored as a separate permanent field — the original wording remains available through the `original input text` field.

The application should eventually understand expressions such as:

- "30 minutes"
- "one and a half hours"
- "two hours"
- "from 10 to 12"
- "today"
- "yesterday"
- "this morning"
- weekdays
- relative dates ("last Tuesday", etc.)

Example:

Input:

`Yesterday I spent 90 minutes researching local AI models.`

Possible structured result:

- date: `2026-09-08` (normalized from "yesterday")
- duration: 90 minutes
- activity: researching local AI models
- category: Research / Learning
- subcategory: AI / Local models

### Prefer deterministic logic where practical

The interpretation system should start simple and become more capable gradually.

Where simple Python logic or a lightweight library can reliably parse things such as dates, durations, or known category mappings, that should be preferred over introducing an LLM for parsing problems that don't require one. LLMs may still be introduced later where they add real value.

---

## Activity categorization

Activities should be mapped into predefined:

1. categories
2. subcategories

The category system should be easy to change later.

Possible high-level categories include:

- Development
- Research / Learning
- Networking / Communication
- Administration
- Business Development
- Planning
- Meetings
- Education / Certification
- Personal / Other

Possible examples:

```
LinkedIn outreach
→ Networking / Communication
→ LinkedIn

Coding the time_tracker app
→ Development
→ time_tracker

Researching Ollama or Qwen
→ Research / Learning
→ AI / Local models

Azure certification study
→ Education / Certification
→ Azure
```

The final category structure has **not** been decided yet.

Suggestions for a useful category/subcategory structure are welcome.

Avoid spreading categorization rules throughout many different files.

The categorization system should preferably have one clear place where categories and rules can later be modified.

---

## Data storage

Each time entry should eventually contain structured data such as:

- date (normalized, concrete date)
- activity description
- duration
- category
- subcategory
- original input text
- input source (text or voice)
- optional start/end timestamps
- optional metadata needed later for analysis

### Duration is the canonical time measurement

- Duration is the canonical measure of time spent on an activity.
- It should preferably be stored as a simple numeric value, such as total minutes.
- Start time and end time may be stored when available, but they remain optional and secondary to duration.
- Start/end time should not be required for every entry.

This keeps statistics simple and consistent, since every entry has a comparable duration value regardless of whether exact start/end times were captured.

### Storage technology

The initial storage solution should be deliberately simple.

Do not introduce a complex database system prematurely. The specific storage/database technology has **not** been chosen yet — this is an open design decision to be discussed before implementation (see [Open design decisions](#open-design-decisions)).

The storage design should, however, make it possible to expand the application later without having to redesign everything.

---

## Statistics

The application should eventually provide statistics such as:

- total time per category
- total time per subcategory
- most time-consuming activities
- time spent per day
- time spent per week
- trends over time

Because duration is stored as a normalized numeric value, these statistics can be computed consistently regardless of whether an entry has exact start/end times.

The purpose is not only traditional time tracking.

The longer-term goal is to understand how time investment relates to business results.

---

## Business outcomes and later analysis

Time entries and business outcomes are related, but they are **conceptually separate datasets**.

- Time entries answer: *"What did I spend time on?"*
- Business outcome data answers: *"What business result occurred?"*

Examples of business outcomes may include:

- professional network growth
- leads
- assignments
- customers
- income

Business outcome data should **not** be embedded as fields inside every individual time entry. Instead, outcomes should be tracked as their own data (e.g. separate records with their own dates), and later analysis may relate time-investment data to outcome data — for example, by date range or category.

This could eventually make it possible to investigate questions such as:

- Which types of activity consume the most time?
- Which activities generate the most leads?
- Which categories contribute most to network growth?
- Which activities appear to generate the highest income?
- Where is time spent without producing meaningful outcomes?

This functionality belongs to a later phase (Phase 5).

**Do not implement correlation or business-outcome analysis in version 0.1.**

---

## Development phases

### Phase 1 — Basic usable time tracker

Goal: establish the smallest usable technical foundation for the application.

Includes:

- basic Flask application
- mobile-friendly interface
- manual structured time entry (date, duration, category, subcategory, description, via simple form fields)
- category and subcategory selection
- store entries
- display and edit existing entries
- establish the data model and processing pipeline that later phases will build on
- a simple free-text input field may exist for convenience, but advanced natural-language interpretation of it is not required yet

Explicitly **not** in Phase 1:

- No Whisper.
- No LLM-based parsing.
- No business correlation analysis.

Keep this phase deliberately small.

### Phase 2 — Natural-language input

Goal: interpret natural-language sentences into the structured fields established in Phase 1.

Allow the user to enter sentences such as:

`Yesterday I spent an hour and a half working on LinkedIn outreach.`

Convert these into structured fields:

- date (normalized from relative expressions such as "yesterday")
- duration
- activity
- category
- subcategory

Start with simple deterministic logic where appropriate (e.g. rule-based date and duration parsing).

Do not automatically introduce an LLM for every parsing problem if simpler logic is sufficient. LLMs may be introduced later where they add real value.

### Phase 3 — Voice input

Add microphone input from the mobile browser.

Use Whisper or a compatible speech-to-text solution.

The transcription should feed into the existing text-processing pipeline.

Voice should therefore be treated as an input method, not as a separate application architecture.

### Phase 4 — Statistics and dashboard

Add useful summaries such as:

- time per category
- time per subcategory
- time per week
- most time-consuming activities
- trends

Visualisations may be added if they provide useful information.

### Phase 5 — Business outcomes

Introduce optional outcome tracking as its **own dataset**, such as:

- network growth
- leads
- assignments
- customers
- income

Then explore relationships between time-investment data and outcome data.

---

## Local AI direction

The Ubuntu server is also intended to become a local AI environment.

Planned technologies include:

- Ollama
- Qwen
- possibly a local Whisper installation later

A longer-term goal is to experiment with local models and AI agents.

Where practical, the application architecture should therefore avoid unnecessary dependence on one specific cloud AI provider.

See also [Security and deployment direction](#security-and-deployment-direction) for how this relates to keeping data and processing local.

However:

**Do not add abstraction layers merely for hypothetical future requirements.**

Version 0.1 should prioritize simplicity while leaving a reasonable path toward local AI later.

---

## Security and deployment direction

- The application should remain **private during development**, and should not be exposed publicly unless there is a specific, discussed reason to do so.
- The Ubuntu server is accessed remotely through a controlled SSH / Tailscale setup, not through open public access.
- Future local processing with Ollama, Qwen, and potentially a local Whisper installation is partly motivated by keeping more data processing inside the local/private environment rather than sending it to external cloud services.
- Cline must **not** expose services publicly, or change firewall, router, port-forwarding, SSH, Tailscale, or other network/security configuration, without discussing it with the user first.
- Network and security changes are explicit architecture decisions, not routine implementation steps, and require explicit user approval before being made.

---

## Architecture principles

Prefer:

- simple Python
- Flask
- understandable code
- clear names
- small modules
- small functions
- incremental development
- minimal dependencies
- simple architecture
- separation of concerns where it genuinely helps
- deterministic parsing (dates, durations, category rules) over LLM calls, where simple logic is reliable enough

Avoid:

- premature microservices
- unnecessary frameworks
- unnecessary abstraction
- complex deployment systems
- premature optimization
- large amounts of generated boilerplate
- introducing technologies simply because they may be useful later

The guiding rule is:

> **Build the simplest version that leaves a reasonable path for later expansion.**

---

## AI-assisted development workflow

Cline is used as the coding agent inside VS Code.

Cline currently accesses Claude through the Anthropic API.

The project itself lives on the Ubuntu server at:

`/home/sg/projects/time_tracker`

The user interacts with the server through VS Code Remote SSH from Windows.

Cline should normally follow this workflow:

1. Understand the requested change.
2. Inspect the relevant project files.
3. Explain important decisions.
4. Propose an approach before major architectural changes.
5. Make small and understandable changes.
6. Explain what was changed.
7. Run appropriate tests when relevant.
8. Avoid unrelated changes.
9. Do not make network, security, or deployment changes without explicit discussion (see [Security and deployment direction](#security-and-deployment-direction)).

Do not make large architectural decisions without discussing them first.

---

## Learning requirement

This is both a software project and a learning project.

The user wants to understand:

- Python
- Flask
- VS Code
- Linux / Ubuntu
- virtual environments
- server architecture
- APIs
- AI agents
- local AI
- MCP later

Therefore, when making non-trivial technical changes, explain:

- what is being changed
- why it is needed
- where it runs
- how it relates to the rest of the architecture

Do not merely generate working code without explanation.

---

## Cline permissions philosophy

Use conservative permissions.

Cline may normally be allowed to:

- read project files
- execute clearly safe commands

Cline should not automatically be allowed to:

- access arbitrary files outside the project
- execute unrestricted shell commands
- change firewall, router, port-forwarding, SSH, Tailscale, or other network/security configuration
- use MCP servers unless intentionally enabled
- use browser access unless intentionally needed

For significant file changes, network/security changes, or architectural decisions, prefer explicit user review.

---

## Current status

The project is at the very beginning.

Currently:

- `/home/sg/projects/time_tracker` exists
- `.venv` exists
- Flask is installed in the virtual environment
- VS Code Remote SSH works
- Cline is installed in the remote workspace
- Cline is connected to Claude through the Anthropic API
- application structure has not yet been finalized
- no significant application implementation has been approved yet

The next step is to agree on a minimal v0.1 project structure before implementation begins.

---

## Open design decisions

The following decisions are intentionally left open and should be discussed before or during implementation:

- **Storage technology**: which simple storage mechanism to use for time entries in v0.1 (e.g. flat file, SQLite, or similar) has not been chosen yet.
- **Final category/subcategory list**: the concrete set of categories and subcategories has not been finalized.
- **v0.1 folder/file structure**: the exact Flask project layout for the first milestone has not been agreed yet.
- **Date normalization approach**: whether to use a library or hand-written rules for turning relative date expressions into concrete dates.
- **Business outcome data model**: the exact shape of outcome records (fields, granularity) is not yet defined; only the principle that it is a separate dataset has been agreed.
