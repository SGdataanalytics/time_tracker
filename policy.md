# Cline Security Policy

## Purpose

This policy defines mandatory security rules for Cline when working on this project.

The project may use a public GitHub repository. Cline must therefore treat prevention of secret disclosure, accidental commits, and unnecessary access to sensitive local data as a primary constraint.

If there is any uncertainty about whether an action, file, command, configuration value, or location may expose sensitive information, Cline must stop and ask the user before proceeding.

---

## 1. Secrets and credentials

Secrets, credentials, API keys, access tokens, refresh tokens, passwords, private SSH keys, certificates containing private keys, connection strings, authentication cookies, and other sensitive values must:

- never be committed to Git
- never be pushed to GitHub
- never be hard-coded in source code
- never be placed in tracked configuration files
- never be written into Markdown documentation or prompts
- never be exposed in logs or terminal output
- never be copied into Cline context
- never be transmitted to Cline or an external model

Real secrets must remain under the user's control on the Ubuntu server.

---

## 2. Secret storage

Real secrets must be stored outside the Git-tracked project source whenever practical.

Preferred structure:

```text
/home/sg/projects/<project-name>/    # Cline workspace and Git repository
/home/sg/secrets/                    # User-controlled secret storage
```

Cline may design the project to consume secrets through environment variables, but must not require access to the underlying secret file.

Application code should use patterns such as:

```python
import os

api_key = os.environ["OPENAI_API_KEY"]
```

Application source code must not hard-code the location of the user's real secret files unless the user explicitly approves that design.

Secret injection is an external runtime concern controlled by the user.

---

## 3. Files Cline must not access

Cline must not read, inspect, print, summarize, search, copy, modify, transmit, rename, move, delete, change permissions on, source, or otherwise manipulate files containing real secrets.

Protected locations and file types include, but are not limited to:

- `.env`
- `.env.*`, except explicitly safe public templates such as `.env.example`
- `/home/sg/secrets/`
- private SSH keys
- credential stores
- token files
- password files
- private-key files
- secret-manager data
- shell files known or suspected to contain credentials
- files outside the project that may contain credentials or other sensitive values

Cline must not attempt to discover the contents of protected locations.

If a file may contain sensitive information and its status is uncertain, Cline must ask the user before reading it.

---

## 4. Safe public templates

`.env.example` may be tracked publicly only if it contains:

- environment-variable names
- safe explanatory comments
- empty values or clearly non-sensitive placeholders

It must never contain:

- real credentials
- real API keys
- real tokens
- passwords
- private endpoints that the user considers confidential
- customer-specific confidential values
- internal hostnames or identifiers unless explicitly approved for publication

Example:

```dotenv
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
DATABASE_URL=
```

Cline may create and maintain `.env.example`.

Cline must not create or populate a real `.env` file unless the user explicitly requests the exact operation, and Cline must never insert real secret values.

---

## 5. Command restrictions

Cline must not run commands whose purpose or likely effect is to reveal secret values.

This includes direct and indirect methods such as:

```text
cat .env
less .env
head .env
tail .env
grep <secret-file>
printenv
env
set
source .env
```

It also includes using interpreters or tooling to bypass the restriction, for example:

- Python commands that read secret files or print environment variables
- Node.js commands that read secret files or print environment variables
- shell scripts that reveal protected values
- `docker inspect` or container inspection intended to reveal environment secrets
- process-environment inspection
- `systemctl show` when it may reveal credentials
- `journalctl` searches intended to retrieve credentials
- shell-profile inspection when credentials may be stored there
- credential-helper or password-store inspection

Cline must not use an alternative tool or command to circumvent a blocked or prohibited secret-access operation.

If a diagnostic task may expose a secret indirectly, stop and ask the user first.

---

## 6. What Cline should do when a secret is required

When an application component requires a secret, Cline must:

1. create only the safe code, folder structure, configuration template, or placeholder
2. state the exact environment-variable name that is required
3. explain where the application consumes the variable
4. stop before inserting or inspecting any real value
5. instruct the user to add or expose the real secret manually outside Cline's control
6. continue only after the user confirms that the required runtime setup is ready, without asking for the secret value

Cline must never ask the user to paste a real secret into chat.

---
## 7. Architecture rules

When designing components that require credentials:

- application code must read secrets from environment variables or another mechanism explicitly approved by the user
- secret values must remain outside source code
- real secret storage must remain outside the public repository
- secret handling should remain simple and local unless another mechanism is explicitly approved
- Cline should not depend on knowledge of real secret values
- Cline should not require access to real secret files to build or test ordinary application logic
- tests should use mock, dummy, or temporary non-sensitive values
- documentation must use placeholders only

Cline may create the architecture around secret handling, but the user remains responsible for inserting and maintaining real credentials.

---

## 8. Workspace boundary

Cline should treat the opened project workspace as its normal working boundary.

For example:

```text
/home/sg/projects/time_tracker/
```

Cline must not traverse outside the project workspace to inspect user files unless the user explicitly requests a specific, non-sensitive operation.

In particular, Cline must not access:

```text
/home/sg/secrets/
```

or other credential-bearing locations.

A request to inspect the broader server filesystem must not be interpreted as permission to inspect secrets.

---

## 9. Git safety

Before every commit or push, Cline must:

1. run `git status`
2. review the intended changes
3. review staged changes with `git diff --cached`
4. verify that no credentials, API keys, tokens, passwords, private keys, secret files, or other sensitive values are included
5. confirm that protected files remain ignored by Git
6. ask for explicit user approval before committing
7. ask for explicit user approval before pushing

Cline must not use `git add .` by default.

Cline should stage intended files explicitly by path.

Cline must not use force-push, destructive Git commands, history rewriting, or secret-removal operations without explicit user approval.

If Cline suspects that a secret has already been committed, it must stop, warn the user, and ask how to proceed. It must not display the suspected secret value.

---

## 10. `.gitignore`

The repository must keep real secret-bearing files ignored by Git.

At minimum, where relevant:

```gitignore
.env
.env.*
!.env.example
secrets/
*.pem
*.key
```

Cline must not remove secret-protection entries from `.gitignore` without explicit user approval.

Cline must not assume that `.gitignore` alone is permission to read an ignored file.

Ignored secret files remain prohibited from Cline access.

---

## 11. Cline-specific access principle

Security instructions in this policy are mandatory behavioral constraints.

Cline must not interpret technical access to a file as authorization to access it.

If Cline can technically access a protected file through the terminal, filesystem tools, scripts, extensions, plugins, MCP tools, hooks, or another mechanism, the access is still prohibited by this policy.

Cline must never attempt to bypass an access restriction.

---

## 12. Logs, debugging, and error handling

Cline must avoid introducing logging that may expose credentials.

Never log:

- environment-variable values containing secrets
- authorization headers
- bearer tokens
- API keys
- passwords
- authentication cookies
- private connection strings

When debugging authentication or configuration problems, Cline may verify that a variable exists, but must not print its value.

Prefer safe checks that result only in information such as:

```text
OPENAI_API_KEY is set
```

or:

```text
OPENAI_API_KEY is missing
```

Never output the value itself.

---

## 13. External services and data transmission

Cline must not upload, paste, transmit, or send secret-bearing files or sensitive values to:

- GitHub
- external APIs
- model providers
- paste services
- issue trackers
- third-party tools
- remote debugging services

unless the user explicitly approves a specific, safe use case and the action does not expose credentials.

---

## 14. User approval and uncertainty

When in doubt, Cline must stop and ask.

Explicit approval is required before:

- commit
- push
- changing secret-handling architecture
- accessing a file that may contain sensitive information
- moving or deleting security-related files
- weakening `.gitignore` or other protections
- changing permissions on protected locations
- running a command that may expose credentials
- introducing a new external service that will receive project data

Silence or prior approval for a different task does not count as approval.

---

## 15. General operating principle

Cline should build and maintain the machinery around secrets, but never handle the real secrets themselves.

The intended separation is:

```text
Cline:
    source code
    tests
    documentation
    public configuration templates
    Git operations with user approval
    application architecture

User:
    real API keys
    real passwords
    real tokens
    private SSH keys
    secret files
    secret injection into the runtime
```

When these responsibilities conflict, protection of secrets takes priority.

_________________________________________________________________________________________
The end.


