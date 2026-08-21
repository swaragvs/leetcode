"""
sync_leetcode.py

Reads your recent ACCEPTED LeetCode submissions and writes any new ones
into solutions/<id>-<slug>/solution.py in this repo.

Auth: LeetCode has no official public API for private submission history,
so this uses the same (unofficial) GraphQL endpoint the LeetCode website
itself calls from your browser. It needs two cookies from an active,
logged-in LeetCode session:

    LEETCODE_SESSION
    csrftoken

For LOCAL testing, put them in a .env file (already gitignored):

    LEETCODE_SESSION=xxxx
    LEETCODE_CSRF_TOKEN=xxxx
    LEETCODE_USERNAME=your_username

Run locally with:
    pip install -r requirements.txt
    python scripts/sync_leetcode.py --dry-run

--dry-run prints what it *would* create without touching the filesystem.
Remove --dry-run once you've verified the output looks right.
"""

import os
import re
import json
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
REPO_ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS_DIR = REPO_ROOT / "solutions"

LANG_EXTENSIONS = {
    "python": "py",
    "python3": "py",
    "java": "java",
    "cpp": "cpp",
    "c": "c",
    "csharp": "cs",
    "javascript": "js",
    "typescript": "ts",
    "golang": "go",
    "kotlin": "kt",
    "swift": "swift",
    "rust": "rs",
    "ruby": "rb",
    "scala": "scala",
    "php": "php",
}

SUBMISSION_LIST_QUERY = """
query submissionList($offset: Int!, $limit: Int!, $lastKey: String) {
  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey) {
    lastKey
    hasNext
    submissions {
      id
      titleSlug
      title
      statusDisplay
      lang
      timestamp
    }
  }
}
"""

SUBMISSION_DETAIL_QUERY = """
query submissionDetails($submissionId: Int!) {
  submissionDetails(submissionId: $submissionId) {
    code
    lang {
      name
    }
    question {
      questionFrontendId
      title
      titleSlug
    }
  }
}
"""


def get_session():
    """Build a requests.Session authenticated with LeetCode cookies."""
    lc_session = os.environ.get("LEETCODE_SESSION")
    csrf_token = os.environ.get("LEETCODE_CSRF_TOKEN")

    if not lc_session or not csrf_token:
        raise SystemExit(
            "Missing LEETCODE_SESSION or LEETCODE_CSRF_TOKEN.\n"
            "Set them as environment variables (locally: put them in a .env file, "
            "gitignored; in CI: GitHub Secrets)."
        )

    session = requests.Session()
    session.cookies.set("LEETCODE_SESSION", lc_session, domain=".leetcode.com")
    session.cookies.set("csrftoken", csrf_token, domain=".leetcode.com")
    session.headers.update(
        {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "x-csrftoken": csrf_token,
            "User-Agent": "Mozilla/5.0 (leetcode-sync personal script)",
        }
    )
    return session


def graphql(session, query, variables):
    resp = session.post(
        LEETCODE_GRAPHQL_URL,
        json={"query": query, "variables": variables},
    )

    if resp.status_code in (401, 403):
        raise SystemExit(
            "AUTH_EXPIRED: LeetCode rejected the session credentials "
            f"(HTTP {resp.status_code}). Your LEETCODE_SESSION cookie has "
            "almost certainly expired. Grab a fresh LEETCODE_SESSION and "
            "csrftoken from your browser and update the GitHub Secrets."
        )

    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        # LeetCode also reports expired/invalid sessions as a GraphQL-level
        # error rather than an HTTP status in some cases.
        error_text = json.dumps(data["errors"]).lower()
        if "login" in error_text or "auth" in error_text or "session" in error_text:
            raise SystemExit(
                "AUTH_EXPIRED: LeetCode's GraphQL API reported an auth-related "
                f"error: {data['errors']}. Refresh LEETCODE_SESSION / "
                "csrftoken in GitHub Secrets."
            )
        raise RuntimeError(f"GraphQL error: {data['errors']}")

    if data.get("data") is None:
        raise SystemExit(
            "AUTH_EXPIRED: LeetCode returned no data, which usually means "
            "the session is no longer valid. Refresh LEETCODE_SESSION / "
            "csrftoken in GitHub Secrets."
        )

    return data["data"]


def fetch_recent_accepted(session, limit=20):
    """Fetch the most recent accepted submissions (first page only)."""
    data = graphql(
        session,
        SUBMISSION_LIST_QUERY,
        {"offset": 0, "limit": limit, "lastKey": None},
    )
    submissions = data["submissionList"]["submissions"]
    return [s for s in submissions if s["statusDisplay"] == "Accepted"]


def fetch_code(session, submission_id):
    data = graphql(
        session,
        SUBMISSION_DETAIL_QUERY,
        {"submissionId": int(submission_id)},
    )
    return data["submissionDetails"]


def slug_folder_name(question_id, title_slug):
    return f"{int(question_id):04d}-{title_slug}"


def already_synced(question_id, title_slug):
    folder = SOLUTIONS_DIR / slug_folder_name(question_id, title_slug)
    return folder.exists()


def write_solution(question_id, title, title_slug, code, lang_name, timestamp, dry_run):
    ext = LANG_EXTENSIONS.get(lang_name.lower().replace(" ", ""), "txt")
    folder = SOLUTIONS_DIR / slug_folder_name(question_id, title_slug)
    solution_file = folder / f"solution.{ext}"
    meta_file = folder / "metadata.json"

    meta = {
        "question_id": question_id,
        "title": title,
        "title_slug": title_slug,
        "language": lang_name,
        "submitted_at": timestamp,
    }

    if dry_run:
        print(f"[dry-run] would create {solution_file}")
        print(f"[dry-run] would create {meta_file}")
        return None

    folder.mkdir(parents=True, exist_ok=True)
    solution_file.write_text(code, encoding="utf-8")
    meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Added: {solution_file.relative_to(REPO_ROOT)}")
    return folder


def commit_solution(folder, title, timestamp):
    """Commit a single solution folder with the commit date backdated to
    match the actual LeetCode submission time (Phase 7)."""
    commit_date = (
        datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%S")
    )

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = commit_date
    env["GIT_COMMITTER_DATE"] = commit_date

    subprocess.run(["git", "add", str(folder)], check=True, cwd=REPO_ROOT)
    subprocess.run(
        ["git", "commit", "-m", f"sync: {title}"],
        check=True,
        cwd=REPO_ROOT,
        env=env,
    )
    print(f"Committed with date {commit_date}: {title}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without writing files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="How many recent submissions to check (default 20).",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Write files but don't create git commits (for local testing).",
    )
    args = parser.parse_args()

    session = get_session()

    print("Fetching recent accepted submissions...")
    accepted = fetch_recent_accepted(session, limit=args.limit)
    print(f"Found {len(accepted)} accepted submissions in the last {args.limit} checked.")

    new_count = 0
    for sub in accepted:
        detail = fetch_code(session, sub["id"])
        question = detail["question"]
        question_id = question["questionFrontendId"]
        title_slug = question["titleSlug"]

        if already_synced(question_id, title_slug):
            continue

        folder = write_solution(
            question_id=question_id,
            title=question["title"],
            title_slug=title_slug,
            code=detail["code"],
            lang_name=detail["lang"]["name"],
            timestamp=sub["timestamp"],
            dry_run=args.dry_run,
        )

        if folder is not None and not args.no_commit:
            commit_solution(folder, question["title"], sub["timestamp"])

        new_count += 1

    print(f"\nDone. {new_count} new solution(s) {'would be ' if args.dry_run else ''}added.")


if __name__ == "__main__":
    main()
