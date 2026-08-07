#!/usr/bin/env python3
"""Validate a project's canonical documentation set without modifying it."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from canonical_paths import (
    ALWAYS_REQUIRED_PATHS,
    canonical_path_mappings,
    render_template,
    select_canonical_paths,
)
from managed_blocks import (
    ManagedBlockError,
    locate_visible_asset_block,
    markdown_h1_lines,
)


COMPETING_PATHS = (
    "docs/INDEX.md",
    "docs/通用工程规范.md",
)

IGNORED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    "target",
}

AGENTS_SECTION_TITLES = ("项目文档导航", "项目文档内容边界")
CONTRIBUTING_SECTION_TITLES = ("通用设计原则", "通用实现原则", "完成定义")
DEVELOPMENT_SECTION_TITLES = ("通用规模与职责规则",)
LEGACY_DOC_PATHS = (
    "docs/INDEX.md",
)

INLINE_LINK_RE = re.compile(
    r"!?\[[^\]]*\]\((?P<target><[^>]+>|[^)\s]+)(?:\s+['\"][^)]*)?\)"
)
REFERENCE_LINK_RE = re.compile(
    r"^\s*\[[^\]]+\]:\s*(?P<target><[^>]+>|\S+)", re.MULTILINE
)
THRESHOLD_RE = re.compile(
    r"(?:(?:超过|大于|达到|约|不少于|>=?|≤)\s*`?(?:240|300|500|50)`?\s*(?:行|lines?)|"
    r"(?:240|300|500|50)\s*(?:行|lines?)\s*(?:阈值|上限|限制))",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "验证固定项目文档的中英文 canonical 路径、共享内容、"
            "开发规范专项引用、根 AGENTS.md 文档区块和本地 Markdown 链接。"
        )
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="项目根目录，默认为当前目录。",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "把旧 canonical 路径、嵌套 AGENTS.md 引用、可能重复规则等迁移警告"
            "视为失败；共享内容缺失、漂移或区块边界错误在普通模式也会失败。"
        ),
    )
    return parser.parse_args()


def markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if path.is_file() and not path.is_symlink():
            files.append(path)
    return sorted(files)


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def extract_link_targets(text: str) -> list[str]:
    targets = [match.group("target") for match in INLINE_LINK_RE.finditer(text)]
    targets.extend(match.group("target") for match in REFERENCE_LINK_RE.finditer(text))
    return targets


def legacy_path_references(
    text: str, selected: dict[str, str]
) -> list[tuple[int, str]]:
    references: list[tuple[int, str]] = []
    stale_paths = LEGACY_DOC_PATHS + tuple(
        old_path for old_path, _ in canonical_path_mappings(selected)
    )
    for line_number, line in enumerate(text.splitlines(), start=1):
        for legacy_path in stale_paths:
            if legacy_path in line:
                references.append((line_number, legacy_path))
    return references


def complete_section_asset_issue(
    data: bytes, section_titles: tuple[str, ...], label: str
) -> str | None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return f"{label} 不是有效 UTF-8"
    if b"\r" in data or not data.endswith(b"\n") or data.endswith(b"\n\n"):
        return f"{label} 必须使用 LF，并保留且仅保留一个尾随换行"
    try:
        span = locate_visible_asset_block(text, text, section_titles, label)
    except ManagedBlockError as error:
        return str(error)
    if span is None:
        headings = "、".join(f"## {title}" for title in section_titles)
        return f"{label} 缺少托管标题：{headings}"
    if span.start != 0 or span.end != len(text):
        return f"{label} 的托管标题必须覆盖整个 asset"
    return None


def validate_link(source: Path, raw_target: str, root: Path) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if not target or target.startswith("#"):
        return None

    parsed = urlsplit(target)
    if parsed.scheme or target.startswith("//") or target.startswith("/"):
        return None

    relative_path = unquote(parsed.path)
    if not relative_path:
        return None

    resolved = (source.parent / relative_path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return f"{display_path(source, root)}: 链接越出项目根目录：{raw_target}"

    if not resolved.exists():
        return f"{display_path(source, root)}: 本地链接目标不存在：{raw_target}"
    return None


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    skill_root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        print(f"错误：项目根目录不存在或不是目录：{root}", file=sys.stderr)
        return 2

    docs_directory = root / "docs"
    if docs_directory.is_symlink():
        print("错误：")
        print("- docs 目录不得使用符号链接")
        return 1

    for relative in ALWAYS_REQUIRED_PATHS:
        path = root / relative
        if not path.is_file():
            errors.append(f"缺少固定文档：{relative}")
        elif path.is_symlink():
            errors.append(f"固定文档不得使用符号链接：{relative}")

    selected, path_errors = select_canonical_paths(root)
    errors.extend(path_errors)
    for relative in selected.values():
        path = root / relative
        if path.is_symlink():
            errors.append(f"固定文档不得使用符号链接：{relative}")
        elif path.exists() and not path.is_file():
            errors.append(f"固定文档必须是普通文件：{relative}")

    for relative in COMPETING_PATHS:
        if (root / relative).exists():
            warnings.append(f"存在竞争或遗留 canonical 路径：{relative}")

    development_rules = root / selected["development_rules"]
    if development_rules.is_file() and not development_rules.is_symlink():
        try:
            development_text = development_rules.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            pass
        else:
            has_canonical_prefix = (
                development_text == "# 开发规范"
                or development_text.startswith("# 开发规范\n")
            )
            if (
                not has_canonical_prefix
                or markdown_h1_lines(development_text) != ["# 开发规范"]
            ):
                errors.append(
                    f"{selected['development_rules']} 必须以唯一的"
                    "“# 开发规范”标题开头"
                )

    development_asset = skill_root / "assets" / "开发规范-规模规则区块.md"
    development_asset_issue: str | None = None
    if development_asset.is_symlink() or not development_asset.is_file():
        errors.append("skill 缺少普通共享资源：assets/开发规范-规模规则区块.md")
    else:
        try:
            expected_development_block = render_template(
                development_asset.read_bytes(),
                selected,
                "开发规范规模规则 asset",
            )
        except ValueError as error:
            errors.append(f"skill 共享资源无效：{error}")
            expected_development_block = b""
        development_asset_issue = complete_section_asset_issue(
            expected_development_block,
            DEVELOPMENT_SECTION_TITLES,
            "开发规范规模规则 asset",
        )
        if development_asset_issue:
            errors.append(f"skill 共享资源无效：{development_asset_issue}")
    if (
        development_asset.is_file()
        and not development_asset.is_symlink()
        and not development_asset_issue
        and development_rules.is_file()
        and not development_rules.is_symlink()
    ):
        actual_development = development_rules.read_bytes()
        try:
            actual_development_text = actual_development.decode("utf-8")
            expected_development_text = expected_development_block.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{selected['development_rules']} 不是有效 UTF-8")
        else:
            try:
                span = locate_visible_asset_block(
                    actual_development_text,
                    expected_development_text,
                    DEVELOPMENT_SECTION_TITLES,
                    "开发规范的规模规则引用区块",
                )
            except ManagedBlockError as error:
                errors.append(str(error))
            else:
                if span is None:
                    errors.append(
                        f"{selected['development_rules']} 缺少规模规则引用区块"
                    )
                elif actual_development_text[: span.start] not in {
                    "# 开发规范\n\n",
                    "# 开发规范\r\n\r\n",
                }:
                    errors.append(
                        f"{selected['development_rules']} 的规模规则引用区块"
                        "必须紧跟标题"
                    )
                elif (
                    actual_development_text[span.start : span.end]
                    != expected_development_text
                    or actual_development_text.count(expected_development_text)
                    != 1
                ):
                    errors.append(
                        f"{selected['development_rules']} 的规模规则引用区块"
                        "已漂移，必须用 asset 完整替换"
                    )

    source_asset = skill_root / "assets" / "源代码规模与职责规则.md"
    project_source_rules = root / selected["source_size_rules"]
    if source_asset.is_symlink() or not source_asset.is_file():
        errors.append("skill 缺少普通共享资源：assets/源代码规模与职责规则.md")
    elif project_source_rules.is_file():
        try:
            expected_source_rules = render_template(
                source_asset.read_bytes(), selected, "源代码规模与职责规则 asset"
            )
        except ValueError as error:
            errors.append(f"skill 共享资源无效：{error}")
        else:
            if project_source_rules.read_bytes() != expected_source_rules:
                errors.append(
                    f"{selected['source_size_rules']} 与 skill asset 的路径渲染结果"
                    "不一致"
                )

    contributing_asset = skill_root / "assets" / "CONTRIBUTING-通用区块.md"
    contributing = root / "CONTRIBUTING.md"
    asset_issue: str | None = None
    if contributing_asset.is_symlink() or not contributing_asset.is_file():
        errors.append("skill 缺少普通共享资源：assets/CONTRIBUTING-通用区块.md")
    else:
        try:
            expected_contributing_block = render_template(
                contributing_asset.read_bytes(), selected, "CONTRIBUTING 共享 asset"
            )
        except ValueError as error:
            errors.append(f"skill 共享资源无效：{error}")
            expected_contributing_block = b""
        asset_issue = complete_section_asset_issue(
            expected_contributing_block,
            CONTRIBUTING_SECTION_TITLES,
            "CONTRIBUTING 共享 asset",
        )
        if asset_issue:
            errors.append(f"skill 共享资源无效：{asset_issue}")
    if (
        contributing_asset.is_file()
        and not contributing_asset.is_symlink()
        and not asset_issue
        and contributing.is_file()
    ):
        try:
            actual_contributing_text = contributing.read_bytes().decode("utf-8")
            expected_contributing_text = expected_contributing_block.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("CONTRIBUTING.md 不是有效 UTF-8")
        else:
            try:
                span = locate_visible_asset_block(
                    actual_contributing_text,
                    expected_contributing_text,
                    CONTRIBUTING_SECTION_TITLES,
                    "CONTRIBUTING.md 的共享区块",
                )
            except ManagedBlockError as error:
                errors.append(str(error))
            else:
                if span is None:
                    errors.append("CONTRIBUTING.md 缺少共享 contribution asset")
                elif (
                    actual_contributing_text[span.start : span.end]
                    != expected_contributing_text
                    or actual_contributing_text.count(expected_contributing_text)
                    != 1
                ):
                    errors.append(
                        "CONTRIBUTING.md 的共享区块已漂移，"
                        "必须用 asset 完整替换"
                    )

    agents_asset = skill_root / "assets" / "AGENTS-文档导航区块.md"
    root_agents = root / "AGENTS.md"
    agents_asset_issue: str | None = None
    if agents_asset.is_symlink() or not agents_asset.is_file():
        errors.append("skill 缺少普通共享资源：assets/AGENTS-文档导航区块.md")
    else:
        try:
            expected_agents_block = render_template(
                agents_asset.read_bytes(), selected, "AGENTS 文档区块 asset"
            )
        except ValueError as error:
            errors.append(f"skill 共享资源无效：{error}")
            expected_agents_block = b""
        agents_asset_issue = complete_section_asset_issue(
            expected_agents_block,
            AGENTS_SECTION_TITLES,
            "AGENTS 文档区块 asset",
        )
        if agents_asset_issue:
            errors.append(f"skill 共享资源无效：{agents_asset_issue}")
    if (
        agents_asset.is_file()
        and not agents_asset.is_symlink()
        and not agents_asset_issue
        and root_agents.exists()
    ):
        if root_agents.is_symlink():
            warnings.append("根 AGENTS.md 是符号链接，未验证或管理其文档区块")
        elif not root_agents.is_file():
            warnings.append("根 AGENTS.md 不是普通文件，未验证或管理其文档区块")
        else:
            actual = root_agents.read_bytes()
            try:
                agents_text = actual.decode("utf-8")
                expected_agents_text = expected_agents_block.decode("utf-8")
            except UnicodeDecodeError:
                errors.append("AGENTS.md 不是有效 UTF-8")
                agents_text = actual.decode("utf-8", errors="replace")
            else:
                try:
                    span = locate_visible_asset_block(
                        agents_text,
                        expected_agents_text,
                        AGENTS_SECTION_TITLES,
                        "根 AGENTS.md 的文档区块",
                    )
                except ManagedBlockError as error:
                    errors.append(str(error))
                else:
                    if span is None:
                        errors.append("现有根 AGENTS.md 缺少文档区块 asset")
                    elif (
                        agents_text[span.start : span.end]
                        != expected_agents_text
                        or agents_text.count(expected_agents_text) != 1
                    ):
                        errors.append(
                            "根 AGENTS.md 的文档区块已漂移，"
                            "必须用 asset 完整替换"
                        )
            for line_number, legacy_path in legacy_path_references(
                agents_text, selected
            ):
                errors.append(
                    f"AGENTS.md:{line_number}: 仍引用旧 canonical 路径：{legacy_path}"
                )

    docs = markdown_files(root)
    for path in docs:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{display_path(path, root)}: 不是有效 UTF-8 Markdown")
            continue
        for target in extract_link_targets(text):
            issue = validate_link(path, target, root)
            if issue:
                errors.append(issue)

        relative = path.relative_to(root).as_posix()
        if relative not in {
            selected["source_size_rules"],
            selected["architecture"],
        }:
            for line_number, line in enumerate(text.splitlines(), start=1):
                if THRESHOLD_RE.search(line):
                    message = (
                        f"{relative}:{line_number}: 可能重复了共享规模阈值；"
                        "应改为链接"
                    )
                    if relative == selected["development_rules"]:
                        errors.append(message)
                    else:
                        warnings.append(message)

    for agents_path in sorted(root.rglob("AGENTS.md")):
        relative_path = agents_path.relative_to(root)
        if agents_path == root_agents or any(
            part in IGNORED_PARTS for part in relative_path.parts
        ):
            continue
        relative = relative_path.as_posix()
        if agents_path.is_symlink():
            warnings.append(f"{relative}: 嵌套 AGENTS.md 是符号链接，未检查旧路径")
            continue
        if not agents_path.is_file():
            continue
        try:
            agents_text = agents_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, legacy_path in legacy_path_references(agents_text, selected):
            warnings.append(
                f"{relative}:{line_number}: 嵌套 AGENTS.md 仍引用旧 canonical 路径："
                f"{legacy_path}"
            )

    if errors:
        print("错误：")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("警告：")
        for item in warnings:
            print(f"- {item}")
    if not errors and not warnings:
        print("项目文档验证通过。")
    elif not errors:
        print("项目文档基础验证通过，但仍有迁移警告。")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
