# BIS Intelligence QA Plan

Owner: Ujjwal  
Priority: P0 tests run during development; P1 document and documentation checks are tracked alongside them.

## P0 AI acceptance tests

| ID    | Prompt                                   | Expected result                                               | Automated check                                      |
| ----- | ---------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| AI-01 | What is IS 2347?                         | Verified pressure-cooker standard guidance                    | `test_p0_bis_questions_return_verified_guidance`     |
| AI-02 | I want to manufacture a pressure cooker. | Standard, requirements, testing and next action               | `test_p0_bis_questions_return_verified_guidance`     |
| AI-03 | What tests are required?                 | Testing guidance for the covered product                      | `test_p0_bis_questions_return_verified_guidance`     |
| AI-04 | How do I get BIS certification?          | BIS certification guidance                                    | `test_p0_bis_questions_return_verified_guidance`     |
| AI-05 | What should I do after testing?          | Follow-up action involving documents/certification            | `test_p0_bis_questions_return_verified_guidance`     |
| AI-06 | What is XYZ-999?                         | Verified information could not be found; no invented standard | `test_p0_unknown_standard_is_not_invented`           |
| AI-07 | Who will win today's cricket match?      | BIS-domain limitation response                                | `test_p0_non_bis_question_returns_domain_limitation` |

## P0 end-to-end journey

The backend portion is covered by `test_p0_pressure_cooker_api_journey`:

```text
Login -> Dashboard -> Pressure Cooker -> IS 2347 -> Requirements -> Testing
-> Documents -> Certification -> Roadmap -> Progress -> Next Action -> Source
```

The API journey is automated. Browser navigation remains a manual smoke test because Playwright is not configured in this repository.

## P1 document tests

| File type | Upload works                           | Analysis works | Issues identified | Results understandable    | Current status |
| --------- | -------------------------------------- | -------------- | ----------------- | ------------------------- | -------------- |
| PDF       | Yes, multipart API and frontend picker | Yes            | Returned as list  | Returned as readable text | Passed         |
| Excel     | Yes, `.xls`/`.xlsx` supported          | Yes            | Returned as list  | Returned as readable text | Passed         |
| Word      | Yes, `.doc`/`.docx` supported          | Yes            | Returned as list  | Returned as readable text | Passed         |

The endpoint validates the extension and non-empty content and returns a structured analysis result. Deep OCR and clause-level extraction remain future enhancements.

## Run commands

```powershell
python -m pytest tests/test_qa_acceptance.py -q -rA
python -m pytest tests/test_bis_ps_validation.py -q -rA
```

Both commands pass in the configured environment.
