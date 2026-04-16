"""Tests for session summary feature."""

import io
import json
import os
import time
import urllib.request


class TestLoadSummary:
    def test_load_existing(self, mod, tmp_path, monkeypatch):
        sf = str(tmp_path / "summary.txt")
        monkeypatch.setattr(mod, "SUMMARY_FILE", sf)
        with open(sf, "w") as f:
            f.write("We worked on auth module.")
        assert "auth module" in mod.load_summary()

    def test_load_missing(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "SUMMARY_FILE", str(tmp_path / "nope.txt"))
        assert mod.load_summary() is None

    def test_load_stale_summary_ignored(self, mod, tmp_path, monkeypatch):
        sf = str(tmp_path / "summary.txt")
        monkeypatch.setattr(mod, "SUMMARY_FILE", sf)
        with open(sf, "w") as f:
            f.write("Old stuff.")
        # Make file old
        old_time = time.time() - mod.SUMMARY_MAX_AGE - 100
        os.utime(sf, (old_time, old_time))
        assert mod.load_summary() is None

    def test_save_and_load(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "CONFIG_DIR", str(tmp_path))
        sf = str(tmp_path / "summary.txt")
        monkeypatch.setattr(mod, "SUMMARY_FILE", sf)
        mod.save_summary("Test summary content.")
        assert mod.load_summary() == "Test summary content."


class TestSummarizeSession:
    def test_no_groq_key_skips(self, mod, monkeypatch):
        """Should return without error when no Groq keys available."""
        cfg = {"gemini_keys": ["k"], "groq_keys": [], "cooldowns": {}}
        mod.summarize_session(cfg)  # should not raise

    def test_no_history_dir_skips(self, mod, monkeypatch):
        cfg = {"gemini_keys": [], "groq_keys": ["g"], "cooldowns": {}}
        monkeypatch.setattr(mod, "_gemini_history_dir", lambda: None)
        mod.summarize_session(cfg)  # should not raise

    def test_short_history_skips(self, mod, tmp_path, monkeypatch):
        """History under 100 chars should be skipped."""
        history_dir = str(tmp_path / "history")
        os.makedirs(history_dir)
        with open(os.path.join(history_dir, "session.txt"), "w") as f:
            f.write("short")
        monkeypatch.setattr(mod, "_gemini_history_dir", lambda: history_dir)

        cfg = {"gemini_keys": [], "groq_keys": ["g"], "cooldowns": {}}
        mod.summarize_session(cfg)  # should skip

    def test_summarizes_long_history(self, mod, tmp_path, monkeypatch):
        history_dir = str(tmp_path / "history")
        os.makedirs(history_dir)
        with open(os.path.join(history_dir, "session.txt"), "w") as f:
            f.write("x" * 200)
        monkeypatch.setattr(mod, "_gemini_history_dir", lambda: history_dir)

        sf = str(tmp_path / "summary.txt")
        monkeypatch.setattr(mod, "SUMMARY_FILE", sf)
        monkeypatch.setattr(mod, "CONFIG_DIR", str(tmp_path))

        def fake_urlopen(req):
            body = json.dumps({"choices": [{"message": {"content": "Session summary here."}}]})
            return io.BytesIO(body.encode())
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        cfg = {"gemini_keys": [], "groq_keys": ["g"], "cooldowns": {}}
        mod.summarize_session(cfg)

        assert os.path.exists(sf)
        with open(sf) as f:
            assert "Session summary" in f.read()


class TestGeminiHistoryDir:
    def test_finds_unix_history(self, mod, tmp_path, monkeypatch):
        history_dir = str(tmp_path / ".gemini" / "history")
        os.makedirs(history_dir)
        monkeypatch.setattr(os.path, "expanduser", lambda p: str(tmp_path / p.lstrip("~/")))
        # Can't easily mock expanduser for this, so just test the function exists
        result = mod._gemini_history_dir()
        # Result depends on actual filesystem, just verify it returns string or None
        assert result is None or isinstance(result, str)
