import tempfile
import unittest
from pathlib import Path

from prepare_upstream import MARKER, publish


class PublishTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.source = root / "staging"
        self.source.mkdir()
        (self.source / MARKER).write_text("{}")
        (self.source / "payload").write_text("new")
        self.target = root / "output"
        self.target.mkdir()

    def test_accepts_empty_gradle_output_directory(self):
        publish(self.source, self.target)
        self.assertEqual((self.target / "payload").read_text(), "new")
        self.assertFalse(self.source.exists())

    def test_preserves_unmanaged_nonempty_directory(self):
        user_file = self.target / "user-data"
        user_file.write_text("keep")
        with self.assertRaisesRegex(ValueError, "unmanaged directory"):
            publish(self.source, self.target)
        self.assertEqual(user_file.read_text(), "keep")
        self.assertEqual((self.source / "payload").read_text(), "new")

    def test_replaces_previously_generated_directory(self):
        (self.target / MARKER).write_text("{}")
        (self.target / "stale").write_text("old")
        publish(self.source, self.target)
        self.assertEqual((self.target / "payload").read_text(), "new")
        self.assertFalse((self.target / "stale").exists())


if __name__ == "__main__":
    unittest.main()
