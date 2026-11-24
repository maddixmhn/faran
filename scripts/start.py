"""Start a fresh, local Faran stack with persistent volumes and local-only ports."""

import argparse
import os
from pathlib import Path
import secrets
import subprocess

ROOT = Path(__file__).resolve().parents[1]
KEYS = (
    "N8N_DB_PASSWORD", "N8N_ENCRYPTION_KEY", "BETTER_AUTH_SECRET",
    "PAPERCLIP_TOOL_ACTION_SIGNING_SECRET", "FARAN_LMS_DB_PASSWORD", "MOODLE_ADMIN_PASSWORD",
)
PORTS = (
    ("FARAN_WEB_PORT", 18000, "Faran", "/"),
    ("FARAN_EVAL_PORT", 18001, "Evaluator", "/"),
    ("FARAN_N8N_PORT", 15678, "n8n", "/"),
    ("FARAN_PAPERCLIP_PORT", 13100, "Paperclip", "/"),
    ("FARAN_MOODLE_PORT", 18700, "Moodle", "/"),
)

def local_environment(path):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="ascii") as env:
            if os.name != "nt":
                path.chmod(0o600)
            for key in KEYS:
                token = secrets.token_hex(32)
                env.write(f"{key}={'Faran9!' if key == 'MOODLE_ADMIN_PASSWORD' else ''}{token}\n")
    except FileExistsError:
        pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=("up", "status", "stop"), default="up")
    parser.add_argument("--project", default="faran-demo")
    args = parser.parse_args()
    envfile = ROOT / ".faran" / f"{args.project}.env"
    if not args.project or not all(c in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in args.project) or not args.project[0].isalnum():
        parser.error("--project must start with a lowercase letter or digit and contain only lowercase letters, digits, underscores and hyphens")
    if args.action == "up":
        local_environment(envfile)
    elif not envfile.is_file():
        parser.error("Start this project first.")
    base = ["docker", "compose", "--project-name", args.project,
            "--env-file", str(envfile), "-f", str(ROOT / "compose.yaml")]
    if args.action == "up":
        subprocess.run(base + ["up", "-d", "--build", "--wait", "--wait-timeout", "1200"], cwd=ROOT, check=True)
        for key, default, name, route in PORTS:
            print(f"{name}: http://localhost:{os.environ.get(key, default)}{route}")
        print("Moodle admin password is stored in", envfile)
    elif args.action == "status":
        subprocess.run(base + ["ps", "-a"], cwd=ROOT, check=True)
    else:
        subprocess.run(base + ["stop"], cwd=ROOT, check=True)

if __name__ == "__main__":
    main()
