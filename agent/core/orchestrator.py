"""Central orchestrator coordinating the multi-agent autonomous coding workflow."""
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel

from agent.core.config import AgentConfig
from agent.core.llm import LLMClient
from agent.core.state import TaskExecutionContext
from agent.database.models import RunRecord, TaskRecord, RunStatus, TaskStatus
from agent.database.repository import TaskDatabase
from agent.services.repository_service import RepositoryService
from agent.services.git_service import GitService
from agent.services.github_service import GitHubService
from agent.services.test_service import TestService
from agent.services.report_service import ReportService
from agent.agents.repository_analyst import RepositoryAnalystAgent
from agent.agents.task_planner import TaskPlannerAgent
from agent.agents.developer import DeveloperAgent
from agent.agents.tester import TesterAgent
from agent.agents.reviewer import CodeReviewerAgent
from agent.agents.github_agent import GitHubAgent

logger = logging.getLogger(__name__)


class ExecutionSummary(BaseModel):
    run_id: str
    status: RunStatus
    tasks_identified: int
    tasks_attempted: int
    tasks_completed: int
    tasks_failed: int
    total_tokens_used: int
    report_markdown_path: str
    report_json_path: str


class AgentOrchestrator:
    """End-to-end multi-agent execution orchestrator."""

    def __init__(self, config: AgentConfig, repo_root: Optional[str] = None):
        self.config = config
        self.repo_root = os.path.abspath(repo_root or ".")
        self.target_path = os.path.abspath(os.path.join(self.repo_root, config.target_repo_path))

        # Ensure target path exists (or points to repo_root if target is empty)
        if not os.path.exists(self.target_path):
            self.target_path = self.repo_root

        # Initialize services
        self.db = TaskDatabase(os.path.join(self.repo_root, config.database.db_path))
        self.repo_service = RepositoryService(self.target_path)
        
        try:
            self.git_service = GitService(self.repo_root)
        except Exception:
            logger.warning(f"Git repository not found at {self.repo_root}. Git operations will be simulated.")
            self.git_service = None

        self.github_service = GitHubService(
            token=config.github.token,
            owner=config.github.owner,
            repo=config.github.repo
        )
        self.test_service = TestService(
            project_path=self.target_path,
            timeout_seconds=config.groq.timeout_seconds * 3
        )
        self.report_service = ReportService(os.path.join(self.repo_root, config.reports.output_dir))

        # Initialize LLM Client
        self.llm = LLMClient(
            api_key=config.groq.api_key,
            model=config.groq.model,
            temperature=config.groq.temperature,
            max_retries=config.groq.max_retries,
            timeout_seconds=config.groq.timeout_seconds
        )

        # Initialize Specialized Agents
        self.analyst_agent = RepositoryAnalystAgent(self.llm, self.repo_service)
        self.planner_agent = TaskPlannerAgent(self.llm, self.db)
        self.developer_agent = DeveloperAgent(self.llm, self.repo_service)
        self.tester_agent = TesterAgent(self.test_service)
        self.reviewer_agent = CodeReviewerAgent(self.llm)
        self.github_agent = GitHubAgent(self.git_service, self.github_service) if self.git_service else None

    def execute(self, max_tasks: Optional[int] = None, dry_run: Optional[bool] = None) -> ExecutionSummary:
        """Run the daily autonomous coding cycle."""
        is_dry_run = dry_run if dry_run is not None else self.config.execution.dry_run
        daily_limit = max_tasks if max_tasks is not None else self.config.execution.max_daily_tasks

        run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"--- Starting Autonomous Coding Cycle [{run_id}] (Dry-Run: {is_dry_run}) ---")
        run_record = self.db.start_run(run_id, trigger="MANUAL" if is_dry_run else "SCHEDULED")

        # 1. Baseline verification: Run initial compile check
        logger.info("[Step 1] Verifying repository baseline and Maven status...")
        baseline_test = self.tester_agent.verify_compilation()
        if not baseline_test.compilation_success and not is_dry_run:
            logger.warning(f"Baseline repository has compilation errors: {baseline_test.compilation_errors}")

        # 2. Agent 1: Repository Analyst
        logger.info("[Step 2] Invoking Repository Analyst Agent...")
        arch, findings = self.analyst_agent.analyze()
        logger.info(f"Analysis complete: {len(arch.controllers)} controllers, {len(arch.services)} services, {len(arch.missing_test_targets)} missing tests.")

        # 3. Agent 2: Task Planner
        logger.info(f"[Step 3] Invoking Task Planner Agent (Limit: {daily_limit} tasks)...")
        tasks = self.planner_agent.plan_tasks(arch, findings, run_id, max_tasks=daily_limit)
        logger.info(f"Planned {len(tasks)} actionable tasks.")

        attempted_tasks: List[TaskRecord] = []
        completed_tasks: List[TaskRecord] = []
        failed_tasks: List[TaskRecord] = []

        # 4. Execute Tasks Sequentially
        for idx, task in enumerate(tasks, start=1):
            logger.info(f"\n>>> Executing Task {idx}/{len(tasks)}: '{task.title}' [{task.category.value}] <<<")
            task.status = TaskStatus.IN_PROGRESS
            task.branch_name = f"{self.config.github.branch_prefix}{task.id}"
            self.db.update_task(task)
            attempted_tasks.append(task)

            # Isolated Branch Creation (in non-dry-run mode)
            if self.git_service and not is_dry_run:
                self.git_service.create_feature_branch(task.branch_name, self.config.github.target_branch)

            success = self._execute_task_lifecycle(task, is_dry_run)

            # Update DB status
            self.db.update_task(task)

            if success:
                completed_tasks.append(task)
                logger.info(f"Task {task.id} successfully completed and committed!")
            else:
                failed_tasks.append(task)
                logger.warning(f"Task {task.id} failed: {task.error_message}")
                # Rollback changes to keep tree clean
                if self.git_service and not is_dry_run:
                    self.git_service.rollback(self.config.github.target_branch)

        # 5. Summarize and persist run state
        if not attempted_tasks:
            final_status = RunStatus.SUCCESS
            logger.info("No new or uncompleted tasks found for this cycle. Repository is up-to-date!")
        elif len(completed_tasks) == len(attempted_tasks):
            final_status = RunStatus.SUCCESS
        elif completed_tasks:
            final_status = RunStatus.PARTIAL_SUCCESS
        else:
            final_status = RunStatus.FAILED

        self.db.finish_run(
            run_id=run_id,
            status=final_status,
            tasks_identified=len(tasks),
            tasks_attempted=len(attempted_tasks),
            tasks_completed=len(completed_tasks),
            tasks_failed=len(failed_tasks),
            tokens_used=self.llm.total_tokens_used
        )

        run_record.status = final_status
        run_record.tasks_identified = len(tasks)
        run_record.tasks_attempted = len(attempted_tasks)
        run_record.tasks_completed = len(completed_tasks)
        run_record.tasks_failed = len(failed_tasks)
        run_record.total_tokens_used = self.llm.total_tokens_used

        # 6. Generate Daily Reports
        logger.info("[Step 6] Generating daily execution reports...")
        report_files = self.report_service.generate_daily_report(
            run_record=run_record,
            tasks=attempted_tasks,
            repo_name=f"{self.config.github.owner}/{self.config.github.repo}",
            groq_model=self.config.groq.model,
            target_branch=self.config.github.target_branch
        )

        logger.info(f"Report saved to: {report_files['markdown_path']}")

        return ExecutionSummary(
            run_id=run_id,
            status=final_status,
            tasks_identified=len(tasks),
            tasks_attempted=len(attempted_tasks),
            tasks_completed=len(completed_tasks),
            tasks_failed=len(failed_tasks),
            total_tokens_used=self.llm.total_tokens_used,
            report_markdown_path=report_files["markdown_path"],
            report_json_path=report_files["json_path"]
        )

    def _execute_task_lifecycle(self, task: TaskRecord, dry_run: bool) -> bool:
        """Execute developer -> test -> repair -> review -> git publish lifecycle for a task."""
        modified_paths: List[str] = []

        # Keep backups of files to cleanly restore in dry-run mode or on failure
        file_backups = {}
        for f_path in task.target_files:
            try:
                file_backups[f_path] = self.repo_service.read_file_safe(f_path)
            except Exception:
                file_backups[f_path] = None

        try:
            # Step A: Developer Agent generates solution
            logger.info("-> Invoking Developer Agent...")
            solution = self.developer_agent.implement_task(task)

            # Step B: Validate and apply file operations
            for f_op in solution.files:
                if f_op.path not in file_backups:
                    try:
                        file_backups[f_op.path] = self.repo_service.read_file_safe(f_op.path)
                    except Exception:
                        file_backups[f_op.path] = None

                self.repo_service.write_file_safe(
                    f_op.path,
                    f_op.content,
                    self.config.execution.allowlist_extensions
                )
                full_written_path = os.path.join(self.target_path, f_op.path)
                repo_rel_path = os.path.relpath(full_written_path, self.repo_root)
                modified_paths.append(repo_rel_path)

            # Step C: Testing Agent verifies compilation & tests
            logger.info("-> Invoking Testing Agent (Maven compile and test)...")
            test_res = self.tester_agent.run_tests()

            # Step D: Bounded Repair Loop if tests failed
            repair_attempts = 0
            while not test_res.success and repair_attempts < self.config.execution.max_repair_attempts:
                repair_attempts += 1
                task.repair_attempts = repair_attempts
                logger.info(f"-> Tests failed. Invoking Repair Attempt {repair_attempts}/{self.config.execution.max_repair_attempts}...")

                error_summary = test_res.raw_output[-2500:] if test_res.raw_output else test_res.output_summary
                solution = self.developer_agent.repair_code(task, error_summary, solution)

                for f_op in solution.files:
                    self.repo_service.write_file_safe(
                        f_op.path,
                        f_op.content,
                        self.config.execution.allowlist_extensions
                    )
                    full_written_path = os.path.join(self.target_path, f_op.path)
                    repo_rel_path = os.path.relpath(full_written_path, self.repo_root)
                    if repo_rel_path not in modified_paths:
                        modified_paths.append(repo_rel_path)

                test_res = self.tester_agent.run_tests()

            if not test_res.success:
                task.status = TaskStatus.BUILD_FAILED if not test_res.compilation_success else TaskStatus.TEST_FAILED
                task.error_message = f"Tests failed after {repair_attempts} repairs: {test_res.output_summary}"
                # Restore original file states on failure
                self._restore_backups(file_backups)
                return False

            # Step E: Code Reviewer Agent validates the diff
            logger.info("-> Invoking Code Reviewer Agent...")
            diff_text = self.git_service.get_diff() if self.git_service else "Diff unavailable (no git)"
            review = self.reviewer_agent.review(task, diff_text)
            task.reviewer_score = review.score

            if not review.approved or review.score < 7:
                task.status = TaskStatus.REVIEW_REJECTED
                task.error_message = f"Review rejected (Score: {review.score}/10). Comments: {', '.join(review.comments)}"
                # Restore original file states on reject
                self._restore_backups(file_backups)
                return False

            # Step F: GitHub Agent stages, commits, pushes, and opens PR
            logger.info("-> Invoking GitHub Agent to commit and create PR...")
            if self.github_agent:
                commit_sha, pr_url = self.github_agent.commit_and_publish(
                    task=task,
                    modified_files=modified_paths,
                    review=review,
                    target_branch=self.config.github.target_branch,
                    auto_merge=self.config.github.auto_merge,
                    dry_run=dry_run
                )
                task.commit_sha = commit_sha
                task.pr_url = pr_url
            else:
                task.commit_sha = "simulated_sha"
                task.pr_url = f"https://github.com/{self.config.github.owner}/{self.config.github.repo}/pull/simulated"

            task.status = TaskStatus.COMPLETED

            # If dry_run, restore files so working tree remains pristine
            if dry_run:
                self._restore_backups(file_backups)

            return True

        except Exception as e:
            logger.error(f"Task lifecycle error: {e}", exc_info=True)
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self._restore_backups(file_backups)
            return False

    def _restore_backups(self, backups: dict) -> None:
        """Safely restore file backups."""
        for rel_path, content in backups.items():
            try:
                full_path = os.path.join(self.target_path, rel_path)
                if content is None:
                    if os.path.exists(full_path):
                        os.remove(full_path)
                else:
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
            except Exception:
                pass
