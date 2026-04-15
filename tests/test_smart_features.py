"""Tests for smart routing, prompt enhancement, and session summary."""

import json
import io
import os
import urllib.request


def _mock_groq(monkeypatch, content):
    """Helper: mock Groq API to return a specific response."""
    def fake_urlopen(req):
        body = json.dumps({"choices": [{"message": {"content": content}}]})
        return io.BytesIO(body.encode())
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)


class TestSmartRouting:
    def test_routes_simple_question(self, mod, monkeypatch):
        _mock_groq(monkeypatch, "SIMPLE")
        cfg = {"gemini_keys": [], "groq_keys": ["gsk_fake"], "cooldowns": {}}
        assert mod.route_query(cfg, "what is 2+2") == "simple"

    def test_routes_complex_question(self, mod, monkeypatch):
        _mock_groq(monkeypatch, "COMPLEX")
        cfg = {"gemini_keys": [], "groq_keys": ["gsk_fake"], "cooldowns": {}}
        assert mod.route_query(cfg, "refactor the auth module") == "complex"

    def test_no_groq_keys_returns_complex(self, mod):
        cfg = {"gemini_keys": ["k1"], "groq_keys": [], "cooldowns": {}}
        assert mod.route_query(cfg, "hello") == "complex"

    def test_groq_error_returns_complex(self, mod, monkeypatch):
        import urllib.error
        def fake_urlopen(req):
            raise urllib.error.HTTPError(req.full_url, 500, "err", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        cfg = {"gemini_keys": [], "groq_keys": ["gsk_fake"], "cooldowns": {}}
        assert mod.route_query(cfg, "hello") == "complex"


class TestPromptEnhancer:
    def test_enhances_prompt(self, mod, monkeypatch):
        enhanced = "Please explain what a mutex is and when to use one"
        _mock_groq(monkeypatch, enhanced)
        cfg = {"gemini_keys": [], "groq_keys": ["gsk_fake"], "cooldowns": {}}
        result = mod.enhance_prompt(cfg, "what is mutex")
        assert result == enhanced

    def test_no_groq_returns_original(self, mod):
        cfg = {"gemini_keys": ["k1"], "groq_keys": [], "cooldowns": {}}
        assert mod.enhance_prompt(cfg, "hello") == "hello"


class TestSessionSummary:
    def test_save_and_load_summary(self, mod, tmp_path, monkeypatch):
        summary_file = str(tmp_path / "summary.txt")
        monkeypatch.setattr(mod, "SUMMARY_FILE", summary_file)
        monkeypatch.setattr(mod, "CONFIG_DIR", str(tmp_path))

        mod.save_summary("We worked on the auth module and fixed a bug.")
        loaded = mod.load_summary()
        assert "auth module" in loaded

    def test_load_missing_returns_none(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "SUMMARY_FILE", str(tmp_path / "nope.txt"))
        assert mod.load_summary() is None
