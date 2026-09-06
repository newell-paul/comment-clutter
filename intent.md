# When AI-Generated Comments Cause More Harm Than Good

AI coding assistants are getting better at changing code.

But there is a quieter failure mode that deserves more attention:

**The code changes, but the comment does not.**

That sounds trivial. Sometimes it is.

But once stale comments are fed back into future AI sessions, reviewed by humans, copied into documentation, or used by another agent as context, a tiny inconsistency can become a much larger reliability problem.

## A tiny example

Start with this:

```js
// make a equal to b
let a = b;
```

Now imagine we give a small coding model this instruction:

> Change only the code so that `a != b`.

A perfectly plausible result is:

```js
// make a equal to b
let a = b + 1;
```

The executable code now does what was requested.

The comment is wrong.

At first glance, this looks like a minor documentation issue. The program may still run correctly. Tests may still pass. The compiler certainly does not care.

But the file now contains two contradictory pieces of information:

```text
Comment: a should equal b
Code:    a should not equal b
```

Which one represents the intended behavior?

That question becomes much more important when another human or AI sees the file later.

## Why this gets worse across sessions

Suppose a new AI agent opens the repository next week.

It sees:

```js
// make a equal to b
let a = b + 1;
```

The agent does not have the full history of why the code changed.

It only has the current context.

Now imagine the next prompt says:

> Fix any inconsistencies you find in this function.

What should the model do?

It may decide the implementation is wrong and change it back:

```js
// make a equal to b
let a = b;
```

The first agent followed the requirement correctly.

The second agent "fixed" it based on stale documentation.

The bug was not introduced because either model was completely incapable of coding. It appeared because **the context contained conflicting semantic signals**.

This is where a small comment problem becomes a multi-turn reliability problem.

## A more realistic example: `isAdmin`

Now consider something closer to production code:

```js
// Only admins can access this page
if (isAdmin) {
  grantAccess();
}
```

So far, everything agrees.

Now the product requirement changes.

Authenticated users should also be allowed through, and an AI agent receives a narrow instruction such as:

> Change only the condition so authenticated users can access the page.

It produces:

```js
// Only admins can access this page
if (isAdmin || isAuthenticated) {
  grantAccess();
}
```

Again, the code may be correct.

The comment is now false.

And this time the false comment describes an **authorization rule**.

That is considerably more dangerous.

A developer reviewing the code quickly might read:

```js
// Only admins can access this page
```

and assume the security boundary is still admin-only.

A later AI agent may make the same assumption.

Suppose a future task says:

> There is a permissions bug here. Make sure the implementation follows the documented access policy.

A model could reasonably produce:

```js
// Only admins can access this page
if (isAdmin) {
  grantAccess();
}
```

It has just removed legitimate authenticated-user access because it treated the stale comment as the source of truth.

## Comments become part of the model's environment

Developers often think of comments as passive documentation.

For AI agents, they are also **input tokens**.

When an agent reads a repository, comments influence its understanding of:

* intended behavior
* invariants
* security assumptions
* architecture
* business rules
* edge cases
* what should and should not be changed

That means a stale comment is not merely something a human might misunderstand.

It can actively influence future code generation.

Consider the state:

```js
// Only admins can access this page
if (isAdmin || isAuthenticated) {
  grantAccess();
}
```

A human may notice the contradiction.

A model may notice it too.

But neither knows automatically which side is stale.

The repository has lost semantic consistency.

## The feedback loop

The worrying part is what happens after several AI-assisted changes.

A stale comment can move through the system like this:

```text
Requirement changes
        ↓
AI updates code
        ↓
Comment remains stale
        ↓
Future AI reads stale comment
        ↓
AI interprets old behavior as intended behavior
        ↓
Code, tests, or docs are changed around that assumption
        ↓
More future context reinforces the wrong interpretation
```

The original problem was one incorrect comment.

A few sessions later, you may have:

* an incorrect comment
* a test based on the incorrect comment
* documentation based on the incorrect comment
* a second code change based on the incorrect comment
* an AI-generated explanation supporting all of the above

Now the mistake looks well supported.

It is not.

All of those artifacts may share the same incorrect ancestor.

## More context does not always mean more truth

There is an interesting assumption in AI-assisted development:

> Giving the model more repository context should improve its decisions.

Usually, that is true.

But context quality matters.

If the context contains stale or contradictory information, adding more of it can amplify the problem.

Imagine a future agent sees all of these:

```js
// Only admins can access this page
```

A test named:

```js
test("rejects non-admin users", ...)
```

And documentation saying:

```text
This endpoint is restricted to administrators.
```

Three pieces of evidence seem to agree.

But perhaps all three were generated after the original comment became stale.

Meanwhile, the real product requirement was:

```text
Authenticated users should also have access.
```

What looks like corroboration is actually **shared-error propagation**.

## Small models may be especially interesting here

This failure mode is worth testing across model sizes.

A high-capability model might notice:

```js
// make a equal to b
let a = b + 1;
```

and decide that the comment should probably be updated too.

A lower-level model may follow the local instruction more literally:

> Change only the code.

That creates an interesting tension between two desirable behaviors:

**Instruction following**

and

**maintaining semantic consistency**

If the model edits the comment, it may technically violate a narrow instruction.

If it leaves the comment unchanged, it may make the codebase less reliable.

That trade-off is worth measuring.

## A simple experiment

You could test this with a small benchmark.

Start with:

```js
// make a equal to b
let a = b;
```

Then prompt:

> Change only the executable code so that `a != b`.

Measure whether the model produces something like:

```js
// make a equal to b
let a = b + 1;
```

Then feed that result into another session and ask:

> Fix inconsistencies in this file.

Record whether the model:

1. changes the comment,
2. changes the code back,
3. leaves the contradiction untouched.

Then repeat the same idea with an authorization example:

```js
// Only admins can access this page
if (isAdmin) {
  grantAccess();
}
```

Ask the first agent to allow authenticated users.

Then ask later agents questions about the intended permissions model.

The interesting measurement is not only whether the first model makes a mistake.

It is whether the inconsistency **changes the probability of mistakes in later turns**.

## The important metric is not one-turn accuracy

Most coding benchmarks measure something close to:

> Did the generated code satisfy the task?

That matters.

But agentic coding systems also need another metric:

> Did this edit leave the repository in a state that future agents can correctly understand?

Those are not the same thing.

An edit can be locally correct while making the system globally harder to reason about.

For example:

```js
// make a equal to b
let a = b + 1;
```

may satisfy the immediate task perfectly.

But it reduces the reliability of the context available to the next developer or model.

Likewise:

```js
// Only admins can access this page
if (isAdmin || isAuthenticated) {
  grantAccess();
}
```

may implement the new product requirement correctly while leaving behind a misleading description of a security boundary.

## Comments are executable context

Comments are not executable by JavaScript.

But in AI-assisted software development, they are effectively **executable context**.

They influence what the next model generates.

That means maintaining comment correctness is no longer just a documentation-quality concern.

It is part of maintaining the input state of future agents.

The more AI systems repeatedly read, modify, summarize, and regenerate the same repository, the more important this becomes.

A single stale comment may be harmless.

A stale comment that survives ten agent sessions may not be.

And when both humans and models begin making decisions based on it, the impact can multiply.

The question is therefore not simply:

> Can AI write incorrect comments?

We already know the answer to that.

The more interesting question is:

> **Can small semantic inconsistencies introduced during one AI coding session propagate through future context and systematically increase the error rate of both agents and humans?**

That seems like a failure mode worth testing.
