"""Tests for rate-limit cooldown tracking."""

import time


class TestCooldowns:
    def test_fresh_key_is_available(self, mod):
        cfg = {"keys": [{"provider": "gemini"}], "cooldowns": {}}
        assert mod.is_available(cfg, 0) is True

    def test_just_limited_key_is_unavailable(self, mod):
        cfg = {"keys": [{"provider": "gemini"}], "cooldowns": {"0": time.time()}}
        assert mod.is_available(cfg, 0) is False

    def test_expired_cooldown_is_available(self, mod):
        old_time = time.time() - mod.COOLDOWN_SECS - 1
        cfg = {"keys": [{"provider": "gemini"}], "cooldowns": {"0": old_time}}
        assert mod.is_available(cfg, 0) is True

    def test_mark_limited_persists(self, mod, tmp_path, monkeypatch):
        import os
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        cfg = {"keys": [{"provider": "gemini"}], "cooldowns": {}}
        mod.mark_limited(cfg, 0)

        assert "0" in cfg["cooldowns"]
        # Verify it was saved to disk
        loaded = mod.load_config()
        assert "0" in loaded["cooldowns"]

    def test_status_line_counts(self, mod):
        cfg = {
            "keys": [
                {"provider": "gemini"},
                {"provider": "gemini"},
                {"provider": "groq"},
            ],
            "cooldowns": {"0": time.time()},  # first gemini is limited
        }
        line = mod.status_line(cfg)
        assert "Gemini: 1/2" in line
        assert "Groq: 1/1" in line
