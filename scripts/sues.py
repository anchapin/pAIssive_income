"""SUES utility script for special maintenance or migration tasks."""

# Standard library imports
import argparse
import datetime

# Third-party imports
# Local imports
import logging
import shutil
import sys
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


# Configure logger
# logging.basicConfig will be moved to the main() function


def cleanup_task(path: str, dry_run: bool) -> None:
    """
    Clean up temporary files and directories.

    Args:
        path: Path to clean up
        dry_run: If True, only print what would be done without making changes

    """
    if not path:
        logger.error("No path specified for cleanup task.")
        return

    path_obj = Path(path)
    if not path_obj.exists():
        message = f"Path {path} does not exist."
        logger.warning(message)
        return

    # Define patterns for files to clean up
    temp_patterns = ["*.tmp", "*.bak", "*.log", "*.cache"]

    # Find and clean up files
    for pattern in temp_patterns:
        files = list(path_obj.glob(pattern))
        for file in files:
            if dry_run:
                message = f"[Dry Run] Would delete: {file}"
                logger.info(message)
            else:
                try:
                    Path(file).unlink()
                    message = f"Deleted: {file}"
                    logger.info(message)
                except Exception:
                    message = f"Error deleting {file}"
                    logger.exception(message)


def migrate_task(path: str, dry_run: bool) -> None:
    """
    Migrate files from one format to another.

    Args:
        path: Path to migrate
        dry_run: If True, only print what would be done without making changes

    """
    if not path:
        logger.error("No path specified for migration task.")
        return

    path_obj = Path(path)
    if not path_obj.exists():
        message = f"Path {path} does not exist."
        logger.warning(message)
        return

    # Example migration: rename all .txt files to .md
    files = list(path_obj.glob("*.txt"))
    for file in files:
        new_name = file.with_suffix(".md")
        if dry_run:
            message = f"[Dry Run] Would rename: {file} -> {new_name}"
            logger.info(message)
        else:
            try:
                file.rename(new_name)
                message = f"Renamed: {file} -> {new_name}"
                logger.info(message)
            except Exception:
                message = f"Error renaming {file}"
                logger.exception(message)


def backup_task(path: str, dry_run: bool) -> None:
    """
    Create backups of files or directories.

    Args:
        path: Path to back up
        dry_run: If True, only print what would be done without making changes

    """
    if not path:
        logger.error("No path specified for backup task.")
        return

    path_obj = Path(path)
    if not path_obj.exists():
        message = f"Path {path} does not exist."
        logger.warning(message)
        return

    # Create backup directory if it doesn't exist
    backup_dir = Path("backups")
    if not backup_dir.exists():
        if dry_run:
            message = f"[Dry Run] Would create backup directory: {backup_dir}"
            logger.info(message)
        else:
            try:
                backup_dir.mkdir(exist_ok=True)
                message = f"Created backup directory: {backup_dir}"
                logger.info(message)
            except Exception:
                logger.exception("Error creating backup directory")
                return

    # Create backup filename with timestamp
    timestamp = datetime.datetime.now(tz=datetime.timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )
    backup_name = f"{path_obj.name}_{timestamp}"
    backup_path = backup_dir / backup_name

    # Create the backup
    if dry_run:
        message = f"[Dry Run] Would back up: {path} -> {backup_path}"
        logger.info(message)
    else:
        try:
            if path_obj.is_dir():
                shutil.copytree(path_obj, backup_path)
            else:
                shutil.copy2(path_obj, backup_path)
            message = f"Created backup: {path} -> {backup_path}"
            logger.info(message)
        except Exception:
            logger.exception("Error creating backup")


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments

    """
    parser = argparse.ArgumentParser(
        description="SUES utility script for maintenance tasks"
    )
    parser.add_argument(
        "--task",
        type=str,
        choices=["cleanup", "migrate", "backup"],
        help="Task to perform",
    )
    parser.add_argument("--path", type=str, help="Path to operate on")
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run without changes"
    )

    return parser.parse_args()


def main() -> None:
    """Execute the main script functionality."""
    # Configure logging at the start of main execution
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    args = parse_args()

    if not args.task:
        logger.error("No task specified. Use --task to specify a task.")
        sys.exit(1)

    message = f"Running task: {args.task}"
    logger.info(message)

    # Validate path argument for tasks that require it
    if args.task in ["cleanup", "migrate", "backup"] and not args.path:
        message = f"The {args.task} task requires a --path argument."
        logger.error(message)
        sys.exit(1)

    # Execute the requested task
    if args.task == "cleanup":
        cleanup_task(args.path, args.dry_run)
    elif args.task == "migrate":
        migrate_task(args.path, args.dry_run)
    elif args.task == "backup":
        backup_task(args.path, args.dry_run)
    else:
        message = f"Unknown task {args.task}"
        logger.error(message)
        sys.exit(1)

    logger.info("Task completed successfully.")


if __name__ == "__main__":
    main()
