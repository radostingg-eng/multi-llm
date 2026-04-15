"""
Global test fixtures for multi-llm.

Guardrails:
- os.fork is blocked (no real CLI launches)
- subprocess.call is blocked (no real git calls)
- urllib is blocked (no real API calls)
"""

import os
import urllib.request
import pytest


@pytest.fixture(autouse=True)
def _block_fork(monkeypatch):
    if hasattr(os, "fork"):
        monkeypatch.setattr(os, "fork", lambda: (_ for _ in ()).throw(
            RuntimeError("Test tried to fork — mock it!")))


@pytest.fixture(autouse=True)
def _block_subprocess(monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess, "call", lambda *a, **kw: 0)


@pytest.fixture(autouse=True)
def _block_http(monkeypatch):
    def _blocked(*a, **kw):
        raise RuntimeError("Test tried to make HTTP request — mock it!")
    monkeypatch.setattr(urllib.request, "urlopen", _blocked)


@pytest.fixture
def mod():
    """Import the multi-llm module."""
    import importlib.util
    import importlib.machinery
    filepath = os.path.join(os.path.dirname(__file__), "..", "multi-llm")
    loader = importlib.machinery.SourceFileLoader("multi_llm", filepath)
    spec = importlib.util.spec_from_loader("multi_llm", loader)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules["multi_llm"] = module
    spec.loader.exec_module(module)
    return module
