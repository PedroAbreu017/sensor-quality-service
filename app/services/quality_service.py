import logging
import psycopg2
from datetime import datetime
from typing import Optional

from app.config import get_settings
from app.models.quality import QualityReport, TagAnomalyStats

logger = logging.getLogger("quality.service")


def get_connection():
    settings = get_settings()
    return psycopg2.connect(**settings.db_config)


class QualityService:

    def get_report(self, tenant: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> QualityReport:
        try:
            conn = get_connection()
            cur = conn.cursor()

            conditions = []
            params = []

            if start:
                conditions.append("timestamp >= %s")
                params.append(start)
            if end:
                conditions.append("timestamp <= %s")
                params.append(end)

            where = "WHERE " + " AND ".join(conditions) if conditions else ""

            query = f"""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN quality = 'saudavel' THEN 1 ELSE 0 END) as healthy,
                    SUM(CASE WHEN quality = 'outlier' THEN 1 ELSE 0 END) as outlier,
                    SUM(CASE WHEN quality LIKE '%spike%' THEN 1 ELSE 0 END) as spike,
                    SUM(CASE WHEN quality LIKE '%congelado%' THEN 1 ELSE 0 END) as frozen
                FROM sensor_readings
                {where}
            """

            cur.execute(query, params if params else None)
            row = cur.fetchone()

            total = row[0] or 0
            healthy = row[1] or 0
            outlier = row[2] or 0
            spike = row[3] or 0
            frozen = row[4] or 0

            health_score = round((healthy / total * 100), 2) if total > 0 else 0.0

            cur.execute("""
                SELECT
                    t.id,
                    t.name,
                    COUNT(*) as total,
                    SUM(CASE WHEN r.quality != 'saudavel' THEN 1 ELSE 0 END) as anomalies
                FROM sensor_readings r
                JOIN tag t ON t.id = r.tag_id
                WHERE r.quality != 'saudavel'
                GROUP BY t.id, t.name
                ORDER BY anomalies DESC
                LIMIT 5
            """)

            top_tags = []
            for tag_row in cur.fetchall():
                tag_total = tag_row[2] or 1
                anomaly_count = tag_row[3] or 0
                top_tags.append(TagAnomalyStats(
                    tag_id=tag_row[0],
                    tag_name=tag_row[1],
                    total_readings=tag_total,
                    anomaly_count=anomaly_count,
                    anomaly_rate=round(anomaly_count / tag_total * 100, 2),
                ))

            cur.close()
            conn.close()

            return QualityReport(
                tenant=tenant,
                period_start=start,
                period_end=end,
                total_records=total,
                healthy_records=healthy,
                outlier_records=outlier,
                spike_records=spike,
                frozen_records=frozen,
                duplicate_records=outlier,
                health_score=health_score,
                top_anomalous_tags=top_tags,
            )

        except Exception as e:
            logger.error(f"[quality] Error generating report: {e}", exc_info=True)
            raise

    def get_summary(self) -> dict:
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN quality = 'saudavel' THEN 1 ELSE 0 END) as healthy,
                    SUM(CASE WHEN quality != 'saudavel' THEN 1 ELSE 0 END) as anomalies,
                    MIN(timestamp) as first_reading,
                    MAX(timestamp) as last_reading
                FROM sensor_readings
            """)
            row = cur.fetchone()

            cur.execute("SELECT COUNT(DISTINCT tag_id) FROM sensor_readings")
            tag_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(DISTINCT equipment_id) FROM sensor_readings")
            equipment_count = cur.fetchone()[0]

            cur.close()
            conn.close()

            total = row[0] or 0
            healthy = row[1] or 0

            return {
                "total_records": total,
                "healthy_records": healthy,
                "anomaly_records": row[2] or 0,
                "health_score": round((healthy / total * 100), 2) if total > 0 else 0.0,
                "first_reading": row[3],
                "last_reading": row[4],
                "active_tags": tag_count,
                "active_equipments": equipment_count,
            }

        except Exception as e:
            logger.error(f"[quality] Error getting summary: {e}", exc_info=True)
            raise