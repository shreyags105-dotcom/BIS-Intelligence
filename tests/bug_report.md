# Bug Report

## Overview

This file records the key issues, validation findings, and known limitations of the BIS Intelligence MVP.

## Bug ID: BIS-001

### Title

Unsupported queries sometimes return a generic BIS fallback instead of a domain-specific explanation.

### Severity

Medium

### Status

Resolved

### Description

When a user asks a non-BIS question, the assistant should clearly state that it only supports BIS-related topics. The fallback response should not sound like a fabricated BIS answer.

### Steps to reproduce

1. Send a non-BIS query such as:
   - "Who will win the cricket match today?"
2. Submit the request to /chat.
3. Observe the response.

### Expected result

The assistant should respond with a clear message such as:

- "I can assist with Indian Standards and BIS-related services. I do not have verified BIS information for this query."

### Actual result

Earlier versions responded with a generic fallback that could be interpreted as a BIS answer.

### Fix applied

The AI response logic was updated to clearly reject unsupported queries and avoid pretending to have BIS information outside the domain.

### Verification

Validated through the automated test:

- test_unsupported_query_is_safe

---

## Bug ID: BIS-002

### Title

Hallucination risk for invalid or fake standards.

### Severity

High

### Status

Resolved

### Description

An invalid standard such as "IS 99999 for teleportation machines" must not be treated as a real BIS standard.

### Steps to reproduce

1. Send a request such as:
   - "What is BIS standard IS 99999 for teleportation machines?"
2. Submit to /chat.
3. Observe the response.

### Expected result

The assistant must refuse to invent information and must return a safe fallback.

### Actual result

A hallucination risk existed in an unguarded version of the logic.

### Fix applied

The system now returns N/A and a clear verification message when the standard is not in the BIS knowledge base.

### Verification

Validated through the automated test:

- test_hallucination_guard_hard_mode

---

## Bug ID: BIS-003

### Title

Knowledge coverage is limited to a set of supported products and service queries.

### Severity

Medium

### Status

Known limitation

### Description

The current MVP can answer representative BIS and service questions, but it is not a complete BIS knowledge base for all products and all services.

### Impact

This limits broad product coverage beyond the current supported dataset.

### Current status

The system clearly indicates when information is unavailable instead of inventing it.

---

## Bug ID: BIS-004

### Title

FastAPI/Starlette dependency warning from test client environment.

### Severity

Low

### Status

Observed / non-blocking

### Description

The test suite emits deprecation warnings because of the current Starlette-FastAPI dependency combination.

### Impact

Warnings do not affect test success, but they indicate a future maintenance item.

### Current status

No functional breakage observed.

---

## Bug ID: BIS-005

### Title

Frontend standards search called a missing backend route.

### Severity

High

### Status

Resolved

### Description

The frontend requested `GET /standards`, but the backend did not expose the route. Standard and service navigation could therefore fail even when the frontend was running.

### Fix applied

Added `GET /standards`, `GET /standard/{standard_id}`, and service endpoints for certification, hallmarking, and laboratories. Versioned standards such as `IS 2347:2023` now also match the user-friendly `IS 2347` form.

### Verification

Validated through `test_p0_pressure_cooker_api_journey` and `test_standard_lookup_endpoint`.

---

## Bug ID: BIS-006

### Title

Document analysis was simulated in the browser and excluded Excel files.

### Severity

High

### Status

Resolved

### Description

The document page used a fixed timer instead of uploading a file to the backend, and its file picker accepted only PDF and Word formats.

### Fix applied

Added `POST /documents/analyze` with PDF, Excel, and Word validation. The frontend now sends the selected file and renders the returned standard, issue count, and analysis result.

### Verification

Validated for `.pdf`, `.xlsx`, and `.docx` by `test_p1_document_upload_and_analysis`.

---

## Bug ID: BIS-007

### Title

Legacy PS tests depended on retired response fields and an unavailable optional RAG module.

### Severity

Medium

### Status

Resolved

### Description

The legacy tests imported `ai.rag`, which required unavailable `faiss`, and asserted response fields no longer returned by the active FastAPI contract.

### Fix applied

Updated the validation suite to use the active knowledge-base contract and added compatibility aliases for older API clients.

### Verification

The combined PS and QA suites now pass with 21 tests.

---

## Summary

The critical functional issues affecting reliability are resolved:

- unsupported queries are handled safely
- fake standards are blocked
- product recommendation and BIS guidance are validated
- standards and service navigation endpoints are available
- PDF, Excel, and Word document analysis is validated
- legacy and acceptance tests pass together

The system is considered ready for the current MVP demo and PS validation. Remaining limitations are deep OCR/clause extraction, browser automation, and non-blocking dependency warnings.
