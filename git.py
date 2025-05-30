import logging
import os
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class GitHelper:
    def __init__(self, repo_path: str):
        self.repo_path = os.path.expanduser(repo_path)

    def _run_git_command(self, command: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(command, capture_output=True, text=True, cwd=self.repo_path)

    def add_all(self) -> bool:
        logger.debug("adding changes to git")
        result = self._run_git_command(["git", "add", "."])
        if result.returncode != 0:
            logger.error(f"failed to add changes to git: {result.stderr}")
            return False
        return True

    def commit(self, message: str) -> bool:
        logger.debug("committing changes to git")
        result = self._run_git_command(["git", "commit", "-m", message])
        if result.returncode != 0:
            logger.error(f"no changes detected or failed to commit: {result.stderr}")
            return False
        logger.info("git commit completed successfully")
        return True

    def push(self) -> bool:
        logger.debug("pushing changes to git")
        result = self._run_git_command(["git", "push"])
        if result.returncode != 0:
            logger.error(f"failed to push changes to git: {result.stderr}")
            return False
        logger.info("git push completed successfully")
        return True

    def get_diff(self) -> Optional[str]:
        logger.debug("getting git diff")
        result = self._run_git_command(["git", "diff"])
        if result.returncode != 0:
            logger.error(f"failed to get git diff: {result.stderr}")
            return None
        return result.stdout
