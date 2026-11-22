"""audit_history.py - list every risky file that was EVER commited to this repo.

A file untracked today can still live in an old commit.
This script asks git for the WHOLE history, not just today's files.
"""
import subprocess

RISKY_ENDINGS = (".db", ".sqlite", ".sqlite3", ".env", ".csv", ".pem", ".key")
RISKY_WORDS = ("backup", "before_restore", "secret", "password", "bank")


def run_git(args):
    """Run one git command and give back its output as a list of lines."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return result.stdout.splitlines()


def all_paths_ever():
    """Every path that appears in any commit, on any branch."""
    lines = run_git(["log", "--all", "--name-only", "--pretty=format:"])
    return {line.strip() for line in lines if line.strip()}


def tracked_now():
    """Paths git tracks today."""
    return set(run_git(["ls-files"]))


def is_risky(path):
    name = path.lower()
    if name.endswith(RISKY_ENDINGS):
        return True
    return any(word in name for word in RISKY_WORDS)


def main():
    ever = all_paths_ever()
    now = tracked_now()
    risky = sorted(p for p in ever if is_risky(p))
    print(f"Paths ever committed: {len(ever)} | tracked now: {len(now)}")
    print(f"Risky paths in history: {len(risky)}")
    for path in risky:
        if path in now:
            status = "STILL TRACKED"
        else:
            status = "gone today, STILL IN HISTORY"
        print(f"   {path} -> {status}")


if __name__ == "__main__":
    main()