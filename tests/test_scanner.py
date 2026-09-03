from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gx_migration_toolbox.cli import main
from gx_migration_toolbox.scanner import build_report, scan_source_tree


class ScannerTests(unittest.TestCase):
    def test_scans_supported_files_and_ignores_build_directories(self) -> None:
        with TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            (root / "src").mkdir()
            (root / "node_modules").mkdir()
            (root / "src" / "Example.java").write_text(
                "import legacy.runtime.Client;\npublic class Example {}\n",
                encoding="utf-8",
            )
            (root / "src" / "program.cs").write_text(
                "using System.Text;\npublic record Report(string Name);\n",
                encoding="utf-8",
            )
            (root / "node_modules" / "ignored.js").write_text(
                "function ignored() {}\n",
                encoding="utf-8",
            )

            files = scan_source_tree(root, runtime_patterns=["legacy.runtime."])
            report = build_report(root, files)

            self.assertEqual(report["summary"]["files"], 2)
            self.assertEqual(report["summary"]["runtime_references"], 1)
            self.assertEqual(files[0].imports, ["legacy.runtime.Client"])
            self.assertEqual(files[1].declarations, ["Report"])

    def test_cli_writes_json_report(self) -> None:
        with TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            source = root / "source"
            source.mkdir()
            (source / "schema.sql").write_text(
                "CREATE TABLE accounts (id INTEGER);\nSELECT * FROM accounts;\n",
                encoding="utf-8",
            )
            output = root / "reports" / "inventory.json"

            main(["scan", "--source", str(source), "--output", str(output)])

            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["files"], 1)
            self.assertEqual(payload["files"][0]["declarations"], ["accounts"])
            self.assertEqual(payload["files"][0]["imports"], ["accounts"])


if __name__ == "__main__":
    unittest.main()
