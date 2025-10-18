#!/usr/bin/env python3
"""
Sync GitHub repositories, then embed them into the vector store.

Usage:
  # Use repos from settings.GITHUB_REPOS
  python -m backend.scripts.sync_and_embed

  # Explicit repos + options
  python -m backend.scripts.sync_and_embed \
      --repo https://github.com/user/repo1 \
      --repo https://github.com/org/repo2 \
      --target data/repositories \
      --glob "**/*" \
      --chunk-size 600 --chunk-overlap 80
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backend.config.logging import setup_logging

# Reuse functions from sibling scripts
from backend.scripts.sync_repositories import main as sync_main
from backend.scripts.embed_repositories import main as embed_main

def main():
    setup_logging()
    log = logging.getLogger(__name__)

    # We’ll proxy arguments to each script.
    p = argparse.ArgumentParser(description="Sync repos then embed them.")
    p.add_argument("--repo", action="append", help="Repository URL (repeatable)")
    p.add_argument("--repos-file", type=str, help="File with repo URLs (one per line)")
    p.add_argument("--target", type=str, default="data/repositories", help="Repo root folder")
    p.add_argument("--token-env", type=str, default="GITHUB_TOKEN", help="Env var for token")
    p.add_argument("--shallow", action="store_true", help="Shallow clone")
    p.add_argument("--branch", type=str, default=None, help="Branch to checkout")

    # embed options
    p.add_argument("--glob", type=str, default="**/*", help="File glob to include in embedding")
    p.add_argument("--chunk-size", type=int, default=600, help="Code chunk size")
    p.add_argument("--chunk-overlap", type=int, default=80, help="Code chunk overlap")

    args = p.parse_args()

    # 1) Sync step — rebuild argv for sync_repositories
    sync_argv = ["--target", args.target, "--token-env", args.token-env if False else args.token_env]
    if args.shallow:
        sync_argv.append("--shallow")
    if args.branch:
        sync_argv.extend(["--branch", args.branch])
    if args.repos_file:
        sync_argv.extend(["--repos-file", args.repos_file])
    if args.repo:
        for r in args.repo:
            sync_argv.extend(["--repo", r])

    log.info("🔄 Syncing repositories...")
    sys.argv = ["sync_repositories"] + sync_argv
    sync_main()

    # 2) Embed step — rebuild argv for embed_repositories
    embed_argv = ["--repos", args.target, "--glob", args.glob,
                  "--chunk-size", str(args.chunk_size),
                  "--chunk-overlap", str(args.chunk_overlap)]
    log.info("🧠 Embedding repositories into vector store...")
    sys.argv = ["embed_repositories"] + embed_argv
    embed_main()

    log.info("✅ Sync + Embed complete.")

if __name__ == "__main__":
    main()
