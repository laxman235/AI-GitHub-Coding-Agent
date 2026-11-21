import os
import git
import pytest
from agent.services.git_service import GitService


@pytest.fixture
def temp_git_repo(tmp_path):
    repo = git.Repo.init(tmp_path)
    file_path = tmp_path / "README.md"
    file_path.write_text("# Test Repo", encoding="utf-8")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")
    return tmp_path


def test_git_branch_commit_and_diff(temp_git_repo):
    git_service = GitService(str(temp_git_repo))
    assert git_service.is_clean()

    # Create feature branch
    git_service.create_feature_branch("agent/task-test")

    # Modify file
    new_file = temp_git_repo / "NewFeature.java"
    new_file.write_text("public class NewFeature {}", encoding="utf-8")

    git_service.stage_files(["NewFeature.java"])
    sha = git_service.commit("feat: add new feature")
    assert sha is not None
    assert len(sha) == 40

    diff = git_service.get_diff()
    assert "NewFeature" in diff


def test_git_push_safety(temp_git_repo):
    git_service = GitService(str(temp_git_repo))
    # Direct push to main should be blocked
    with pytest.raises(ValueError):
        git_service.push_branch("main")
