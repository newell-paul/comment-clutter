
## 2026-09-05 (n=10 per fixture)

| model | fixture | t1 stale comment | t2 comment_updated | t2 code_reverted | t2 untouched | t2 other | reverted rate |
|---|---|---|---|---|---|---|---|
| qwen2.5-coder:1.5b | a_equals_b | 6/10 | 1 | 0 | 6 | 3 | 0% |
| qwen2.5-coder:1.5b | is_admin | 0/10 | 0 | 0 | 8 | 2 | 0% |
| qwen3-coder:30b | a_equals_b | 10/10 | 0 | 0 | 0 | 10 | 0% |
| qwen3-coder:30b | is_admin | 10/10 | 0 | 10 | 0 | 0 | 100% |

## Inspect logs

| model | fixture | n | t1 refused | t1 stale comment | t2 refused | t2 comment_updated | t2 code_reverted | t2 untouched | t2 other | reverted rate |
|---|---|---|---|---|---|---|---|---|---|---|
| ollama/qwen2.5-coder:1.5b | a_equals_b | 10 | 0 | 4 | 0 | 1 | 2 | 6 | 1 | 20% |
| ollama/qwen2.5-coder:1.5b | is_admin | 10 | 0 | 1 | 0 | 1 | 0 | 9 | 0 | 0% |
| ollama/qwen3-coder:30b | a_equals_b | 10 | 0 | 10 | 0 | 0 | 10 | 0 | 0 | 100% |
| ollama/qwen3-coder:30b | is_admin | 10 | 0 | 10 | 0 | 0 | 8 | 1 | 1 | 80% |
| anthropic/claude-haiku-4-5 | a_equals_b | 10 | 0 | 10 | 0 | 0 | 10 | 0 | 0 | 100% |
| anthropic/claude-haiku-4-5 | is_admin | 10 | 0 | 10 | 0 | 0 | 10 | 0 | 0 | 100% |
| anthropic/claude-opus-5 | a_equals_b | 10 | 0 | 10 | 0 | 1 | 8 | 0 | 1 | 80% |
| anthropic/claude-opus-5 | is_admin | 10 | 7 | 3 | 3 | 0 | 0 | 0 | 0 | n/a |
