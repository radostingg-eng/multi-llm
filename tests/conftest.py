"""
Global test fixtures for multi-llm.

Guardrails:
- os.fork is blocked (no real CLI launches in tests)
- subprocess.call is blocked (no real git/CLI calls)
"""

import os
import pytest


@pytest.fixture(autouse=True)
def _block_fork(monkeypatch):
    """Prevent tests from forking real CLI processes."""
    if hasattr(os, "fork"):
        monkeypatch.setattr(os, "fork", lambda: (_ for _ in ()).throw(
            RuntimeError("Test tried to fork — mock it!")))


@pytest.fixture(autouse=True)
def _block_subprocess(monkeypatch):
    """Prevent real subprocess calls."""
    import subprocess
    monkeypatch.setattr(subprocess, "call", lambda *a, **kw: 0)


@pytest.fixture
def mod():
    """Import the multi-llm module for testing."""
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
