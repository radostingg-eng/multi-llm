"""Tests for config load/save."""

import os


class TestConfig:
    def test_save_and_load(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        cfg = {"keys": ["key1", "key2"], "cooldowns": {}}
        mod.save_config(cfg)
        assert mod.load_config() == cfg

    def test_load_missing_returns_none(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "CONFIG_FILE", str(tmp_path / "nope.json"))
        assert mod.load_config() is None

    def test_file_permissions(self, mod, tmp_path, monkeypatch):
        if os.name == "nt":
            return
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        mod.save_config({"keys": []})
        assert oct(os.stat(cfg_file).st_mode & 0o777) == "0o600"
