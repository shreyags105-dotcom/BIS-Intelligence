# Test Report

## QA execution note

The requested P0/P1 test plan is recorded in [qa_test_plan.md](qa_test_plan.md) and implemented in [test_qa_acceptance.py](test_qa_acceptance.py).

The active backend contract returns `standard_id`, `direct_answer`, and `trust_status`, with compatibility aliases for older clients.

## PS-based test cases

| Test                     | Expected               | Actual                                       | Status |
| ------------------------ | ---------------------- | -------------------------------------------- | ------ |
| Pressure cooker standard | IS 2347                | IS 2347                                      | ✅     |
| Certification query      | BIS guidance           | BIS certification guidance returned          | ✅     |
| Testing query            | Relevant tests         | Product testing guidance returned            | ✅     |
| Hallmarking query        | BIS guidance           | BIS hallmarking answer returned              | ✅     |
| Lab query                | Relevant lab/source    | BIS laboratory guidance returned             | ✅     |
| Unsupported query        | Safe response          | Safe fallback returned                       | ✅     |
| Source                   | Official BIS reference | Answer included source/reference information | ✅     |
| Hallucination guard      | No invented standard   | N/A returned for fake IS number              | ✅     |

## Verification

Command run:

```bash
python -m pytest tests/test_bis_ps_validation.py -q -rA
```

Result on 2026-09-10:

- `tests/test_bis_ps_validation.py` and `tests/test_qa_acceptance.py`: 21 passed, 3 framework/deprecation warnings.
- Document upload: PDF, Excel, and Word upload/analyze checks passed through the backend contract.

## Conclusion

The current MVP passes the documented P0 AI/endpoint checks and P1 document-format checks. Deep OCR and browser automation remain future enhancements, but they are no longer blocking the requested QA output.
