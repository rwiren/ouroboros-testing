# Contributing

Thanks for your interest in improving **Ouroboros Testing**.

## Workflow

1. Fork the repository and create a feature branch from `main`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make focused changes with clear commit messages.
4. Run tests locally:
   ```bash
   python -m pytest -q
   ```
5. Open a pull request with:
   - a clear summary of what changed,
   - why the change is needed,
   - any validation results (tests, plots, or analysis output).

## Coding and quality expectations

- Keep experiments reproducible (`--seed` support where randomness is used).
- Preserve compatibility with existing CLI entry points unless intentionally changed.
- Add or update tests for behavioral changes.
- Update docs (`README.md`, `docs/methods.md`, and `CHANGELOG.md`) when relevant.

## Reporting issues

When filing a bug, include:

- command used,
- expected behavior,
- actual behavior,
- error output/traceback,
- Python version and OS.
