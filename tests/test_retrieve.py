import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.retrieve import host_allowed, load_manifest, search


class RetrieveTests(unittest.TestCase):
    def test_manifest_snapshots_exist(self) -> None:
        missing = []
        for source in load_manifest():
            if source.snapshot and not (ROOT / source.snapshot).is_file():
                missing.append(source.id)
        self.assertEqual(missing, [], f"manifest points at missing snapshots: {missing}")

    def test_tinnitus_hits_ear_or_hearing_source(self) -> None:
        hits = search("tinnitus hearing loss artillery MOS", k=5)
        self.assertTrue(hits)
        ids = {h.source.id for h in hits}
        self.assertTrue(
            ids & {"38cfr-4.87", "38cfr-3.385", "m21-1-auditory"},
            f"expected an auditory source, got {ids}",
        )
        self.assertTrue(all(h.source.official_url for h in hits))

    def test_allowlist_rejects_random_host(self) -> None:
        self.assertFalse(host_allowed("https://example.com/secret"))
        self.assertTrue(host_allowed("https://www.va.gov/disability/"))


if __name__ == "__main__":
    unittest.main()
