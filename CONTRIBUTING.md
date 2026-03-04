# Contributing to EveBloom

Thank you for your interest in contributing. This guide covers the development workflow, code conventions, and how to run the test suite before submitting changes.

## Requirements

- Python 3.12+
- Node.js 20+
- PostgreSQL 14+

## Local Setup

```bash
# Clone the repository
git clone https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction.git
cd multi-stage-reproductive-health-risk-prediction

# Create and activate Python environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..

# Set up backend environment
cp backend/.env.example backend/.env
# Edit backend/.env and fill in POSTGRES_PASSWORD and DATABASE_URL

# Create database and run migrations
psql -U postgres -c "CREATE DATABASE reproductive_health;"
alembic -c backend/alembic.ini upgrade head
```

## Branching Convention

| Branch prefix | Purpose                                     |
| ------------- | ------------------------------------------- |
| `feature/`    | New features                                |
| `fix/`        | Bug fixes                                   |
| `refactor/`   | Code restructuring without behaviour change |
| `docs/`       | Documentation-only changes                  |
| `chore/`      | Dependency bumps, CI config, tooling        |

Branch from and target `main` for pull requests.

## Code Style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use type annotations for all function signatures.
- Format with `black` (line length 100).
- Lint with `flake8` or `ruff`.

### TypeScript / React

- Follow the existing ESLint configuration in `frontend/eslint.config.js`.
- Use functional components and React hooks.
- Keep component files small and single-responsibility.

## Running the Test Suite

```bash
# Set up a separate test database
psql -U postgres -c "CREATE DATABASE reproductive_health_test;"
export DATABASE_URL="postgresql+psycopg2://postgres:<password>@localhost:5432/reproductive_health_test"
alembic -c backend/alembic.ini upgrade head

# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run only unit tests (no PostgreSQL required)
pytest backend/tests/unit/

# Run only integration tests
pytest backend/tests/integration/
```

All tests must pass before opening a pull request.

## Pull Request Process

1. Fork the repository (external contributors) or branch from `main` (team members).
2. Make your changes in a well-named branch (e.g. `feature/postpartum-follow-up-chart`).
3. Write or update tests to cover your changes.
4. Run `pytest` and confirm all tests pass.
5. Ensure the backend and frontend start cleanly with `docker compose up --build`.
6. Open a pull request against `main` with:
   - A clear title and description of the change.
   - Reference to any related issue (e.g. `Closes #42`).
   - Screenshots or API response examples if the change affects user-facing behaviour.

## ML Model Changes

If you modify training pipelines or model artifacts:

- Run the full relevant pipeline script (`notebooks/run_*_pipeline.py`) and confirm the output metrics are consistent or improved.
- Include the updated evaluation report from `evaluation/` in your pull request.
- Do **not** commit raw DHS data files. See [data/README.md](data/README.md).

## Reporting Issues

Open a GitHub Issue and include:

- Steps to reproduce
- Expected vs actual behaviour
- Python/Node version and OS
- Relevant logs or error output

## Disclaimer

EveBloom is a research and educational ML system. Contributions must not introduce medical advice, diagnostic claims, or anything that could be misconstrued as a replacement for professional healthcare.
