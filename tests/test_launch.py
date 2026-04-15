"""Tests for key selection logic."""

import time


class TestKeySelection:
    def test_skips_cooled_down(self, mod):
        cfg = {"gemini_keys": ["k1", "k2"], "groq_keys": [], "cooldowns": {"gemini:0": time.time()}}
        assert mod.is_available(cfg, "gemini", 0) is False
        assert mod.is_available(cfg, "gemini", 1) is True

    def test_all_ready_when_fresh(self, mod):
        cfg = {"gemini_keys": ["k1", "k2", "k3"], "groq_keys": ["g1"], "cooldowns": {}}
        line = mod.status_line(cfg)
        assert "Gemini: 3/3" in line
        assert "Groq: 1/1" in line

    def test_all_exhausted(self, mod):
        now = time.time()
        cfg = {"gemini_keys": ["k1", "k2"], "groq_keys": [], "cooldowns": {"gemini:0": now, "gemini:1": now}}
        assert "0/2" in mod.status_line(cfg)
