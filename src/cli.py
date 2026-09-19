#!/usr/bin/env python3
"""VSO Agent CLI — chat copilot and packet assembler."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PATH = ROOT / "agents" / "SYSTEM.md"


def load_system() -> str:
    return SYSTEM_PATH.read_text(encoding="utf-8")


def run_chat(prompt: str) -> str:
    load_dotenv()
    from openai import OpenAI

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


def run_assemble(case_path: Path, output: Path | None) -> Path:
    from src.packet import load_case, write_packet

    case = load_case(case_path)
    dest = output
    if dest is None:
        dest = Path("packets") / f"{case_path.stem}-packet.md"
    return write_packet(case, dest)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VSO Agent local CLI")
    sub = parser.add_subparsers(dest="cmd")

    chat = sub.add_parser("chat", help="Freeform VSO copilot (needs a local or compatible model)")
    chat.add_argument("prompt", nargs="+", help="Intake notes or VSO question")

    assemble = sub.add_parser("assemble", help="Build cover sheet + evidence index + draft narrative")
    assemble.add_argument("case", type=Path, help="Path to case JSON")
    assemble.add_argument("-o", "--output", type=Path, help="Output markdown path")

    parser.add_argument("legacy_prompt", nargs="*", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "assemble":
        dest = run_assemble(args.case, args.output)
        print(dest)
        return
    if args.cmd == "chat":
        print(run_chat(" ".join(args.prompt)))
        return
    if args.legacy_prompt:
        print(run_chat(" ".join(args.legacy_prompt)))
        return
    parser.print_help()
    raise SystemExit(2)


if __name__ == "__main__":
    main()
