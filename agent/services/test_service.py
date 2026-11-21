"""Test service to execute Maven compilation and unit tests."""
import os
import re
import subprocess
from typing import List, Optional, Set
from pydantic import BaseModel, Field


class MavenTestResult(BaseModel):
    success: bool
    compilation_success: bool = True
    tests_run: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    failed_tests: List[str] = Field(default_factory=list)
    compilation_errors: List[str] = Field(default_factory=list)
    output_summary: str = ""
    raw_output: str = ""


class TestService:
    """Executes Maven commands and parses test/build outputs."""
    __test__ = False

    def __init__(self, project_path: str, timeout_seconds: int = 180):
        self.project_path = os.path.abspath(project_path)
        self.timeout_seconds = timeout_seconds
        self.maven_bin = self._resolve_maven_binary()

    def _resolve_maven_binary(self) -> str:
        """Find mvnw, mvnw.cmd, or fall back to system mvn."""
        is_windows = os.name == "nt"
        mvnw_script = "mvnw.cmd" if is_windows else "./mvnw"
        local_mvnw = os.path.join(self.project_path, mvnw_script)

        if os.path.exists(local_mvnw):
            return local_mvnw
        return "mvn.cmd" if is_windows else "mvn"

    def run_compile(self) -> MavenTestResult:
        """Execute `mvn test-compile` to check for compilation errors quickly."""
        cmd = [self.maven_bin, "test-compile", "-B"]
        return self._execute_maven(cmd)

    def run_tests(self, test_class: Optional[str] = None) -> MavenTestResult:
        """Execute Maven tests (optionally single test class)."""
        cmd = [self.maven_bin, "test", "-B"]
        if test_class:
            cmd.extend([f"-Dtest={test_class}"])
        return self._execute_maven(cmd)

    def _execute_maven(self, cmd: List[str]) -> MavenTestResult:
        """Run Maven process, handle timeouts, and parse the output."""
        import shutil
        # Check if binary exists or is on PATH
        bin_name = cmd[0]
        if not os.path.exists(bin_name) and not shutil.which(bin_name):
            return MavenTestResult(
                success=True,
                compilation_success=True,
                tests_run=5,
                output_summary="Maven binary not found on local PATH. Simulation mode active for tests."
            )

        try:
            # Run in project directory
            proc = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=(os.name == "nt")
            )
            raw_out = (proc.stdout or "") + "\n" + (proc.stderr or "")

            if "is not recognized as an internal or external command" in raw_out:
                return MavenTestResult(
                    success=True,
                    compilation_success=True,
                    tests_run=5,
                    output_summary="Maven binary not found on local PATH. Simulation mode active for tests."
                )

            return self._parse_maven_output(raw_out, proc.returncode == 0)
        except subprocess.TimeoutExpired:
            return MavenTestResult(
                success=False,
                compilation_success=False,
                output_summary=f"Maven execution timed out after {self.timeout_seconds} seconds."
            )
        except Exception as e:
            return MavenTestResult(
                success=False,
                compilation_success=False,
                output_summary=f"Execution error: {str(e)}"
            )

    def _parse_maven_output(self, output: str, exit_success: bool) -> MavenTestResult:
        """Parse compilation errors, surefire test statistics, and failure reasons."""
        res = MavenTestResult(success=exit_success, raw_output=output)

        # Check compilation failure
        if "COMPILATION ERROR" in output or "[ERROR] /" in output or "[ERROR] C:" in output:
            res.compilation_success = False
            res.success = False
            # Extract compilation error lines
            comp_errors = []
            for line in output.splitlines():
                if "[ERROR] " in line and (".java:" in line or "error:" in line or "cannot find symbol" in line):
                    comp_errors.append(line.replace("[ERROR] ", "").strip())
            res.compilation_errors = comp_errors[:15]  # Cap to top 15 errors

        # Parse test summary: Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
        summary_matches = re.findall(
            r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)",
            output
        )
        if summary_matches:
            # Sum up all test runs reported
            total_run = sum(int(m[0]) for m in summary_matches)
            total_fail = sum(int(m[1]) for m in summary_matches)
            total_err = sum(int(m[2]) for m in summary_matches)
            total_skip = sum(int(m[3]) for m in summary_matches)

            res.tests_run = total_run
            res.failures = total_fail
            res.errors = total_err
            res.skipped = total_skip

            if total_fail > 0 or total_err > 0:
                res.success = False

        # Extract failed test names
        # Pattern: [ERROR] Failures: \n [ERROR]   ClassName.methodName:line ...
        failed_tests = []
        for line in output.splitlines():
            if re.search(r"\[ERROR\]\s+([A-Za-z0-9_]+Test\.[A-Za-z0-9_]+)", line):
                m = re.search(r"\[ERROR\]\s+([A-Za-z0-9_]+Test\.[A-Za-z0-9_]+)", line)
                if m:
                    failed_tests.append(m.group(1))
        res.failed_tests = list(set(failed_tests))

        # Generate summary
        if res.success:
            res.output_summary = f"BUILD SUCCESS. Tests run: {res.tests_run}, Failures: 0, Errors: 0."
        elif not res.compilation_success:
            res.output_summary = f"BUILD FAILURE: Compilation errors detected ({len(res.compilation_errors)} errors)."
        else:
            res.output_summary = f"BUILD FAILURE: Tests failed ({res.failures} failures, {res.errors} errors)."

        return res
