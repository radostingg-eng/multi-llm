"""Tests for CLI launch logic — all fork/exec is mocked."""

import os


class TestLaunchSelection:
    def test_skips_cooled_down_gemini(self, mod):
        """Cooled-down keys should be skipped."""
        import time
        cfg = {
            "gemini_keys": ["k1", "k2"],
            "groq_keys": [],
            "cooldowns": {"gemini:0": time.time()},
        }
        # Key 0 is on cooldown, key 1 is available
        assert mod.is_available(cfg, "gemini", 0) is False
        assert mod.is_available(cfg, "gemini", 1) is True

    def test_all_exhausted_message(self, mod, capsys):
        """When everything is on cooldown, tell the user."""
        import time
        cfg = {
            "gemini_keys": ["k1"],
            "groq_keys": ["g1"],
            "cooldowns": {
                "gemini:0": time.time(),
                "groq:0": time.time(),
            },
        }
        # Both should be unavailable
        assert mod.is_available(cfg, "gemini", 0) is False
        assert mod.is_available(cfg, "groq", 0) is False

    def test_status_shows_all_ready_when_fresh(self, mod):
        cfg = {
            "gemini_keys": ["k1", "k2", "k3"],
            "groq_keys": ["g1", "g2"],
            "cooldowns": {},
        }
        line = mod.status_line(cfg)
        assert "Gemini: 3/3" in line
        assert "Groq: 2/2" in line
