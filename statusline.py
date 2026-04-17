#!/usr/bin/env python3
import sys
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CACHE = Path.home() / ".claude" / "statusline-debug.json"

def bar(pct, width=10):
    try:
        pct = float(pct)
    except Exception:
        pct = 0
    pct = max(0, min(100, pct))
    filled = int(round(width * pct / 100))
    return "█" * filled + "░" * (width - filled)

def time_left(ts):
    try:
        ts = int(ts)
        now = int(datetime.now(timezone.utc).timestamp())
        diff = max(0, ts - now)
        d = diff // 86400
        h = (diff % 86400) // 3600
        m = (diff % 3600) // 60
        if d > 0:
            return f"{d}d {h}h"
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m"
    except Exception:
        return ""

def git_text():
    project = os.path.basename(os.getcwd())
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        branch = ""

    dirty = ""
    try:
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode == 0
        if inside:
            dirty_work = subprocess.run(
                ["git", "diff", "--quiet"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ).returncode != 0
            dirty_index = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ).returncode != 0
            if dirty_work or dirty_index:
                dirty = "*"
    except Exception:
        pass

    if branch:
        return f"{project} git:({branch}{dirty})"
    return project

def load_json(text):
    try:
        return json.loads(text) if text else {}
    except Exception:
        return {}

raw = sys.stdin.read().strip()
current = load_json(raw)

cached = {}
if CACHE.exists():
    try:
        cached = json.loads(CACHE.read_text())
    except Exception:
        cached = {}

if current.get("rate_limits"):
    try:
        CACHE.write_text(json.dumps(current))
    except Exception:
        pass

if not current.get("rate_limits") and cached.get("rate_limits"):
    current["rate_limits"] = cached["rate_limits"]

for key in ["model", "context_window", "workspace", "cwd"]:
    if not current.get(key) and cached.get(key):
        current[key] = cached[key]

data = current

model = data.get("model", {}).get("display_name") or "Sonnet 4.6"
plan = "Max"

ctx = data.get("context_window", {}).get("used_percentage")
if ctx is None:
    ctx = 0

five = data.get("rate_limits", {}).get("five_hour", {})
week = data.get("rate_limits", {}).get("seven_day", {})

five_pct = five.get("used_percentage", 0)
week_pct = week.get("used_percentage", 0)

five_left = time_left(five.get("resets_at"))
week_left = time_left(week.get("resets_at"))

line1 = f"[{model} | {plan}] | {git_text()}"
line2 = (
    f"Context {bar(ctx)} {int(ctx)}% | "
    f"Usage {bar(five_pct)} {int(five_pct)}%"
    + (f" ({five_left})" if five_left else "")
    + " | "
    f"Weekly {bar(week_pct)} {int(week_pct)}%"
    + (f" ({week_left})" if week_left else "")
)

print(line1)
print(line2)