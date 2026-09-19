"""
Jev questions for the Community Content Policy.

Criteria and definitions below are extracted directly from `policy.md`
(sections 2, 3, and 4) so that Jev's judgment is grounded in the same
language the policy uses, rather than in a paraphrase invented separately.
"""

from typesafe_sdk import Choice, Noul, Score

QUESTIONS = {
    "violates_policy": Noul(
        instructions=(
            "Does this content violate the platform's Community Content Policy? "
            "Consider the content in light of context and apparent intent: quoting "
            "or discussing harmful content to condemn or warn about it is not itself "
            "a violation, and ordinary disagreement, criticism, negative reviews, "
            "and untargeted profanity are not violations."
        ),
        criteria={
            "true": "The content falls into one of the policy's violation categories.",
            "false": "The content is acceptable under the policy (the 'No Violation' category).",
        },
    ),
    "violation_category": Choice(
        instructions=(
            "Which single category from the Community Content Policy best captures "
            "the most serious concern in this content? If multiple categories "
            "plausibly apply, choose the one representing the most serious concern."
        ),
        criteria={
            "harassment_bullying": (
                "Targets a specific person or group with insults, threats, degrading "
                "language, unwanted persistent contact, or attempts to intimidate, "
                "shame, or provoke fear in them."
            ),
            "hate_speech": (
                "Attacks, demeans, or dehumanizes people based on protected "
                "characteristics (race, ethnicity, religion, gender, sexual "
                "orientation, disability, national origin), including slurs, "
                "stereotypes framed as fact, or calls for exclusion/violence against a group."
            ),
            "spam_scams": (
                "Unsolicited repetitive advertising, irrelevant links, engagement bait, "
                "or deceptive content designed to defraud users (fake giveaways, "
                "phishing links, fraudulent payment requests, impersonating official "
                "accounts for financial gain)."
            ),
            "misinformation": (
                "False or misleading factual claims presented as true, where the "
                "falsehood is material (health, safety, or platform-mechanics claims), "
                "not opinion or clearly-framed satire."
            ),
            "self_harm_dangerous_content": (
                "Encourages, instructs, or glorifies self-harm, suicide, or dangerous "
                "activities likely to cause serious injury to the poster or others. "
                "Does not include someone seeking help or support for themselves."
            ),
            "adult_nsfw": (
                "Sexually explicit text or solicitation posted outside any designated "
                "adult section of the platform."
            ),
            "ip_violation": (
                "Reproduces copyrighted material without permission, or impersonates a "
                "brand/seller to sell counterfeit goods."
            ),
            "no_violation": (
                "Does not meaningfully fall into any violation category: ordinary "
                "disagreement, criticism, negative reviews, untargeted profanity, or "
                "dark humor without a genuine target."
            ),
        },
    ),
    "severity": Score(
        instructions=(
            "Assess the severity of this content under the Community Content Policy. "
            "Severity should reflect potential for harm, not just the category name — "
            "a low-severity example of a serious-sounding category is possible, just "
            "as a high-severity example of a mundane-sounding category is possible."
        ),
        criteria=[
            "None: no credible violation; content is acceptable as-is.",
            "Low: a minor or borderline issue that is ambiguous, low-reach, or clearly not malicious in intent.",
            "Medium: a clear, unambiguous violation of one category, contained to a single incident, without direct threats or large-scale harm.",
            "High: a clear violation involving explicit targeting of a person or group, direct threats, coordinated/large-scale scam or spam activity, or dangerous misinformation with real-world safety implications.",
            "Critical: credible threats of violence, explicit incitement, detailed self-harm instructions, sexual content involving minors, or large-scale fraud actively victimizing users.",
        ],
    ),
    "recommended_action": Choice(
        instructions=(
            "Given the content and the posting user's history, what enforcement action "
            "does the Community Content Policy call for? Someone with a record of prior "
            "warnings or suspensions should generally receive a more severe action than "
            "a first-time poster with the same content, and Critical-severity content "
            "warrants strong action regardless of history."
        ),
        criteria={
            "no_action": "Used when severity is None.",
            "warning": (
                "A private notice to the user; typically appropriate for Low severity on "
                "a first offense, or in some cases Medium severity with a clean history."
            ),
            "content_removal": (
                "The content is taken down but the account is otherwise unaffected; "
                "typically appropriate for Medium severity, or Low severity from a "
                "repeat offender."
            ),
            "temporary_suspension": (
                "The account is locked for a period of time; typically appropriate for "
                "High severity, or Medium severity from a user with multiple prior warnings."
            ),
            "permanent_ban": (
                "The account is permanently removed; typically appropriate for Critical "
                "severity, or High severity from a repeat offender who has already "
                "received a prior suspension."
            ),
        },
    ),
}
