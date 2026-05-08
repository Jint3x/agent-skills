---
name: unit-testing
description: Design, add, repair, and review unit tests for application code. Use when you need to create focused tests for functions, classes, modules, domain logic, service orchestration, error paths, regressions, edge cases, or refactors.
---

## Purpose

Create unit tests that give confidence in local behavior. Prefer tests that are easy to understand, hard to break accidentally, and useful when they fail.

Use the repository's existing test framework, naming conventions, fixtures, helpers, and command patterns. Do not introduce a new framework, assertion library, mocking library, or test architecture unless the existing project lacks one or the user asks for it.

High-quality unit tests are behavioral, deterministic, isolated, local, readable, fast, and diagnostic. A failing test should point to a specific broken expectation, not merely announce that something somewhere changed.

## Language References

Load language references only when they match the codebase under test.

- When testing Python code, always read `references/python-unit-testing.md` before writing or changing tests.
- When the Python project uses pytest, also read `references/python-pytest.md`. Treat that file as the pytest 9.x guidance layer.

## Workflow

1. Inspect the behavior under test before editing tests.
2. Find nearby tests and mirror their style, file layout, naming, fixtures, and assertion patterns.
3. Identify the unit boundary: the smallest meaningful behavior that can be tested without real external systems.
4. Choose high-value cases before chasing coverage numbers.
5. Write tests that arrange only necessary state, execute one behavior, and assert observable results.
6. For bug fixes, make the regression test fail for the right reason before or during the fix when practical.
7. Run the narrowest relevant test command first, then broaden if the change touches shared behavior.
8. If a failure exposes a product bug, report it clearly instead of weakening the test to pass.

## What Counts As Unit Testing

Treat a test as a unit test when it verifies local code behavior without depending on real external infrastructure.

Good unit-test subjects:

- Pure functions and deterministic transformations.
- Class or module behavior.
- Domain rules, validators, parsers, formatters, mappers, reducers, and calculators.
- Service or use-case orchestration with dependencies replaced by fakes, stubs, spies, or mocks.
- Error handling, fallback logic, retries, and boundary conditions.
- Regression cases for specific bugs.

Usually not unit tests:

- Tests using a real database, broker, network service, browser, filesystem-heavy workflow, container, cloud API, or full application server.
- Tests whose main purpose is framework wiring, routing, migrations, serialization across process boundaries, or end-to-end user flow.
- Tests that rely on timing, real randomness, live credentials, current dates, local machine state, or test order.

Lightweight temporary filesystem use can still be unit-level when the file behavior is the unit's contract and the test uses isolated temp paths with reliable cleanup. Do not use broad project directories, user files, or machine-specific paths.

If a requested case crosses the unit boundary, either isolate the dependency with a test double or explain that the behavior is better covered by an integration test.

## Test Case Selection

Prioritize behavior and risk over implementation details.

Cover:

- The normal path users or callers rely on.
- Important branches and decision points.
- Boundary values: empty, missing, null, min, max, malformed, duplicate, large, and unusual input.
- Error paths and expected failure modes.
- Previously broken behavior.
- Invariants that must remain true across refactors.

Avoid:

- One test per line of code.
- Tests that only prove the implementation was written exactly as it currently is.
- Broad snapshots or golden files when focused assertions would be clearer.
- Exhaustive permutations with little additional risk coverage.
- Tests that only increase coverage metrics without increasing confidence.

Use coverage reports as a gap-finding tool, not as proof of quality. If coverage is required by the project, satisfy it with meaningful behavioral tests rather than superficial execution tests.

## Test Shape

Prefer a clear Arrange, Act, Assert structure, whether written explicitly or implied by local style.

Each test should:

- Have a name that describes the behavior and condition.
- Set up the smallest meaningful state.
- Exercise one behavior or scenario.
- Assert specific observable outcomes.
- Fail with a message or assertion diff that helps locate the problem.
- Be deterministic and independent of test order.

Split tests when one test has multiple unrelated reasons to fail. Keep related assertions together when they describe one behavior and splitting would make the test harder to read.

Use parameterized or table-driven tests when the same behavior must be checked across multiple compact examples. Do not parameterize cases that need substantially different setup or assertions; separate named tests are clearer.

Use property-based tests only when there is a clear invariant, input generator, and shrinkable failure signal. Do not use generated inputs as a substitute for understanding the expected behavior.

## Assertions

Assert outcomes, not incidental implementation.

Prefer:

- Return values.
- Public state changes.
- Emitted domain events or messages.
- Raised errors and error details.
- Calls to a collaborator only when the interaction is itself the contract.
- Structured outputs over raw string matching when structure is the contract.

Avoid:

- Asserting private methods, private fields, call order, or intermediate variables unless they are the public contract in that codebase.
- Reproducing the implementation algorithm inside the test.
- Assertions so broad that failures do not identify the broken behavior.
- Assertions so weak that the test would pass if the feature were removed.

## Test Doubles

Use the lightest double that preserves confidence.

- Use real local objects when they are simple, deterministic, and cheap.
- Use fakes for meaningful in-memory substitutes.
- Use stubs for fixed dependency responses.
- Use spies or mocks when verifying an interaction is part of the required behavior.
- Use mocks to isolate slow, flaky, nondeterministic, or external dependencies.

Do not over-mock. If a test mocks every collaborator and only checks that methods call other methods, it probably tests implementation rather than behavior.

## Isolation And Determinism

Control unstable inputs.

- Freeze or inject time.
- Seed or inject randomness.
- Replace network, database, filesystem, subprocess, and environment dependencies unless local project conventions intentionally allow lightweight local use.
- Clean up modified global state, environment variables, registries, monkeypatches, and singletons.
- Avoid sleeps and real waiting; use fake clocks, explicit synchronization, or direct state transitions.
- Ensure tests can run alone, in any order, repeatedly, and in parallel when the project supports parallel execution.

## Maintainability

Keep tests simple enough to act as executable examples.

Do:

- Use shared helpers only when they remove real duplication without hiding the scenario.
- Prefer readable literals and small fixtures.
- Keep fixture data close to the test when it is scenario-specific.
- Name constants and builders around domain meaning, not test mechanics.
- Update tests when behavior intentionally changes.
- Prefer builders or factories when many tests need valid domain objects and inline setup would distract from the behavior.

Do not:

- Hide essential setup behind opaque helpers.
- Add large fixture files for small scenarios.
- Make tests depend on exact formatting when structure is what matters.
- Use brittle snapshots as the default assertion strategy.
- Delete or weaken failing tests without proving the expected behavior changed.

## Production Code Changes For Testability

Prefer tests that exercise existing public behavior without production changes. When code is too coupled to test responsibly, make the smallest behavior-preserving change that improves design as well as testability.

Good testability changes:

- Inject clocks, randomness, clients, repositories, or configuration instead of reading them globally.
- Extract pure logic from framework handlers, controllers, jobs, or adapters.
- Wrap external services behind narrow interfaces.
- Separate parsing, validation, mapping, and decision logic from side effects.

Avoid test-only production changes:

- Public methods, flags, branches, or constructors used only by tests.
- Weakened encapsulation that exposes internals without a production reason.
- Conditional behavior based on test environment names.
- Replacing useful design pressure with excessive mocking.

## Existing Code And Legacy Code

When adding tests to existing code, characterize current behavior before refactoring. If the code is hard to test, prefer small, behavior-preserving seams such as dependency injection, pure helper extraction, or adapter wrapping, but keep production changes minimal and justified by testability or correctness.

For bug fixes, prefer a regression test that fails before the fix and passes after it. If the bug cannot be reproduced in a true unit test, state the limitation and recommend the smallest integration test that would catch it.

## Agent Rules

Always:

- Read nearby tests before inventing style.
- Use the project's existing test commands and tooling.
- Keep edits scoped to the requested behavior.
- Preserve the production contract unless the user asked for behavior changes.
- Run relevant tests when possible and report what was run.
- Preserve unrelated user changes.
- Explain any untested residual risk.

Never:

- Add a new dependency just to write ordinary unit tests unless necessary.
- Convert a unit-test request into a broad integration or end-to-end suite without saying why.
- Mock the unit under test.
- Assert implementation details when a public behavior assertion is practical.
- Make network calls, use live credentials, or require external services in unit tests.
- Mark tests skipped, flaky, or xfail to hide unresolved failures.
- Change production behavior only to satisfy a poorly designed test.
- Chase coverage numbers at the expense of useful behavioral confidence.
- Leave tests dependent on wall-clock time, network availability, test order, or shared mutable state.

## Completion Standard

The task is complete when the added or repaired tests are focused, deterministic, aligned with local conventions, meaningful against the production contract, and verified with the narrowest practical test run. If tests cannot be run, report the exact blocker and the command that should be run later.
