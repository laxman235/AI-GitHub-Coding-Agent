import os
import tempfile
import pytest
from agent.database.models import TaskRecord, RunRecord, TaskStatus, RunStatus, TaskCategory
from agent.database.repository import TaskDatabase


@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_tasks.db")
    db = TaskDatabase(db_path)
    yield db


def test_run_lifecycle(temp_db):
    run = temp_db.start_run("run_123", trigger="SCHEDULED")
    assert run.id == "run_123"
    assert run.status == RunStatus.RUNNING

    temp_db.finish_run(
        run_id="run_123",
        status=RunStatus.SUCCESS,
        tasks_identified=3,
        tasks_attempted=3,
        tasks_completed=3,
        tasks_failed=0,
        tokens_used=1500
    )


def test_task_lifecycle_and_deduplication(temp_db):
    temp_db.start_run("run_test", trigger="MANUAL")

    task = TaskRecord(
        id="task_001",
        run_id="run_test",
        title="Add Bean Validation to ProductDto",
        category=TaskCategory.FEATURE,
        description="Add Bean Validation annotations to ProductDto.",
        target_files=["src/main/java/com/example/demo/dto/ProductDto.java"],
        priority=8,
        status=TaskStatus.PENDING
    )
    task_id = temp_db.create_task(task)
    assert task_id == "task_001"

    # Mark completed
    task.status = TaskStatus.COMPLETED
    task.branch_name = "agent/improve-task_001"
    task.commit_sha = "abc1234"
    temp_db.update_task(task)

    completed_titles = temp_db.get_completed_task_titles()
    assert "add bean validation to productdto" in completed_titles

    count_today = temp_db.get_today_completed_count()
    assert count_today == 1

    tasks = temp_db.get_tasks_for_run("run_test")
    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.COMPLETED
