# Testing

## Backend

```bash
cd backend
python -m unittest discover -v tests
```

Additional baseline config:

- `pytest.ini`
- `tests/conftest.py`

## Frontend

```bash
cd frontend
npm install
npm run typecheck
npm run test
```

## E2E smoke

```bash
cd frontend
npm run test:e2e
```

## CI

GitHub Actions runs:

- backend lint and tests
- frontend typecheck, tests, and build
- compose validation
