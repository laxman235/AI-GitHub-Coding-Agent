"""Agent 1: Repository Analyst Agent."""
import os
from typing import List
from pydantic import BaseModel, Field
from agent.core.llm import LLMClient
from agent.services.repository_service import RepositoryService, RepositoryArchitecture


class AnalystFindings(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    technical_debt: List[str] = Field(default_factory=list)
    missing_tests: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)


class RepositoryAnalystAgent:
    """Understands project architecture, technical debt, and missing tests."""

    def __init__(self, llm: LLMClient, repo_service: RepositoryService):
        self.llm = llm
        self.repo_service = repo_service
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "analyst.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Analyze the Java Spring Boot repository architecture."

    def analyze(self) -> tuple[RepositoryArchitecture, AnalystFindings]:
        """Perform static scan and LLM-driven architectural evaluation."""
        arch = self.repo_service.scan_repository()

        summary_text = (
            f"Java Version: {arch.java_version}\n"
            f"Spring Boot Version: {arch.spring_boot_version or '3.x'}\n"
            f"Dependencies ({len(arch.dependencies)}): {', '.join(arch.dependencies[:15])}\n"
            f"Controllers ({len(arch.controllers)}): {[c.class_name for c in arch.controllers]}\n"
            f"Services ({len(arch.services)}): {[s.class_name for s in arch.services]}\n"
            f"Repositories ({len(arch.repositories)}): {[r.class_name for r in arch.repositories]}\n"
            f"Entities ({len(arch.entities)}): {[e.class_name for e in arch.entities]}\n"
            f"DTOs ({len(arch.dtos)}): {[d.class_name for d in arch.dtos]}\n"
            f"Tests ({len(arch.tests)}): {[t.class_name for t in arch.tests]}\n"
            f"Missing Test Targets: {arch.missing_test_targets}\n"
        )

        user_prompt = f"Analyze this Spring Boot project structure and report findings:\n\n{summary_text}"
        findings = self.llm.generate_structured(self.prompt_template, user_prompt, AnalystFindings)
        return arch, findings
