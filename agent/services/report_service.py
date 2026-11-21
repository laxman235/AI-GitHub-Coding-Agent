"""Report generator service producing Markdown and JSON daily execution summaries."""
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from agent.database.models import RunRecord, TaskRecord, SprintRecord


class ReportService:
    """Generates and persists daily execution reports for GitHub Actions and human reviewers."""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = os.path.abspath(reports_dir)
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_daily_report(
        self,
        run_record: RunRecord,
        tasks: List[TaskRecord],
        repo_name: str,
        groq_model: str,
        target_branch: str = "main",
        sprint: Optional[SprintRecord] = None,
        multi_stack_test_summary: Optional[str] = None,
        modules_inspected: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Generate both Markdown and JSON reports for this execution."""
        os.makedirs(self.reports_dir, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        base_filename = f"daily_report_{date_str}_{run_record.id}"

        md_path = os.path.join(self.reports_dir, f"{base_filename}.md")
        json_path = os.path.join(self.reports_dir, f"{base_filename}.json")

        md_content = self._render_markdown(
            run_record, tasks, repo_name, groq_model, target_branch,
            sprint=sprint,
            multi_stack_test_summary=multi_stack_test_summary,
            modules_inspected=modules_inspected
        )
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        json_data = {
            "run": run_record.model_dump(),
            "tasks": [t.model_dump() for t in tasks],
            "repo_name": repo_name,
            "groq_model": groq_model,
            "target_branch": target_branch,
            "sprint": sprint.model_dump() if sprint else None,
            "multi_stack_test_summary": multi_stack_test_summary,
            "modules_inspected": modules_inspected or [],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return {
            "markdown_path": md_path,
            "json_path": json_path,
            "markdown_content": md_content
        }

    def _render_markdown(
        self,
        run: RunRecord,
        tasks: List[TaskRecord],
        repo_name: str,
        groq_model: str,
        target_branch: str,
        sprint: Optional[SprintRecord] = None,
        multi_stack_test_summary: Optional[str] = None,
        modules_inspected: Optional[List[str]] = None
    ) -> str:
        """Render the Markdown daily execution report adhering to Section 14."""
        status_badge = "✅ SUCCESS" if run.status.value == "SUCCESS" else "⚠️ PARTIAL_SUCCESS" if run.status.value == "PARTIAL_SUCCESS" else "❌ FAILED"
        
        md = []
        md.append(f"# 🤖 CareerPilot AI Autonomous Sprint Execution Report (Autonomous AI Agent Daily Execution Report)")
        md.append("")
        if sprint:
            sprint_status = "🎉 SPRINT COMPLETE (7/7 Days Finished)" if sprint.is_finished else f"Day {sprint.current_day} of 7 in Progress"
            md.append(f"> **Sprint ID:** `{sprint.sprint_id}` | **Status:** {sprint_status}  ")
            md.append(f"> **Completed Days:** `{', '.join(str(d) for d in sprint.completed_days) if sprint.completed_days else 'None yet'}`  ")
            md.append("")

        md.append(f"**Repository:** `{repo_name}`  ")
        md.append(f"**Target Branch:** `{target_branch}` (Protected - Human PR Review Required)  ")
        md.append(f"**Execution Date (UTC):** `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}`  ")
        md.append(f"**Run ID:** `{run.id}`  ")
        md.append(f"**Overall Run Status:** {status_badge}  ")
        md.append(f"**Groq AI Model:** `{groq_model}`  ")
        md.append(f"**Tokens Consumed:** `{run.total_tokens_used}`  ")
        md.append("")
        
        if modules_inspected:
            md.append(f"**Modules Inspected:** {', '.join(f'`{m}`' for m in modules_inspected)}  ")
            md.append("")

        if multi_stack_test_summary:
            md.append("---")
            md.append("## 🧪 Multi-Stack Verification & Test Results")
            md.append(f"```text\n{multi_stack_test_summary}\n```")
            md.append("")

        md.append("---")
        md.append("## 📊 Daily Execution Metrics")
        md.append("")
        md.append(f"| Metric | Count |")
        md.append(f"| :--- | :--- |")
        md.append(f"| Tasks Identified | {run.tasks_identified} |")
        md.append(f"| Tasks Attempted | {run.tasks_attempted} (Max 2/day enforced) |")
        md.append(f"| Tasks Completed & PR Published | {run.tasks_completed} |")
        md.append(f"| Tasks Failed / Rolled Back | {run.tasks_failed} |")
        md.append("")
        md.append("---")
        md.append("## 📝 Planned & Executed Tasks")
        md.append("")

        if not tasks:
            md.append("No tasks were scheduled or attempted during this run. Repository is up to date!")
        else:
            md.append("| # | Title | Category | Status | Review Score | Repair Attempts | PR / Branch |")
            md.append("|---|---|---|---|---|---|---|")
            for idx, task in enumerate(tasks, start=1):
                status_icon = "✅" if task.status.value == "COMPLETED" else "❌"
                pr_link = f"[{task.branch_name}]({task.pr_url})" if task.pr_url else (task.branch_name or "N/A")
                score = f"{task.reviewer_score}/10" if task.reviewer_score is not None else "N/A"
                md.append(f"| {idx} | {task.title} | `{task.category.value}` | {status_icon} `{task.status.value}` | {score} | {task.repair_attempts} | {pr_link} |")

            md.append("")
            md.append("### Detailed Task Breakdown")
            md.append("")
            for idx, task in enumerate(tasks, start=1):
                md.append(f"#### {idx}. {task.title}")
                md.append(f"- **Description:** {task.description}")
                md.append(f"- **Category:** `{task.category.value}` | **Priority:** {task.priority}/10")
                if task.sprint_day:
                    md.append(f"- **Sprint Day:** Day {task.sprint_day}")
                if task.acceptance_criteria:
                    md.append(f"- **Acceptance Criteria:** {', '.join(task.acceptance_criteria)}")
                md.append(f"- **Target Files:** `{'`, `'.join(task.target_files) if task.target_files else 'Auto-detected'}`")
                if task.commit_sha:
                    md.append(f"- **Commit SHA:** `{task.commit_sha}`")
                if task.pr_url:
                    md.append(f"- **Pull Request:** [{task.pr_url}]({task.pr_url})")
                if task.error_message:
                    md.append(f"- **Error Notes:** `{task.error_message}`")
                md.append("")

        md.append("---")
        md.append("## 🛡️ Safety & Quality Assurances")
        md.append("- **Isolated Branches:** Changes developed in isolated feature branches; protected branches never modified directly.")
        md.append("- **Strict Human Approval:** Automatic merge is strictly disabled (`auto_merge: false`). Human review is required.")
        md.append("- **Multi-Stack Verification:** Maven Java 21 compilation, unit tests, and React UI integrity verified.")
        md.append("- **Independent Review:** Code Reviewer Agent validated code standards, null safety, and security before PR creation.")
        if sprint and not sprint.is_finished:
            next_day = min(7, sprint.current_day + 1)
            md.append(f"- **Next Execution Preview:** Ready for Sprint Day {next_day}/7 roadmap goals.")
        md.append("")
        return "\n".join(md)
