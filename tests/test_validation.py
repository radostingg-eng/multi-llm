"""Tests for key validation."""

import io
import json
import urllib.request


class TestValidation:
    def test_gemini_valid_key(self, mod, monkeypatch):
        def fake_urlopen(req, timeout=None):
            return io.BytesIO(b'{"models": []}')
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_gemini_key("AIza-good") is True

    def test_gemini_invalid_key(self, mod, monkeypatch):
        import urllib.error
        def fake_urlopen(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 400, "bad", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_gemini_key("bad-key") is False

    def test_groq_valid_key(self, mod, monkeypatch):
        def fake_urlopen(req, timeout=None):
            return io.BytesIO(b'{"data": []}')
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_groq_key("gsk_good") is True

    def test_groq_invalid_key(self, mod, monkeypatch):
        import urllib.error
        def fake_urlopen(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 401, "unauth", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_groq_key("bad-key") is False

    def test_network_error_returns_false(self, mod, monkeypatch):
        import urllib.error
        def fake_urlopen(req, timeout=None):
            raise urllib.error.URLError("no internet")
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_gemini_key("key") is False
        assert mod.validate_groq_key("key") is False
