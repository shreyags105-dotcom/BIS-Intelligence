import sys
from pathlib import Path

from fastapi.testclient import TestClient

from ai.rag import ask_bis

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from main import app

client = TestClient(app)


def test_pressure_cooker_standard_recommendation():
    response = client.post(
        "/chat",
        json={
            "question": "I want to manufacture domestic pressure cookers. Which BIS standard applies and what tests are required?",
            "mode": "industry",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "IS2347" in body["standard"] or "2347" in body["standard"]
    assert "pressure" in body["answer"].lower()
    assert "test" in body["answer"].lower()
    assert body["source"]
    assert body["references"]


def test_certification_guidance_query():
    response = client.post(
        "/chat",
        json={"question": "How do I get BIS certification for my product?", "mode": "industry"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "certif" in body["answer"].lower()
    assert "bis" in body["answer"].lower()


def test_hallmarking_query():
    response = client.post(
        "/chat",
        json={"question": "What is BIS hallmarking and how does it work?", "mode": "consumer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "hallmark" in body["answer"].lower()
    assert "bis" in body["answer"].lower()


def test_laboratory_guidance_query():
    response = client.post(
        "/chat",
        json={"question": "How can I find a relevant BIS testing laboratory?", "mode": "consumer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "laborator" in body["answer"].lower() or "lab" in body["answer"].lower()
    assert "bis" in body["answer"].lower()


def test_unsupported_query_is_safe():
    response = client.post(
        "/chat",
        json={"question": "Who will win the cricket match today?", "mode": "consumer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "I can assist with Indian Standards and BIS-related services" in body["answer"]


def test_hallucination_guard_hard_mode():
    response = client.post(
        "/chat",
        json={"question": "What is BIS standard IS 99999 for teleportation machines?", "mode": "industry"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["standard"] == "N/A"
    assert "not have verified BIS information" in body["answer"] or "not available" in body["answer"].lower()


def test_standard_lookup_endpoint():
    response = client.get("/standard/IS2347")
    assert response.status_code == 200
    body = response.json()
    assert body["product"]
    assert "IS2347" in body["id"]


def test_service_endpoints_exist():
    for path in ["/certification", "/hallmarking", "/labs"]:
        response = client.get(path)
        assert response.status_code == 200
        body = response.json()
        assert body


def test_ask_bis_accepts_pressure_cooker_query():
    result = ask_bis("I want to manufacture a pressure cooker.")
    assert result["product"] == "Pressure Cooker"
    assert result["needs_clarification"] is False
    assert result["intent"] == "MANUFACTURING_GUIDANCE"
    assert result["answer"]
