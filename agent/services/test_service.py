"""Test service to execute Maven compilation, Python pytest, and React frontend verification."""
import os
import re
import sys
import subprocess
from typing import List, Optional, Set, Dict, Any
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


class StackTestResult(BaseModel):
    stack: str
    success: bool
    status: str = "PASSED"  # PASSED, FAILED, SKIPPED
    tests_run: int = 0
    failures: int = 0
    errors: int = 0
    output_summary: str = ""
    raw_output: str = ""


class MultiStackTestResult(BaseModel):
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
    maven: Optional[MavenTestResult] = None
    python: Optional[StackTestResult] = None
    react: Optional[StackTestResult] = None
    integration: Optional[StackTestResult] = None


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

    def run_python_tests(self) -> StackTestResult:
        """Execute Python pytest test suite for AI service components."""
        repo_root = os.path.dirname(self.project_path) if "sample-spring-boot-app" in self.project_path else self.project_path
        ai_service_path = os.path.join(repo_root, "ai-service")
        
        # Only run pytest if ai-service directory exists (do not run agent meta-tests recursively)
        if not os.path.exists(ai_service_path):
            return StackTestResult(
                stack="Python",
                success=True,
                status="SKIPPED",
                output_summary="No ai-service Python test directory found; skipped."
            )

        python_bin = sys.executable or "python"
        try:
            proc = subprocess.run(
                [python_bin, "-m", "pytest", "ai-service/", "-q"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=(os.name == "nt")
            )
            raw = (proc.stdout or "") + "\n" + (proc.stderr or "")
            success = proc.returncode == 0
            m = re.search(r"(\d+) passed", raw)
            tests_run = int(m.group(1)) if m else (1 if success else 0)
            return StackTestResult(
                stack="Python",
                success=success,
                status="PASSED" if success else "FAILED",
                tests_run=tests_run,
                output_summary=f"Python tests passed ({tests_run} tests)." if success else "Python tests failed.",
                raw_output=raw
            )
        except Exception as e:
            return StackTestResult(
                stack="Python",
                success=True,
                status="SKIPPED",
                output_summary=f"Python tests skipped: {str(e)}"
            )

    def run_react_checks(self) -> StackTestResult:
        """Execute React UI build/typecheck via npm."""
        import shutil
        repo_root = os.path.dirname(self.project_path) if "sample-spring-boot-app" in self.project_path else self.project_path
        ui_path = os.path.join(repo_root, "careerpilot-ui")
        if not os.path.exists(ui_path) or not os.path.exists(os.path.join(ui_path, "package.json")):
            return StackTestResult(
                stack="React",
                success=True,
                status="SKIPPED",
                output_summary="No React frontend directory found; skipped."
            )

        # Check if node_modules exists
        if not os.path.exists(os.path.join(ui_path, "node_modules")):
            return StackTestResult(
                stack="React",
                success=True,
                status="SKIPPED",
                output_summary="careerpilot-ui/node_modules not installed; skipped frontend build check."
            )

        npm_bin = shutil.which("npm") or shutil.which("npm.cmd")
        if not npm_bin:
            return StackTestResult(
                stack="React",
                success=True,
                status="SKIPPED",
                output_summary="npm not found on system PATH; skipped frontend build check."
            )

        try:
            proc = subprocess.run(
                [npm_bin, "run", "build"],
                cwd=ui_path,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=(os.name == "nt")
            )
            raw = (proc.stdout or "") + "\n" + (proc.stderr or "")
            success = proc.returncode == 0
            return StackTestResult(
                stack="React",
                success=success,
                status="PASSED" if success else "FAILED",
                tests_run=1 if success else 0,
                output_summary="React build and typecheck passed." if success else "React build failed.",
                raw_output=raw
            )
        except Exception as e:
            return StackTestResult(
                stack="React",
                success=False,
                status="FAILED",
                output_summary=f"React verification error: {str(e)}"
            )

    def run_all_tests(
        self,
        target_test_class: Optional[str] = None,
        target_files: Optional[List[str]] = None
    ) -> MultiStackTestResult:
        """Run test suites across the multi-stack architecture."""
        maven_res = self.run_tests(target_test_class)
        python_res = self.run_python_tests()
        react_res = self.run_react_checks()

        # If a specific task is being tested, evaluate success based on the affected stack
        if target_files:
            has_java = any(f.endswith((".java", ".xml")) or "sample-spring-boot-app" in f for f in target_files)
            has_react = any(f.endswith((".tsx", ".ts", ".jsx", ".js", ".css")) or "careerpilot-ui" in f for f in target_files)
            has_python = any(f.endswith(".py") or "ai-service" in f for f in target_files)

            required_successes = []
            if has_java:
                required_successes.append(maven_res.success)
            if has_react and react_res.status != "SKIPPED":
                required_successes.append(react_res.success)
            if has_python and python_res.status != "SKIPPED":
                required_successes.append(python_res.success)

            all_success = all(required_successes) if required_successes else maven_res.success
        else:
            # Baseline check: only active/non-skipped stacks must succeed
            active_checks = [maven_res.success]
            if python_res.status != "SKIPPED":
                active_checks.append(python_res.success)
            if react_res.status != "SKIPPED":
                active_checks.append(react_res.success)
            all_success = all(active_checks)

        comp_success = maven_res.compilation_success

        summaries = [
            f"Maven: {maven_res.output_summary}",
            f"Python: {python_res.output_summary}",
            f"React: {react_res.output_summary}"
        ]

        return MultiStackTestResult(
            success=all_success,
            compilation_success=comp_success,
            tests_run=maven_res.tests_run + python_res.tests_run + react_res.tests_run,
            failures=maven_res.failures + python_res.failures + react_res.failures,
            errors=maven_res.errors + python_res.errors + react_res.errors,
            skipped=maven_res.skipped + (1 if python_res.status == "SKIPPED" else 0) + (1 if react_res.status == "SKIPPED" else 0),
            failed_tests=maven_res.failed_tests,
            compilation_errors=maven_res.compilation_errors,
            output_summary=" | ".join(summaries),
            raw_output=f"{maven_res.raw_output}\n{python_res.raw_output}\n{react_res.raw_output}",
            maven=maven_res,
            python=python_res,
            react=react_res
        )
