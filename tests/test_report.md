# Test Report

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

Result:

- 8 passed
- 0 failed
- 2 deprecation warnings only

## Conclusion

The current MVP satisfies the core PS validation conditions for BIS-related product recommendation, certification, testing, consumer questions, hallmarking, lab guidance, and hallucination-safe behavior.
