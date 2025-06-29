from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from app.db import get_connection
from app.helpers import calculate_metrics
from app.queries import (
    get_dashboard_metadata,
    get_dashboard_metrics,
    get_shared_managers,
    insert_dashboard_share,
    create_dashboard_query,
    insert_dashboard_metrics_query
)

router = APIRouter()

class CreateDashboardRequest(BaseModel):
    title: str
    created_by: str  # employee_id
    department: str
    start_date: str
    end_date: str

class ShareDashboardRequest(BaseModel):
    manager_ids: list[str]

@router.post("/dashboard")
def create_dashboard(payload: CreateDashboardRequest):
    dashboard_id = str(uuid4())
    conn = get_connection()
    try:
        metrics = calculate_metrics(conn, payload.department, payload.start_date, payload.end_date)

        with conn.cursor() as cur:
            # Insert dashboard
            cur.execute(
                create_dashboard_query,
                (
                    dashboard_id,
                    payload.title,
                    payload.created_by,
                    payload.department,
                    payload.start_date,
                    payload.end_date
                )
            )

            # Insert metrics
            for metric, value in metrics.items():
                cur.execute(
                    insert_dashboard_metrics_query,
                    (dashboard_id, metric, value)
                )

        conn.commit()
        return {"dashboard_id": dashboard_id, "metrics": metrics}
    finally:
        conn.close()
@router.get("/dashboard/{dashboard_id}")
def get_dashboard(dashboard_id: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get dashboard metadata
            cur.execute(get_dashboard_metadata, (dashboard_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Dashboard not found")

            dashboard = {
                "dashboard_id": dashboard_id,
                "title": row[0],
                "department": row[1],
                "start_date": row[2],
                "end_date": row[3]
            }

            # Get metrics
            cur.execute(get_dashboard_metrics, (dashboard_id,))
            dashboard["metrics"] = {
                metric: float(value) for metric, value in cur.fetchall()
            }

            # Get shared managers
            cur.execute(get_shared_managers, (dashboard_id,))
            dashboard["shared_with"] = [
                {"manager_id": emp_id, "name": name, "email": email}
                for emp_id, name, email in cur.fetchall()
            ]

        return dashboard
    finally:
        conn.close()


@router.post("/dashboard/{dashboard_id}/share")
def share_dashboard(dashboard_id: str, payload: ShareDashboardRequest):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for manager_id in payload.manager_ids:
                cur.execute(insert_dashboard_share, (dashboard_id, manager_id))
        conn.commit()
        return {"dashboard_id": dashboard_id, "shared_with": payload.manager_ids}
    finally:
        conn.close()


@router.get("/health_check")
def check_health():
    return {"healthy": True}


@router.get("/db_health_check")
def check_db_health():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            return {"db_healthy": True}
    except Exception as e:
        return {"db_healthy": False, "error": str(e)}
    finally:
        if conn:
            conn.close()

