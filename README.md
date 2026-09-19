# jevtest

A small test harness for TypeSafe's Jev model: given a written policy, have
Jev make moderation decisions on real-looking content and see how it reasons.

The scenario is a **Community Content Policy** for a marketplace/forum. Jev is
asked four questions about each piece of content, using criteria taken
directly from the policy text:

| Question              | Primitive | What it answers                                          |
| --------------------- | --------- | --------------------------------------------------------- |
| `violates_policy`     | Noul      | Does this violate the policy at all? (0-1 probability)     |
| `violation_category`  | Choice    | Which policy category best fits (harassment, spam, etc.)? |
| `severity`            | Score     | How severe, on the policy's None→Critical scale?           |
| `recommended_action`  | Choice    | What enforcement action follows, given severity + history? |

## Layout

- `policy.md` — the policy itself: violation categories, severity levels,
  enforcement actions, and notes on how they interact with a poster's history.
- `questions.py` — the "state" question bank: the four Jev questions above,
  built with the SDK's `Noul`/`Choice`/`Score` types, asked against a state
  that includes the full text of `policy.md`. Every criterion/definition
  (`CATEGORIES`, `SEVERITY_LEVELS`, `ACTIONS`) is lifted from `policy.md`
  rather than paraphrased separately, so Jev is judging against the same
  language a human moderator would read.
- `questions_inline.py` — the "inline" question bank: the same four questions
  and the same definitions (imported from `questions.py`), but with no policy
  in state. Each question carries whatever definitions it needs in its own
  instructions/criteria instead (e.g. `violates_policy` lists every category,
  `recommended_action` lists the severity scale).
- `mock_content.json` — 12 mock posts to evaluate, each with an `id`, `text`,
  and `author_history` (used to test how prior warnings/suspensions shift the
  recommended action). Mix includes clean posts, spam/phishing, harassment,
  hate speech, dangerous misinformation, a deliberately ambiguous case,
  repeat offenders, and two posts that quote or discuss abuse/scams only to
  report or warn about them (which the policy says are not violations).
- `evaluate.py` — loads `mock_content.json`, sends each item to Jev with the
  chosen question bank, prints a summary per item, and writes full structured
  results to `results_<bank>.json`.
- `.env` — holds `TYPESAFE_API_KEY`. Not committed (see `.gitignore`).

## Setup

Requires [uv](https://docs.astral.sh/uv/) and a TypeSafe API key.

```bash
uv sync
```

Put your key in `.env`:

```
TYPESAFE_API_KEY=apikey_...
```

## Running it

```bash
uv run evaluate.py                # policy-in-state bank (default)
uv run evaluate.py --bank inline  # definitions inlined in each question
```

This calls the live TypeSafe API (`jev-latest`) once per mock item. For each
one it prints the content, the poster's history, and Jev's four answers:

```
[post_005] "People from [ethnic group] are the reason this neighborhood is falling apart..."
  history: No prior warnings or violations.
  violates_policy: 0.97
  violation_category: hate_speech (confidence 1.00)
  severity: 2.81 (confidence 0.84)
  recommended_action: permanent_ban (confidence 0.37)
```

Each item also gets a final `=> decision:` line. The four questions are
independent, so `evaluate.py` composes them in code: if `violates_policy` is
below `VIOLATION_THRESHOLD` (0.5), the category/severity/action answers are
ignored and the decision is `no_action`. This keeps a post that merely quotes
abuse to report it from being suspended just because its category and severity
answers describe abuse. The raw answers are still saved untouched, and gated
items are flagged in the output.

`results_state.json` / `results_inline.json` get the same data in full
(probabilities over every option, score legend) for closer inspection, so the
two banks can be diffed. The run also prints total input tokens, which is the
main cost difference between them: sending the whole policy with every
request costs more than inlining only the definitions each question needs.

## Extending this

- **New test cases**: add entries to `mock_content.json` with `id`, `text`,
  and `author_history`. `evaluate.py` sends Jev a shared `state` of
  `{policy, content, author_history}` (the full text of `policy.md`, the post,
  and the poster's record), and every question's instructions reference those
  fields by name. To give Jev more context, add a field to that state in
  `evaluate.py` and reference it in the relevant question's instructions.
- **New questions**: add a `Noul`/`Choice`/`Score` entry to `QUESTIONS` in
  `questions.py`. Keep criteria grounded in `policy.md` rather than invented
  ad hoc, so an update to the policy has one clear place to propagate from.
- **A different policy domain entirely**: swap out `policy.md` and rewrite
  `questions.py`/`mock_content.json` to match — the shape of `evaluate.py`
  doesn't assume anything about content moderation specifically.
