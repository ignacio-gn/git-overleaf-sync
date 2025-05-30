# git-overleaf-sync
Automate the process of downloading Overleaf projects, sync them into a local Git repository, generate AI-assisted commit messages, and sync the changes remotely.

## Features
- 🔄 Sync Overleaf Projects: Helps download .zip exports of Overleaf projects via Selenium.
- 🧠 AI-Powered Commit Messages: Uses OpenWebUI with LLaMA model to generate meaningful commit messages based on git diff.
- 🧪 Logging: Logs everything into timestamped log files.

## Requirements
- Python 3.9+
- Firefox (for Selenium)
- geckodriver in $PATH
- Overleaf account (read-only share URL)
- Git repository for syncing, git configuration set up 
- OpenWebUI instance with API access

## Setup
1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Set up .env
Create a .env file in the root directory:

```env
OVERLEAF_URL=https://www.overleaf.com/read/abc123...
GIT_REPO_PATH=~/your/local/git/repo
TMP_ZIP_FOLDER=/tmp/
LOGS_FOLDER=/tmp/overleaf_logs
OPENWEBUI_URL=http://localhost:3000
API_KEY=your_openwebui_api_key
```
3. Install Firefox & Geckodriver

4. Run the main script:

```bash
python main.py --overleaf_url https://www.overleaf.com/read/abc123 \
               --git_path ~/my-paper \
               --log_level DEBUG \
               --openwebui_url http://localhost:3000 \
               --api_key sk-abc...
```
You can omit CLI args to use values from .env.
> [!NOTE]
> Configuring a cron job to run this script periodically is recommended for continuous syncing.


## Environment Variables
| Variable         | Description                                             |
|------------------|---------------------------------------------------------|
| `OVERLEAF_URL`   | Share URL of the Overleaf project (read-only)          |
| `GIT_REPO_PATH`  | Path to the local Git repo where LaTeX files are synced |
| `TMP_ZIP_FOLDER` | Temp directory for Overleaf .zip downloads             |
| `LOGS_FOLDER`    | Directory for storing log files                        |
| `OPENWEBUI_URL`  | Base URL of the OpenWebUI instance                     |
| `API_KEY`        | API key for authenticating with OpenWebUI              |


## How it works
- Launches a headless Firefox browser via Selenium.
- Logs into Overleaf (via shared link), simulates a download click to trigger `PUT` event in the Overleaf Backend.
- Downloads the .zip file of the project.
- Unzips the .zip archive into a Git repo.
- Runs git diff to detect changes.
- Sends the diff to OpenWebUI for commit message generation.
- Adds, commits, and pushes the changes to the remote repo.

### File Structure
```text
main.py         - Entry point
helpers.py      - Logging, datetime utilities, OpenWebUI helper
parser.py       - Selenium-based Overleaf project downloader
git.py          - Git CLI wrapper for add/commit/push/diff
```

## Potential Issues
- geckodriver must be installed and match Firefox version.
- Assumes Overleaf’s UI doesn’t change, based on XPath selectors
- AI-generated commit messages may contain errors or irrelevant text.

> [!IMPORTANT]
> This tool is intended for personal use. It helps download Overleaf projects via publicly shared read-only URLs.
> It is the user's responsibility to ensure their use of this tool complies with [Overleaf's terms](https://www.overleaf.com/legal#Terms).
> The authors take no responsibility for misuse of this software.

## License
See [LICENSE](LICENSE) for details.

