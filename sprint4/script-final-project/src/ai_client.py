"""AI provider client: JSON-only chat completions with explicit error handling.

The client follows the same shape as ``tmdb_client``: requests go through an
injectable session, the key is read from the environment, and every failure
mode raises ``AiError`` with a readable message.  ``describe_ai_error()``
maps those errors to the Thai wording shared by the presentation layers.
"""

import json

import requests

from .config import AI_BASE_URL, AI_MODEL, AI_TIMEOUT, get_ai_api_key


class AiError(Exception):
    """Raised when an AI request cannot be completed."""


class AiClient:
    """Minimal chat client for the AI provider used by this project.

    Talks to the provider's OpenAI-compatible ``/chat/completions``
    endpoint, disables thinking mode (answers stay fast and cheap), and
    forces a strict JSON object as the reply so callers can validate it.
    """

    def __init__(self, api_key=None, base_url=AI_BASE_URL, model=AI_MODEL,
                 timeout=AI_TIMEOUT, session=None):
        """Build a client; without ``api_key`` the environment is consulted."""
        self.api_key = api_key if api_key is not None else get_ai_api_key()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()

    def chat_json(self, system_prompt, user_prompt, max_tokens=800,
                  temperature=0):
        """Send one chat turn and return the parsed JSON reply as a dict.

        Raises ``AiError`` for every failure mode: network problems,
        auth failures, rate limits, timeouts, unexpected statuses, and
        replies that are missing or not a valid JSON object.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            raise AiError("the AI request timed out") from exc
        except requests.RequestException as exc:
            raise AiError(f"the AI request failed: {exc}") from exc

        if response.status_code == 401:
            raise AiError("the AI provider rejected the API key (HTTP 401)")
        if response.status_code == 429:
            raise AiError("the AI rate limit was hit (HTTP 429) - slow down")
        if response.status_code != 200:
            raise AiError(f"unexpected AI status {response.status_code}")

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except ValueError as exc:
            raise AiError("the AI provider returned invalid JSON") from exc
        except (KeyError, IndexError, TypeError) as exc:
            raise AiError("the AI response is missing a message") from exc

        try:
            answer = json.loads(content)
        except (ValueError, TypeError) as exc:
            raise AiError("the AI reply is not valid JSON") from exc
        if not isinstance(answer, dict):
            raise AiError("the AI reply must be a JSON object")
        return answer


def describe_ai_error(exc):
    """Map an AiError to a friendly Thai message (shared by the pages)."""
    message = str(exc)
    if "401" in message:
        return "คีย์ AI ไม่ถูกต้องหรือถูกปฏิเสธ (401) — ตรวจสอบค่า DEEPSEEK_API_KEY"
    if "429" in message:
        return "เรียกใช้บริการ AI ถี่เกินไป (429) — รอสักครู่แล้วลองใหม่"
    if "timed out" in message:
        return "เชื่อมต่อบริการ AI หมดเวลา — ลองใหม่อีกครั้ง"
    looks_bad = (
        "invalid JSON" in message
        or "not valid JSON" in message
        or "missing a message" in message
        or "JSON object" in message
    )
    if looks_bad:
        return "AI ตอบกลับผิดรูปแบบ — ลองใหม่อีกครั้ง"
    if "request failed" in message:
        return "เชื่อมต่อบริการ AI ไม่สำเร็จ — ตรวจสอบอินเทอร์เน็ตแล้วลองใหม่"
    return f"เชื่อมต่อบริการ AI ไม่สำเร็จ: {message}"
