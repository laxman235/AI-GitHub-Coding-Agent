"""Configuration management using Pydantic and YAML."""
import os
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field


class GroqSettings(BaseModel):
    api_key: Optional[str] = None
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.1
    max_retries: int = 3
    timeout_seconds: int = 60


class GitHubSettings(BaseModel):
    token: Optional[str] = None
    owner: str = "laxman235"
    repo: str = "AI-GitHub-Coding-Agent"
    target_branch: str = "main"
    branch_prefix: str = "agent/improve-"
    pull_request_enabled: bool = True
    auto_merge: bool = False


class ExecutionSettings(BaseModel):
    max_daily_tasks: int = 10
    max_repair_attempts: int = 2
    dry_run: bool = False
    allowlist_extensions: List[str] = Field(
        default_factory=lambda: [".java", ".xml", ".properties", ".yml", ".yaml", ".sql", ".md"]
    )
    denylist_paths: List[str] = Field(
        default_factory=lambda: [".env", ".git", ".github", "secrets", "credentials"]
    )


class DatabaseSettings(BaseModel):
    db_path: str = "data/agent_tasks.db"


class ReportSettings(BaseModel):
    output_dir: str = "reports"


class AgentConfig(BaseModel):
    groq: GroqSettings = Field(default_factory=GroqSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    reports: ReportSettings = Field(default_factory=ReportSettings)
    target_repo_path: str = "sample-spring-boot-app"


def load_config(config_file: Optional[str] = None) -> AgentConfig:
    """Load configuration from YAML file and override with environment variables."""
    config_dict = {}

    # Default file path
    default_yaml = os.path.join(os.path.dirname(__file__), "..", "..", "config", "default_config.yaml")
    target_file = config_file or default_yaml

    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    config_dict = loaded
        except Exception:
            pass

    config = AgentConfig(**config_dict)

    # Environment variable overrides
    if os.getenv("GROQ_API_KEY"):
        config.groq.api_key = os.getenv("GROQ_API_KEY")
    if os.getenv("GROQ_MODEL"):
        config.groq.model = os.getenv("GROQ_MODEL")
    if os.getenv("GROQ_TEMPERATURE"):
        try:
            config.groq.temperature = float(os.getenv("GROQ_TEMPERATURE"))
        except ValueError:
            pass

    if os.getenv("GITHUB_TOKEN"):
        config.github.token = os.getenv("GITHUB_TOKEN")
    if os.getenv("REPO_OWNER"):
        config.github.owner = os.getenv("REPO_OWNER")
    if os.getenv("REPO_NAME"):
        config.github.repo = os.getenv("REPO_NAME")
    if os.getenv("TARGET_BRANCH"):
        config.github.target_branch = os.getenv("TARGET_BRANCH")

    if os.getenv("MAX_DAILY_TASKS"):
        try:
            config.execution.max_daily_tasks = int(os.getenv("MAX_DAILY_TASKS"))
        except ValueError:
            pass
    if os.getenv("MAX_REPAIR_ATTEMPTS"):
        try:
            config.execution.max_repair_attempts = int(os.getenv("MAX_REPAIR_ATTEMPTS"))
        except ValueError:
            pass
    if os.getenv("DRY_RUN"):
        config.execution.dry_run = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

    if os.getenv("TARGET_REPO_PATH"):
        config.target_repo_path = os.getenv("TARGET_REPO_PATH")
    if os.getenv("DATABASE_PATH"):
        config.database.db_path = os.getenv("DATABASE_PATH")
    if os.getenv("REPORTS_DIR"):
        config.reports.output_dir = os.getenv("REPORTS_DIR")

    return config
