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

### Status

No functional breakage observed.

---

## Summary

The critical functional issues affecting reliability are resolved:

- unsupported queries are handled safely
- fake standards are blocked
- product recommendation and BIS guidance are validated

The system is considered ready for the current MVP demo and PS validation.
