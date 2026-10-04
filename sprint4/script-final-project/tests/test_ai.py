"""Unit tests for the AI client and the AI advisor (network calls mocked)."""

import json
from unittest.mock import Mock

import pytest
import requests

from fakes import FakeAiClient, FakeResponse, FakeTmdbClient
from src.ai_advisor import AiAdvisor
from src.ai_client import AiClient, AiError, describe_ai_error
from src.config import AI_BASE_URL, AI_MODEL
from src.discovery import DiscoveryService
from src.movie_store import MovieStore
from src.sample_data import SAMPLE_MOVIES


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


@pytest.fixture()
def store():
    db = MovieStore(":memory:")
    yield db
    db.close()


def build_advisor(store, ai_client):
    """An advisor over the fake TMDB data; ``ai_client`` may be None."""
    return AiAdvisor(ai_client, DiscoveryService(FakeTmdbClient(), store),
                     store)


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

# ---------- advisor: recommendations ----------


def test_recommend_keeps_only_valid_candidates(store):
    fake = FakeAiClient(reply={"picks": [
        {"id": 103, "reason": "สนุกมาก"},
        {"id": 999, "reason": "ไม่อยู่ในชุด"},
        {"id": 105, "reason": "น่าดู"},
    ]})
    picks = build_advisor(store, fake).recommend(27205)
    assert [movie["id"] for movie in picks] == [103, 105]
    assert picks[0]["title"] == "Cobalt Night"
    assert picks[0]["reason"] == "สนุกมาก"


def test_recommend_dedupes_and_caps_picks(store):
    fake = FakeAiClient(reply={"picks": [
        {"id": 103, "reason": "a"},
        {"id": 103, "reason": "ซ้ำ"},
        {"id": 101, "reason": "b"},
        {"id": 102, "reason": "c"},
    ]})
    picks = build_advisor(store, fake).recommend(27205, picks=2)
    assert [movie["id"] for movie in picks] == [103, 101]


def test_recommend_prompt_lists_candidates_and_mood(store):
    fake = FakeAiClient(reply={"picks": [{"id": 103, "reason": "ok"}]})
    build_advisor(store, fake).recommend(27205, mood="อยากดูเบา ๆ")
    call = fake.calls[0]
    assert "103" in call["user"]
    assert "Cobalt Night" in call["user"]
    assert "อยากดูเบา ๆ" in call["user"]
    assert "JSON" in call["system"]


def test_recommend_rejects_non_list_picks(store):
    fake = FakeAiClient(reply={"picks": "oops"})
    with pytest.raises(AiError, match="no usable picks"):
        build_advisor(store, fake).recommend(27205)


def test_recommend_rejects_blank_reasons(store):
    fake = FakeAiClient(reply={"picks": [{"id": 103, "reason": "   "}]})
    with pytest.raises(AiError, match="no usable picks"):
        build_advisor(store, fake).recommend(27205)


def test_recommend_without_candidates_raises(store):
    fake = FakeAiClient(reply={"picks": []})
    advisor = AiAdvisor(fake, DiscoveryService(
        FakeTmdbClient(similar=[], recommendations=[]), store), store)
    with pytest.raises(AiError, match="no similar movies"):
        advisor.recommend(27205)
    assert fake.calls == []


def test_recommend_second_call_uses_the_cache(store):
    fake = FakeAiClient(replies=[
        {"picks": [{"id": 103, "reason": "a"}]},
        {"picks": [{"id": 101, "reason": "b"}]},
    ])
    advisor = build_advisor(store, fake)
    first = advisor.recommend(27205, mood="ตลก")
    second = advisor.recommend(27205, mood="ตลก")
    assert first == second
    assert len(fake.calls) == 1
    other = advisor.recommend(27205, mood="เศร้า")
    assert other[0]["id"] == 101  # different mood -> fresh AI call
    assert len(fake.calls) == 2


def test_recommend_corrupt_cache_is_refetched(store):
    fake = FakeAiClient(replies=[
        {"picks": [{"id": 103, "reason": "a"}]},
        {"picks": [{"id": 105, "reason": "b"}]},
    ])
    advisor = build_advisor(store, fake)
    advisor.recommend(27205, mood="x")
    store.conn.execute("UPDATE api_cache SET payload = 'not json'")
    store.conn.commit()
    picks = advisor.recommend(27205, mood="x")
    assert len(fake.calls) == 2
    assert picks[0]["id"] == 105


def test_recommend_without_ai_client_raises(store):
    advisor = build_advisor(store, None)
    with pytest.raises(AiError, match="not configured"):
        advisor.recommend(27205)


def test_recommend_propagates_ai_errors(store):
    fake = FakeAiClient(error=AiError("the AI request timed out"))
    with pytest.raises(AiError, match="timed out"):
        build_advisor(store, fake).recommend(27205)


def test_suggest_candidates_returns_similar_movies(store):
    fake = FakeAiClient()
    advisor = build_advisor(store, fake)
    candidates = advisor.suggest_candidates(27205)
    assert [movie["id"] for movie in candidates][:3] == [103, 105, 101]
    assert fake.calls == []  # no AI involved


# ---------- advisor: Thai summaries ----------


def test_summarize_returns_and_caches(store):
    fake = FakeAiClient(reply={"summary": "เรื่องย่อไทย",
                               "why": ["ก", "ข", "ค"]})
    advisor = build_advisor(store, fake)
    movie = dict(SAMPLE_MOVIES[0])
    first = advisor.summarize(movie)
    assert first["summary"] == "เรื่องย่อไทย"
    assert first["why"] == ["ก", "ข", "ค"]
    second = advisor.summarize(movie)
    assert second == first
    assert len(fake.calls) == 1
    assert store.get_cached("ai:summary:101") is not None


def test_summarize_accepts_stored_movie_shape(store):
    store.add_movie(dict(SAMPLE_MOVIES[0]))
    stored = store.get_movie(101)  # keyed by tmdb_id, not id
    fake = FakeAiClient(reply={"summary": "s", "why": ["w"]})
    result = build_advisor(store, fake).summarize(stored)
    assert result["summary"] == "s"
    assert store.get_cached("ai:summary:101") is not None


def test_summarize_incomplete_reply_raises(store):
    fake = FakeAiClient(reply={"summary": "   ", "why": ["ก"]})
    with pytest.raises(AiError, match="incomplete"):
        build_advisor(store, fake).summarize(dict(SAMPLE_MOVIES[0]))


def test_summarize_without_why_raises(store):
    fake = FakeAiClient(reply={"summary": "เนื้อเรื่อง", "why": []})
    with pytest.raises(AiError, match="incomplete"):
        build_advisor(store, fake).summarize(dict(SAMPLE_MOVIES[0]))


def test_summarize_caps_field_lengths(store):
    fake = FakeAiClient(reply={"summary": "ส" * 900,
                               "why": ["ข" * 300, "ค" * 300,
                                       "ง" * 300, "จ" * 300]})
    result = build_advisor(store, fake).summarize(dict(SAMPLE_MOVIES[0]))
    assert len(result["summary"]) == 700
    assert [len(part) for part in result["why"]] == [160, 160, 160]


def test_summarize_without_ai_client_raises(store):
    advisor = build_advisor(store, None)
    with pytest.raises(AiError, match="not configured"):
        advisor.summarize(dict(SAMPLE_MOVIES[0]))


# ---------- Thai message mapping: advisor cases ----------


def test_describe_ai_error_no_candidates():
    error = AiError("no similar movies are available for this seed")
    assert "ยังมีข้อมูลไม่พอจะแนะนำ" in describe_ai_error(error)


def test_describe_ai_error_no_picks():
    error = AiError("the AI reply contains no usable picks")
    assert "คัดเลือกไม่ได้" in describe_ai_error(error)


def test_describe_ai_error_incomplete():
    error = AiError("the AI summary reply is incomplete")
    assert "ผิดรูปแบบ" in describe_ai_error(error)
