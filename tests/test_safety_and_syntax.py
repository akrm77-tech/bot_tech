from pathlib import Path
import py_compile
import unittest


class BotSafetyTests(unittest.TestCase):
    def setUp(self):
        self.source = Path(__file__).parents[1] / "src" / "main.py"
        self.text = self.source.read_text(encoding="utf-8")

    def test_source_compiles(self):
        py_compile.compile(str(self.source), doraise=True)

    def test_token_is_loaded_from_environment(self):
        self.assertIn('os.environ.get("BOT_TOKEN"', self.text)
        self.assertNotIn("8446461024:", self.text)


if __name__ == "__main__":
    unittest.main()
