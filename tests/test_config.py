"""Tests for config load/save and key import."""

import json
import os


class TestConfig:
    def test_save_and_load(self, mod, tmp_path, monkeypatch):
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        cfg = {"keys": [{"provider": "gemini", "encrypted": "abc"}], "cooldowns": {}}
        mod.save_config(cfg)

        loaded = mod.load_config()
        assert loaded == cfg

    def test_load_missing_returns_none(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "CONFIG_FILE", str(tmp_path / "nope.json"))
        assert mod.load_config() is None

    def test_config_file_permissions_unix(self, mod, tmp_path, monkeypatch):
        if os.name == "nt":
            return  # skip on Windows
        cfg_dir = str(tmp_path / ".multi-llm")
        cfg_file = os.path.join(cfg_dir, "config.json")
        monkeypatch.setattr(mod, "CONFIG_DIR", cfg_dir)
        monkeypatch.setattr(mod, "CONFIG_FILE", cfg_file)

        mod.save_config({"keys": []})
        perms = oct(os.stat(cfg_file).st_mode & 0o777)
        assert perms == "0o600"


class TestImportEnvKeys:
    @staticmethod
    def _clear_llm_env(monkeypatch):
        """Remove any real GEMINI/GROQ keys so tests are isolated."""
        for var in list(os.environ.keys()):
            if var.startswith("GEMINI_API_KEY") or var.startswith("GROQ_API_KEY"):
                monkeypatch.delenv(var)

    def test_imports_gemini_keys(self, mod, monkeypatch):
        self._clear_llm_env(monkeypatch)
        monkeypatch.setenv("GEMINI_API_KEY", "key1")
        monkeypatch.setenv("GEMINI_API_KEY_2", "key2")

        cfg = {"keys": []}
        count = mod._import_env_keys(cfg, "pass")
        assert count == 2
        assert all(k["provider"] == "gemini" for k in cfg["keys"])

    def test_imports_groq_keys(self, mod, monkeypatch):
        self._clear_llm_env(monkeypatch)
        monkeypatch.setenv("GROQ_API_KEY", "gsk_abc")
        monkeypatch.setenv("GROQ_API_KEY_2", "gsk_def")

        cfg = {"keys": []}
        count = mod._import_env_keys(cfg, "pass")
        assert count == 2
        assert all(k["provider"] == "groq" for k in cfg["keys"])

    def test_imports_mixed_keys(self, mod, monkeypatch):
        self._clear_llm_env(monkeypatch)
        monkeypatch.setenv("GEMINI_API_KEY", "g1")
        monkeypatch.setenv("GROQ_API_KEY", "gsk_1")

        cfg = {"keys": []}
        count = mod._import_env_keys(cfg, "pass")
        assert count == 2

    def test_skips_empty_values(self, mod, monkeypatch):
        self._clear_llm_env(monkeypatch)
        monkeypatch.setenv("GEMINI_API_KEY", "")

        cfg = {"keys": []}
        count = mod._import_env_keys(cfg, "pass")
        assert count == 0

    def test_imported_keys_are_decryptable(self, mod, monkeypatch):
        self._clear_llm_env(monkeypatch)
        monkeypatch.setenv("GEMINI_API_KEY", "my-secret-key")

        cfg = {"keys": []}
        mod._import_env_keys(cfg, "test-pass")
        decrypted = mod.decrypt_key(cfg["keys"][0]["encrypted"], "test-pass")
        assert decrypted == "my-secret-key"
