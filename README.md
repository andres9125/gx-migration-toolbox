# GX Migration Toolbox

[![Validation](https://github.com/andres9125/gx-migration-toolbox/actions/workflows/validation.yml/badge.svg)](https://github.com/andres9125/gx-migration-toolbox/actions/workflows/validation.yml)

GX Migration Toolbox is a local, read-only command-line utility for building a
portable source inventory before a modernization effort. It scans Java, C#,
JavaScript, CSS, and SQL files, then emits a JSON report with file counts,
imports, declarations, and configurable runtime-reference signals.

It never sends files to a service, modifies the scanned source tree, executes
source code, or generates replacement code.

## Why use it

- Establish a repeatable inventory of a legacy source tree.
- Identify imports and declarations before choosing a migration path.
- Flag references to platform-specific packages using your own patterns.
- Produce a small JSON artifact that can be reviewed, versioned, or consumed by
  another internal tool.

## Install

Python 3.10 or later is required.

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
~~~

## Scan a source tree

~~~powershell
gx-migration-toolbox scan --source C:\work\legacy-app --output reports\inventory.json --runtime-pattern "legacy.runtime." --runtime-pattern "vendor.framework."
~~~

The command prints a summary and writes the JSON report. Runtime patterns are
optional and are matched case-insensitively.

## Report shape

~~~json
{
  "schema_version": 1,
  "source_root": "C:/work/legacy-app",
  "summary": {
    "files": 42,
    "lines": 8200,
    "imports": 121,
    "declarations": 64,
    "runtime_references": 17
  },
  "languages": {
    "java": {"files": 18, "lines": 4300}
  },
  "files": []
}
~~~

The file-level list contains only relative paths and static analysis results.
Source text is never copied into the report.

## Supported files

| Language | Extensions |
| --- | --- |
| Java | .java |
| C# | .cs |
| JavaScript | .js, .mjs, .cjs |
| CSS | .css |
| SQL | .sql |

The scanner skips directories such as .git, .venv, node_modules, build, dist,
bin, and obj. Use a dedicated copy of a source tree if it contains files that
must not be analyzed.

## Limitations

This is a lightweight static inventory, not a parser or a correctness proof.
Regular-expression extraction can miss language constructs or report
approximate declarations. Treat its output as a planning aid and validate
important findings with the source owners.

## Development

~~~powershell
python -m unittest discover -s tests -v
python -m compileall -q src
~~~

See CONTRIBUTING.md and SECURITY.md before opening a pull request.

## License

Copyright 2026 Eximus. Licensed under [Apache-2.0](LICENSE).
