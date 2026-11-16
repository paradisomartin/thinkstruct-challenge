from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase


class HealthTests(TestCase):
    def test_health_queries_the_database(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})

    def test_database_failure_returns_503_without_details(self):
        with patch("api.api.connection.cursor", side_effect=OperationalError("private details")):
            with self.assertLogs("thinkstruct.health", level="WARNING") as captured:
                response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(), {"status": "unavailable", "database": "unavailable"}
        )
        self.assertNotIn("private details", response.content.decode())
        self.assertNotIn("private details", "\n".join(captured.output))

    def test_openapi_describes_health_responses(self):
        response = self.client.get("/api/openapi.json")
        self.assertEqual(response.status_code, 200)
        responses = response.json()["paths"]["/api/health"]["get"]["responses"]
        self.assertIn("200", responses)
        self.assertIn("503", responses)

    def test_interactive_documentation_renders(self):
        response = self.client.get("/api/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("swagger", response.content.decode().lower())
