"""Tests for cooldown tracking."""

import os
import time


class TestCooldowns:
    def test_fresh_key_available(self, mod):
        cfg = {"gemini_keys": ["k"], "groq_keys": [], "cooldowns": {}}
        assert mod.is_available(cfg, "gemini", 0) is True

    def test_just_limited_unavailable(self, mod):
        cfg = {"gemini_keys": ["k"], "groq_keys": [], "cooldowns": {"gemini:0": time.time()}}
        assert mod.is_available(cfg, "gemini", 0) is False

    def test_expired_cooldown_available(self, mod):
        old = time.time() - mod.COOLDOWN_SECS - 1
        cfg = {"gemini_keys": ["k"], "groq_keys": [], "cooldowns": {"gemini:0": old}}
        assert mod.is_available(cfg, "gemini", 0) is True

    def test_groq_cooldowns_independent(self, mod):
        cfg = {
            "gemini_keys": ["k"], "groq_keys": ["g"],
            "cooldowns": {"gemini:0": time.time()},
        }
        assert mod.is_available(cfg, "gemini", 0) is False
        assert mod.is_available(cfg, "groq", 0) is True

    def test_mark_limited_persists(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        cfg = {"gemini_keys": ["k"], "groq_keys": [], "cooldowns": {}}
        mod.mark_limited(cfg, "gemini", 0)
        loaded = mod.load_config()
        assert "gemini:0" in loaded["cooldowns"]

    def test_status_line(self, mod):
        cfg = {
            "gemini_keys": ["k1", "k2"],
            "groq_keys": ["g1"],
            "cooldowns": {"gemini:0": time.time()},
        }
        line = mod.status_line(cfg)
        assert "Gemini: 1/2" in line
        assert "Groq: 1/1" in line

    def test_get_groq_key_returns_available(self, mod):
        cfg = {"gemini_keys": [], "groq_keys": ["g1", "g2"], "cooldowns": {"groq:0": time.time()}}
        key, idx = mod.get_groq_key(cfg)
        assert key == "g2"
        assert idx == 1

    def test_get_groq_key_returns_none_when_exhausted(self, mod):
        now = time.time()
        cfg = {"gemini_keys": [], "groq_keys": ["g1"], "cooldowns": {"groq:0": now}}
        key, idx = mod.get_groq_key(cfg)
        assert key is None
