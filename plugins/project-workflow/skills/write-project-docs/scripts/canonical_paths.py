#!/usr/bin/env python3
"""Resolve the one selected Chinese or English path for each canonical document."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CanonicalDocument:
    key: str
    label: str
    chinese_path: str
    english_path: str
    template_token: str


CANONICAL_DOCUMENTS = (
    CanonicalDocument(
        "product",
        "产品说明",
        "docs/产品说明.md",
        "docs/product.md",
        "PRODUCT_DOC",
    ),
    CanonicalDocument(
        "architecture",
        "架构说明",
        "docs/架构说明.md",
        "docs/architecture.md",
        "ARCHITECTURE_DOC",
    ),
    CanonicalDocument(
        "development_rules",
        "开发规范",
        "docs/开发规范.md",
        "docs/development-rules.md",
        "DEVELOPMENT_RULES_DOC",
    ),
    CanonicalDocument(
        "source_size_rules",
        "源代码规模与职责规则",
        "docs/源代码规模与职责规则.md",
        "docs/source-code-size-and-responsibility-rules.md",
        "SOURCE_SIZE_RULES_DOC",
    ),
)

ALWAYS_REQUIRED_PATHS = (
    "README.md",
    "STATUS.md",
    "CONTRIBUTING.md",
    "docs/README.md",
)

TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")


def path_is_present(path: Path) -> bool:
    """Treat broken symlinks as present so validation can report them precisely."""

    return path.exists() or path.is_symlink()


def select_canonical_paths(
    root: Path, *, require_existing: bool = True
) -> tuple[dict[str, str], list[str]]:
    """Select one path per authority, preferring Chinese only when neither exists."""

    selected: dict[str, str] = {}
    errors: list[str] = []
    for document in CANONICAL_DOCUMENTS:
        candidates = (document.chinese_path, document.english_path)
        present = [
            relative
            for relative in candidates
            if path_is_present(root / relative)
        ]
        if len(present) > 1:
            errors.append(
                f"{document.label}同时存在中文和英文 canonical 文件："
                f"{document.chinese_path}、{document.english_path}；必须只保留一个"
            )
            selected[document.key] = document.chinese_path
        elif present:
            selected[document.key] = present[0]
        else:
            selected[document.key] = document.chinese_path
            if require_existing:
                errors.append(
                    f"缺少固定文档：{document.chinese_path} 或 "
                    f"{document.english_path}"
                )
    return selected, errors


def render_template(data: bytes, selected: dict[str, str], label: str) -> bytes:
    """Replace only declared canonical-path tokens in a UTF-8 managed asset."""

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} 不是有效 UTF-8") from error

    for document in CANONICAL_DOCUMENTS:
        token = "{{" + document.template_token + "}}"
        basename_token = "{{" + document.template_token + "_BASENAME}}"
        text = text.replace(token, selected[document.key])
        text = text.replace(basename_token, Path(selected[document.key]).name)

    unresolved = sorted(set(TOKEN_RE.findall(text)))
    if unresolved:
        raise ValueError(f"{label} 含有未知模板变量：{', '.join(unresolved)}")
    return text.encode("utf-8")


def canonical_path_mappings(
    selected: dict[str, str],
) -> tuple[tuple[str, str], ...]:
    """Map each unselected bilingual counterpart to the project's selected path."""

    mappings: list[tuple[str, str]] = []
    for document in CANONICAL_DOCUMENTS:
        chosen = selected[document.key]
        for candidate in (document.chinese_path, document.english_path):
            if candidate != chosen:
                mappings.append((candidate, chosen))
    return tuple(mappings)
