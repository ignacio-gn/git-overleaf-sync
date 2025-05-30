import argparse
import logging
import os
import subprocess
import sys

from dotenv import load_dotenv

import helpers
from git import GitHelper
from parser import OverleafParser

# load config from .env file
load_dotenv()
OVERLEAF_URL = os.getenv("OVERLEAF_URL")
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH")
TMP_ZIP_FOLDER = os.getenv("TMP_ZIP_FOLDER", "/tmp/")
LOGS_FOLDER = os.getenv("LOGS_FOLDER", "/tmp/overleaf_logs")
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL")
API_KEY = os.getenv("API_KEY")

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
    logger.debug(f"downloading overleaf project from {args.overleaf_url} to {os.path.expanduser(args.git_path)}")
    parser = OverleafParser(args.overleaf_url)
    try:
        parser.download(download_dir=TMP_ZIP_FOLDER)
    except Exception as e:
        logger.error(f"failed to download overleaf project: {e}")
        return 1

    # move downloaded files to git repo
    logger.debug(f"moving downloaded files from {TMP_ZIP_FOLDER} to {os.path.expanduser(args.git_path)}")
    proces_unzip = subprocess.run(
        ["unzip", "-o", os.path.join(TMP_ZIP_FOLDER, parser.get_filename()), "-d", os.path.expanduser(args.git_path)],
        capture_output=True,
        text=True
    )
    if proces_unzip.returncode != 0:
        logger.error(f"failed to unzip downloaded files: {proces_unzip.stderr}")
        return 1
    logger.debug("unzip completed successfully")

    # get git changes
    git = GitHelper(args.git_path)
    if not (git_diff := git.get_diff()):
        logger.info("no changes detected, exiting")
        return 0
    logger.info("changes detected, proceeding with git operations")

    # analyze changes and prepare commit message
    openwebui = helpers.OpenWebUIHelper(
        openwebui_url=args.openwebui_url,
        api_key=args.api_key,
    )
    commit_message = openwebui.chat_with_model(
        git_diff
    )
    logger.info(f"commit message: {commit_message}")

    # git add, commit, and push
    if not git.add_all():
        return 1
    if not git.commit(commit_message):
        return 0
    if not git.push():
        return 1

    return 0


if __name__ == "__main__":
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
    parser.add_argument(
        "--openwebui_url",
        type=str,
        help="URL of the OpenWebUI instance to use for commit message generation.",
        default=OPENWEBUI_URL
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=API_KEY,
        help="API key for the OpenWebUI instance."
    )

    args = parser.parse_args()
    sys.exit(main(args))
