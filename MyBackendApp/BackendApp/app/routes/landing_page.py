import os
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.tables import AuditLog
from ..utils.loguru_config import logger

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def landing_page():
    """
    Render the landing page with Bootstrap (Dark Theme).
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Landing Page</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body class="bg-dark text-light">
        <div class="container text-center mt-5">
            <h1 class="mb-4">Welcome to Communication LTD API</h1>
            <div class="d-grid gap-2 d-md-flex justify-content-center">
                <button class="btn btn-primary me-md-2" onclick="location.href='/docs'">Documentation</button>
                <button class="btn btn-secondary" onclick="location.href='/audit-logs-view'">Logs</button>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/audit-logs-view", response_class=HTMLResponse)
def audit_logs_view():
    """
    Render a page to view and filter Audit Logs.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audit Logs</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body class="bg-dark text-light">
        <div class="container mt-5">
            <h1 class="text-center mb-4">Audit Logs</h1>
            <div class="mb-3">
                <label for="userIdInput" class="form-label">Filter by User ID</label>
                <input type="text" id="userIdInput" class="form-control" placeholder="Enter User ID">
            </div>
            <button class="btn btn-primary mb-4" onclick="filterLogs()">Filter Logs</button>
            <table class="table table-dark table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>User ID</th>
                        <th>Action</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody id="auditLogsTable">
                </tbody>
            </table>
        </div>

        <script>
            async function fetchLogs(userId = null) {
                const endpoint = userId ? `/audit-logs?user_id=${userId}` : '/audit-logs';
                const response = await fetch(endpoint);
                const logs = await response.json();
                const tableBody = document.getElementById("auditLogsTable");
                tableBody.innerHTML = "";
                logs.forEach(log => {
                    const row = `<tr>
                        <td>${log.id}</td>
                        <td>${log.user_id}</td>
                        <td>${log.action}</td>
                        <td>${new Date(log.timestamp).toLocaleString()}</td>
                    </tr>`;
                    tableBody.innerHTML += row;
                });
            }

            function filterLogs() {
                const userId = document.getElementById("userIdInput").value.trim();
                fetchLogs(userId || null);
            }

            // Load logs on page load
            document.addEventListener("DOMContentLoaded", () => fetchLogs());
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/audit-logs-view-filter")
def get_audit_logs(user_id: str = None, db: Session = Depends(get_db)):
    """
    Fetch Audit Logs, optionally filtered by User ID.
    :param user_id: Optional User ID to filter logs.
    :param db: Database session.
    :return: List of audit logs.
    """
    logger.info("Fetching audit logs from the database.")
    if user_id:
        logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
        logger.debug(f"Fetched {len(logs)} logs for User ID: {user_id}.")
    else:
        logs = db.query(AuditLog).all()
        logger.debug(f"Fetched {len(logs)} logs.")
    return [{"id": log.id, "user_id": log.user_id, "action": log.action, "timestamp": log.timestamp} for log in logs]
