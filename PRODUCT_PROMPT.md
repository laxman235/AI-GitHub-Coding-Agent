# 🎯 PRODUCT REQUIREMENTS – CAREERPILOT AI

## 1. Product Overview

**Product Name:** CareerPilot AI

**Product Type:** Agentic AI-powered Job Search, Resume Optimization and Career Management Platform.

**Product Vision:**

Build an autonomous AI career assistant that searches for relevant jobs daily, analyzes job descriptions, recommends matching opportunities, improves candidate resumes and manages the entire job application journey.

The platform should provide capabilities similar to Naukri and LinkedIn Jobs, enhanced with autonomous AI agents.

### Target Users
- Software developers
- Java Backend Developers
- Full Stack Developers
- Experienced IT professionals
- Fresh graduates
- Job seekers looking for career growth

### Target Technology Stack

**Backend**
- Java 21
- Spring Boot 3.x
- Spring Security
- Spring Data JPA
- Hibernate
- MySQL
- REST APIs
- Apache Kafka
- Spring Scheduler
- Spring AI / LangChain4j

**Frontend**
- React.js
- TypeScript
- Material UI
- HTML, CSS and JavaScript

**AI Integration**
- OpenAI API / Gemini API
- LLM-based job matching
- Resume analysis
- AI content generation
- Agentic AI workflows

**Infrastructure**
- Docker
- GitHub Actions
- AWS
- Maven
- JUnit 5
- Mockito

---

## 2. Core Modules & Features

### Module 1: User Authentication & Profile Management

- [ ] User registration and login.
- [ ] JWT authentication.
- [ ] BCrypt password encryption.
- [ ] User roles: USER and ADMIN.
- [ ] Candidate profile management.
- [ ] Store name, email, phone, location and experience.
- [ ] Store current designation and expected salary.
- [ ] Store technical skills and preferred technologies.
- [ ] Configure preferred job locations.
- [ ] Configure remote, hybrid and office preferences.
- [ ] Configure preferred job portals.
- [ ] Configure job-search frequency.
- [ ] Profile update and password reset.
- [ ] Unit and integration tests.

### Module 2: Resume & CV Management

- [ ] Upload existing resume in PDF and DOCX.
- [ ] Extract resume text.
- [ ] Analyze resume using AI.
- [ ] Identify technical skills.
- [ ] Extract experience and education.
- [ ] Identify missing technical keywords.
- [ ] Analyze resume formatting.
- [ ] Generate ATS-friendly resumes.
- [ ] Generate professional career summaries.
- [ ] Improve project descriptions.
- [ ] Improve professional experience descriptions.
- [ ] Customize resume according to job descriptions.
- [ ] Generate multiple resume versions.
- [ ] Download resume in PDF and DOCX.
- [ ] Maintain resume version history.
- [ ] Never change factual employment or educational details without user approval.

### Module 3: Autonomous Daily Job Search Agent

- [ ] Create an autonomous job search agent.
- [ ] Run scheduled job searches daily.
- [ ] Use Spring Scheduler for scheduled execution.
- [ ] Search supported job sources, including Naukri, LinkedIn Jobs and other job boards.
- [ ] Use official APIs, authorized integrations or permitted job feeds.
- [ ] Allow users to configure preferred job portals.
- [ ] Search jobs by designation.
- [ ] Search jobs by technical skills.
- [ ] Search jobs by experience.
- [ ] Search jobs by location.
- [ ] Filter jobs by salary.
- [ ] Filter jobs by remote, hybrid and office work.
- [ ] Find recently posted jobs.
- [ ] Avoid duplicate job listings.
- [ ] Store job title, company, location, salary, description and original job URL.
- [ ] Store job posting date when available.
- [ ] Track last search execution.
- [ ] Handle source failures and retry mechanisms.
- [ ] Maintain job search history.

### Module 4: AI Job Matching & Recommendation Engine

- [ ] Analyze candidate resume.
- [ ] Analyze job descriptions.
- [ ] Match candidate skills against job requirements.
- [ ] Calculate job matching percentage.
- [ ] Compare experience requirements.
- [ ] Compare location preferences.
- [ ] Compare salary expectations.
- [ ] Generate personalized job recommendations.
- [ ] Explain why a job is recommended.
- [ ] Identify missing skills.
- [ ] Rank jobs based on relevance.
- [ ] Provide high, medium and low match classifications.
- [ ] Allow users to save favorite jobs.
- [ ] Provide recommendation history.

### Module 5: AI Resume Optimization Agent

- [ ] Accept job description as input.
- [ ] Compare job description with candidate resume.
- [ ] Identify important missing keywords.
- [ ] Generate job-specific professional summaries.
- [ ] Improve project descriptions.
- [ ] Suggest relevant technical skills.
- [ ] Optimize experience descriptions.
- [ ] Generate customized resumes.
- [ ] Compare original and optimized resumes.
- [ ] Provide an ATS compatibility checklist.
- [ ] Ask for approval before saving a new resume version.
- [ ] Never fabricate candidate experience or skills.

### Module 6: Job Application Management

- [ ] Save recommended jobs.
- [ ] Track job applications.
- [ ] Store company information.
- [ ] Store job application URLs.
- [ ] Track application dates.
- [ ] Application statuses: SAVED, APPLIED, UNDER_REVIEW, SHORTLISTED, INTERVIEW, REJECTED, OFFERED.
- [ ] Add recruiter information.
- [ ] Add interview dates.
- [ ] Add application notes.
- [ ] Track application history.
- [ ] Generate application statistics.
- [ ] Prevent duplicate application records.
- [ ] Support manual application status updates.
- [ ] Require user approval before submitting any application.

### Module 7: AI Interview Preparation Agent

- [ ] Generate Java interview questions.
- [ ] Generate Java 8 and Java 21 questions.
- [ ] Generate Spring Boot questions.
- [ ] Generate Microservices questions.
- [ ] Generate Hibernate and JPA questions.
- [ ] Generate SQL and MySQL questions.
- [ ] Generate Kafka questions.
- [ ] Generate coding challenges.
- [ ] Generate questions based on job descriptions.
- [ ] Generate company-specific preparation plans.
- [ ] Evaluate candidate answers.
- [ ] Provide explanations and improvement suggestions.
- [ ] Maintain interview preparation history.

### Module 8: Notification & Daily Reports

- [ ] Email notifications for new matching jobs.
- [ ] Daily job recommendation summary.
- [ ] Notify users about high-matching jobs.
- [ ] Notify users about upcoming interviews.
- [ ] Send resume improvement suggestions.
- [ ] Send application status reminders.
- [ ] Support email and in-app notifications.
- [ ] Use Kafka for asynchronous notification processing.
- [ ] Allow notification preferences.

### Module 9: Admin Dashboard & Analytics

- [ ] Total registered users.
- [ ] Total jobs collected.
- [ ] Total active job sources.
- [ ] Total job applications.
- [ ] Total resume analyses.
- [ ] Daily job search statistics.
- [ ] AI API usage statistics.
- [ ] Job source health monitoring.
- [ ] Manage users.
- [ ] Manage job source configurations.
- [ ] Monitor agent execution logs.
- [ ] Monitor failed scheduled jobs.

---

## 3. Agentic AI Architecture

Build independent AI agents that work together.

### Agent 1: Job Discovery Agent
Responsible for discovering new job opportunities from authorized job sources.

### Agent 2: Job Analysis Agent
Reads job descriptions and extracts required skills, experience, location and salary information.

### Agent 3: Resume Analysis Agent
Analyzes candidate resumes and extracts professional information.

### Agent 4: Job Matching Agent
Compares candidate profiles with job requirements and calculates matching scores.

### Agent 5: Resume Optimization Agent
Creates customized resumes based on selected job descriptions.

### Agent 6: Interview Preparation Agent
Creates interview questions and personalized preparation plans.

### Agent 7: Notification Agent
Sends daily job recommendations and important career notifications.

### Agent Orchestrator
Coordinates all agents, manages execution order, handles failures and maintains workflow status.

---

## 4. Architecture & Quality Requirements

1. Use layered architecture: Controller, Service, Repository and Entity.
2. Use constructor-based dependency injection.
3. Use Java 21 features where appropriate.
4. Use DTO records for API requests and responses.
5. Implement Bean Validation.
6. Implement GlobalExceptionHandler using @RestControllerAdvice.
7. Use Spring Security and JWT.
8. Use MySQL as the primary database.
9. Use Apache Kafka for asynchronous communication.
10. Use Spring Scheduler for recurring job searches.
11. Implement pagination, sorting and filtering.
12. Implement structured application logging.
13. Write JUnit 5 and Mockito tests.
14. Implement integration tests.
15. Document APIs using Swagger/OpenAPI.
16. Use environment variables for API keys and secrets.
17. Implement retry mechanisms for external integrations.
18. Protect user resumes and personal information.
19. Implement role-based authorization.
20. Follow SOLID principles and clean code architecture.

---

## 5. Important REST API Endpoints

### Authentication
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/profile

### Resume
- POST /api/resumes/upload
- GET /api/resumes
- POST /api/resumes/analyze
- POST /api/resumes/optimize/{jobId}
- GET /api/resumes/{id}/download

### Job Search
- POST /api/jobs/search
- GET /api/jobs
- GET /api/jobs/{id}
- GET /api/jobs/recommended
- GET /api/jobs/search-history

### Job Applications
- POST /api/applications
- GET /api/applications
- GET /api/applications/{id}
- PUT /api/applications/{id}/status

### AI Interview Preparation
- POST /api/interviews/generate-questions
- POST /api/interviews/evaluate-answer
- GET /api/interviews/preparation-history

### Notifications
- GET /api/notifications
- PUT /api/notifications/{id}/read
- GET /api/reports/daily

### Agent Management
- POST /api/agents/job-search/run
- GET /api/agents/status
- GET /api/agents/execution-history
- GET /api/agents/execution-history/{id}

---

## 6. Autonomous Coding Agent Development Instructions

The coding agent must:

1. Read this PRODUCT_REQUIREMENTS.md before each development cycle.
2. Inspect the existing application before writing code.
3. Identify implemented and missing features.
4. Maintain existing working functionality.
5. Prioritize features according to development phases.
6. Implement one logical feature at a time.
7. Generate required entities, DTOs, repositories, services and controllers.
8. Write unit and integration tests.
9. Run Maven tests after implementation.
10. Fix compilation and test failures.
11. Update this requirements document after successful implementation.
12. Never mark a feature complete if it has not been tested.
13. Maintain backward compatibility.
14. Provide a summary of changes after each development cycle.
15. Never invent external API integrations or claim unsupported job portals are connected.

---

## 7. Development Roadmap

**Phase 1:** Authentication and Candidate Profile.

**Phase 2:** Resume Upload and AI Resume Analysis.

**Phase 3:** Daily Job Discovery Agent.

**Phase 4:** AI Job Matching and Recommendations.

**Phase 5:** Resume Optimization Agent.

**Phase 6:** Application Tracking.

**Phase 7:** Interview Preparation Agent.

**Phase 8:** Notifications and Daily Reports.

**Phase 9:** Admin Dashboard and Analytics.

**Phase 10:** Docker, Cloud Deployment and Production Optimization.

---

## 8. Definition of Done

A feature is complete only when:

- [ ] Implementation is complete.
- [ ] APIs are functional.
- [ ] Validation is implemented.
- [ ] Exception handling is implemented.
- [ ] Unit tests pass.
- [ ] Integration tests pass where applicable.
- [ ] Security requirements are satisfied.
- [ ] API documentation is updated.
- [ ] Existing functionality is not broken.
- [ ] Product requirements are updated.

**Final Product Goal:**

Build a production-ready Agentic AI Career Assistant that autonomously discovers relevant job opportunities every day, recommends the best jobs, optimizes candidate resumes, and helps candidates manage their complete job search journey.