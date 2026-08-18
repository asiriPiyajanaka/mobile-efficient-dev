# Contributing

Thanks for helping make `mobile-development-skills` more trustworthy.

## Project principles

- Preserve correctness over token savings.
- Keep repository policy separate from this skill's workflow guidance.
- Prefer deterministic, scoped checks over broad model-visible output.
- Avoid adding dependencies unless they materially improve reliability.
- Keep examples honest; do not claim measured savings without benchmark data.

## Development setup

This repository has no third-party Python dependency requirement.

```bash
python3 -m unittest discover -s tests -v
```

## Pull requests

Good pull requests usually include:

- a focused explanation of the workflow or helper behavior being changed;
- tests for script changes;
- README/reference updates when user-facing behavior changes;
- no generated caches, local logs, or target app artifacts.

For classifier changes, add or update tests in `tests/test_plan.py`. For deterministic rule behavior, use `tests/test_rule_guard.py`. For command-output handling, use `tests/test_run_quiet.py`.

## Documentation style

- Be concrete and conservative.
- Prefer examples that show what should be skipped as well as what should run.
- Avoid broad claims such as guaranteed percentage savings.
- Keep the opening README sections short enough that users quickly see what the skill does.
