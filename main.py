import argparse
import logging
import os
import subprocess
import sys
from ast import parse
from datetime import datetime

from dotenv import load_dotenv

import helpers
from parser import OverleafParser

# load config from .env file
load_dotenv()
OVERLEAF_URL = os.getenv("OVERLEAF_URL")
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH")
TMP_ZIP_FOLDER = os.getenv("TMP_ZIP_FOLDER", "/tmp/")
LOGS_FOLDER = os.getenv("LOGS_FOLDER", "/tmp/overleaf_logs")

def main(args):
    # logging
    logger = logging.getLogger(__name__)

    logging.basicConfig(filename=f'{LOGS_FOLDER}/{helpers.get_hour()}.log', level=args.log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info(f"started, args: {args}")

    # check constraints
    if not args.overleaf_url.startswith("https://www.overleaf.com/read/"):
        logger.error("invalid overleaf URL: need read (`https://www.overleaf.com/read/...`)")
        return 1
    if not os.path.isdir(os.path.join(os.path.expanduser(GIT_REPO_PATH), ".git")):
        logger.error(f"git repo path {GIT_REPO_PATH} does not contain a .git folder")
        return 1

    # download overleaf project
    logger.info(f"downloading overleaf project from {args.overleaf_url} to {os.path.expanduser(args.git_path)}")
    parser = OverleafParser(args.overleaf_url)
    try:
        parser.download(download_dir=TMP_ZIP_FOLDER)
    except Exception as e:
        logger.error(f"failed to download overleaf project: {e}")
        return 1

    # move downloaded files to git repo
    logger.info(f"moving downloaded files from {TMP_ZIP_FOLDER} to {os.path.expanduser(args.git_path)}")
    proces_unzip = subprocess.run(
        ["unzip", "-o", os.path.join(TMP_ZIP_FOLDER, parser.get_filename()), "-d", os.path.expanduser(args.git_path)],
        capture_output=True,
        text=True
    )
    if proces_unzip.returncode != 0:
        logger.error(f"failed to unzip downloaded files: {proces_unzip.stderr}")
        return 1
    logger.info("unzip completed successfully")

    # commit changes to git
    logger.info("committing changes to git")
    os.chdir(os.path.expanduser(args.git_path))
    proces_git_add = subprocess.run(
        ["git", "add", "."],
        capture_output=True,
        text=True
    )
    if proces_git_add.returncode != 0:
        logger.error(f"failed to add changes to git: {proces_git_add.stderr}")
        return 1
    proces_git_commit = subprocess.run(
        ["git", "commit", "-m", f"[update] {helpers.get_hour()}"],
        capture_output=True,
        text=True
    )
    if proces_git_commit.returncode != 0:
        logger.error(f"no changes detected or failed to commit changes to git: {proces_git_commit.stderr}")
        return 0
    logger.info("git commit completed successfully")

    # push changes to git
    logger.info("pushing changes to git")
    proces_git_push = subprocess.run(
        ["git", "push"],
        capture_output=True,
        text=True
    )
    if proces_git_push.returncode != 0:
        logger.error(f"failed to push changes to git: {proces_git_push.stderr}")
        return 1
    logger.info("git push completed successfully")

    return 0


if __name__ == "__main__":
    # argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--overleaf_url",
        type=str,
        help="The URL of the Overleaf project to clone.",
        default=OVERLEAF_URL
    )
    parser.add_argument(
        "--git_path",
        type=str,
        default=GIT_REPO_PATH
    )
    parser.add_argument(
        "--log_level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level."
    )

    args = parser.parse_args()
    sys.exit(main(args))
