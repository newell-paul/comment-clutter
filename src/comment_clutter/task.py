from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import (
    ChatMessageSystem,
    ChatMessageUser,
    GenerateConfig,
    get_model,
)
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import Generate, Solver, TaskState, solver

from comment_clutter.classify import (
    T2_OUTCOMES,
    classify_turn1,
    classify_turn2,
    extract_file,
)
from comment_clutter.fixtures import (
    BY_NAME,
    FIXTURES,
    SYSTEM,
    turn1_prompt,
    turn2_prompt,
)


@solver
def two_turn() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        f = BY_NAME[state.metadata["fixture"]]
        model = get_model()

        t1 = await model.generate(
            [
                ChatMessageSystem(content=SYSTEM),
                ChatMessageUser(content=turn1_prompt(f)),
            ]
        )
        file1 = extract_file(t1.completion)
        state.store.set("turn1_response", t1.completion)
        state.store.set("turn1_file", file1)
        state.store.set("turn1_stop", t1.stop_reason)

        if t1.stop_reason == "content_filter":
            state.output = t1
            return state

        t2_messages = [
            ChatMessageSystem(content=SYSTEM),
            ChatMessageUser(content=turn2_prompt(file1)),
        ]
        t2 = await model.generate(t2_messages)
        state.messages = [*t2_messages, t2.message]
        state.output = t2
        return state

    return solve


@scorer(
    metrics={
        "t1_refused": [mean(), stderr()],
        "t1_stale_comment": [mean(), stderr()],
        "t2_refused": [mean(), stderr()],
        **{f"t2_{o}": [mean(), stderr()] for o in T2_OUTCOMES},
    }
)
def outcome():
    async def score(state: TaskState, target: Target) -> Score:
        f = BY_NAME[state.metadata["fixture"]]
        file1 = state.store.get("turn1_file")
        refused = state.store.get("turn1_stop") == "content_filter"
        refused2 = not refused and state.output.stop_reason == "content_filter"
        file2 = "" if (refused or refused2) else extract_file(state.output.completion)
        c1 = "refused" if refused else classify_turn1(f, file1)
        if refused:
            c2 = "not_run"
        elif refused2:
            c2 = "refused"
        else:
            c2 = classify_turn2(f, file1, file2)
        value = {
            "t1_refused": int(refused),
            "t1_stale_comment": int(c1 == "stale_comment"),
            "t2_refused": int(refused2),
        }
        value.update({f"t2_{o}": int(c2 == o) for o in T2_OUTCOMES})
        return Score(
            value=value,
            answer=file2,
            explanation=f"turn1={c1} turn2={c2}",
            metadata={"turn1": c1, "turn2": c2, "turn1_file": file1},
        )

    return score


@task
def stale_comment(epochs: int = 10) -> Task:
    return Task(
        dataset=[
            Sample(id=f.name, input=turn1_prompt(f), metadata={"fixture": f.name})
            for f in FIXTURES
        ],
        solver=two_turn(),
        scorer=outcome(),
        epochs=epochs,
        config=GenerateConfig(temperature=0.7),
    )
