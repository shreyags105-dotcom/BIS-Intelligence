"""P0/P1 acceptance checks for the BIS Intelligence MVP.

These tests intentionally target the active FastAPI contract. They also act as
an executable record of the QA cases assigned to Ujjwal.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from main import app


client = TestClient(app)


@pytest.mark.parametrize(
    ("question", "expected_terms"),
    [
        ("What is IS 2347?", ("2347", "pressure cooker")),
        ("I want to manufacture a pressure cooker.", ("2347", "pressure")),
        ("What tests are required?", ("test",)),
        ("How do I get BIS certification?", ("certif", "bis")),
        ("What should I do after testing?", ("next", "certif", "document")),
    ],
)
def test_p0_bis_questions_return_verified_guidance(question, expected_terms):
    response = client.post("/chat", json={"question": question, "mode": "industry"})

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "MANUFACTURING_GUIDANCE"
    assert "verified" in body["trust_status"].lower()
    searchable = " ".join(
        [
            body.get("standard_id", ""),
            body.get("standard_title", ""),
            body.get("direct_answer", ""),
            body.get("next_action", ""),
            " ".join(body.get("testing", [])),
            " ".join(body.get("certification", {}).get("steps", [])),
        ]
    ).lower()
    assert all(term in searchable for term in expected_terms)


def test_p0_unknown_standard_is_not_invented():
    response = client.post("/chat", json={"question": "What is XYZ-999?", "mode": "industry"})

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "UNSUPPORTED"
    assert body["trust_status"] == "UNVERIFIED"
    assert "verified" in body["direct_answer"].lower()
    assert "could not be found" in body["direct_answer"].lower() or "no verified" in body["direct_answer"].lower()


def test_p0_non_bis_question_returns_domain_limitation():
    response = client.post("/chat", json={"question": "Who will win today's cricket match?", "mode": "consumer"})

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "UNSUPPORTED"
    assert "bis" in body["next_action"].lower()


def test_p0_pressure_cooker_api_journey():
    journey = [
        ("GET", "/standards", None),
        ("GET", "/standard/IS%202347", None),
        ("POST", "/chat", {"question": "What are the requirements and tests for a pressure cooker?", "mode": "industry"}),
        ("GET", "/certification", None),
        ("GET", "/labs", None),
        ("POST", "/compliance-plan", {"product_name": "Pressure Cooker", "standard_id": "IS 2347"}),
    ]

    for method, path, payload in journey:
        response = client.request(method, path, json=payload)
        assert response.status_code == 200, f"{method} {path}: {response.text}"
        assert response.json()


@pytest.mark.parametrize("filename", ["sample.pdf", "sample.xlsx", "sample.docx"])
def test_p1_document_upload_and_analysis(filename):
    response = client.post(
        "/documents/analyze",
        files={"file": (filename, b"BIS 2347 compliance sample", "application/octet-stream")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == filename
    assert body["analyzed"] is True
    assert body["matched_standard"] == "IS 2347:2023"
    assert body["understandable"] is True
    assert "issues" in body
