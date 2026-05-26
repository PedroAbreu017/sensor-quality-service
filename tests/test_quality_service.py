import pytest
from unittest.mock import MagicMock, patch
from app.services.quality_service import QualityService
from app.models.quality import QualityReport


@pytest.fixture
def service():
    return QualityService()


@pytest.fixture
def mock_conn():
    with patch("app.services.quality_service.get_connection") as mock:
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value = cur
        mock.return_value = conn
        yield cur


# ─── get_summary ──────────────────────────────────────────────────────────────

def test_get_summary_returns_dict(service, mock_conn):
    mock_conn.fetchone.side_effect = [
        (1000, 950, 50, "2024-01-01T00:00:00", "2024-12-31T23:59:59"),
        (5,),
        (3,),
    ]
    mock_conn.fetchall.return_value = []

    result = service.get_summary()

    assert isinstance(result, dict)
    assert result["total_records"] == 1000
    assert result["healthy_records"] == 950
    assert result["anomaly_records"] == 50
    assert result["health_score"] == 95.0
    assert result["active_tags"] == 5
    assert result["active_equipments"] == 3


def test_get_summary_zero_records(service, mock_conn):
    mock_conn.fetchone.side_effect = [
        (0, 0, 0, None, None),
        (0,),
        (0,),
    ]

    result = service.get_summary()

    assert result["total_records"] == 0
    assert result["health_score"] == 0.0


def test_get_summary_perfect_health(service, mock_conn):
    mock_conn.fetchone.side_effect = [
        (500, 500, 0, "2024-01-01", "2024-12-31"),
        (10,),
        (5,),
    ]

    result = service.get_summary()

    assert result["health_score"] == 100.0
    assert result["anomaly_records"] == 0


# ─── get_report ───────────────────────────────────────────────────────────────

def test_get_report_returns_quality_report(service, mock_conn):
    mock_conn.fetchone.return_value = (500, 480, 10, 5, 5)
    mock_conn.fetchall.return_value = []

    result = service.get_report("ORION")

    assert isinstance(result, QualityReport)
    assert result.tenant == "ORION"
    assert result.total_records == 500
    assert result.healthy_records == 480
    assert result.health_score == 96.0


def test_get_report_with_anomalous_tags(service, mock_conn):
    mock_conn.fetchone.return_value = (1000, 900, 50, 30, 20)
    mock_conn.fetchall.return_value = [
        (1, "TEMP_01", 200, 30),
        (2, "PRESS_01", 150, 20),
    ]

    result = service.get_report("ORION")

    assert len(result.top_anomalous_tags) == 2
    assert result.top_anomalous_tags[0].tag_name == "TEMP_01"
    assert result.top_anomalous_tags[0].anomaly_count == 30
    assert result.top_anomalous_tags[1].tag_name == "PRESS_01"


def test_get_report_health_score_calculation(service, mock_conn):
    mock_conn.fetchone.return_value = (200, 150, 30, 10, 10)
    mock_conn.fetchall.return_value = []

    result = service.get_report("NEXUS")

    assert result.health_score == 75.0


def test_get_report_zero_total(service, mock_conn):
    mock_conn.fetchone.return_value = (0, 0, 0, 0, 0)
    mock_conn.fetchall.return_value = []

    result = service.get_report("ATLAS")

    assert result.total_records == 0
    assert result.health_score == 0.0


def test_get_report_all_tenants(service, mock_conn):
    for tenant in ["ORION", "NEXUS", "ATLAS"]:
        mock_conn.fetchone.return_value = (100, 90, 5, 3, 2)
        mock_conn.fetchall.return_value = []

        result = service.get_report(tenant)

        assert result.tenant == tenant
        assert result.total_records == 100