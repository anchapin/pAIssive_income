import os
import subprocess
import sys
from pathlib import Path

def get_changed_files():
    # Try to get files changed in PR or last commit
    github_event_name = os.getenv("GITHUB_EVENT_NAME")
    github_base_ref = os.getenv("GITHUB_BASE_REF")
    github_head_ref = os.getenv("GITHUB_HEAD_REF")

    # Default to HEAD^..HEAD if not in a PR
    if github_event_name == "pull_request" and github_base_ref and github_head_ref:
        # Fetch base branch to compare
        subprocess.run(["git", "fetch", "origin", github_base_ref], check=True)
        diff_range = f"origin/{github_base_ref}...HEAD"
    else:
        diff_range = "HEAD^..HEAD"

    result = subprocess.run(
        ["git", "diff", "--name-only", diff_range],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return files

def is_doc_file(path):
    p = Path(path)
    # Any Markdown file at repo root
    if p.suffix.lower() == ".md" and len(p.parts) == 1:
        return True
    # Any file in docs/ or docs_source/
    if len(p.parts) > 1 and p.parts[0] in {"docs", "docs_source"}:
        return True
    return False

def main():
    changed_files = get_changed_files()
    if not changed_files:
        print("No files changed.")
        sys.exit(0)

    doc_files = [f for f in changed_files if is_doc_file(f)]
    non_doc_files = [f for f in changed_files if not is_doc_file(f)]

    if non_doc_files and not doc_files:
        print("❌ Documentation not updated! The following files were changed without any documentation update:")
        for f in non_doc_files:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅ Documentation check passed.")

if __name__ == "__main__":
    main()