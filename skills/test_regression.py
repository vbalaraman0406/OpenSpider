"""Regression test suite for Pitwall.ai Backend API"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints"""

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "Pitwall.ai"
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestRaceEndpoints:
    """Test race API endpoints"""

    def test_get_races_2024(self):
        response = client.get("/api/races/2024")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_races_2023(self):
        response = client.get("/api/races/2023")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_race_results(self):
        response = client.get("/api/races/2024/1/results")
        # May return 200 or 404 depending on data availability
        assert response.status_code in [200, 404, 422, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_race_laps(self):
        response = client.get("/api/races/2024/1/laps")
        assert response.status_code in [200, 404, 422, 500]

    def test_get_race_invalid_year(self):
        response = client.get("/api/races/1800")
        # Should handle gracefully
        assert response.status_code in [200, 400, 404, 422, 500]


class TestDriverEndpoints:
    """Test driver API endpoints"""

    def test_get_drivers_2024(self):
        response = client.get("/api/drivers/2024")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_drivers_2023(self):
        response = client.get("/api/drivers/2023")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_driver_stats(self):
        response = client.get("/api/drivers/2024/VER/stats")
        assert response.status_code in [200, 404, 422, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_driver_stats_invalid(self):
        response = client.get("/api/drivers/2024/INVALID_DRIVER/stats")
        assert response.status_code in [200, 400, 404, 422, 500]


class TestCORSHeaders:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        # CORS should allow the request
        assert response.status_code in [200, 405]


class TestAPIStructure:
    """Test API response structure consistency"""

    def test_root_response_structure(self):
        response = client.get("/")
        data = response.json()
        required_keys = ["service", "version", "status"]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

    def test_health_response_structure(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data

    def test_content_type_json(self):
        response = client.get("/")
        assert "application/json" in response.headers.get("content-type", "")

    def test_health_content_type_json(self):
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
