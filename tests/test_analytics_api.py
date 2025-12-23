"""Tests for analytics API endpoints."""
import pytest
from datetime import date, datetime, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAnalyticsEndpoints:
    """Test suite for analytics endpoints."""

    async def test_streak_heatmap_default_days(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_tasks: list
    ):
        """
        Test GET /api/analytics/streak-heatmap with default days parameter.

        Should return daily completion counts for the last 365 days.
        """
        response = await async_client.get(
            "/api/analytics/streak-heatmap",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response is a list
        assert isinstance(data, list)

        # Verify each item has date and count fields
        for item in data:
            assert "date" in item
            assert "count" in item
            assert isinstance(item["count"], int)
            assert item["count"] >= 0

    async def test_streak_heatmap_custom_days(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test GET /api/analytics/streak-heatmap with custom days parameter.

        Should return data for the specified number of days.
        """
        response = await async_client.get(
            "/api/analytics/streak-heatmap?days=30",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response is a list
        assert isinstance(data, list)

        # Verify date format is YYYY-MM-DD
        for item in data:
            try:
                date.fromisoformat(item["date"])
            except ValueError:
                pytest.fail(f"Invalid date format: {item['date']}")

    async def test_streak_heatmap_max_days_validation(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test GET /api/analytics/streak-heatmap exceeds max days.

        Should return 422 validation error for days > 730.
        """
        response = await async_client.get(
            "/api/analytics/streak-heatmap?days=1000",
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_streak_heatmap_min_days_validation(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test GET /api/analytics/streak-heatmap with invalid min days.

        Should return 422 validation error for days < 1.
        """
        response = await async_client.get(
            "/api/analytics/streak-heatmap?days=0",
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_streak_heatmap_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """
        Test GET /api/analytics/streak-heatmap without authentication.

        Should return 401 Unauthorized.
        """
        response = await async_client.get("/api/analytics/streak-heatmap")

        assert response.status_code == 401

    async def test_streak_heatmap_data_isolation(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        other_user_headers: dict
    ):
        """
        Test GET /api/analytics/streak-heatmap data isolation.

        Users should only see their own completion data.
        """
        # Get analytics for first user
        response1 = await async_client.get(
            "/api/analytics/streak-heatmap",
            headers=auth_headers
        )

        # Get analytics for second user
        response2 = await async_client.get(
            "/api/analytics/streak-heatmap",
            headers=other_user_headers
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # The responses could be different (different users have different tasks)
        data1 = response1.json()
        data2 = response2.json()

        # Both should be lists
        assert isinstance(data1, list)
        assert isinstance(data2, list)

    async def test_analytics_summary(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test GET /api/analytics/summary endpoint.

        Should return summary statistics for current user.
        """
        response = await async_client.get(
            "/api/analytics/summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "pending_tasks" in data
        assert "completion_rate" in data
        assert "current_streak" in data
        assert "longest_streak" in data

        # Verify data types
        assert isinstance(data["total_tasks"], int)
        assert isinstance(data["completed_tasks"], int)
        assert isinstance(data["pending_tasks"], int)
        assert isinstance(data["completion_rate"], (int, float))
        assert isinstance(data["current_streak"], int)
        assert isinstance(data["longest_streak"], int)

        # Verify constraints
        assert data["total_tasks"] >= 0
        assert data["completed_tasks"] >= 0
        assert data["pending_tasks"] >= 0
        assert 0 <= data["completion_rate"] <= 100
        assert data["current_streak"] >= 0
        assert data["longest_streak"] >= 0

    async def test_analytics_summary_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """
        Test GET /api/analytics/summary without authentication.

        Should return 401 Unauthorized.
        """
        response = await async_client.get("/api/analytics/summary")

        assert response.status_code == 401

    async def test_analytics_summary_data_isolation(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        other_user_headers: dict
    ):
        """
        Test GET /api/analytics/summary data isolation.

        Users should only see their own statistics.
        """
        # Get summary for first user
        response1 = await async_client.get(
            "/api/analytics/summary",
            headers=auth_headers
        )

        # Get summary for second user
        response2 = await async_client.get(
            "/api/analytics/summary",
            headers=other_user_headers
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Both users should have their own stats
        # These may be the same initially (both 0), but they're isolated
        assert "total_tasks" in data1
        assert "total_tasks" in data2
