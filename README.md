# BIS Intelligence

BIS Intelligence is an AI-powered assistant for Indian Standards and BIS-related services.

## Project overview

This project helps users:

- ask BIS-related questions in natural language
- identify applicable standards for products
- understand certification and testing requirements
- access BIS guidance for hallmarking and laboratories
- receive source-backed answers instead of unsupported guesses

## Tech stack

- Frontend: Next.js
- Backend: FastAPI
- AI layer: BIS-grounded retrieval / mock AI module
- Data source: BIS knowledge base in the data folder

## Core features

- Product-to-standard recommendation
- Industry and consumer modes
- Certification guidance
- Testing information
- Hallmarking guidance
- Laboratory guidance
- Safe fallback for unsupported topics
- Source/reference links

## Quick start

### Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Demo scenario

> “I want to manufacture a pressure cooker. What BIS standard applies, what are the requirements and tests, and how do I get certification?”

## Validation

The project includes a BIS PS validation suite in:

- [tests/test_bis_ps_validation.py](tests/test_bis_ps_validation.py)

Run it with:

```bash
python -m pytest tests/test_bis_ps_validation.py -q -rA
```

## Documentation

- [docs/architecture-diagram.md](docs/architecture-diagram.md)
- [docs/user-flow.md](docs/user-flow.md)
- [docs/use-case-diagram.md](docs/use-case-diagram.md)
- [docs/test-report.md](docs/test-report.md)
- [docs/ps-requirement-checklist.md](docs/ps-requirement-checklist.md)

## MVP status

The current MVP is validated for the main BIS problem statement requirements and covers the standard recommendation, certification, testing, consumer guidance, hallmarking, lab guidance, and safe unsupported-query behavior.
