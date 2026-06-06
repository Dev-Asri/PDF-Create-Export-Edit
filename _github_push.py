# -*- coding: utf-8 -*-
"""Commit project to GitHub via API (no git binary needed)."""
import os, json, base64, mimetypes, time
import requests

TOKEN = os.environ.get("GH_TOKEN", "")
OWNER = "Uzman-lab"
REPO = "PDF-Create-Export-Edit"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}
API = "https://api.github.com"
PROJECT = r"D:\AICodeProje\PDFIMAGEEXPORT"

def api(method, url, data=None):
    r = requests.request(method, url, headers=HEADERS, json=data)
    if r.status_code >= 400:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        return None
    return r.json()

def get_gitignore_patterns():
    patterns = []
    gi = os.path.join(PROJECT, ".gitignore")
    if os.path.exists(gi):
        with open(gi, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

def should_ignore(name, patterns):
    for p in patterns:
        if p.endswith("/"):
            if name == p.rstrip("/") or name.startswith(p):
                return True
        elif p.startswith("*"):
            if name.endswith(p[1:]):
                return True
        elif name == p:
            return True
    return False

def walk_files():
    ignore_patterns = get_gitignore_patterns()
    files = []
    for root, dirs, fnames in os.walk(PROJECT):
        # Skip ignored dirs
        dirs[:] = [d for d in dirs if not should_ignore(d, ignore_patterns) and d != ".git"]
        rel = os.path.relpath(root, PROJECT)
        for fname in fnames:
            if should_ignore(fname, ignore_patterns):
                continue
            fpath = os.path.join(root, fname)
            rel_path = os.path.join(rel, fname) if rel != "." else fname
            files.append((rel_path.replace("\\", "/"), fpath))
    return files

def main():
    print("1. Verify repo exists...")
    repo = api("GET", f"{API}/repos/{OWNER}/{REPO}")
    if repo is None:
        print("  Creating repo...")
        repo = api("POST", f"{API}/user/repos", {"name": REPO, "private": False})
        if repo is None:
            print("  FAILED to create repo")
            return
        print(f"  Created: {repo['html_url']}")
    else:
        print(f"  Found: {repo['html_url']}")

    print("2. Get current head ref (if any)...")
    ref = api("GET", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/main")
    parent_sha = None
    if ref:
        parent_sha = ref["object"]["sha"]
        print(f"  Existing head: {parent_sha[:8]}")
    else:
        print("  No existing commits (initial commit)")

    print("3. Walk project files...")
    file_list = walk_files()
    # Filter: only include files we want to commit (code, assets)
    exclude_exts = {".pyc", ".spec"}
    exclude_names = {"PDF_Create_Export_Edit.exe", "_splitter.py", "pdf_to_images.py"}
    to_commit = []
    for rel_path, abs_path in file_list:
        ext = os.path.splitext(rel_path)[1]
        base = os.path.basename(rel_path)
        if ext in exclude_exts or base in exclude_names:
            continue
        # Skip dist/ and build/ (already in gitignore but just in case)
        if rel_path.startswith("dist/") or rel_path.startswith("build/"):
            continue
        to_commit.append((rel_path, abs_path))
    print(f"  {len(to_commit)} files to commit")

    print("4. Create blobs for each file...")
    blobs = {}
    for rel_path, abs_path in to_commit:
        with open(abs_path, "rb") as f:
            content = f.read()
        # Use creating-a-blob API
        encoding = "base64"
        b64 = base64.b64encode(content).decode("ascii")
        blob = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/blobs",
                   {"content": b64, "encoding": "base64"})
        if blob is None:
            print(f"  Failed blob for {rel_path}")
            return
        blobs[rel_path] = blob["sha"]
        print(f"  blob {rel_path} -> {blob['sha'][:8]}")

    print("5. Create tree...")
    tree_items = []
    for rel_path, sha in blobs.items():
        tree_items.append({"path": rel_path, "mode": "100644", "type": "blob", "sha": sha})
    tree_data = {"tree": tree_items}
    if parent_sha:
        tree_data["base_tree"] = parent_sha
    tree = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/trees", tree_data)
    if tree is None:
        print("  FAILED to create tree")
        return
    tree_sha = tree["sha"]
    print(f"  Tree: {tree_sha[:8]}")

    print("6. Create commit...")
    commit_data = {
        "message": "Proje yeniden yapılandırıldı - src/ paket yapısı",
        "tree": tree_sha,
    }
    if parent_sha:
        commit_data["parents"] = [parent_sha]
    commit = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/commits", commit_data)
    if commit is None:
        print("  FAILED to create commit")
        return
    commit_sha = commit["sha"]
    print(f"  Commit: {commit_sha[:8]}")

    print("7. Update main branch...")
    result = api("PATCH", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/main",
                 {"sha": commit_sha, "force": False})
    if result is None:
        # Try creating the ref if it doesn't exist
        result = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/refs",
                     {"ref": "refs/heads/main", "sha": commit_sha})
    if result:
        print(f"\n SUCCESS! Pushed to main branch")
        print(f"  https://github.com/{OWNER}/{REPO}")
    else:
        print("  FAILED to update ref")

if __name__ == "__main__":
    main()
