"""Tests for key validation and setup checks."""

import io
import os
import urllib.request


class TestGeminiValidation:
    def test_valid_key(self, mod, monkeypatch):
        def fake_urlopen(req, timeout=None):
            return io.BytesIO(b'{"models": []}')
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_gemini_key("AIza-good") is True

    def test_invalid_key(self, mod, monkeypatch):
        import urllib.error
        def fake_urlopen(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 400, "bad", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_gemini_key("bad-key") is False

    def test_network_error(self, mod, monkeypatch):
        import urllib.error
        def fake_urlopen(req, timeout=None):
            raise urllib.error.URLError("no internet")
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_gemini_key("key") is False


class TestGroqValidation:
    def test_valid_key(self, mod, monkeypatch):
        def fake_urlopen(req, timeout=None):
            return io.BytesIO(b'{"data": []}')
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_groq_key("gsk_good") is True

    def test_invalid_key(self, mod, monkeypatch):
        import urllib.error
        def fake_urlopen(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 401, "unauth", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert mod.validate_groq_key("bad-key") is False


class TestDuplicateKeys:
    def test_detects_duplicate(self, mod):
        assert mod._is_duplicate_key("key1", ["key1", "key2"]) is True

    def test_allows_new_key(self, mod):
        assert mod._is_duplicate_key("key3", ["key1", "key2"]) is False


class TestGeminiCLICheck:
    def test_gemini_found(self, mod, monkeypatch):
        import shutil
        monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/gemini")
        assert mod.check_gemini_cli() is True

    def test_gemini_not_found(self, mod, monkeypatch):
        import shutil
        monkeypatch.setattr(shutil, "which", lambda cmd: None)
        assert mod.check_gemini_cli() is False
