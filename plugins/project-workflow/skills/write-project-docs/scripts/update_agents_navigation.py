#!/usr/bin/env python3
"""Update the documentation sections in an existing root AGENTS.md."""

from __future__ import annotations

import argparse
import os
import stat
import tempfile
from pathlib import Path

from canonical_paths import (
    canonical_path_mappings,
    render_template,
    select_canonical_paths,
)
from managed_blocks import (
    ManagedBlockError,
    locate_visible_asset_block,
    visible_section_titles,
)


SECTION_TITLES = ("项目文档导航", "项目文档内容边界")
FIXED_PATH_MAPPINGS = (
    ("docs/INDEX.md", "docs/README.md"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "仅更新现有项目根 AGENTS.md 的托管文档导航、内容边界和明确旧路径。"
        )
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="项目根目录，默认为当前目录。",
    )
    return parser.parse_args()


def insert_or_replace_block(text: str, asset: str) -> tuple[str, str]:
    try:
        span = locate_visible_asset_block(
            text, asset, SECTION_TITLES, "根 AGENTS.md 的文档区块"
        )
    except ManagedBlockError as error:
        raise ValueError(str(error)) from error

    if span is None:
        existing_titles = visible_section_titles(text, SECTION_TITLES)
        if existing_titles:
            titles = "、".join(f"## {title}" for title in sorted(existing_titles))
            raise ValueError(f"根 AGENTS.md 的文档区块已漂移：{titles}")
        prefix = text
        newline = "\r\n" if "\r\n" in prefix else "\n"
        if prefix and not prefix.endswith(newline):
            prefix += newline
        if prefix and not prefix.endswith(newline * 2):
            prefix += newline
        return prefix + asset, "inserted"

    return text[: span.start] + asset + text[span.end :], "replaced"


def write_atomically(path: Path, text: str) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=".AGENTS.md.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary_path = Path(handle.name)
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    agents_path = root / "AGENTS.md"
    skill_root = Path(__file__).resolve().parent.parent
    asset_path = skill_root / "assets" / "AGENTS-文档导航区块.md"

    if not root.is_dir():
        print(f"错误：项目根目录不存在或不是目录：{root}")
        return 2
    if asset_path.is_symlink() or not asset_path.is_file():
        print("错误：skill 缺少普通文件 assets/AGENTS-文档导航区块.md")
        return 2
    if agents_path.is_symlink():
        print("错误：根 AGENTS.md 是符号链接；未修改")
        return 1
    if not agents_path.exists():
        print("跳过：项目根 AGENTS.md 不存在；未创建")
        return 0
    if not agents_path.is_file():
        print("错误：根 AGENTS.md 不是普通文件；未修改")
        return 1

    try:
        with agents_path.open("r", encoding="utf-8", newline="") as handle:
            original = handle.read()
        asset_template = asset_path.read_bytes()
    except UnicodeDecodeError:
        print("错误：根 AGENTS.md 不是有效 UTF-8；未修改")
        return 1

    selected, path_errors = select_canonical_paths(root)
    if path_errors:
        print("错误：")
        for error in path_errors:
            print(f"- {error}")
        print("未修改根 AGENTS.md")
        return 1
    try:
        asset = render_template(
            asset_template, selected, "AGENTS 文档区块 asset"
        ).decode("utf-8")
    except ValueError as error:
        print(f"错误：{error}")
        return 2

    try:
        asset_span = locate_visible_asset_block(
            asset, asset, SECTION_TITLES, "AGENTS 文档区块 asset"
        )
    except ManagedBlockError:
        asset_span = None
    if (
        asset_span is None
        or asset_span.start != 0
        or asset_span.end != len(asset)
        or not asset.endswith("\n")
        or asset.endswith("\n\n")
        or "\r" in asset
    ):
        print("错误：AGENTS 文档区块 asset 格式无效")
        return 2

    replacements: list[str] = []
    normalized_original = original
    path_mappings = canonical_path_mappings(selected) + FIXED_PATH_MAPPINGS
    for old_path, new_path in path_mappings:
        count = normalized_original.count(old_path)
        if count:
            normalized_original = normalized_original.replace(old_path, new_path)
            replacements.append(f"{old_path} → {new_path}（{count} 处）")

    try:
        updated, block_action = insert_or_replace_block(
            normalized_original, asset
        )
    except ValueError as error:
        print(f"错误：{error}；未修改")
        return 1

    if updated == original:
        print("根 AGENTS.md 已符合文档区块规范；未修改")
        return 0

    write_atomically(agents_path, updated)
    action_text = "已插入" if block_action == "inserted" else "已更新"
    print(f"{action_text}根 AGENTS.md 文档区块。")
    for replacement in replacements:
        print(f"已修正：{replacement}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
