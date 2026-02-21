---
name: smart-commit
description: Use once a full unit of work is completed, create a well-structured Git commit. Analyze all changes (staged and unstaged), auto-stages them, classifies the work type, and generates a clear, standards-compliant commit message.
---

# Smart Commit

An AI agent skill for creating Git commits.

---

## When to Use This Skill

Invoke this skill after completing a unit of work such as:
- Implementing a new feature
- Fixing a bug
- Writing or updating tests
- Refactoring code
- Updating documentation
- Any other meaningful code change

---

## Commit Message Format

Every commit message follows this structure:

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

### Rules

1. **Subject line** (first line):
   - Must start with a valid `<type>`
   - Use **imperative mood** ("add", "fix", "remove" — NOT "added", "fixed", "removed")
   - Keep to **50 characters or fewer**
   - Do NOT end with a period
   - Capitalize the first letter of the description

2. **Blank line** separates subject from body (when body is present)

3. **Body** (optional):
   - Wrap lines at **72 characters**
   - Explain **what** and **why**, not how (the code shows how)
   - Can be multiple paragraphs

4. **Footer(s)** (optional):
   - Use `token: value` or `token #value` format
   - `BREAKING CHANGE:` must be uppercase and followed by description
   - Issue references: `Closes #123`, `Fixes #456`, `Refs #789`

---

## Commit Types

### `feat` - [Feature] Introduces new functionality or capability for the user.
### `fix` - [Bug Fix] Corrects a defect in existing functionality.
### `test` - [Tests] Adds, modifies, or fixes tests. No production code changes.
### `refactor` - [Refactoring] Restructures code without changing external behavior.
### `docs` - [Documentation] Changes only documentation (README, comments, docstrings, guides).
### `style` - [Code Style] Formatting changes that do not affect logic (whitespace, linting fixes).
### `perf` - [Performance] Improves performance without changing functionality.
### `build` - [Build System] Changes to build tools, dependencies, or project configuration.
### `ci` - [CI/CD] Changes to continuous integration/deployment configuration and scripts.
### `chore` - [Maintenance] Routine tasks that don't modify source or test files.
### `revert` - [Revert] Undoes a previous commit. The body MUST include the reverted commit hash.

### Examples

**1. Simple commit (subject only):**
```
feat: add dark mode toggle to settings page
```

**2. Commit with body and issue reference:**
```
fix: resolve crash when input list is empty

The calculate_average function threw a ZeroDivisionError when
called with an empty list. Added a guard clause to return 0.

Fixes #87
```

**3. Breaking change with body and footer:**
```
feat!: remove deprecated authentication endpoints

The /api/v1/auth/* endpoints have been removed. All clients
must migrate to /api/v2/auth/* which uses OAuth 2.0.

BREAKING CHANGE: Removed /api/v1/auth/login, /api/v1/auth/logout,
and /api/v1/auth/refresh endpoints.
```

---

## Breaking Changes

A breaking change is any commit that introduces an incompatible change to the public API or expected behavior. There are **two ways** to signal a breaking change:

Method 1: `!` after the type (for the subject line)
Method 2: `BREAKING CHANGE` footer (always valid)
Both methods can be combined

## Edge Cases & Special Situations

### Multiple types of changes in one commit
If your changes span multiple types, choose the **most significant** type. If the changes are truly unrelated, consider splitting into multiple commits.

Priority order when choosing type:
1. `feat` or `fix` (user-facing changes take precedence)
2. `refactor` or `perf`
3. `test`, `docs`, `style`, `build`, `ci`, `chore`

### Commit with issue/ticket references

```
fix: prevent duplicate form submissions

Added debounce logic to the submit button and server-side
idempotency check using request IDs.

Fixes #234
Refs #200
```

### Commit with co-authors

```
feat: implement real-time notifications

Co-authored-by: Alice Smith <alice@example.com>
Co-authored-by: Bob Jones <bob@example.com>
```

### Merge commits
Do not modify merge commit messages. Let Git generate them using its default format.

### Initial commit

```
chore: initialize project structure

Set up directory layout, package configuration, and basic
development tooling (linter, formatter, test runner).
```

### Very small or trivial changes
Even trivial changes get a proper type and description:

```
style: remove trailing whitespace
```

```
chore: bump version to 1.2.3
```

### Changes that include both a fix and a test for the fix

```
fix: handle null response from external API

Added null check before processing the API response. Previously,
a null response caused an unhandled TypeError.

Includes regression test to prevent recurrence.
Fixes #312
```

---

## Agent Workflow

When this skill is invoked, follow these steps **in order**:

### Step 1: Stage All Changes

Auto-stage everything (tracked changes AND new untracked files):

```bash
git add -A
```

### Step 2: Analyze Changes

Run both commands to capture the full picture:

```bash
git diff --staged
```

If the output is empty, inform the user there are no changes to commit and stop.

### Step 3: Classify the Change

Based on the diff, determine:
- **Type**: Which of the commit types best describes the primary change?
- **Is it a breaking change?**: Does it change public APIs, expected behavior, or data formats?
- **Does it need a body?**: Is the change non-trivial and would benefit from explanation?
- **Are there related issues?**: Look for TODO/FIXME comments referencing issues.

### Step 4: Compose the Commit Message

Construct the message following all rules in this document.

### Step 5: Execute the Commit

```bash
git commit -m "<subject>" -m "<body>" -m "<footer>"
```

Or for subject-only commits:

```bash
git commit -m "<subject>"
```

### Step 6: Confirm

Display:
- The commit hash (abbreviated)
- The full commit message
- Summary of files changed (count of files, insertions, deletions)