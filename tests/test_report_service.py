import os
import json
import pytest
from agent.database.models import RunRecord, TaskRecord, RunStatus, TaskStatus, TaskCategory
from agent.services.report_service import ReportService


def test_generate_daily_report(tmp_path):
    report_service = ReportService(str(tmp_path))

    run = RunRecord(
        id="run_999",
        status=RunStatus.SUCCESS,
        tasks_identified=2,
        tasks_attempted=2,
        tasks_completed=2,
        tasks_failed=0,
        total_tokens_used=1200
    )

    task1 = TaskRecord(
        id="task_1",
        run_id="run_999",
        title="Add validation annotations",
        category=TaskCategory.FEATURE,
        description="Add Bean Validation to DTO.",
        priority=8,
        status=TaskStatus.COMPLETED,
        branch_name="agent/improve-task_1",
        pr_url="https://github.com/laxman235/AI-GitHub-Coding-Agent/pull/1",
        commit_sha="abcd123",
        reviewer_score=9
    )

    result = report_service.generate_daily_report(
        run_record=run,
        tasks=[task1],
        repo_name="laxman235/AI-GitHub-Coding-Agent",
        groq_model="llama-3.3-70b-versatile"
    )

    assert os.path.exists(result["markdown_path"])
    assert os.path.exists(result["json_path"])

    with open(result["markdown_path"], "r", encoding="utf-8") as f:
        md = f.read()
    assert "Autonomous AI Agent Daily Execution Report" in md
    assert "Add validation annotations" in md
    assert "llama-3.3-70b-versatile" in md
