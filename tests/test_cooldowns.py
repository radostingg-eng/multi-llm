"""Tests for rate-limit cooldown tracking."""

import os
import time


class TestCooldowns:
    def test_fresh_key_available(self, mod):
        cfg = {"keys": ["k"], "cooldowns": {}}
        assert mod.is_available(cfg, 0) is True

    def test_just_limited_unavailable(self, mod):
        cfg = {"keys": ["k"], "cooldowns": {"0": time.time()}}
        assert mod.is_available(cfg, 0) is False

    def test_expired_cooldown_available(self, mod):
        old = time.time() - mod.COOLDOWN_SECS - 1
        cfg = {"keys": ["k"], "cooldowns": {"0": old}}
        assert mod.is_available(cfg, 0) is True

    def test_mark_limited_persists(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        cfg = {"keys": ["k"], "cooldowns": {}}
        mod.mark_limited(cfg, 0)
        assert "0" in cfg["cooldowns"]
        assert "0" in mod.load_config()["cooldowns"]

    def test_status_line(self, mod):
        cfg = {"keys": ["k1", "k2", "k3"], "cooldowns": {"0": time.time()}}
        assert "2/3" in mod.status_line(cfg)
