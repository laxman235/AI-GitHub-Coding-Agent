import os
import pytest
from agent.core.llm import LLMClient
from agent.database.models import TaskRecord, TaskCategory
from agent.database.repository import TaskDatabase
from agent.services.repository_service import RepositoryService
from agent.agents.repository_analyst import RepositoryAnalystAgent
from agent.agents.task_planner import TaskPlannerAgent
from agent.agents.developer import DeveloperAgent
from agent.agents.reviewer import CodeReviewerAgent


def test_agents_in_simulated_mode(tmp_path):
    # LLMClient in simulation mode without external key
    llm = LLMClient(api_key="")
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample-spring-boot-app")
    repo_service = RepositoryService(sample_path)
    db = TaskDatabase(str(tmp_path / "test.db"))

    # Agent 1: Analyst
    analyst = RepositoryAnalystAgent(llm, repo_service)
    arch, findings = analyst.analyze()
    assert arch.java_version == "21"
    assert len(findings.strengths) >= 1

    # Agent 2: Planner
    planner = TaskPlannerAgent(llm, db)
    tasks = planner.plan_tasks(arch, findings, run_id="run_1", max_tasks=5)
    assert len(tasks) >= 1
    assert tasks[0].priority >= 1

    # Agent 3: Developer
    developer = DeveloperAgent(llm, repo_service)
    solution = developer.implement_task(tasks[0])
    assert len(solution.files) >= 1

    # Agent 5: Reviewer
    reviewer = CodeReviewerAgent(llm)
    review = reviewer.review(tasks[0], "diff --git a/test b/test")
    assert review.approved is True
    assert review.score >= 7
