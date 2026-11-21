"""GitHub REST API integration service for Pull Request creation."""
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class GitHubService:
    """Manages GitHub PR creation, issue labels, and pull request metadata."""

    def __init__(self, token: Optional[str], owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"

    @property
    def is_configured(self) -> bool:
        return bool(self.token and self.token.strip() and self.owner and self.repo)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        dry_run: bool = False
    ) -> Optional[str]:
        """Create a pull request on GitHub or simulate if dry-run."""
        if dry_run or not self.is_configured:
            simulated_url = f"https://github.com/{self.owner}/{self.repo}/pull/simulated-{head_branch}"
            logger.info(f"[GitHubService] Dry-run/Mock PR created: {simulated_url}")
            return simulated_url

        url = f"{self.base_url}/pulls"
        payload = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
            "maintainer_can_modify": True
        }

        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            if response.status_code == 201:
                pr_data = response.json()
                html_url = pr_data.get("html_url")
                logger.info(f"Successfully opened Pull Request: {html_url}")
                return html_url
            else:
                logger.error(f"Failed to create PR ({response.status_code}): {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error calling GitHub PR API: {e}")
            return None
