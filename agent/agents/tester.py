"""Agent 4: Testing Agent."""
from typing import Optional, Union, Any
from agent.services.test_service import TestService, MavenTestResult, MultiStackTestResult


class TesterAgent:
    """Executes multi-stack test suites (Java Maven, Python pytest, React), verifies compilation, and detects regressions."""

    def __init__(self, test_service: TestService):
        self.test_service = test_service

    def verify_compilation(self) -> MavenTestResult:
        """Verify code compiles without syntax or classpath issues."""
        return self.test_service.run_compile()

    def run_tests(
        self,
        target_test_class: Optional[str] = None,
        task: Optional[Any] = None
    ) -> MultiStackTestResult:
        """Execute unit and integration tests across multi-stack architecture."""
        target_files = getattr(task, "target_files", None) if task else None
        return self.test_service.run_all_tests(
            target_test_class=target_test_class,
            target_files=target_files
        )

    def run_maven_tests_only(self, target_test_class: Optional[str] = None) -> MavenTestResult:
        """Execute Maven tests only."""
        return self.test_service.run_tests(test_class=target_test_class)
