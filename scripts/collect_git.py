#!/usr/bin/env python3
"""Collect local git evidence for daily-work-report.

This script is intentionally dependency-free. It reads local repositories,
classifies same-day git activity, and writes an auditable JSON evidence ledger.

It does not call external APIs by default. Use --fetch-mr-refs only when the
current network/remote access is authorized.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


FIELD_SEP = "\x1f"


DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "Library",
    ".Trash",
    "dist",
    "build",
    ".next",
}


def local_date() -> str:
    return dt.datetime.now().astimezone().date().isoformat()


def local_offset() -> str:
    return dt.datetime.now().astimezone().strftime("%z")


def since_expr(day: str) -> str:
    offset = local_offset()
    if len(offset) == 5:
        offset = f"{offset[:3]}:{offset[3:]}"
    return f"{day} 00:00 {offset}"


def run(cmd: list[str], cwd: str | None = None, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def git(repo: str, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", repo, *args], check=check)


def repo_root(path: str) -> str | None:
    proc = git(path, ["rev-parse", "--show-toplevel"])
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def discover_repos(roots: list[str], excludes: set[str]) -> list[str]:
    repos: list[str] = []
    seen: set[str] = set()

    def add_repo(path: str) -> None:
        resolved = str(Path(path).resolve())
        if resolved not in seen:
            seen.add(resolved)
            repos.append(resolved)

    for raw_root in roots:
        root_path = Path(raw_root).expanduser().resolve()
        if not root_path.exists():
            continue

        top = repo_root(str(root_path))
        if top:
            add_repo(top)

        if root_path.is_file():
            continue

        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if d not in excludes and not d.startswith(".cache")]
            if ".git" in dirnames or ".git" in filenames:
                add_repo(dirpath)
                dirnames[:] = []

    return repos


def parse_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.strip()]


def current_branch(repo: str) -> str:
    proc = git(repo, ["branch", "--show-current"])
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    proc = git(repo, ["rev-parse", "--short", "HEAD"])
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def status(repo: str) -> dict[str, Any]:
    proc = git(repo, ["status", "--short", "--branch"])
    status_lines = parse_lines(proc.stdout) if proc.returncode == 0 else []
    dirty_files = [line for line in status_lines if not line.startswith("## ")]
    diff = git(repo, ["diff", "--stat"])
    return {
        "branch": current_branch(repo),
        "status_lines": status_lines,
        "dirty": bool(dirty_files),
        "dirty_files": dirty_files,
        "diff_stat": diff.stdout.strip() if diff.returncode == 0 else "",
    }


def collect_commits(repo: str, since: str, author_terms: list[str]) -> list[dict[str, Any]]:
    fmt = FIELD_SEP.join(["%H", "%h", "%ad", "%an", "%ae", "%D", "%s"])
    proc = git(repo, ["log", "--all", f"--since={since}", "--date=iso-strict", f"--pretty=format:{fmt}"])
    commits: list[dict[str, Any]] = []
    if proc.returncode != 0:
        return commits
    for line in parse_lines(proc.stdout):
        parts = line.split(FIELD_SEP)
        if len(parts) != 7:
            continue
        full, short, date, author_name, author_email, refs, subject = parts
        author_blob = f"{author_name} {author_email}".lower()
        author_match = not author_terms or any(term in author_blob for term in author_terms)
        commits.append(
            {
                "sha": full,
                "short_sha": short,
                "date": date,
                "author_name": author_name,
                "author_email": author_email,
                "author_match": author_match,
                "refs": refs,
                "subject": subject,
            }
        )
    return commits


def collect_refs(repo: str, day: str, author_terms: list[str]) -> list[dict[str, Any]]:
    fmt = FIELD_SEP.join(
        [
            "%(refname:short)",
            "%(objectname)",
            "%(committerdate:iso8601)",
            "%(authorname)",
            "%(authoremail)",
            "%(subject)",
        ]
    )
    proc = git(repo, ["for-each-ref", "--sort=-committerdate", f"--format={fmt}", "refs/heads", "refs/remotes"])
    refs: list[dict[str, Any]] = []
    if proc.returncode != 0:
        return refs
    for line in parse_lines(proc.stdout):
        parts = line.split(FIELD_SEP)
        if len(parts) != 6:
            continue
        name, sha, commit_date, author_name, author_email, subject = parts
        if not commit_date.startswith(day):
            continue
        author_blob = f"{author_name} {author_email}".lower()
        author_match = not author_terms or any(term in author_blob for term in author_terms)
        refs.append(
            {
                "name": name,
                "sha": sha,
                "short_sha": sha[:9],
                "date": commit_date,
                "author_name": author_name,
                "author_email": author_email,
                "author_match": author_match,
                "subject": subject,
            }
        )
    return refs


def exact_mr_refs(repo: str) -> dict[str, list[str]]:
    fmt = FIELD_SEP.join(["%(refname:short)", "%(objectname)"])
    proc = git(repo, ["for-each-ref", f"--format={fmt}", "refs/remotes/origin/merge-requests"])
    by_sha: dict[str, list[str]] = {}
    if proc.returncode != 0:
        return by_sha
    for line in parse_lines(proc.stdout):
        parts = line.split(FIELD_SEP)
        if len(parts) != 2:
            continue
        ref, sha = parts
        by_sha.setdefault(sha, []).append(ref)
    return by_sha


def existing_target(repo: str, targets: list[str]) -> str | None:
    for target in targets:
        proc = git(repo, ["rev-parse", "--verify", "--quiet", target])
        if proc.returncode == 0:
            return target
    return None


def merged_state(repo: str, ref: str, target: str | None) -> str:
    if not target:
        return "unknown"
    proc = git(repo, ["merge-base", "--is-ancestor", ref, target])
    if proc.returncode == 0:
        return "merged"
    if proc.returncode == 1:
        return "not_merged"
    return "unknown"


def fetch_mr_refs(repo: str) -> dict[str, Any]:
    proc = git(repo, ["fetch", "origin", "+refs/merge-requests/*/head:refs/remotes/origin/merge-requests/*", "--prune"])
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def collect_worktrees(repo: str) -> list[dict[str, Any]]:
    proc = git(repo, ["worktree", "list", "--porcelain"])
    if proc.returncode != 0:
        return []

    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in proc.stdout.splitlines():
        if not line.strip():
            if current:
                records.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            current["path"] = line.removeprefix("worktree ").strip()
        elif line.startswith("HEAD "):
            current["head"] = line.removeprefix("HEAD ").strip()
        elif line.startswith("branch "):
            current["branch"] = line.removeprefix("branch ").strip().removeprefix("refs/heads/")
        elif line.startswith("detached"):
            current["detached"] = True
        elif line.startswith("prunable"):
            current["prunable"] = True
    if current:
        records.append(current)

    enriched: list[dict[str, Any]] = []
    for record in records:
        path = record.get("path")
        if not path or not Path(path).exists():
            enriched.append({**record, "accessible": False})
            continue
        wt_status = status(path)
        enriched.append({**record, "accessible": True, "status": wt_status})
    return enriched


def collect_repo(repo: str, day: str, since: str, author_terms: list[str], targets: list[str], fetch_mrs: bool) -> dict[str, Any]:
    fetch_result = fetch_mr_refs(repo) if fetch_mrs else {"ok": None, "note": "not requested"}
    stat = status(repo)
    commits = collect_commits(repo, since, author_terms)
    refs = collect_refs(repo, day, author_terms)
    mr_by_sha = exact_mr_refs(repo)
    target = existing_target(repo, targets)

    branches: list[dict[str, Any]] = []
    for ref in refs:
        if author_terms and not ref.get("author_match"):
            continue
        if ref["name"].startswith("origin/merge-requests/"):
            continue
        mr_refs = mr_by_sha.get(ref["sha"], [])
        state = merged_state(repo, ref["name"], target)
        branch_status = "merged" if state == "merged" else "pushed_branch" if ref["name"].startswith("origin/") else "local_commit"
        if mr_refs:
            branch_status = "merged" if state == "merged" else "mr_open"
        branches.append({**ref, "status": branch_status, "target": target, "merge_state": state, "mr_refs": mr_refs})

    merge_requests: list[dict[str, Any]] = []
    for sha, refs_for_sha in mr_by_sha.items():
        if any(ref["sha"] == sha for ref in refs):
            for mr_ref in refs_for_sha:
                merge_requests.append(
                    {
                        "ref": mr_ref,
                        "sha": sha,
                        "short_sha": sha[:9],
                        "merge_state": merged_state(repo, mr_ref, target),
                        "target": target,
                    }
                )

    return {
        "path": repo,
        "current": stat,
        "target_branch": target,
        "fetch_mr_refs": fetch_result,
        "commits": commits,
        "branches": branches,
        "merge_requests": merge_requests,
        "worktrees": collect_worktrees(repo),
    }


def load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def identity_terms(args: argparse.Namespace, config: dict[str, Any]) -> list[str]:
    identity = config.get("identity", {}) if isinstance(config, dict) else {}
    terms = list(args.author or [])
    for key in ("display_names", "git_author_names", "git_author_emails", "gitlab_usernames", "github_usernames"):
        value = identity.get(key, [])
        if isinstance(value, str):
            terms.append(value)
        elif isinstance(value, list):
            terms.extend(str(v) for v in value)
    return [term.lower() for term in terms if term]


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect git evidence for daily work reports.")
    parser.add_argument("--date", default=local_date(), help="Report date in YYYY-MM-DD. Defaults to local today.")
    parser.add_argument("--roots", nargs="+", default=["."], help="Roots or repos to scan.")
    parser.add_argument("--config", help="Optional JSON config path.")
    parser.add_argument("--author", action="append", help="Author/name/email term to mark as identity match. Can repeat.")
    parser.add_argument("--output", help="Write evidence JSON to this path.")
    parser.add_argument("--fetch-mr-refs", action="store_true", help="Fetch GitLab-style refs/merge-requests from origin.")
    parser.add_argument("--target", action="append", help="Target branch to test merge state. Can repeat.")
    args = parser.parse_args()

    config = load_config(args.config)
    repo_config = config.get("repositories", {}) if isinstance(config, dict) else {}
    excludes = set(repo_config.get("exclude_dirs", [])) or DEFAULT_EXCLUDES
    targets = args.target or repo_config.get("target_branches") or ["origin/master", "origin/main", "master", "main"]
    roots = args.roots or repo_config.get("roots") or ["."]
    terms = identity_terms(args, config)
    since = since_expr(args.date)

    repos = discover_repos(roots, excludes)
    evidence = {
        "schema_version": "daily-work-report.git-evidence.v1",
        "generated_at": dt.datetime.now().astimezone().isoformat(),
        "date": args.date,
        "since": since,
        "identity_terms_present": bool(terms),
        "repo_count": len(repos),
        "repositories": [
            collect_repo(repo, args.date, since, terms, targets, args.fetch_mr_refs)
            for repo in repos
        ],
    }

    text = json.dumps(evidence, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
