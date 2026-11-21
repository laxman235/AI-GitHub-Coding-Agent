"""Agent 5: Code Reviewer Agent."""
import os
from typing import List
from pydantic import BaseModel, Field
from agent.core.llm import LLMClient
from agent.database.models import TaskRecord


class ReviewResult(BaseModel):
    approved: bool
    score: int = Field(default=5, ge=1, le=10)
    comments: List[str] = Field(default_factory=list)
    security_flags: List[str] = Field(default_factory=list)


class CodeReviewerAgent:
    """Independent reviewer enforcing Java standards, security, and null safety."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "reviewer.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Review the code diff for quality, standards, and security."

    def review(self, task: TaskRecord, diff_text: str) -> ReviewResult:
        """Review unified diff and approve or reject."""
        user_prompt = (
            f"TASK REVIEW:\n"
            f"Title: {task.title}\n"
            f"Description: {task.description}\n\n"
            f"UNIFIED DIFF:\n"
            f"{diff_text}\n\n"
            f"Rigorously review the diff. Reject if incomplete, insecure, or introduces regressions."
        )

        return self.llm.generate_structured(self.prompt_template, user_prompt, ReviewResult)
