"""CLI entrypoint for Autonomous AI GitHub Coding Agent."""
import sys
import argparse
import logging
from agent.core.config import load_config
from agent.core.orchestrator import AgentOrchestrator


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous AI GitHub Coding Agent for Java Spring Boot Repositories"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without pushing git branches or creating real GitHub PRs"
    )
    parser.add_argument(
        "--max-tasks",
        "-m",
        type=int,
        default=None,
        help="Maximum tasks to execute in this run (up to 10)"
    )
    parser.add_argument(
        "--target-path",
        "-t",
        type=str,
        default=None,
        help="Path to Java Spring Boot repository or project root"
    )
    parser.add_argument(
        "--force",
        "--ignore-daily-cap",
        action="store_true",
        help="Ignore daily task limit (e.g. for testing or executing next sprint day immediately)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed debug logging"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    config = load_config(args.config)

    if args.dry_run:
        config.execution.dry_run = True
    if args.max_tasks:
        config.execution.max_daily_tasks = args.max_tasks
    if args.target_path:
        config.target_repo_path = args.target_path

    print("=" * 60)
    print(" 🤖 Autonomous AI GitHub Coding Agent (Java Spring Boot)")
    print("=" * 60)
    print(f" Target Project Path : {config.target_repo_path}")
    print(f" Groq Model          : {config.groq.model}")
    print(f" Daily Tasks Limit   : {config.execution.max_daily_tasks}")
    print(f" Max Repair Attempts : {config.execution.max_repair_attempts}")
    print(f" Dry-Run Mode        : {config.execution.dry_run}")
    print("=" * 60)

    orchestrator = AgentOrchestrator(config)
    summary = orchestrator.execute(
        max_tasks=config.execution.max_daily_tasks,
        dry_run=config.execution.dry_run,
        ignore_daily_cap=args.force
    )

    print("\n" + "=" * 60)
    print(" 📊 Execution Complete")
    print("=" * 60)
    print(f" Run ID           : {summary.run_id}")
    print(f" Status           : {summary.status.value}")
    print(f" Tasks Attempted  : {summary.tasks_attempted}")
    print(f" Tasks Completed  : {summary.tasks_completed}")
    print(f" Tasks Failed     : {summary.tasks_failed}")
    print(f" Tokens Used      : {summary.total_tokens_used}")
    print(f" Report Saved     : {summary.report_markdown_path}")
    print("=" * 60)

    sys.exit(0 if summary.status.value in ("SUCCESS", "PARTIAL_SUCCESS") else 1)


if __name__ == "__main__":
    main()
