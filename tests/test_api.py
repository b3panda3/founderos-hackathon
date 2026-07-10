"""Smoke tests for stable, dependency-free API contracts."""

import unittest

import httpx

from backend.main import app


class ApiContractTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_health_endpoint_returns_ok(self) -> None:
        response = await self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    async def test_agents_endpoint_returns_all_agents(self) -> None:
        response = await self.client.get("/api/agents")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["agents"]), 6)

    async def test_chat_rejects_an_unknown_agent(self) -> None:
        response = await self.client.post(
            "/chat",
            json={"message": "Hello", "agent": "unknown-agent", "stream": False},
        )

        self.assertEqual(response.status_code, 422)

    async def test_knowledge_write_requires_a_key(self) -> None:
        response = await self.client.post("/knowledge", json={"text": "Private data"})

        self.assertIn(response.status_code, {401, 503})


if __name__ == "__main__":
    unittest.main()
