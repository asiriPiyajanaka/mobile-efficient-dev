# Example repo guidance for mobile-efficient-dev

For Flutter and React Native implementation tasks, use the `mobile-efficient-dev` skill when available.

Project-specific requirements remain authoritative. In particular:

- reuse design-system components before creating new UI primitives;
- follow the nearest feature/module architecture;
- do not skip checks required by CI or acceptance criteria;
- load detailed engineering rules only when their paths/concerns are relevant;
- when the working tree has unrelated changes, scope skill helpers to files touched by the current task.

If `.mobile-agent-rules.json` exists, route/check relevant deterministic rules after a coherent edit batch.
