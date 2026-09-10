# BIS Intelligence API Documentation

Base URL: `http://127.0.0.1:8000`

## Authentication

### `POST /auth/signup`

Request: `{ "full_name": "Ujjwal", "email": "user@example.com", "password": "...", "role": "consumer" }`

Returns `201` with a new `user_id`.

### `POST /auth/login`

Request: `{ "email": "user@example.com", "password": "..." }`

Returns `200` with `access_token`, `token_type`, `user_id`, and `full_name`.

## BIS guidance

### `POST /chat`

Request: `{ "question": "I want to manufacture a pressure cooker.", "mode": "industry" }`

Verified responses include `intent`, `product`, `standard_id`, `direct_answer`, `requirements`, `testing`, `certification`, `official_source`, `next_action`, and `trust_status`.

Unknown queries return `intent: "UNSUPPORTED"` and must not invent a standard.

### `GET /standard/{standard_id}`

Returns the matching knowledge-base record, or an unsupported record when no verified standard is found.

### `GET /standards`

Returns `{ "standards": [...] }` for the frontend standards index.

### `POST /compliance-plan`

Request: `{ "product_name": "Pressure Cooker", "standard_id": "IS 2347" }`

Returns checklist items, progress, and `next_recommended_action`.

### `GET /certification`, `GET /hallmarking`, `GET /labs`

Returns service guidance payloads.

### `POST /documents/analyze`

Multipart field: `file`. Supported types are PDF, Excel (`.xls`, `.xlsx`), and Word (`.doc`, `.docx`). Returns the filename, detected type, matched standard, issues, and readable analysis results.
