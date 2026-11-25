"""Server-side, atomic quota reservations. No credentials or user text stored."""
import os
import sqlite3
import time
from pathlib import Path

def reserve(path=None, now=None):
    """Return (allowed, reason). Count attempts before calling the provider."""
    path = path or os.getenv("NEXUS_QUOTA_DB", "/tmp/nexus-quota.sqlite3")
    now = time.time() if now is None else now
    minute = int(os.getenv("NEXUS_REQUESTS_PER_MINUTE", "5"))
    daily = int(os.getenv("NEXUS_REQUESTS_PER_DAY", "50"))
    if minute < 1 or daily < 1:
        return False, "AI requests are disabled by the administrator."
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=5) as db:
        db.execute("CREATE TABLE IF NOT EXISTS attempts (ts REAL NOT NULL)")
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM attempts WHERE ts <= ?", (now-86400,))
        count_day = db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        count_min = db.execute("SELECT COUNT(*) FROM attempts WHERE ts > ?", (now-60,)).fetchone()[0]
        if count_day >= daily:
            return False, "The public AI demo has reached its rolling 24-hour quota."
        if count_min >= minute:
            return False, "The public AI demo is busy. Try again shortly."
        db.execute("INSERT INTO attempts VALUES (?)", (now,))
        return True, ""
