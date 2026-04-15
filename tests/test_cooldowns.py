"""Tests for rate-limit cooldown tracking."""

import os
import time


class TestCooldowns:
    def test_fresh_key_is_available(self, mod):
        cfg = {"gemini_keys": ["k"], "cooldowns": {}}
        assert mod.is_available(cfg, "gemini", 0) is True

    def test_just_limited_key_is_unavailable(self, mod):
        cfg = {"gemini_keys": ["k"], "cooldowns": {"gemini:0": time.time()}}
        assert mod.is_available(cfg, "gemini", 0) is False

    def test_expired_cooldown_is_available(self, mod):
        old = time.time() - mod.COOLDOWN_SECS - 1
        cfg = {"gemini_keys": ["k"], "cooldowns": {"gemini:0": old}}
        assert mod.is_available(cfg, "gemini", 0) is True

    def test_mark_limited_persists(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        cfg = {"gemini_keys": ["k"], "groq_keys": [], "cooldowns": {}}
        mod.mark_limited(cfg, "gemini", 0)

        assert "gemini:0" in cfg["cooldowns"]
        loaded = mod.load_config()
        assert "gemini:0" in loaded["cooldowns"]

    def test_status_line_counts(self, mod):
        cfg = {
            "gemini_keys": ["k1", "k2"],
            "groq_keys": ["g1"],
            "cooldowns": {"gemini:0": time.time()},
        }
        line = mod.status_line(cfg)
        assert "Gemini: 1/2" in line
        assert "Groq: 1/1" in line
