"""
Evaluate mock community content against the Community Content Policy using
TypeSafe's Jev model, via four questions defined in questions.py:
violates_policy (Noul), violation_category (Choice), severity (Score), and
recommended_action (Choice).
"""

import json

from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient

from questions import QUESTIONS

load_dotenv()


def format_answer(name: str, answer) -> str:
    if answer.type == "noul":
        return f"  {name}: {answer.noul:.2f}"
    if answer.type == "choice":
        return f"  {name}: {answer.choice} (confidence {answer.confidence:.2f})"
    if answer.type == "score":
        return f"  {name}: {answer.score:.2f} (confidence {answer.confidence:.2f})"
    return f"  {name}: {answer}"


def main() -> None:
    with open("mock_content.json") as f:
        mock_content = json.load(f)

    results = []

    with TypeSafeClient() as client:
        for item in mock_content:
            response = client.system_one(
                model="jev-latest",
                state=item,
                questions=QUESTIONS,
            )

            print(f"[{item['id']}] {item['text']!r}")
            print(f"  history: {item['author_history']}")
            for name, answer in response.answers.items():
                print(format_answer(name, answer))
            print()

            results.append(
                {
                    "id": item["id"],
                    "text": item["text"],
                    "author_history": item["author_history"],
                    "answers": {
                        name: answer.model_dump()
                        for name, answer in response.answers.items()
                    },
                }
            )

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"Wrote {len(results)} results to results.json")


if __name__ == "__main__":
    main()
