# 🚀 CareerPilot AI & Autonomous Coding Agent

<div align="center">

[![Firebase Hosting](https://img.shields.io/badge/Frontend-Firebase%20Hosting-FFCA28?logo=firebase&logoColor=black)](https://careerpilot-ai-cd651.web.app)
[![Render Backend](https://img.shields.io/badge/Backend-Render%20Cloud-46E3B7?logo=render&logoColor=black)](https://careerpilot-backend-sq7w.onrender.com)
[![Java 21](https://img.shields.io/badge/Java-21-ED8B00?logo=openjdk&logoColor=white)](https://www.oracle.com/java/)
[![Spring Boot 3.3](https://img.shields.io/badge/Spring%20Boot-3.3.0-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Groq LLM](https://img.shields.io/badge/AI%20Model-Llama--3.3--70B-F05032?logo=groq&logoColor=white)](https://groq.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/laxman235/AI-GitHub-Coding-Agent/actions)

**An autonomous multi-agent developer system that engineers, tests, and deploys a multi-stack AI Career Platform.**

[🌐 Live Web Application](https://careerpilot-ai-cd651.web.app) • [⚙️ Live Backend API](https://careerpilot-backend-sq7w.onrender.com) • [📋 Product Vision & Roadmap](PRODUCT_PROMPT.md)

</div>

---

## 🌟 Overview

This repository houses two tightly integrated systems:

1. **🤖 The Autonomous AI GitHub Coding Agent**: An autonomous multi-agent engineering team (Repository Analyst, Task Planner, Developer, Stack-Aware Tester, Code Reviewer, and GitHub Agent) powered by Python, Groq LLMs (Llama 3.3 70B), and GitHub Actions. Every day, it inspects the codebase, plans prioritized sprint tasks, writes clean code, verifies test suites, and opens Pull Requests.
2. **💼 CareerPilot AI (The Live Application)**: A modern, AI-powered career acceleration platform built with a **Java 21 Spring Boot 3** backend and a **React 18 / TypeScript / Vite** frontend. Features include candidate authentication, daily job discovery, semantic ATS resume scoring, and application tracking.

---

## 🌐 Live Deployments

| Component | Platform | URL | Status |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | Firebase Hosting | [careerpilot-ai-cd651.web.app](https://careerpilot-ai-cd651.web.app) | ![Online](https://img.shields.io/badge/Live-BrightGreen) |
| **Backend API** | Render Cloud (Docker) | [careerpilot-backend-sq7w.onrender.com](https://careerpilot-backend-sq7w.onrender.com) | ![Online](https://img.shields.io/badge/Live-BrightGreen) |
| **Health Check** | Spring Boot REST | [careerpilot-backend-sq7w.onrender.com/api/health](https://careerpilot-backend-sq7w.onrender.com/api/health) | `{"status":"UP"}` |

---

## 🏗️ Multi-Agent Architecture

```
                                 ┌───────────────────────────────────┐
                                 │     Full-Stack Application        │
                                 │  • Java 21 Spring Boot Backend    │
                                 │  • React 18 / Vite / TS Frontend  │
                                 └─────────────────┬─────────────────┘
                                                   │
                                                   ▼
┌───────────────────────┐              ┌───────────────────────┐
│   Task Database       │ <=========== │ Agent 1: Repo Analyst │
│ (SQLite Persistence)  │              │ Static AST / Pom scan │
└───────────┬───────────┘              └───────────┬───────────┘
            │                                      │
            └─────────────────┬────────────────────┘
                              │
                              ▼
                   ┌───────────────────────┐
                   │ Agent 2: Task Planner │
                   │  Top Sprint Backlog   │
                   └──────────┬────────────┘
                              │
                              ▼
                   ┌───────────────────────┐
                   │ Agent 3: Developer    │
                   │ Java 21 & React Code  │
                   └──────────┬────────────┘
                              │
                              ▼
                   ┌───────────────────────┐
                   │ Agent 4: Tester       │ <────┐ (Bounded Repair Loop)
                   │  Stack-Aware Testing  │ ─────┘ (Up to 2 Retries)
                   │  • Maven / JUnit 5    │
                   │  • Vite / TypeScript  │
                   └──────────┬────────────┘
                              │
                              ▼ (Tests Pass)
                   ┌───────────────────────┐
                   │ Agent 5: Reviewer     │
                   │ Security & SOLID Gate │
                   └──────────┬────────────┘
                              │
                              ▼ (Score >= 7)
                   ┌───────────────────────┐
                   │ Agent 6: GitHub Agent │
                   │ Branch -> Commit -> PR│
                   └───────────────────────┘
```

### The 6 Specialized Agents

| # | Agent Name | Core Responsibility |
|:---:|:---|:---|
| **1** | **Repository Analyst** | Scans `pom.xml`, controllers, services, repositories, DTOs, and frontend components to detect technical debt and missing test scenarios. |
| **2** | **Task Planner** | Evaluates the 7-day product roadmap against completed task history in SQLite to plan actionable, deduplicated sprint tasks (max 2/day). |
| **3** | **Developer Agent** | Implements clean, maintainable code following SOLID principles, Bean Validation, and modern design patterns. |
| **4** | **Testing Agent** | Stack-aware testing engine. Verifies Java with Maven (`mvn test`), React with Vite build and TypeScript checks, and Python with Pytest. |
| **5** | **Code Reviewer** | Analyzes git diffs for null safety, security vulnerabilities, OWASP standards, and code quality before approval. |
| **6** | **GitHub Agent** | Commits to dedicated feature branches (`agent/improve-task_xxx`), pushes changes, and creates comprehensive Pull Requests. |

---

## 🔒 Safety & Production Guardrails

1. **No Direct Pushes to Protected Branches**: All autonomous changes are committed to isolated feature branches.
2. **Never Force-Push**: Force-pushing is strictly forbidden and blocked.
3. **Strict Extension Allowlist**: Modifications are constrained strictly to `.java`, `.tsx`, `.ts`, `.css`, `.html`, `.xml`, `.properties`, `.yml`, `.sql`, and `.md`.
4. **Denylist Protections**: Files matching `.env*`, `credentials`, `id_rsa`, or `secrets.json` are rejected with errors.
5. **Pre-Commit Verification**: No code is committed unless the target stack's tests compile and pass.
6. **Bounded Repair Limit**: If a build fails, the Developer Agent is permitted at most 2 targeted repair attempts; otherwise, changes are rolled back.
7. **Human Approval Gate**: Pull requests require human review and merge (`auto_merge: false`).

---

## 🛠️ Multi-Stack Technology

### Autonomous Coding Agent
- **Language**: Python 3.11+
- **LLM Engine**: [Groq API](https://console.groq.com) (`llama-3.3-70b-versatile`) with offline fallback simulation engine
- **Libraries**: LangChain, Pydantic v2, GitPython, HTTPX
- **Persistence**: SQLite (`data/agent_tasks.db`)
- **CI/CD Automation**: GitHub Actions scheduled daily with manual dispatch

### CareerPilot AI Application
- **Backend**: Java 21, Spring Boot 3.3.0, Spring Data JPA, Hibernate, Bean Validation
- **Database**: PostgreSQL (Production) / H2 In-Memory (Local Testing)
- **Security**: BCrypt password hashing (`spring-security-crypto`), JWT session support
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Containerization**: Multi-stage Docker build with Alpine JRE 21

---

## 💻 Local Setup & Execution Guide

### 1. Clone the Repository
```bash
git clone https://github.com/laxman235/AI-GitHub-Coding-Agent.git
cd AI-GitHub-Coding-Agent
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
Provide your Groq API key and GitHub credentials in `.env` (this file is excluded from git):
```ini
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GITHUB_TOKEN=ghp_your_github_token
REPO_OWNER=laxman235
REPO_NAME=AI-GitHub-Coding-Agent
```

### 3. Install Agent Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run the Agent Test Suite
```bash
python -m pytest tests/ -v
```

### 5. Execute the Autonomous Coding Agent
```bash
# Run simulation mode without remote git pushes:
python -m agent.main --dry-run --verbose

# Run production cycle (executing sprint tasks):
python -m agent.main --force --verbose
```

### 6. Run CareerPilot AI Locally

**Backend (Spring Boot)**:
```bash
cd sample-spring-boot-app
mvn spring-boot:run
# Backend running at http://localhost:8080
```

**Frontend (React Vite)**:
```bash
cd careerpilot-ui
npm install
npm run dev
# Frontend running at http://localhost:5173
```

---

## 📅 7-Day Autonomous Sprint Roadmap

- [x] **Day 1: Foundation & Auth Baseline**: `User` entity, `Role` enum, DTO validation, JPA repository, and initial unit tests.
- [x] **Day 2: Authentication & Session**: REST login/registration endpoints, BCrypt password hashing, session persistence, and UI modal tabs.
- [ ] **Day 3: Job Discovery Engine**: `Job` entity, multi-attribute search queries, `JobService`, and `JobController` REST endpoints.
- [ ] **Day 4: AI Resume Matching & ATS Scorer**: ATS semantic keyword extraction, score calculation (0–100%), and missing skills breakdown.
- [ ] **Day 5: Job Scraping Connectors**: Automated job ingestion connectors with anti-bot compliance.
- [ ] **Day 6: Application Tracker & Dashboard**: Kanban application status tracker, saved jobs, and real-time statistics grid.
- [ ] **Day 7: E2E Integration & Final Sprint Report**: Multi-stack end-to-end integration verification, security audit, and final sprint report.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
