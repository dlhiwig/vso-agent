import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.packet import PacketError, assemble, case_from_dict, load_case, readiness


class PacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = load_case(ROOT / "examples" / "sample-case.json")

    def test_sample_is_not_file_ready(self) -> None:
        ready = readiness(self.case)
        self.assertFalse(ready["file_ready"])
        self.assertGreater(ready["blocking"], 0)

    def test_draft_banner_and_hypothesized_knee(self) -> None:
        text = assemble(self.case)
        self.assertIn("DRAFT — VSO REVIEW REQUIRED", text)
        self.assertIn("Bilateral knee condition", text)
        self.assertIn("hypothesized", text)
        self.assertIn("NOT FILE-READY", text)
        self.assertNotRegex(text.lower(), r"\bssn\b")

    def test_rejects_bad_evidence_status(self) -> None:
        raw = json.loads((ROOT / "examples" / "sample-case.json").read_text(encoding="utf-8"))
        raw["evidence"][0]["status"] = "on-my-desk"
        with self.assertRaises(PacketError):
            case_from_dict(raw)

    def test_write_roundtrip(self) -> None:
        from src.packet import write_packet

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.md"
            write_packet(self.case, dest)
            self.assertTrue(dest.exists())
            self.assertIn("Evidence index", dest.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
