import os
import shutil
import git
import pytest
from agent.core.config import AgentConfig
from agent.core.orchestrator import AgentOrchestrator


def test_orchestrator_dry_run(tmp_path):
    # Setup an isolated test git repository
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    repo = git.Repo.init(repo_dir)

    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test User")
        cw.set_value("user", "email", "test@example.com")

    # Copy sample-spring-boot-app into the isolated repo
    src_sample = os.path.join(os.path.dirname(__file__), "..", "sample-spring-boot-app")
    dest_sample = repo_dir / "sample-spring-boot-app"
    shutil.copytree(src_sample, dest_sample)

    readme = repo_dir / "README.md"
    readme.write_text("# Test Repo", encoding="utf-8")

    repo.git.add("-A")
    repo.index.commit("Initial test commit")

    # Configure agent to run in isolated temp repo
    config = AgentConfig()
    config.target_repo_path = "sample-spring-boot-app"
    config.execution.dry_run = True
    config.execution.max_daily_tasks = 1
    config.database.db_path = str(tmp_path / "test_tasks.db")
    config.reports.output_dir = str(tmp_path / "reports")

    orchestrator = AgentOrchestrator(config, repo_root=str(repo_dir))

    summary = orchestrator.execute(max_tasks=1, dry_run=True)
    assert summary.run_id.startswith("run_")
    assert summary.tasks_identified >= 1
    assert os.path.exists(summary.report_markdown_path)
    assert os.path.exists(summary.report_json_path)
