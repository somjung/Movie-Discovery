"""Unit tests for the AI client (network calls are mocked)."""

import json
from unittest.mock import Mock

import pytest
import requests

from fakes import FakeResponse
from src.ai_client import AiClient, AiError, describe_ai_error
from src.config import AI_BASE_URL, AI_MODEL


def make_client(session, **kwargs):
    return AiClient(api_key="test-key", base_url="https://ai.test/v1",
                    session=session, **kwargs)


def reply_response(answer):
    """A 200 response whose message content is ``json.dumps(answer)``."""
    body = {"choices": [{"message": {"content": json.dumps(answer)}}]}
    return FakeResponse(200, body)


def content_response(content):
    """A 200 response with a raw string as the message content."""
    body = {"choices": [{"message": {"content": content}}]}
    return FakeResponse(200, body)


# ---------- request shape ----------


def test_chat_json_returns_parsed_reply():
    session = Mock()
    session.post.return_value = reply_response({"status": "ok"})
    client = make_client(session)
    assert client.chat_json("sys", "user") == {"status": "ok"}
    assert session.post.call_count == 1


def test_chat_json_sends_expected_payload():
    session = Mock()
    session.post.return_value = reply_response({"ok": True})
    client = make_client(session, model="test-model", timeout=12)
    client.chat_json("SYSTEM", "USER", max_tokens=123)
    args, kwargs = session.post.call_args
    assert args[0] == "https://ai.test/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["timeout"] == 12
    payload = kwargs["json"]
    assert payload["model"] == "test-model"
    assert payload["messages"][0] == {"role": "system", "content": "SYSTEM"}
    assert payload["messages"][1] == {"role": "user", "content": "USER"}
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["max_tokens"] == 123
    assert payload["temperature"] == 0
    assert payload["stream"] is False


def test_client_defaults_come_from_config(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    client = AiClient(session=Mock())
    assert client.base_url == AI_BASE_URL
    assert client.model == AI_MODEL


# ---------- error mapping ----------


def test_auth_error_raises_ai_error():
    session = Mock()
    session.post.return_value = FakeResponse(401)
    client = make_client(session)
    with pytest.raises(AiError, match="401"):
        client.chat_json("s", "u")


def test_rate_limit_raises_ai_error():
    session = Mock()
    session.post.return_value = FakeResponse(429)
    client = make_client(session)
    with pytest.raises(AiError, match="429"):
        client.chat_json("s", "u")


def test_server_error_raises_ai_error():
    session = Mock()
    session.post.return_value = FakeResponse(500)
    client = make_client(session)
    with pytest.raises(AiError, match="500"):
        client.chat_json("s", "u")


def test_timeout_raises_ai_error():
    session = Mock()
    session.post.side_effect = requests.Timeout("slow")
    client = make_client(session)
    with pytest.raises(AiError, match="timed out"):
        client.chat_json("s", "u")


def test_network_failure_raises_ai_error():
    session = Mock()
    session.post.side_effect = requests.ConnectionError("boom")
    client = make_client(session)
    with pytest.raises(AiError, match="failed"):
        client.chat_json("s", "u")


def test_transport_invalid_json_raises_ai_error():
    session = Mock()
    session.post.return_value = FakeResponse(200, ValueError("bad json"))
    client = make_client(session)
    with pytest.raises(AiError, match="invalid JSON"):
        client.chat_json("s", "u")


def test_reply_not_json_raises_ai_error():
    session = Mock()
    session.post.return_value = content_response("hello there")
    client = make_client(session)
    with pytest.raises(AiError, match="not valid JSON"):
        client.chat_json("s", "u")


def test_reply_must_be_an_object():
    session = Mock()
    session.post.return_value = content_response("[1, 2, 3]")
    client = make_client(session)
    with pytest.raises(AiError, match="JSON object"):
        client.chat_json("s", "u")


def test_missing_message_raises_ai_error():
    session = Mock()
    session.post.return_value = FakeResponse(200, {})
    client = make_client(session)
    with pytest.raises(AiError, match="missing a message"):
        client.chat_json("s", "u")


# ---------- key handling ----------


def test_client_reads_key_from_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "env-key")
    client = AiClient(session=Mock())
    assert client.api_key == "env-key"


def test_missing_key_raises_runtime_error(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        AiClient()


# ---------- Thai message mapping ----------


def test_describe_ai_error_auth():
    error = AiError("the AI provider rejected the API key (HTTP 401)")
    assert "คีย์ AI" in describe_ai_error(error)


def test_describe_ai_error_timeout():
    assert "หมดเวลา" in describe_ai_error(AiError("the AI request timed out"))


def test_describe_ai_error_bad_reply():
    error = AiError("the AI reply is not valid JSON")
    assert "ผิดรูปแบบ" in describe_ai_error(error)


def test_describe_ai_error_default():
    message = describe_ai_error(AiError("unexpected AI status 500"))
    assert "เชื่อมต่อบริการ AI ไม่สำเร็จ" in message
