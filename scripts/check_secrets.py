"""Scan tracked text and reachable commit diffs for common credential formats.
Never print matching secret values. This is not a comprehensive secret scanner.
"""
import re
import subprocess
import sys

PATTERNS = {
    "OpenAI-shaped credential": rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{30,}",
    "GitHub credential": rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})",
    "AWS access key": rb"AKIA[A-Z0-9]{16}",
    "private key": rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
}

def main():
    history = subprocess.check_output(["git", "log", "--all", "-p", "--no-ext-diff", "--no-color"])
    matches = [name for name, pattern in PATTERNS.items() if re.search(pattern, history)]
    if matches:
        print("Potential credential patterns found; investigate privately: " + ", ".join(matches))
        return 1
    print("No common credential patterns detected in reachable commit patches.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
