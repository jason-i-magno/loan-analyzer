# loan-analyzer

Mortgage analyzer with payment breakdowns, amortization schedules, extra-payment modelling, and interest analysis.

- `backend/` — FastAPI service (`POST /analyze`) and the `loan_utils` calculation package
- `frontend/` — static HTML/JS UI styled with Tailwind and charted with Plotly, served by nginx

## Running locally

Compose mounts the frontend sources into nginx, so build the Tailwind CSS first (or keep `npm run watch` running while you work):

```sh
cd frontend && npm ci && npm run build && cd ..
docker compose up --build
```

The UI is at http://localhost:8050 and the API at http://localhost:8001.

## Tests

```sh
cd backend
pip install -e '.[test]'
pytest
```
