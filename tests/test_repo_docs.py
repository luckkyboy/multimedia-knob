import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class RepoDocsTests(unittest.TestCase):
    def test_gitignore_covers_idea_and_pycache(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(".idea/", gitignore)
        self.assertIn("__pycache__/", gitignore)

    def test_readme_mentions_dependency_and_boot_sections(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Dependencies", readme)
        self.assertIn("## Boot behavior", readme)
        self.assertIn("## Troubleshooting", readme)
        self.assertIn("CircuitPython 9.2.2", readme)


if __name__ == "__main__":
    unittest.main()
