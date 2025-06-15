Coding guidelines for Buddy Bot repository:

- Use `pytest` for all tests. Run `pytest --cov=apps --cov-report=term-missing --cov-report=html` before creating a PR.
- Test functions should include identifiers from `docs/Тесты.md` (e.g. `AUTH_01`, `E2E_03`).
- HTML reports are stored in `reports/` and coverage in `htmlcov/`.
