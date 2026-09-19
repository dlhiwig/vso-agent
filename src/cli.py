#!/usr/bin/env python3
"""Minimal local runner for VSO Agent."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PATH = ROOT / "agents" / "SYSTEM.md"


def load_system() -> str:
    return SYSTEM_PATH.read_text(encoding="utf-8")


def run(prompt: str) -> str:
    load_dotenv()
    client = OpenAI(
        base_url=os.getenv("VSO_AGENT_BASE_URL", "http://127.0.0.1:11434/v1"),
        api_key=os.getenv("VSO_AGENT_API_KEY", "ollama"),
    )
    model = os.getenv("VSO_AGENT_MODEL", "llama3.1")
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": load_system()},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content or ""


def main() -> None:
    parser = argparse.ArgumentParser(description="VSO Agent local CLI")
    parser.add_argument("prompt", nargs="+", help="Intake notes or VSO question")
    args = parser.parse_args()
    print(run(" ".join(args.prompt)))


if __name__ == "__main__":
    main()
