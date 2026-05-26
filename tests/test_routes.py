import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.quality import QualityReport, TagAnomalyStats


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_service():
    with patch("app.routes.quality.service") as mock:
        yield mock


# ─── Health ───────────────────────────────────────────────────────────────────

def test_health(client):
    response = client.get("/quality/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "sensor-quality-service"


# ─── Summary ──────────────────────────────────────────────────────────────────

def test_get_summary_success(client, mock_service):
    mock_service.get_summary.return_value = {
        "total_records": 1000,
        "healthy_records": 950,
        "anomaly_records": 50,
        "health_score": 95.0,
        "first_reading": None,
        "last_reading": None,
        "active_tags": 5,
        "active_equipments": 3,
    }

    response = client.get("/quality/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 1000
    assert data["health_score"] == 95.0
    assert data["active_tags"] == 5


def test_get_summary_empty(client, mock_service):
    mock_service.get_summary.return_value = {
        "total_records": 0,
        "healthy_records": 0,
        "anomaly_records": 0,
        "health_score": 0.0,
        "first_reading": None,
        "last_reading": None,
        "active_tags": 0,
        "active_equipments": 0,
    }

    response = client.get("/quality/summary")
    assert response.status_code == 200
    assert response.json()["total_records"] == 0


def test_get_summary_error(client, mock_service):
    mock_service.get_summary.side_effect = Exception("DB error")

    response = client.get("/quality/summary")
    assert response.status_code == 500


# ─── Report ───────────────────────────────────────────────────────────────────

def test_get_report_orion(client, mock_service):
    mock_service.get_report.return_value = QualityReport(
        tenant="ORION",
        total_records=500,
        healthy_records=480,
        outlier_records=10,
        spike_records=5,
        frozen_records=5,
        duplicate_records=10,
        health_score=96.0,
        top_anomalous_tags=[],
    )

    response = client.get("/quality/report/ORION")

    assert response.status_code == 200
    data = response.json()
    assert data["tenant"] == "ORION"
    assert data["total_records"] == 500
    assert data["health_score"] == 96.0


def test_get_report_nexus(client, mock_service):
    mock_service.get_report.return_value = QualityReport(
        tenant="NEXUS",
        total_records=200,
        healthy_records=190,
        outlier_records=5,
        spike_records=3,
        frozen_records=2,
        duplicate_records=5,
        health_score=95.0,
        top_anomalous_tags=[],
    )

    response = client.get("/quality/report/NEXUS")

    assert response.status_code == 200
    assert response.json()["tenant"] == "NEXUS"


def test_get_report_atlas(client, mock_service):
    mock_service.get_report.return_value = QualityReport(
        tenant="ATLAS",
        total_records=300,
        healthy_records=270,
        outlier_records=15,
        spike_records=10,
        frozen_records=5,
        duplicate_records=15,
        health_score=90.0,
        top_anomalous_tags=[],
    )

    response = client.get("/quality/report/ATLAS")

    assert response.status_code == 200
    assert response.json()["tenant"] == "ATLAS"
    assert response.json()["health_score"] == 90.0


def test_get_report_with_anomalous_tags(client, mock_service):
    mock_service.get_report.return_value = QualityReport(
        tenant="ORION",
        total_records=1000,
        healthy_records=900,
        outlier_records=50,
        spike_records=30,
        frozen_records=20,
        duplicate_records=50,
        health_score=90.0,
        top_anomalous_tags=[
            TagAnomalyStats(
                tag_id=1,
                tag_name="TEMP_01",
                total_readings=200,
                anomaly_count=30,
                anomaly_rate=15.0,
            ),
            TagAnomalyStats(
                tag_id=2,
                tag_name="PRESS_01",
                total_readings=150,
                anomaly_count=20,
                anomaly_rate=13.3,
            ),
        ],
    )

    response = client.get("/quality/report/ORION")

    assert response.status_code == 200
    data = response.json()
    assert len(data["top_anomalous_tags"]) == 2
    assert data["top_anomalous_tags"][0]["tag_name"] == "TEMP_01"
    assert data["top_anomalous_tags"][1]["tag_name"] == "PRESS_01"


def test_get_report_error(client, mock_service):
    mock_service.get_report.side_effect = Exception("DB error")

    response = client.get("/quality/report/ORION")
    assert response.status_code == 500


def test_get_report_tenant_uppercase(client, mock_service):
    mock_service.get_report.return_value = QualityReport(
        tenant="ORION",
        total_records=100,
        healthy_records=100,
        outlier_records=0,
        spike_records=0,
        frozen_records=0,
        duplicate_records=0,
        health_score=100.0,
        top_anomalous_tags=[],
    )

    response = client.get("/quality/report/orion")
    assert response.status_code == 200
    assert response.json()["tenant"] == "ORION"