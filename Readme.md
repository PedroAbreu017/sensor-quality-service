# Sensor Quality Service

Data quality analysis and reporting microservice for the Sensor Platform.

---

## Architecture

Part of the **Sensor Platform** microservices ecosystem:
[sensor-data-integrator] → RabbitMQ → [Quality Service] → [PostgreSQL]
↑
[sensor-dashboard]

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Message Broker | RabbitMQ (aio-pika) |
| Database | PostgreSQL 15 + TimescaleDB |
| Testing | Pytest + unittest.mock |

---

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL running (via sensor-platform Docker)
- RabbitMQ running (via sensor-platform Docker)

### 1. Start infrastructure
```bash
cd ../sensor-platform
make infra
```

### 2. Set up environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
cp .env.example .env
```

### 3. Run the service
```bash
python -m uvicorn app.main:app --port 8097 --reload
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quality/summary` | Global quality summary |
| GET | `/quality/report/{tenant}` | Quality report by tenant |
| GET | `/quality/health` | Health check |

### Summary Response
```json
{
  "total_records": 1000,
  "healthy_records": 950,
  "anomaly_records": 50,
  "health_score": 95.0,
  "first_reading": "2024-01-01T00:00:00",
  "last_reading": "2024-12-31T23:59:59",
  "active_tags": 5,
  "active_equipments": 3
}
```

### Report Response
```json
{
  "tenant": "ORION",
  "total_records": 500,
  "healthy_records": 480,
  "outlier_records": 10,
  "spike_records": 5,
  "frozen_records": 5,
  "health_score": 96.0,
  "top_anomalous_tags": [
    {
      "tag_id": 1,
      "tag_name": "TEMP_01",
      "total_readings": 200,
      "anomaly_count": 30,
      "anomaly_rate": 15.0
    }
  ]
}
```

---

## Quality Labels

| Label | Description |
|-------|-------------|
| `saudavel` | Healthy reading |
| `outlier` | Invalid timestamp or value |
| `spike` | Abrupt jump detected (MAD) |
| `congelado` | Frozen sensor |
| `outlier_spike` | Outlier + spike combined |
| `congelado_spike` | Frozen + spike combined |
| `outlier_congelado` | Outlier + frozen combined |

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Project Structure
sensor-quality-service/
├── app/
│   ├── main.py              # FastAPI app + RabbitMQ consumer
│   ├── config.py            # Settings
│   ├── models/
│   │   └── quality.py       # Pydantic models
│   ├── routes/
│   │   └── quality.py       # REST endpoints
│   └── services/
│       ├── quality_service.py  # Business logic
│       └── consumer.py         # RabbitMQ consumer
├── tests/
│   ├── test_quality_service.py
│   └── test_routes.py
├── requirements.txt
├── .env.example
└── README.md

---

## Planned Improvements

- [ ] Integration tests with real database
- [ ] Time-series quality trends endpoint
- [ ] Alert thresholds configuration per tenant

---

## License

MIT