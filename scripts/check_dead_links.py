#!/usr/bin/env python3
"""
check_dead_links.py.

Scans all Markdown documentation for dead links, excluding files/directories in .gitignore.
Outputs a summary report to stdout.

- Checks all HTTP/HTTPS links (reports as dead if HTTP error or timeout).
- Checks file links (relative/absolute) and anchor links (e.g., #section) for existence.
- Prints summary of checked files, total links, and dead/missing links.

Requires: Python 3.8+, requests
"""

import fnmatch
import os
import re
import sys
from urllib.parse import urldefrag, urlparse

import requests

# Config
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TIMEOUT = 7  # seconds
EXCLUDE_PATTERNS = []

def load_gitignore(root):
    ignore = []
    path = os.path.join(root, ".gitignore")
    if not os.path.isfile(path):
        return ignore
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                ignore.append(line)
    return ignore

def should_exclude(path, ignore_patterns) -> bool:
    rel_path = os.path.relpath(path, REPO_ROOT)
    for pat in ignore_patterns:
        if pat.endswith("/"):
            # Directory pattern
            if rel_path.startswith(pat):
                return True
        if fnmatch.fnmatch(rel_path, pat):
            return True
    return False

def find_markdown_files(root, ignore_patterns):
    for dirpath, dirnames, filenames in os.walk(root):
        # Exclude .git and virtualenvs quickly
        if should_exclude(dirpath, ignore_patterns):
            dirnames[:] = []
            continue
        for fname in filenames:
            if fname.lower().endswith(".md"):
                full = os.path.join(dirpath, fname)
                if not should_exclude(full, ignore_patterns):
                    yield full

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_LINK_RE = re.compile(r"<(https?://[^>]+)>")

def extract_links(markdown):
    links = []
    for m in LINK_RE.finditer(markdown):
        url = m.group(2).strip()
        if url.startswith("mailto:"):
            continue
        links.append(url)
    for m in INLINE_LINK_RE.finditer(markdown):
        url = m.group(1).strip()
        links.append(url)
    return links

def check_http_link(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        if resp.status_code < 400:
            return True
        # Some hosts block HEAD; try GET
        resp = requests.get(url, stream=True, timeout=TIMEOUT)
        return resp.status_code < 400
    except Exception:
        return False

def anchors_in_markdown(content):
    """Return a set of valid anchor names in the file, following GitHub's anchor logic."""
    headers = re.findall(r"^#+\s*(.+)$", content, flags=re.MULTILINE)
    anchors = set()
    for h in headers:
        # Basic GitHub-style anchor: lowercase, spaces to -, remove some punctuation
        anchor = h.strip().lower()
        anchor = re.sub(r"[^\w\- ]+", "", anchor)  # Remove most punctuation except -
        anchor = anchor.replace(" ", "-")
        anchors.add(anchor)
    return anchors

def check_file_link(url, basepath) -> bool:
    # Remove anchor
    path, anchor = urldefrag(url)
    path = os.path.normpath(os.path.join(os.path.dirname(basepath), path))
    if not os.path.exists(path):
        return False
    # Anchor: check if anchor exists in file
    if anchor:
        with open(path, encoding="utf-8", errors="ignore") as f:
            txt = f.read()
            anchors = anchors_in_markdown(txt)
            anchor_fmt = anchor.lower().replace(" ", "-")
            if anchor_fmt in anchors:
                return True
        return False
    return True

def main() -> None:
    ignore_patterns = load_gitignore(REPO_ROOT)
    files_checked = 0
    total_links = 0
    dead_links = []

    for mdfile in find_markdown_files(REPO_ROOT, ignore_patterns):
        files_checked += 1
        with open(mdfile, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        links = extract_links(content)
        total_links += len(links)
        file_anchors = anchors_in_markdown(content)
        for link in links:
            parsed = urlparse(link)
            if parsed.scheme in ("http", "https"):
                ok = check_http_link(link)
                if not ok:
                    dead_links.append((mdfile, link))
            elif parsed.scheme == "":
                # Relative file or anchor
                if link.startswith("#"):
                    # Anchor within same file (e.g., [foo](#bar))
                    anchor_fmt = link[1:].lower().replace(" ", "-")
                    if anchor_fmt not in file_anchors:
                        dead_links.append((mdfile, link))
                elif not check_file_link(link, mdfile):
                    dead_links.append((mdfile, link))
            # else: skip mailto:, etc.

    print(f"Markdown files checked: {files_checked}")
    print(f"Links checked: {total_links}")
    print(f"Dead/missing links found: {len(dead_links)}")
    if dead_links:
        print("---- Dead Links ----")
        for fname, url in dead_links:
            print(f"{fname}: {url}")
        sys.exit(1)
    else:
        print("No dead links found!")
        sys.exit(0)

if __name__ == "__main__":
    main()
