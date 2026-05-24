import unittest
from pathlib import Path

from playground_server import DEMO_ROOT, build_command, parse_request, preview_changes


class ParseRequestTests(unittest.TestCase):
    def test_defaults_glob_and_resolves_root(self) -> None:
        req = parse_request(
            {
                "root": str(DEMO_ROOT),
                "find": "OldClass",
                "replace": "NewClass",
            }
        )

        self.assertEqual(req.root, DEMO_ROOT.resolve())
        self.assertEqual(req.glob, "*")
        self.assertFalse(req.dry_run)
        self.assertFalse(req.auto_yes)
        self.assertFalse(req.backup)

    def test_rejects_missing_find(self) -> None:
        with self.assertRaisesRegex(ValueError, "Find pattern is required"):
            parse_request({"root": str(DEMO_ROOT), "replace": "NewClass"})

    def test_rejects_bad_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "Root does not exist"):
            parse_request(
                {
                    "root": str(DEMO_ROOT / "missing"),
                    "find": "OldClass",
                    "replace": "NewClass",
                }
            )


class BuildCommandTests(unittest.TestCase):
    def test_includes_selected_flags(self) -> None:
        req = parse_request(
            {
                "root": str(DEMO_ROOT),
                "glob": "*.md",
                "find": "v1.0.0",
                "replace": "v1.1.0",
                "dry_run": True,
                "auto_yes": True,
                "backup": True,
            }
        )

        command = build_command(req)

        self.assertIn("far -n -y -b", command)
        self.assertIn("'*.md'", command)


class PreviewChangesTests(unittest.TestCase):
    def test_rename_preview_uses_demo_files(self) -> None:
        req = parse_request(
            {
                "root": str(DEMO_ROOT),
                "glob": "*.cpp",
                "find": "OldClass",
                "replace": "NewClass",
            }
        )

        preview = preview_changes(req)

        self.assertEqual(
            preview["matched_files"],
            ["src/Widget.cpp", "src/Parser.cpp"],
        )
        self.assertEqual(
            preview["changed_files"],
            ["src/Widget.cpp", "src/Parser.cpp"],
        )
        self.assertIn("NewClass Widget::Build", preview["sample_diffs"][0]["diff"])
        self.assertIsNone(preview["error"])

    def test_banner_preview_supports_capture_group(self) -> None:
        req = parse_request(
            {
                "root": str(DEMO_ROOT),
                "glob": "*.cpp",
                "find": "// -- (.*) -+$",
                "replace": "// \\1",
            }
        )

        preview = preview_changes(req)
        diffs = "\n".join(item["diff"] for item in preview["sample_diffs"])

        self.assertIn("// Parser implementation", diffs)
        self.assertIn("// Character access", diffs)
        self.assertNotIn("// \\1", diffs)

    def test_no_match_preview_is_empty(self) -> None:
        req = parse_request(
            {
                "root": str(DEMO_ROOT),
                "glob": "*.txt",
                "find": "nothing-here",
                "replace": "still-nothing",
            }
        )

        preview = preview_changes(req)

        self.assertEqual(preview["matched_files"], [])
        self.assertEqual(preview["changed_files"], [])
        self.assertEqual(preview["sample_diffs"], [])
        self.assertFalse(preview["truncated"])


if __name__ == "__main__":
    unittest.main()
