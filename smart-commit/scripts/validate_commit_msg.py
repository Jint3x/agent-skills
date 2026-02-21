"""
Smart Commit - Commit Message Validator
Validates a commit message against the Conventional Commits v1.0.0 spec.

Usage:
    python validate_commit_msg.py "<full commit message>"

Exit codes:
    0 = valid message
    1 = validation errors found
"""

import sys
import re

VALID_TYPES = [
    "feat", "fix", "test", "refactor", "docs",
    "style", "perf", "build", "ci", "chore", "revert"
]

# Common non-imperative verb forms to catch
NON_IMPERATIVE_PATTERNS = [
    r"^(added|adds|adding)\b",
    r"^(fixed|fixes|fixing)\b",
    r"^(removed|removes|removing)\b",
    r"^(updated|updates|updating)\b",
    r"^(changed|changes|changing)\b",
    r"^(created|creates|creating)\b",
    r"^(deleted|deletes|deleting)\b",
    r"^(moved|moves|moving)\b",
    r"^(renamed|renames|renaming)\b",
    r"^(implemented|implements|implementing)\b",
    r"^(resolved|resolves|resolving)\b",
    r"^(improved|improves|improving)\b",
    r"^(replaced|replaces|replacing)\b",
    r"^(corrected|corrects|correcting)\b",
    r"^(enabled|enables|enabling)\b",
    r"^(disabled|disables|disabling)\b",
]

# Regex for the subject line:  type[!]: description
SUBJECT_REGEX = re.compile(
    r"^(?P<type>[a-z]+)"          # type (lowercase)
    r"(?:\((?P<scope>[^)]+)\))?"  # optional (scope)
    r"(?P<breaking>!)?"           # optional ! for breaking
    r":\s+"                       # colon + space
    r"(?P<description>.+)$"       # description
)

FOOTER_REGEX = re.compile(
    r"^(?:BREAKING CHANGE|[\w-]+)(?::\s|\ #).+$"
)


def validate(message: str) -> list[str]:
    """Validate a commit message. Returns a list of error strings (empty = valid)."""
    errors = []

    if not message or not message.strip():
        return ["Commit message is empty."]

    lines = message.split("\n")
    subject = lines[0]

    # ── Subject Line Checks ──────────────────────────────────────────────

    # 1. Parse structure
    match = SUBJECT_REGEX.match(subject)
    if not match:
        errors.append(
            f"Subject does not match format '<type>: <description>'.\n"
            f"  Got: \"{subject}\""
        )
        return errors  # Can't check further if structure is wrong

    msg_type = match.group("type")
    description = match.group("description")

    # 2. Valid type
    if msg_type not in VALID_TYPES:
        errors.append(
            f"Invalid type '{msg_type}'. "
            f"Valid types: {', '.join(VALID_TYPES)}"
        )

    # 3. Subject length (full line ≤ 50 chars)
    if len(subject) > 50:
        errors.append(
            f"Subject is {len(subject)} chars (max 50).\n"
            f"  \"{subject}\""
        )

    # 4. No trailing period
    if description.endswith("."):
        errors.append("Subject must NOT end with a period.")

    # 5. First letter capitalized
    if description[0].islower():
        errors.append(
            f"Description should start with a capital letter.\n"
            f"  Got: \"{description}\"\n"
            f"  Expected: \"{description[0].upper() + description[1:]}\""
        )

    # 6. Imperative mood check
    desc_lower = description.lower()
    for pattern in NON_IMPERATIVE_PATTERNS:
        if re.match(pattern, desc_lower):
            verb = re.match(pattern, desc_lower).group(1)
            errors.append(
                f"Use imperative mood in subject. "
                f"Found '{verb}' — use the base form instead.\n"
                f"  Example: 'Add' not 'Added', 'Fix' not 'Fixed'"
            )
            break

    # ── Blank Line Check ─────────────────────────────────────────────────

    if len(lines) > 1:
        if lines[1].strip() != "":
            errors.append(
                "Missing blank line between subject and body.\n"
                "  Line 2 must be empty."
            )

    # ── Body Checks ──────────────────────────────────────────────────────

    # Find where body starts and footer starts
    body_lines = []
    footer_lines = []
    in_footer = False

    for i, line in enumerate(lines[2:], start=3):  # Skip subject + blank line
        # Detect footer start: a line matching footer format after a blank line
        if not in_footer and FOOTER_REGEX.match(line):
            # Check if preceded by a blank line (or is the first content after blank)
            prev_idx = i - 2  # 0-indexed in lines array
            if prev_idx > 0 and lines[prev_idx - 1].strip() == "":
                in_footer = True

        if in_footer:
            footer_lines.append((i, line))
        else:
            body_lines.append((i, line))

    # Check body line length (72 char wrap)
    for line_num, line in body_lines:
        if len(line) > 72 and line.strip():  # Skip blank lines
            errors.append(
                f"Body line {line_num} is {len(line)} chars (max 72).\n"
                f"  \"{line}\""
            )

    # ── Revert-specific Check ────────────────────────────────────────────

    if msg_type == "revert":
        full_body = "\n".join(line for _, line in body_lines)
        if "revert" not in full_body.lower() and not any(
            re.search(r"[0-9a-f]{7,40}", line) for _, line in body_lines
        ):
            errors.append(
                "Revert commits should include the reverted commit hash in the body."
            )

    # ── Breaking Change Consistency ──────────────────────────────────────

    has_bang = match.group("breaking") == "!"
    has_footer = any(
        line.startswith("BREAKING CHANGE:") or line.startswith("BREAKING-CHANGE:")
        for _, line in footer_lines
    )

    if has_bang and not has_footer:
        # Warning, not error — both methods are valid independently
        pass

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_commit_msg.py \"<commit message>\"")
        print("\nYou can also pipe a message:")
        print("  echo \"feat: add feature\" | python validate_commit_msg.py -")
        sys.exit(1)

    if sys.argv[1] == "-":
        message = sys.stdin.read().strip()
    else:
        message = sys.argv[1]

    errors = validate(message)

    if not errors:
        print("✅ Commit message is valid.")
        sys.exit(0)
    else:
        print(f"❌ Found {len(errors)} issue(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
