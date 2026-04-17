# Claude Code Custom Statusline

A custom status line for Claude Code that renders the information I actually wanted:

- model
- project + git branch
- context usage
- 5-hour usage
- 7-day usage

I initially tried `claude-hud`, but in my setup I kept running into layout issues and inconsistent rendering for the compact horizontal format I wanted. I eventually replaced the plugin-based rendering path with a small custom script that I fully control.

## Why this exists

I wanted a status line that was:

- horizontally scannable
- stable
- easy to debug
- easy to customize
- independent from plugin UI behavior

I also discovered that Claude Code's `statusLine` input is not always consistent. In some runs, `rate_limits` are present. In others, they may be missing. This script uses a simple cache fallback strategy so the display remains useful.

## What it shows

Line 1:

- model
- plan label
- current project
- git branch / dirty state

Line 2:

- context
- usage (5h)
- weekly usage (7d)

Example:

```text
[Sonnet 4.6 | Max] | glia-ios git:(main*)
Context ░░░░░░░░░░ 0% | Usage ██████████ 99% (1h 19m) | Weekly ██░░░░░░░░ 16% (6d 15h)
```

## Installation

Copy the script into your Claude config directory:

```bash
mkdir -p ~/.claude
cp statusline.py ~/.claude/statusline.py
chmod +x ~/.claude/statusline.py
```

Then update `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "swift-lsp@claude-plugins-official": true
  },
  "statusLine": {
    "type": "command",
    "command": "python3 \"$HOME/.claude/statusline.py\""
  }
}
```

Restart Claude Code after updating the config.

## How it works

Claude Code passes JSON into the status line command via stdin.

This script reads that JSON and renders:

- `model.display_name`
- `context_window.used_percentage`
- `rate_limits.five_hour.used_percentage`
- `rate_limits.seven_day.used_percentage`

If `rate_limits` are missing in the current payload, the script falls back to a cached debug JSON file:

```text
~/.claude/statusline-debug.json
```

That makes the display more stable across inconsistent runtime payloads.

## Files

- `statusline.py` — main renderer
- `examples/settings.json` — example Claude Code config

## Known limitations

- Tested on macOS
- Git branch display depends on running inside a git repo
- Some Claude Code runtime payloads may omit rate limit fields
- `Context` may show `0%` when the current payload does not include a usable percentage

## Why not claude-hud?

`claude-hud` was a useful starting point for understanding Claude Code status line customization, but I wanted tighter control over layout and rendering behavior. This project is not a fork of claude-hud — it is a separate script-based approach.

## License

MIT