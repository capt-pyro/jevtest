"""
Evaluate mock community content against the Community Content Policy using
TypeSafe's Jev model. Four questions per item: violates_policy (Noul),
violation_category (Choice), severity (Score), recommended_action (Choice).

Two question banks are available (same questions, different delivery):
  state   - questions.py: full policy.md is sent in state       (default)
  inline  - questions_inline.py: definitions live in each question's own
            instructions/criteria; no policy text in state

Usage: uv run evaluate.py [--bank state|inline]
"""

import argparse
import json

from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient

from questions import QUESTIONS as STATE_QUESTIONS
from questions_inline import QUESTIONS as INLINE_QUESTIONS

load_dotenv()

BANKS = {"state": STATE_QUESTIONS, "inline": INLINE_QUESTIONS}

# violates_policy is a probability of "yes"; below this, the other answers are ignored.
VIOLATION_THRESHOLD = 0.5


def format_answer(name: str, answer) -> str:
    if answer.type == "noul":
        return f"  {name}: {answer.noul:.2f}"
    if answer.type == "choice":
        return f"  {name}: {answer.choice} (confidence {answer.confidence:.2f})"
    if answer.type == "score":
        return f"  {name}: {answer.score:.2f} (confidence {answer.confidence:.2f})"
    return f"  {name}: {answer}"


def decide(answers) -> dict:
    """Compose the raw answers into a final decision, gated on violates_policy.

    The questions are independent, so category/severity/action can describe a
    violation-shaped post (e.g. a report quoting abuse) even when it isn't one.
    Raw answers are kept untouched; this only derives the decision from them.
    """
    action = answers["recommended_action"].choice
    category = answers["violation_category"].choice
    severity = answers["severity"].score
    violates = answers["violates_policy"].noul >= VIOLATION_THRESHOLD
    if violates:
        return {"violates": True, "category": category, "severity": severity,
                "action": action, "gated": False}
    return {"violates": False, "category": "no_violation", "severity": 0.0,
            "action": "no_action", "gated": action != "no_action" or category != "no_violation"}


def build_state(bank: str, item: dict, policy: str) -> dict:
    state = {"content": item["text"], "author_history": item["author_history"]}
    if bank == "state":
        state["policy"] = policy
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", choices=BANKS, default="state")
    bank = parser.parse_args().bank
    questions = BANKS[bank]
    results_path = f"results_{bank}.json"

    with open("policy.md") as f:
        policy = f.read()
    with open("mock_content.json") as f:
        mock_content = json.load(f)

    results = []
    input_tokens = 0

    with TypeSafeClient() as client:
        for item in mock_content:
            response = client.system_one(
                model="jev-latest",
                state=build_state(bank, item, policy),
                questions=questions,
            )
            input_tokens += response.usage.input_tokens or 0

            print(f"[{item['id']}] {item['text']!r}")
            print(f"  history: {item['author_history']}")
            for name, answer in response.answers.items():
                print(format_answer(name, answer))
            decision = decide(response.answers)
            note = " (gated: raw answers said otherwise)" if decision["gated"] else ""
            print(f"  => decision: {decision['action']}{note}")
            print()

            results.append(
                {
                    "id": item["id"],
                    "text": item["text"],
                    "author_history": item["author_history"],
                    "decision": decision,
                    "answers": {
                        name: answer.model_dump()
                        for name, answer in response.answers.items()
                    },
                }
            )

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[{bank}] Wrote {len(results)} results to {results_path} ({input_tokens} input tokens)")


if __name__ == "__main__":
    main()
