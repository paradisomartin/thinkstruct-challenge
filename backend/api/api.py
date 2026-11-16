"""API composition and infrastructure routes."""

import logging
from typing import Literal

from django.db import connection, DatabaseError
from ninja import NinjaAPI, Schema
from api.v1.patents.api import router as patents_router


logger = logging.getLogger("thinkstruct.health")
api = NinjaAPI(title="Thinkstruct API", version="1.0.0")
api.add_router("/v1/patents", patents_router)


class HealthResponse(Schema):
    status: Literal["ok", "unavailable"]
    database: Literal["ok", "unavailable"]


@api.get("/health", response={200: HealthResponse, 503: HealthResponse}, tags=["system"])
def health(request):
    """Readiness: the application can execute a query against PostgreSQL."""
    logger.debug("Database readiness check started")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        # Do not return connection details or credentials to the client.
        logger.warning("Database readiness check failed")
        return 503, {"status": "unavailable", "database": "unavailable"}
    logger.debug("Database readiness check succeeded")
    return 200, {"status": "ok", "database": "ok"}
