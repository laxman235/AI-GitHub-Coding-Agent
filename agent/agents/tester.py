"""Agent 4: Testing Agent."""
from agent.services.test_service import TestService, MavenTestResult


class TesterAgent:
    """Executes Maven test suites, verifies compilation, and detects regressions."""

    def __init__(self, test_service: TestService):
        self.test_service = test_service

    def verify_compilation(self) -> MavenTestResult:
        """Verify code compiles without syntax or classpath issues."""
        return self.test_service.run_compile()

    def run_tests(self, target_test_class: str = None) -> MavenTestResult:
        """Execute unit and integration tests."""
        return self.test_service.run_tests(test_class=target_test_class)
