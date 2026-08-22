import asyncio
import pytest
from src.stream_gateway import stream_analyst_response, format_sse


def test_format_sse():
    data = {"type": "answer", "content": "Hello"}
    assert format_sse(data) == 'data: {"type": "answer", "content": "Hello"}\n\n'


@pytest.mark.asyncio
async def test_stream_generator_error_handling(monkeypatch):
    def mock_exec(*args):
        return None, None, "Database connection failed"

    monkeypatch.setattr("src.stream_gateway.generate_sql_and_execute", mock_exec)

    events = []
    async for event in stream_analyst_response("test", "dataset_id"):
        events.append(event)

    assert len(events) >= 2
    assert "error" in events[-1]
    assert "Database connection failed" in events[-1]
