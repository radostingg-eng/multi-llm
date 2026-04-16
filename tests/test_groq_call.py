"""Tests for groq_call including error handling."""

import io
import json
import urllib.request
import urllib.error


class TestGroqCallNonStreaming:
    def test_success(self, mod, monkeypatch):
        def fake_urlopen(req):
            body = json.dumps({"choices": [{"message": {"content": "hello"}}]})
            return io.BytesIO(body.encode())
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}])
        assert code == 0
        assert text == "hello"

    def test_malformed_json(self, mod, monkeypatch):
        def fake_urlopen(req):
            return io.BytesIO(b"not json at all")
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}])
        assert code == -2
        assert text is None

    def test_missing_fields(self, mod, monkeypatch):
        def fake_urlopen(req):
            return io.BytesIO(json.dumps({"unexpected": "format"}).encode())
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}])
        assert code == -2
        assert text is None

    def test_429_rate_limit(self, mod, monkeypatch):
        def fake_urlopen(req):
            raise urllib.error.HTTPError(req.full_url, 429, "limit", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}])
        assert code == 429
        assert text is None

    def test_500_server_error(self, mod, monkeypatch):
        def fake_urlopen(req):
            raise urllib.error.HTTPError(req.full_url, 500, "err", {}, io.BytesIO(b""))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}])
        assert code == 500

    def test_network_error(self, mod, monkeypatch):
        def fake_urlopen(req):
            raise urllib.error.URLError("connection refused")
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}])
        assert code == -1


class TestGroqCallStreaming:
    def test_success(self, mod, monkeypatch):
        lines = []
        for text in ["Hello", " world"]:
            data = json.dumps({"choices": [{"delta": {"content": text}}]})
            lines.append(("data: %s\n" % data).encode())
        lines.append(b"data: [DONE]\n")

        def fake_urlopen(req):
            return io.BytesIO(b"\n".join(lines))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}], stream=True)
        assert code == 0
        assert text == "Hello world"

    def test_garbled_stream(self, mod, monkeypatch):
        """Malformed SSE lines should be skipped, not crash."""
        lines = [
            b"data: not-json\n",
            b"data: {}\n",
            b"data: [DONE]\n",
        ]
        def fake_urlopen(req):
            return io.BytesIO(b"\n".join(lines))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        text, code = mod.groq_call("key", [{"role": "user", "content": "hi"}], stream=True)
        assert code == 0
        assert text == ""  # no content extracted, but no crash


class TestLaunchGemini:
    def test_gemini_not_installed(self, mod, monkeypatch):
        import shutil
        monkeypatch.setattr(shutil, "which", lambda cmd: None)
        code = mod.launch_gemini("key", [])
        assert code == 127

    def test_gemini_installed_but_fork_blocked(self, mod, monkeypatch):
        """Fork is blocked by conftest, so launch should raise."""
        import shutil
        monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/gemini")
        # fork is blocked by conftest autouse fixture — this tests the guard works
        try:
            mod.launch_gemini("key", [])
            assert False, "Should have raised"
        except RuntimeError:
            pass  # expected — fork blocked


class TestConfigCorruption:
    def test_missing_fields_filled(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        os.makedirs(cfg_dir)
        with open(cfg_file, "w") as f:
            json.dump({"gemini_keys": ["k1"]}, f)  # missing groq_keys and cooldowns

        cfg = mod.load_config()
        assert cfg["groq_keys"] == []
        assert cfg["cooldowns"] == {}

    def test_corrupt_json_returns_none(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        os.makedirs(cfg_dir)
        with open(cfg_file, "w") as f:
            f.write("not json{{{")

        assert mod.load_config() is None


import os
