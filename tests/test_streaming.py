"""Tests for Gemini and Groq streaming — all HTTP mocked."""

import io
import json
import urllib.request
from unittest.mock import MagicMock, patch


def _fake_sse_response(chunks):
    """Build a fake SSE response from a list of text chunks."""
    lines = []
    for text in chunks:
        data = json.dumps({
            "candidates": [{"content": {"parts": [{"text": text}]}}]
        })
        lines.append(("data: %s\n" % data).encode())
    lines.append(b"data: [DONE]\n")
    return io.BytesIO(b"\n".join(lines))


def _fake_groq_sse_response(chunks):
    """Build a fake Groq SSE response."""
    lines = []
    for text in chunks:
        data = json.dumps({
            "choices": [{"delta": {"content": text}}]
        })
        lines.append(("data: %s\n" % data).encode())
    lines.append(b"data: [DONE]\n")
    return io.BytesIO(b"\n".join(lines))


class TestGeminiStream:
    def test_streams_text(self, mod, monkeypatch):
        fake_resp = _fake_sse_response(["Hello", " world"])
        monkeypatch.setattr(urllib.request, "urlopen", lambda req: fake_resp)

        messages = [{"role": "user", "content": "hi"}]
        text, code = mod.gemini_stream("fake-key", messages)
        assert code == 0
        assert text == "Hello world"

    def test_handles_429(self, mod, monkeypatch):
        import urllib.error
        def _raise_429(req):
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", _raise_429)

        text, code = mod.gemini_stream("fake-key", [{"role": "user", "content": "hi"}])
        assert code == 429
        assert text is None

    def test_handles_network_error(self, mod, monkeypatch):
        import urllib.error
        def _raise_url_error(req):
            raise urllib.error.URLError("Connection refused")
        monkeypatch.setattr(urllib.request, "urlopen", _raise_url_error)

        text, code = mod.gemini_stream("fake-key", [{"role": "user", "content": "hi"}])
        assert code == -1
        assert text is None

    def test_conversation_format(self, mod, monkeypatch):
        """Verify multi-turn messages are converted correctly."""
        captured = {}
        def _capture(req):
            captured["body"] = json.loads(req.data.decode())
            return _fake_sse_response(["ok"])
        monkeypatch.setattr(urllib.request, "urlopen", _capture)

        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"},
            {"role": "user", "content": "how are you"},
        ]
        mod.gemini_stream("key", messages)

        contents = captured["body"]["contents"]
        assert contents[0]["role"] == "user"
        assert contents[1]["role"] == "model"  # Gemini uses "model" not "assistant"
        assert contents[2]["role"] == "user"


class TestGroqStream:
    def test_streams_text(self, mod, monkeypatch):
        fake_resp = _fake_groq_sse_response(["Hello", " world"])
        monkeypatch.setattr(urllib.request, "urlopen", lambda req: fake_resp)

        messages = [{"role": "user", "content": "hi"}]
        text, code = mod.groq_stream("fake-key", messages)
        assert code == 0
        assert text == "Hello world"

    def test_handles_429(self, mod, monkeypatch):
        import urllib.error
        def _raise_429(req):
            raise urllib.error.HTTPError(req.full_url, 429, "Rate limit", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", _raise_429)

        text, code = mod.groq_stream("fake-key", [{"role": "user", "content": "hi"}])
        assert code == 429
        assert text is None


class TestSendMessage:
    def test_uses_first_available_key(self, mod, monkeypatch):
        """Should try the first key and succeed."""
        calls = []
        def _fake_gemini(api_key, messages):
            calls.append(api_key)
            return "response", 0
        monkeypatch.setattr(mod, "gemini_stream", _fake_gemini)

        passphrase = "test-pass"
        cfg = {
            "keys": [
                {"provider": "gemini", "encrypted": mod.encrypt_key("key-1", passphrase)},
                {"provider": "gemini", "encrypted": mod.encrypt_key("key-2", passphrase)},
            ],
            "cooldowns": {},
        }
        result = mod.send_message(cfg, passphrase, [{"role": "user", "content": "hi"}])
        assert result == "response"
        assert calls == ["key-1"]

    def test_rotates_on_429(self, mod, monkeypatch, tmp_path):
        """Should skip rate-limited key and try the next one."""
        import os
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        calls = []
        def _fake_gemini(api_key, messages):
            calls.append(api_key)
            if api_key == "key-1":
                return None, 429
            return "from key-2", 0
        monkeypatch.setattr(mod, "gemini_stream", _fake_gemini)

        passphrase = "test-pass"
        cfg = {
            "keys": [
                {"provider": "gemini", "encrypted": mod.encrypt_key("key-1", passphrase)},
                {"provider": "gemini", "encrypted": mod.encrypt_key("key-2", passphrase)},
            ],
            "cooldowns": {},
        }
        result = mod.send_message(cfg, passphrase, [{"role": "user", "content": "hi"}])
        assert result == "from key-2"
        assert calls == ["key-1", "key-2"]

    def test_falls_back_to_groq(self, mod, monkeypatch, tmp_path):
        """When all Gemini keys are limited, falls back to Groq."""
        import os
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        def _fail_gemini(api_key, messages):
            return None, 429
        def _ok_groq(api_key, messages):
            return "groq response", 0
        monkeypatch.setattr(mod, "gemini_stream", _fail_gemini)
        monkeypatch.setattr(mod, "groq_stream", _ok_groq)

        passphrase = "test-pass"
        cfg = {
            "keys": [
                {"provider": "gemini", "encrypted": mod.encrypt_key("g1", passphrase)},
                {"provider": "groq", "encrypted": mod.encrypt_key("gsk_1", passphrase)},
            ],
            "cooldowns": {},
        }
        result = mod.send_message(cfg, passphrase, [{"role": "user", "content": "hi"}])
        assert result == "groq response"

    def test_all_exhausted_returns_none(self, mod, monkeypatch, tmp_path):
        """When every key is rate-limited, returns None."""
        import os
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        def _fail(api_key, messages):
            return None, 429
        monkeypatch.setattr(mod, "gemini_stream", _fail)
        monkeypatch.setattr(mod, "groq_stream", _fail)

        passphrase = "test-pass"
        cfg = {
            "keys": [
                {"provider": "gemini", "encrypted": mod.encrypt_key("g1", passphrase)},
                {"provider": "groq", "encrypted": mod.encrypt_key("gsk_1", passphrase)},
            ],
            "cooldowns": {},
        }
        result = mod.send_message(cfg, passphrase, [{"role": "user", "content": "hi"}])
        assert result is None

    def test_skips_cooled_down_keys(self, mod, monkeypatch):
        """Keys on cooldown should be skipped entirely."""
        import time
        calls = []
        def _fake_gemini(api_key, messages):
            calls.append(api_key)
            return "ok", 0
        monkeypatch.setattr(mod, "gemini_stream", _fake_gemini)

        passphrase = "test-pass"
        cfg = {
            "keys": [
                {"provider": "gemini", "encrypted": mod.encrypt_key("key-1", passphrase)},
                {"provider": "gemini", "encrypted": mod.encrypt_key("key-2", passphrase)},
            ],
            "cooldowns": {"0": time.time()},  # key-1 is on cooldown
        }
        result = mod.send_message(cfg, passphrase, [{"role": "user", "content": "hi"}])
        assert result == "ok"
        assert calls == ["key-2"]  # skipped key-1
