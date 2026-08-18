# Security Policy

## Supported versions

`mobile-development-skills` is in public preview. Security fixes target the latest public-preview version.

## Reporting a vulnerability

Please report security concerns privately through the repository owner's preferred private contact channel. Do not open a public issue for sensitive disclosures.

Useful details include:

- affected file or helper script;
- command or configuration needed to reproduce;
- whether sensitive command output, logs, repository files, or environment values may be exposed;
- suggested mitigation, if known.

## Sensitive logs

`scripts/run_quiet.py` writes full command output to a temporary log while summarizing results. Passing logs are deleted by default. Failed logs remain in the OS temporary directory and may contain secrets printed by the underlying toolchain.

When working in sensitive environments, inspect failed logs carefully and remove them after use.
