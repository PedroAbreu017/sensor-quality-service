from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class QualityLabel(str, Enum):
    SAUDAVEL = "saudavel"
    OUTLIER = "outlier"
    SPIKE = "spike"
    CONGELADO = "congelado"
    OUTLIER_SPIKE = "outlier_spike"
    CONGELADO_SPIKE = "congelado_spike"
    OUTLIER_CONGELADO = "outlier_congelado"


class QualityEvent(BaseModel):
    job_id: str
    tenant: str
    filename: str
    records_processed: int
    records_healthy: int
    records_outlier: int
    records_spike: int
    records_frozen: int
    records_duplicate: int
    timestamp: datetime


class QualityReport(BaseModel):
    tenant: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    total_records: int = 0
    healthy_records: int = 0
    outlier_records: int = 0
    spike_records: int = 0
    frozen_records: int = 0
    duplicate_records: int = 0
    health_score: float = 0.0
    top_anomalous_tags: list = []


class TagAnomalyStats(BaseModel):
    tag_id: int
    tag_name: Optional[str] = None
    total_readings: int
    anomaly_count: int
    anomaly_rate: float
    last_anomaly: Optional[datetime] = None