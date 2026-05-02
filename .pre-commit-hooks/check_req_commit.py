#!/usr/bin/env python3
"""
Pre-commit hook to enforce 'req' type for requirement file commits.

When requirements.md or technical-specifications.md are staged,
the commit message must start with 'req:' or 'req(...):'
"""

import sys
import subprocess


def main(argv=None):
    args = argv or sys.argv[1:]

    if not args:
        print("Error: commit message file path is required")
        return 1

    commit_msg_file = args[0]

    # Read the commit message
    try:
        with open(commit_msg_file, 'r', encoding='utf-8') as f:
            commit_msg = f.read().strip()
    except IOError as e:
        print(f"Error reading commit message file: {e}")
        return 1

    # Get the list of staged files
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=False
        )
        staged_files = result.stdout.strip().split('\n')
    except Exception as e:
        print(f"Error getting staged files: {e}")
        return 1

    # Check if requirements files are staged
    req_files = ['requirements.md', 'technical-specifications.md']
    has_req_files = any(f in staged_files for f in req_files)

    if has_req_files:
        # Check if commit message starts with 'req:' or 'req(...):' (case-insensitive)
        msg_lower = commit_msg.lower()
        if not (msg_lower.startswith('req:') or msg_lower.startswith('req(')):
            print("Error: Commits that modify requirements.md or technical-specifications.md")
            print("       must use the 'req' type: 'req: description' or 'req(scope): description'")
            print(f"\nYour commit message: {commit_msg}")
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
