# BIS Intelligence Demo Script

## Setup

1. Start the backend: `cd backend; python -m uvicorn main:app --reload`.
2. Start the frontend: `cd frontend; npm install; npm run dev`.
3. Open the frontend URL and confirm the BIS Intelligence home screen loads.

## P0 walkthrough

1. Open Login if available, then Dashboard.
2. Ask: `I want to manufacture a pressure cooker.`
3. Confirm the answer identifies the pressure-cooker standard, requirements, testing, certification, next action, and source.
4. Open the standard details for `IS 2347`.
5. Open Requirements, Testing, Documents, Certification, Roadmap, Progress, Next Action, and Source panels where available.
6. Ask: `What is XYZ-999?` and confirm no standard is invented.
7. Ask: `Who will win today's cricket match?` and confirm the response stays within the BIS domain.

## P1 document walkthrough

1. Open Document Analysis.
2. Try one PDF, one Excel file, and one Word file.
3. Record whether upload works, analysis completes, issues are identified, and results are understandable.
4. Confirm the backend returns the filename, detected type, matched standard, issue count, and readable analysis result for each file.

## Evidence to capture

- Screenshot of the verified pressure-cooker answer and source.
- Screenshot of the unknown-standard safe response.
- Screenshot of the unsupported-topic response.
- Test output from `python -m pytest tests/test_qa_acceptance.py -q -rA`.
- Test output from `python -m pytest tests/test_bis_ps_validation.py -q -rA`.
