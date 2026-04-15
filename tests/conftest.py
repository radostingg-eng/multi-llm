"""
Global test fixtures for multi-llm.

Guardrails:
- All HTTP calls are blocked (no real API hits in tests)
- getpass is mocked (no interactive prompts during tests)
"""

import json
import urllib.request
from unittest.mock import MagicMock

import pytest

# ── Block all HTTP calls ─────────────────────────────────────────────────────

_original_urlopen = urllib.request.urlopen


@pytest.fixture(autouse=True)
def _block_http(monkeypatch):
    """Prevent any real HTTP requests from tests."""
    def _blocked(*args, **kwargs):
        raise RuntimeError("Test tried to make a real HTTP request — mock it!")
    monkeypatch.setattr(urllib.request, "urlopen", _blocked)


# ── Block getpass (no interactive prompts) ───────────────────────────────────

@pytest.fixture(autouse=True)
def _block_getpass(monkeypatch):
    """Prevent getpass from blocking on input."""
    import getpass as gp
    monkeypatch.setattr(gp, "getpass", lambda prompt="": "test-passphrase")


# ── Helpers ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_config(tmp_path):
    """Create a temporary config directory and return (config_dir, config_file)."""
    config_dir = str(tmp_path / ".multi-llm")
    config_file = str(tmp_path / ".multi-llm" / "config.json")
    return config_dir, config_file


@pytest.fixture
def sample_config(tmp_path):
    """Return a pre-built config dict with 2 gemini + 1 groq key, encrypted."""
    # Import inline to avoid module-level issues
    import importlib.util
    import importlib.machinery
    import os
    filepath = os.path.join(os.path.dirname(__file__), "..", "multi-llm")
    loader = importlib.machinery.SourceFileLoader("multi_llm", filepath)
    spec = importlib.util.spec_from_loader("multi_llm", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    passphrase = "test-passphrase"
    return {
        "keys": [
            {"provider": "gemini", "encrypted": mod.encrypt_key("AIza-fake-key-1", passphrase)},
            {"provider": "gemini", "encrypted": mod.encrypt_key("AIza-fake-key-2", passphrase)},
            {"provider": "groq", "encrypted": mod.encrypt_key("gsk_fake-groq-key", passphrase)},
        ],
        "cooldowns": {},
        "check": mod.encrypt_key("multi-llm-check", passphrase),
    }


@pytest.fixture
def mod():
    """Import the multi-llm module for testing."""
    import importlib.util
    import importlib.machinery
    import os
    filepath = os.path.join(os.path.dirname(__file__), "..", "multi-llm")
    loader = importlib.machinery.SourceFileLoader("multi_llm", filepath)
    spec = importlib.util.spec_from_loader("multi_llm", loader)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules["multi_llm"] = module
    spec.loader.exec_module(module)
    return module
