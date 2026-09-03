from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Iterable


LANGUAGE_BY_SUFFIX = {
    ".java": "java",
    ".cs": "csharp",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".css": "css",
    ".sql": "sql",
}
DEFAULT_IGNORED_DIRECTORIES = frozenset(
    {".git", ".venv", "venv", "node_modules", "build", "dist", "bin", "obj", "__pycache__"}
)


@dataclass(frozen=True, slots=True)
class FileInventory:
    path: str
    language: str
    lines: int
    imports: list[str]
    declarations: list[str]
    runtime_references: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def scan_source_tree(
    source_root: Path,
    *,
    runtime_patterns: Iterable[str] = (),
    max_file_size_mb: int = 5,
) -> list[FileInventory]:
    root = source_root.resolve()
    if not root.is_dir():
        raise ValueError(f"Source directory does not exist: {source_root}")
    if max_file_size_mb < 1:
        raise ValueError("max_file_size_mb must be at least 1")

    patterns = tuple(pattern.strip() for pattern in runtime_patterns if pattern.strip())
    max_bytes = max_file_size_mb * 1024 * 1024
    results: list[FileInventory] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(part in DEFAULT_IGNORED_DIRECTORIES for part in relative.parts):
            continue
        language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
        if language is None or path.stat().st_size > max_bytes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        results.append(
            FileInventory(
                path=relative.as_posix(),
                language=language,
                lines=line_count(text),
                imports=extract_imports(text, language),
                declarations=extract_declarations(text, language),
                runtime_references=find_runtime_references(text, patterns),
            )
        )
    return results


def line_count(text: str) -> int:
    return 0 if not text else text.count("\n") + 1


def extract_imports(text: str, language: str) -> list[str]:
    expressions = {
        "java": r"^\s*import\s+(?:static\s+)?([\w.*]+)\s*;",
        "csharp": r"^\s*using\s+([\w.]+)\s*;",
        "javascript": r"""(?:^\s*import\s+.*?\s+from\s+['"]([^'"]+)['"]|^\s*(?:const|let|var)\s+\w+\s*=\s*require\(\s*['"]([^'"]+)['"]\s*\))""",
        "css": r"""@import\s+(?:url\()?['"]?([^'")\s;]+)""",
        "sql": r"\b(?:FROM|JOIN|UPDATE|INTO)\s+([A-Za-z_][\w.$]*)",
    }
    expression = expressions.get(language)
    if expression is None:
        return []
    matches = re.findall(expression, text, flags=re.IGNORECASE | re.MULTILINE)
    values = [next((part for part in match if part), "") if isinstance(match, tuple) else match for match in matches]
    return sorted({value.strip() for value in values if value.strip()})


def extract_declarations(text: str, language: str) -> list[str]:
    expressions = {
        "java": r"\b(?:class|interface|enum|record)\s+([A-Za-z_]\w*)",
        "csharp": r"\b(?:class|interface|enum|struct|record)\s+([A-Za-z_]\w*)",
        "javascript": r"\b(?:class|function)\s+([A-Za-z_$][\w$]*)",
        "css": r"\.([A-Za-z_-][\w-]*)\s*[{,:]",
        "sql": r"\bCREATE\s+(?:TABLE|VIEW|PROCEDURE|FUNCTION)\s+([A-Za-z_][\w.$]*)",
    }
    expression = expressions.get(language)
    return sorted(set(re.findall(expression, text, flags=re.IGNORECASE | re.MULTILINE))) if expression else []


def find_runtime_references(text: str, patterns: tuple[str, ...]) -> list[str]:
    return [pattern for pattern in patterns if re.search(re.escape(pattern), text, flags=re.IGNORECASE)]


def build_report(source_root: Path, files: list[FileInventory]) -> dict[str, object]:
    language_counts = Counter(item.language for item in files)
    language_lines = Counter()
    for item in files:
        language_lines[item.language] += item.lines
    return {
        "schema_version": 1,
        "source_root": str(source_root.resolve()),
        "summary": {
            "files": len(files),
            "lines": sum(item.lines for item in files),
            "imports": sum(len(item.imports) for item in files),
            "declarations": sum(len(item.declarations) for item in files),
            "runtime_references": sum(len(item.runtime_references) for item in files),
        },
        "languages": {
            language: {"files": language_counts[language], "lines": language_lines[language]}
            for language in sorted(language_counts)
        },
        "files": [item.to_dict() for item in files],
    }
