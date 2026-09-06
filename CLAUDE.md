# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Benchmark harness plus blog post testing whether stale comments left by one AI coding session cause errors in later sessions. `intent.md` is the design spec: it defines the two test cases (`a = b` and `isAdmin`), the two-turn protocol, and the three turn-2 outcomes to record (comment changed / code reverted / contradiction left). Do not change the experiment design without updating `intent.md` first.

## Stack

- Python managed with `uv`. Run tools as `uv run pytest`, `uv run ruff format`, `uv run inspect eval`. Do not use system `pip` or `/usr/bin/python3`.
- The harness is an Inspect AI task in `src/comment_clutter/task.py`. Run with `uv run inspect eval src/comment_clutter/task.py --model ollama/<name>`. Use absolute imports (`from comment_clutter.x import`) in that file; Inspect loads it as a standalone module so relative imports fail.
- Inspect logs go to `logs/` (gitignored). `uv run python -m comment_clutter.summarize` turns them into the table in `results/summary.md`.
- Local models run through Ollama (Homebrew service, `localhost:11434`) as `ollama/<name>`. Check `ollama list` before a run; if a model is missing, give `ollama pull <model>` rather than assuming it is available.
- Claude models run as `anthropic/<model-id>` (default `anthropic/claude-opus-5`). The key lives in `.env` as `ANTHROPIC_API_KEY`, which Inspect loads itself. Never read, print, or copy `.env`.
- Harness code and blog post are separate concerns. Keep the post in `post.md` (or `drafts/`), not mixed into the harness package.

## Rules

- Two gates reject AI-written comments. A PreToolUse hook denies any Write or Edit that adds a comment line, and `.githooks/pre-commit` rejects staged comment lines when committing inside a Claude session. Say it in the code instead. If a comment is needed to explain why, start it with `why:`. Unmarked comments are by definition human-written. On a fresh clone run `git config core.hooksPath .githooks`.

- Every number in the blog post must come from `results/summary.md` or an Inspect log in `logs/`. Never invent or estimate figures.
- Turn-2 prompts must never include turn-1's instruction or history. The whole point is that the second session only sees the resulting file.
- When writing test fixtures, use the exact code snippets from `intent.md` so results are comparable with the article.
