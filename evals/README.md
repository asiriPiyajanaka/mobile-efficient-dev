# Agent eval scenarios

These are behavior-level evals for testing the skill with a real coding agent. Unit tests under `tests/` validate helper scripts; these scenarios validate **agent behavior**.

For each captured run, score four dimensions:

1. **Outcome** — task completed correctly.
2. **Rule adherence** — repository/user requirements were not weakened.
3. **Efficiency** — no unnecessary broad reads, repeated checks, builds, cache resets, or log dumps.
4. **Verification fit** — selected level matched the actual failure mode and escalated only when evidence required it.

A public release should avoid regressions on the must-pass cases in `cases.json`.
