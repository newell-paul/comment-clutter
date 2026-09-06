---
name: run-experiment
description: Run the stale-comment two-turn benchmark from intent.md against one or more Ollama models with Inspect AI and write a results table. Use when the user asks to run the experiment, benchmark models, or regenerate results.
disable-model-invocation: true
---

Run the stale-comment propagation experiment with Inspect. Arguments: `$ARGUMENTS` is a space-separated list of models. Bare names are Ollama models (e.g. `qwen2.5-coder:1.5b`); names with a provider prefix are passed through (e.g. `anthropic/claude-opus-5`). If empty, use every model listed by `ollama list`.

## Preconditions

1. For Ollama models, check `which ollama` and `ollama list`. If Ollama or a requested model is missing, stop and tell the user the install/pull command. Do not fake results.
2. For `anthropic/` models, the key must be in `.env`. Do not read `.env`; run the eval and relay Inspect's error if the key is absent.
3. The task lives in `src/comment_clutter/task.py`. The two-turn protocol is the `two_turn` solver, the classifier is the `outcome` scorer. Fixtures and prompts are in `fixtures.py`.

## Run

Prefix bare names with `ollama/`, leave prefixed names alone, and join with commas:

```
uv run inspect eval src/comment_clutter/task.py --model ollama/<m1>,ollama/<m2> -T epochs=10 --display plain
uv run python -m comment_clutter.summarize
```

Run it in the background; the 30b model takes a few minutes for 10 epochs. Default epochs is 10 per fixture; pass `-T epochs=N` to change.

## Output

- Inspect writes one `.eval` log per model to `logs/`. `uv run inspect view` opens them in a browser for per-sample review.
- `summarize` appends a model × fixture table to `results/summary.md` with turn-1 stale-comment count, the four turn-2 outcome counts, and the code-reverted rate.
- Print the table to the user. For every sample scored `t2_other`, read `answer` and `metadata.turn1_file` in the log and say what happened, since those are the cases the classifier could not name.
