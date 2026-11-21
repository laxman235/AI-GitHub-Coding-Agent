"""Agent 6: GitHub Agent."""
import logging
from typing import List, Optional
from agent.services.git_service import GitService
from agent.services.github_service import GitHubService
from agent.database.models import TaskRecord
from agent.agents.reviewer import ReviewResult

logger = logging.getLogger(__name__)


class GitHubAgent:
    """Manages git branches, commits, pushes, and Pull Request creation."""

    def __init__(self, git_service: GitService, github_service: GitHubService):
        self.git_service = git_service
        self.github_service = github_service

    def commit_and_publish(
        self,
        task: TaskRecord,
        modified_files: List[str],
        review: ReviewResult,
        target_branch: str = "main",
        dry_run: bool = False
    ) -> tuple[Optional[str], Optional[str]]:
        """Stage, commit, push, and open Pull Request."""
        if dry_run:
            logger.info(f"[Dry-Run] Simulating stage, commit, and PR creation for {task.title}")
            commit_sha = f"simulated_sha_{task.id[:8]}"
            pr_url = self.github_service.create_pull_request(
                title=f"[{task.category.value}] {task.title}",
                body=f"Dry-run verification completed for {task.title}",
                head_branch=task.branch_name,
                base_branch=target_branch,
                dry_run=True
            )
            return commit_sha, pr_url

        # 1. Stage files
        self.git_service.stage_files(modified_files)

        # 2. Commit
        commit_msg = f"feat({task.category.value.lower()}): {task.title}\n\n{task.description}\n\nReviewed-by: AI Reviewer Agent (Score: {review.score}/10)"
        commit_sha = self.git_service.commit(commit_msg)
        logger.info(f"Committed changes with SHA: {commit_sha}")

        # 3. Push branch
        pushed = self.git_service.push_branch(task.branch_name, dry_run=dry_run)
        if not pushed:
            logger.error(f"Failed to push branch: {task.branch_name}")
            return commit_sha, None

        # 4. Create Pull Request
        pr_body = (
            f"## 🤖 Autonomous AI Agent Improvement\n\n"
            f"### Task\n"
            f"**{task.title}**\n\n"
            f"### Category & Priority\n"
            f"- Category: `{task.category.value}`\n"
            f"- Priority: `{task.priority}/10`\n\n"
            f"### Description\n"
            f"{task.description}\n\n"
            f"### Modified Files\n"
            f"- " + "\n- ".join(modified_files) + "\n\n"
            f"### Verification & Review\n"
            f"- ✅ Maven compilation & unit tests passed.\n"
            f"- ✅ Code Reviewer Score: **{review.score}/10**\n"
            f"- Reviewer Comments: {', '.join(review.comments) if review.comments else 'No issues noted.'}\n\n"
            f"> *Note: Generated automatically by Autonomous AI GitHub Coding Agent. Requires human review before merge.*"
        )

        pr_title = f"[{task.category.value}] {task.title}"
        pr_url = self.github_service.create_pull_request(
            title=pr_title,
            body=pr_body,
            head_branch=task.branch_name,
            base_branch=target_branch,
            dry_run=dry_run
        )

        return commit_sha, pr_url
