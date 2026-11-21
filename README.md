# 🤖 Autonomous AI GitHub Coding Agent (Java Spring Boot)

An autonomous multi-agent developer system built with Python, Groq LLM API, LangChain, Git, and Maven. It connects to your Java Spring Boot repository, understands the existing architecture, identifies meaningful improvements, writes clean Java 21 code, executes Maven tests, repairs failures, conducts independent code reviews, commits to dedicated feature branches, and opens GitHub Pull Requests.

---

## 🏗️ Multi-Agent Architecture

```
                                  +----------------------------+
                                  |     Java Spring Boot       |
                                  |   Application (Java 21)    |
                                  +--------------+-------------+
                                                 |
                                                 v
+-----------------------+             +-----------------------+
|  Task Database        | <========== | Agent 1: Repo Analyst |
|  (SQLite Persistence) |             | Static AST / Pom scan |
+-----------+-----------+             +-----------+-----------+
            |                                     |
            +----------------+  +-----------------+
                             |  |
                             v  v
                  +-----------------------+
                  | Agent 2: Task Planner |
                  | Top <= 10 daily tasks |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | Agent 3: Java Dev     |
                  | Spring Boot 3 / Java21|
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | Agent 4: Tester       | <----+ (Auto-Repair Loop)
                  | Maven compile & test  | -----+ (Up to 2 retries)
                  +-----------+-----------+
                              |
                              v (Tests Passed)
                  +-----------------------+
                  | Agent 5: Code Reviewer|
                  | Standards & Security  |
                  +-----------+-----------+
                              |
                              v (Approved score >= 7)
                  +-----------------------+
                  | Agent 6: GitHub Agent |
                  | Commit -> Push -> PR  |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | Daily Execution Report|
                  | (Markdown & JSON)     |
                  +-----------------------+
```

### The 6 Specialized Agents

| # | Agent Name | Primary Responsibility |
|---|---|---|
| **1** | **Repository Analyst** | Scans `pom.xml`, controllers, services, repositories, entities, DTOs, and tests. Pinpoints architectural debt and missing tests. |
| **2** | **Task Planner** | Plans up to 10 meaningful, safe, high-priority tasks per day. Consults SQLite task history to avoid duplicate work. |
| **3** | **Java Developer** | Implements Java 21 / Spring Boot 3 code following SOLID principles, Bean Validation, and constructor injection. |
| **4** | **Testing Agent** | Executes Maven builds (`mvn test`), parses Surefire results, and identifies compilation/test regressions. |
| **5** | **Code Reviewer** | Independently reviews unified diffs for null safety, security vulnerabilities, performance, and best practices. |
| **6** | **GitHub Agent** | Creates isolated branches (`agent/improve-task_xxx`), commits verified changes, pushes branch, and opens detailed Pull Requests. |

---

## 📋 Technology Stack

- **Agent Language**: Python 3.11+
- **LLM Provider**: [Groq API](https://console.groq.com) (Configurable model: e.g., `llama-3.3-70b-versatile`, `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`)
- **Frameworks**: LangChain (`langchain-groq`, `langchain-core`), Pydantic v2
- **Version Control**: GitPython & GitHub REST API v3
- **Target Application**: Java 21, Spring Boot 3.x, Maven, JUnit 5, Mockito
- **Persistence**: SQLite (`data/agent_tasks.db`)
- **Automation**: GitHub Actions (Scheduled daily at 9:00 AM IST / 03:30 UTC)

---

## 🚀 Setup & Execution Guide (Windows PowerShell)

### 1. Clone & Enter Repository

```powershell
cd c:\Users\akjan\AI-GitHub-Coding-Agent
```

### 2. Configure Environment Variables

Copy the example environment template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and provide your credentials:

```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GITHUB_TOKEN=ghp_your_personal_access_token_here
REPO_OWNER=laxman235
REPO_NAME=AI-GitHub-Coding-Agent
TARGET_BRANCH=main
TARGET_REPO_PATH=sample-spring-boot-app
MAX_DAILY_TASKS=10
DRY_RUN=false
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Run the Test Suite

Verify all Python agent components:

```powershell
python -m pytest tests -v
```

### 5. Run the Autonomous Agent

#### A. Dry-Run Mode (Simulation & Verification without Remote Push):
```powershell
python -m agent.main --dry-run --verbose
```

#### B. Live Production Mode:
```powershell
python -m agent.main --max-tasks 5 --verbose
```

#### C. Run Against a Custom Local Spring Boot Project:
```powershell
python -m agent.main --target-path "C:\path\to\your\spring-boot-project"
```

---

## 🔒 Safety & Guardrails

1. **No Direct Pushes to `main`**: All changes are committed to isolated branches (`agent/improve-*`).
2. **Never Force-Push**: Force-pushing is strictly forbidden in the codebase.
3. **No Arbitrary Code Execution**: File modifications are restricted to an explicit extension allowlist (`.java`, `.xml`, `.properties`, `.yml`, `.sql`, `.md`).
4. **Denylist Protections**: Files matching `.env`, `credentials`, `id_rsa`, `secrets.json`, or `.git` are rejected with errors.
5. **Pre-Commit Verification**: No code is ever committed unless Maven compilation and unit tests pass.
6. **Bounded Repair Limit**: If tests fail, the Developer Agent is permitted at most 2 targeted repair attempts. If tests still fail, the change is automatically rolled back.
7. **Independent Reviewer Gate**: Code is rejected if the Reviewer Agent scores below 7/10 or flags security risks.
8. **Human Merge Required**: The agent opens Pull Requests and never auto-merges into production branches.

---

## ⏰ Daily Automation via GitHub Actions

The workflow in [`.github/workflows/daily_agent.yml`](.github/workflows/daily_agent.yml):
- Executes automatically **every day at 9:00 AM IST** (`30 3 * * *` UTC).
- Supports on-demand execution via **Actions -> Run workflow** with parameters `dry_run` and `max_tasks`.
- Enforces single-execution concurrency to prevent race conditions.
- Caches Maven dependencies and the SQLite task history database (`data/agent_tasks.db`) between workflow runs.
- Saves execution reports as workflow artifacts and publishes them directly to the **GitHub Actions Job Summary**.

### Required GitHub Secrets & Permissions

In your GitHub repository settings (**Settings -> Secrets and variables -> Actions**):

1. **Secrets**:
   - `GROQ_API_KEY`: Your Groq Cloud API key.
   - `GITHUB_TOKEN`: GitHub automatically provides this, or you can supply a Personal Access Token with `repo` scope if cross-repository pushes are needed.
2. **Workflow Permissions** (**Settings -> Actions -> General -> Workflow permissions**):
   - Select **Read and write permissions**.
   - Check **Allow GitHub Actions to create and approve pull requests**.

---

## 📊 Sample Daily Report Preview

```markdown
# 🤖 Autonomous AI Agent Daily Execution Report

**Repository:** `laxman235/AI-GitHub-Coding-Agent`  
**Execution Date (UTC):** `2026-11-21 06:12:00`  
**Run ID:** `run_20261121_061200`  
**Overall Status:** ✅ SUCCESS  
**Groq Model Configured:** `llama-3.3-70b-versatile`  

## 📊 Execution Summary
| Metric | Count |
| :--- | :--- |
| Tasks Identified | 2 |
| Tasks Attempted | 2 |
| Tasks Completed & PR'd | 2 |
| Tasks Failed / Rejected | 0 |

## 📝 Task Details
| # | Title | Category | Status | Review Score | PR / Branch |
|---|---|---|---|---|---|
| 1 | Add Bean Validation to ProductDto | `FEATURE` | ✅ `COMPLETED` | 9/10 | [PR #12](https://github.com/...) |
| 2 | Add JUnit 5 Mockito Tests for ProductService | `TEST_IMPROVEMENT` | ✅ `COMPLETED` | 9/10 | [PR #13](https://github.com/...) |
```
