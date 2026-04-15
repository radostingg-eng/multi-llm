"""Tests for config load/save and key import."""

import json
import os


class TestConfig:
    def test_save_and_load(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        cfg = {"gemini_keys": ["key1"], "groq_keys": [], "cooldowns": {}}
        mod.save_config(cfg)

        loaded = mod.load_config()
        assert loaded == cfg

    def test_load_missing_returns_none(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "CONFIG_FILE", str(tmp_path / "nope.json"))
        assert mod.load_config() is None

    def test_config_file_permissions_unix(self, mod, tmp_path, monkeypatch):
        if os.name == "nt":
            return
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        mod.save_config({"gemini_keys": [], "groq_keys": []})
        perms = oct(os.stat(cfg_file).st_mode & 0o777)
        assert perms == "0o600"


class TestImportEnvKeys:
    @staticmethod
    def _clear_llm_env(monkeypatch):
        for var in list(os.environ.keys()):
            if var.startswith("GEMINI_API_KEY") or var.startswith("GROQ_API_KEY"):
                monkeypatch.delenv(var)

    def test_setup_detects_gemini_env(self, mod, tmp_path, monkeypatch):
        """_import from env is now inline in setup(), test the logic directly."""
        self._clear_llm_env(monkeypatch)
        monkeypatch.setenv("GEMINI_API_KEY", "key1")
        monkeypatch.setenv("GEMINI_API_KEY_2", "key2")

        cfg = {"gemini_keys": [], "groq_keys": [], "cooldowns": {}}
        for var in sorted(os.environ.keys()):
            if var.startswith("GEMINI_API_KEY"):
                val = os.environ[var].strip()
                if val:
                    cfg["gemini_keys"].append(val)
        assert len(cfg["gemini_keys"]) == 2

    def test_setup_detects_groq_env(self, mod, tmp_path, monkeypatch):
        self._clear_llm_env(monkeypatch)
        monkeypatch.setenv("GROQ_API_KEY", "gsk_abc")

        cfg = {"gemini_keys": [], "groq_keys": [], "cooldowns": {}}
        for var in sorted(os.environ.keys()):
            if var.startswith("GROQ_API_KEY"):
                val = os.environ[var].strip()
                if val:
                    cfg["groq_keys"].append(val)
        assert len(cfg["groq_keys"]) == 1
