"""Repo-root paths. Keep snapshots and examples off the Python package internals."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "corpus"
MANIFEST_PATH = CORPUS_DIR / "manifest.json"
SNAPSHOT_DIR = CORPUS_DIR / "snapshots"
CACHE_DIR = CORPUS_DIR / ".cache"
AGENTS_DIR = ROOT / "agents"
EXAMPLES_DIR = ROOT / "examples"
SYSTEM_PATH = AGENTS_DIR / "SYSTEM.md"
