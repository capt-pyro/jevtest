"""
Jev questions for the Community Content Policy (option 2: policy inlined).

No policy text is sent in state. Each question instead carries every
definition it needs in its own instructions/criteria, because questions are
independent and cannot see each other's criteria or answers. State is just:
    content         - the post/message being judged
    author_history  - the poster's prior warnings/suspensions

Definitions are imported from questions.py so this bank and the
policy-in-state bank judge against identical wording; the only difference
between them is where that wording is delivered.
"""

from typesafe_sdk import Choice, Noul, Score

from questions import ACTIONS, CATEGORIES, SEVERITY_LEVELS


def _bullets(items: dict[str, str] | list[str]) -> str:
    if isinstance(items, dict):
        return "\n".join(f"- {name}: {text}" for name, text in items.items())
    return "\n".join(f"- {text}" for text in items)


_VIOLATION_CATEGORIES = {k: v for k, v in CATEGORIES.items() if k != "no_violation"}

# policy.md section 5; state bank gets this via the full policy text.
_CONTEXT_NOTE = (
    " Context matters: quoting hateful or abusive content to condemn or report it, "
    "or discussing a scam to warn others about it, is not itself a violation. "
    "Intent is inferred from the content and any available context, not assumed "
    "from category membership alone."
)

QUESTIONS = {
    "violates_policy": Noul(
        instructions=(
            "Does `content` violate the platform's Community Content Policy? "
            "Judge it in light of context and apparent intent: quoting or "
            "discussing harmful content to condemn or warn about it is not itself "
            "a violation, and ordinary disagreement, criticism, negative reviews, "
            "and untargeted profanity are not violations."
        ),
        criteria={
            "true": (
                "`content` falls into one of these violation categories:\n"
                + _bullets(_VIOLATION_CATEGORIES)
            ),
            "false": "`content` is acceptable: " + CATEGORIES["no_violation"],
        },
    ),
    "violation_category": Choice(
        instructions=(
            "Which single category from the platform's Community Content Policy best "
            "captures the most serious concern in `content`? If multiple categories "
            "plausibly apply, choose the one representing the most serious concern."
            + _CONTEXT_NOTE
        ),
        criteria=CATEGORIES,
    ),
    "severity": Score(
        instructions=(
            "Assess the severity of `content` under the platform's Community Content "
            "Policy. Severity should reflect potential for harm, not just the category "
            "name — a low-severity example of a serious-sounding category is possible, "
            "just as a high-severity example of a mundane-sounding category is possible."
            + _CONTEXT_NOTE
        ),
        criteria=SEVERITY_LEVELS,
    ),
    "recommended_action": Choice(
        instructions=(
            "Given `content` and the poster's record in `author_history`, what enforcement "
            "action does the platform's Community Content Policy call for? Severity is "
            "assessed on this scale:\n"
            + _bullets(SEVERITY_LEVELS)
            + "\nSomeone with a record of prior warnings or suspensions should generally "
            "receive a more severe action than a first-time poster with the same content, "
            "and Critical-severity content warrants strong action regardless of history."
            + _CONTEXT_NOTE
        ),
        criteria=ACTIONS,
    ),
}
