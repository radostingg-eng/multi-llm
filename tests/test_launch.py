"""Tests for key selection logic."""

import time


class TestKeySelection:
    def test_skips_cooled_down(self, mod):
        cfg = {"keys": ["k1", "k2"], "cooldowns": {"0": time.time()}}
        assert mod.is_available(cfg, 0) is False
        assert mod.is_available(cfg, 1) is True

    def test_all_ready_when_fresh(self, mod):
        cfg = {"keys": ["k1", "k2", "k3"], "cooldowns": {}}
        assert "3/3" in mod.status_line(cfg)

    def test_all_exhausted(self, mod):
        now = time.time()
        cfg = {"keys": ["k1", "k2"], "cooldowns": {"0": now, "1": now}}
        assert "0/2" in mod.status_line(cfg)
