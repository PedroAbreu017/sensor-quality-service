import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.quality_service import QualityService
from app.models.quality import QualityReport

logger = logging.getLogger("quality.routes")

router = APIRouter(prefix="/quality", tags=["quality"])
service = QualityService()


@router.get("/report/{tenant}", response_model=QualityReport)
def get_report(
    tenant: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
):
    try:
        return service.get_report(tenant.upper(), start, end)
    except Exception as e:
        logger.error(f"Error getting report for {tenant}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def get_summary():
    try:
        return service.get_summary()
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health():
    return {"status": "ok", "service": "sensor-quality-service"}