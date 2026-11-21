import os
import pytest
from agent.core.config import load_config, AgentConfig


def test_load_default_config():
    config = load_config()
    assert isinstance(config, AgentConfig)
    assert config.groq.model == "llama-3.3-70b-versatile"
    assert config.execution.max_daily_tasks == 10
    assert config.execution.max_repair_attempts == 2
    assert ".java" in config.execution.allowlist_extensions


def test_env_override(monkeypatch):
    monkeypatch.setenv("GROQ_MODEL", "mixtral-8x7b-32768")
    monkeypatch.setenv("MAX_DAILY_TASKS", "5")
    monkeypatch.setenv("DRY_RUN", "true")

    config = load_config()
    assert config.groq.model == "mixtral-8x7b-32768"
    assert config.execution.max_daily_tasks == 5
    assert config.execution.dry_run is True
