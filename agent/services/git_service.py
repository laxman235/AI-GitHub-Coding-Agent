"""Safe Git operations service using GitPython and subprocess fallback."""
import os
import subprocess
from typing import List, Optional
import git


class GitService:
    """Manages Git branch isolation, committing, diffing, and safe rollbacks."""

    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.repo = git.Repo(self.repo_path)

    def get_current_branch(self) -> str:
        """Return the active branch name."""
        try:
            return self.repo.active_branch.name
        except Exception:
            return "main"

    def is_clean(self) -> bool:
        """Check if the working tree has no uncommitted modifications."""
        return not self.repo.is_dirty(untracked_files=True)

    def has_commits(self) -> bool:
        """Check if repository has at least one commit."""
        try:
            _ = self.repo.head.commit
            return True
        except Exception:
            return False

    def create_feature_branch(self, branch_name: str, base_branch: str = "main") -> None:
        """Create and switch to an isolated feature branch."""
        if not self.has_commits():
            # If repo has no commits yet, ensure git user is set and create initial commit
            try:
                with self.repo.config_writer() as cw:
                    if not cw.has_section("user"):
                        cw.add_section("user")
                    if not cw.has_option("user", "name"):
                        cw.set_value("user", "name", "AI GitHub Agent")
                    if not cw.has_option("user", "email"):
                        cw.set_value("user", "email", "agent@github.actions")
                self.repo.git.add("-A")
                self.repo.index.commit("Initial commit: project baseline")
            except Exception:
                pass

        # Ensure base branch is active or checkout
        try:
            if base_branch in self.repo.heads:
                self.repo.heads[base_branch].checkout()
        except Exception:
            pass

        # Create or checkout feature branch
        if branch_name in self.repo.heads:
            self.repo.heads[branch_name].checkout()
        else:
            try:
                new_branch = self.repo.create_head(branch_name)
                new_branch.checkout()
            except Exception:
                try:
                    self.repo.git.checkout("-b", branch_name)
                except Exception:
                    pass

    def stage_files(self, file_paths: List[str]) -> None:
        """Stage specified file paths."""
        for path in file_paths:
            rel_path = os.path.relpath(os.path.join(self.repo_path, path), self.repo_path)
            self.repo.git.add(rel_path)

    def commit(self, message: str) -> str:
        """Commit staged changes and return commit SHA."""
        commit_obj = self.repo.index.commit(message)
        return commit_obj.hexsha

    def get_diff(self) -> str:
        """Return unified diff of current changes."""
        try:
            return self.repo.git.diff("HEAD~1")
        except Exception:
            return self.repo.git.diff()

    def rollback(self, base_branch: str = "main") -> None:
        """Safely discard unstaged/staged changes and return to base branch."""
        try:
            self.repo.git.reset("--hard")
            self.repo.git.clean("-fd", "-e", "reports", "-e", "data")
            if base_branch in self.repo.heads:
                self.repo.heads[base_branch].checkout()
        except Exception:
            # Fallback to subprocess
            try:
                subprocess.run(["git", "reset", "--hard"], cwd=self.repo_path, check=False)
                subprocess.run(["git", "clean", "-fd", "-e", "reports", "-e", "data"], cwd=self.repo_path, check=False)
                subprocess.run(["git", "checkout", base_branch], cwd=self.repo_path, check=False)
            except Exception:
                pass

    def push_branch(self, branch_name: str, remote_name: str = "origin", dry_run: bool = False) -> bool:
        """Push branch to remote. NEVER force-push. NEVER push to main directly."""
        if branch_name in ["main", "master", "release"]:
            raise ValueError(f"Direct push to protected branch '{branch_name}' is forbidden.")

        if dry_run:
            return True

        try:
            remote = self.repo.remote(name=remote_name)
            remote.push(refspec=f"{branch_name}:{branch_name}")
            return True
        except Exception as e:
            # Subprocess fallback
            cmd = ["git", "push", "-u", remote_name, branch_name]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            return result.returncode == 0
