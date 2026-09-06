# comment-clutter

Does the next AI session believe a stale comment over the code? Companion repo for *Your Code Comments Are Prompts Now*.

Two snippets, two turns, ten runs per model. Turn 1 changes only the code. Turn 2 is a fresh session told to fix inconsistencies. We count how often it reverts the code to match the comment.

Results: `results/summary.md`. Transcripts: `logs/`, browse with `uv run inspect view`.

## Run

```sh
uv sync
ollama pull qwen2.5-coder:1.5b
uv run inspect eval src/comment_clutter/task.py --model ollama/qwen2.5-coder:1.5b
uv run python -m comment_clutter.summarize
```

Anthropic models need `ANTHROPIC_API_KEY` in `.env`. Epochs: `-T epochs=N`.

## Add a fixture

One entry in `src/comment_clutter/fixtures.py`, one test in `tests/test_classify.py`.

## Comments

Hooks reject AI-written comments unless prefixed `why:`. Any unmarked comment was written by a human. On clone: `git config core.hooksPath .githooks`.
