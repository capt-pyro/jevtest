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
- `questions.py` — the four Jev questions above, built with the SDK's
  `Noul`/`Choice`/`Score` types. Every criterion/definition here is lifted
  from `policy.md` rather than paraphrased separately, so Jev is judging
  against the same language a human moderator would read.
- `mock_content.json` — 10 mock posts to evaluate, each with an `id`, `text`,
  and `author_history` (used to test how prior warnings/suspensions shift the
  recommended action). Mix includes clean posts, spam/phishing, harassment,
  hate speech, dangerous misinformation, a deliberately ambiguous case, and
  repeat offenders.
- `evaluate.py` — loads `mock_content.json`, sends each item to Jev with the
  questions from `questions.py`, prints a summary per item, and writes full
  structured results to `results.json`.
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
uv run evaluate.py
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

`results.json` gets the same data in full (probabilities over every option,
score legend, token usage) for closer inspection.

## Extending this

- **New test cases**: add entries to `mock_content.json` — only `id`, `text`,
  and `author_history` are required, and they're passed to Jev as `state`
  as-is, so extra fields are fine if `questions.py` is written to reference them.
- **New questions**: add a `Noul`/`Choice`/`Score` entry to `QUESTIONS` in
  `questions.py`. Keep criteria grounded in `policy.md` rather than invented
  ad hoc, so an update to the policy has one clear place to propagate from.
- **A different policy domain entirely**: swap out `policy.md` and rewrite
  `questions.py`/`mock_content.json` to match — the shape of `evaluate.py`
  doesn't assume anything about content moderation specifically.
