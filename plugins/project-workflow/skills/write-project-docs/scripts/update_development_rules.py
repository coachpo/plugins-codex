#!/usr/bin/env python3
"""Update the managed source-size-policy link in the development rules."""

from __future__ import annotations

import argparse
import os
import stat
import tempfile
from pathlib import Path

from canonical_paths import render_template, select_canonical_paths
from managed_blocks import (
    ManagedBlockError,
    locate_managed_block,
    markdown_h1_lines,
)


START_MARKER = "<!-- write-project-docs:development-source-size:start -->"
END_MARKER = "<!-- write-project-docs:development-source-size:end -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="更新开发规范中指向源代码规模与职责规则的托管区块。"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="项目根目录，默认为当前目录。",
    )
    return parser.parse_args()


def insert_after_title(text: str, asset: str) -> str:
    if markdown_h1_lines(text) != ["# 开发规范"]:
        raise ValueError("开发规范必须包含唯一的“# 开发规范”标题")

    if text == "# 开发规范":
        return text + "\n\n" + asset
    if text.startswith("# 开发规范\r\n"):
        title_end = len("# 开发规范\r\n")
        newline = "\r\n"
    elif text.startswith("# 开发规范\n"):
        title_end = len("# 开发规范\n")
        newline = "\n"
    else:
        raise ValueError("开发规范必须以“# 开发规范”标题开头")

    prefix = text[:title_end] + newline
    remainder = text[title_end:]
    if remainder and not remainder.startswith(("\n", "\r\n")):
        remainder = newline + remainder
    return prefix + asset + remainder


def insert_or_replace_block(text: str, asset: str) -> tuple[str, str]:
    try:
        span = locate_managed_block(
            text, START_MARKER, END_MARKER, "开发规范的规模规则引用区块"
        )
    except ManagedBlockError as error:
        raise ValueError(str(error)) from error

    if span is None:
        return insert_after_title(text, asset), "inserted"

    prefix = text[: span.start]
    if prefix in {"# 开发规范\n\n", "# 开发规范\r\n\r\n"}:
        return prefix + asset + text[span.end :], "replaced"

    newline = "\r\n" if text.startswith("# 开发规范\r\n") else "\n"
    before = text[: span.start].rstrip("\r\n")
    after = text[span.end :].lstrip("\r\n")
    without_block = before
    if after:
        without_block += newline * 2 + after
    return insert_after_title(without_block, asset), "replaced"


def write_atomically(path: Path, text: str) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
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
    skill_root = Path(__file__).resolve().parent.parent
    asset_path = skill_root / "assets" / "开发规范-规模规则区块.md"

    if not root.is_dir():
        print(f"错误：项目根目录不存在或不是目录：{root}")
        return 2
    if asset_path.is_symlink() or not asset_path.is_file():
        print("错误：skill 缺少普通文件 assets/开发规范-规模规则区块.md")
        return 2

    selected, path_errors = select_canonical_paths(root)
    if path_errors:
        print("错误：")
        for error in path_errors:
            print(f"- {error}")
        return 1

    development_path = root / selected["development_rules"]
    if development_path.is_symlink():
        print("错误：开发规范是符号链接；未修改")
        return 1
    if not development_path.is_file():
        print(f"错误：开发规范不存在或不是普通文件：{development_path}")
        return 1

    try:
        asset = render_template(
            asset_path.read_bytes(), selected, "开发规范规模规则 asset"
        ).decode("utf-8")
        with development_path.open("r", encoding="utf-8", newline="") as handle:
            original = handle.read()
    except UnicodeDecodeError:
        print("错误：开发规范或 asset 不是有效 UTF-8；未修改")
        return 1
    except ValueError as error:
        print(f"错误：{error}")
        return 2

    try:
        asset_span = locate_managed_block(
            asset, START_MARKER, END_MARKER, "开发规范规模规则 asset"
        )
    except ManagedBlockError:
        asset_span = None
    if (
        asset_span is None
        or asset_span.start != 0
        or asset_span.end != len(asset)
        or not asset.endswith("\n")
    ):
        print("错误：开发规范规模规则 asset 格式无效")
        return 2

    try:
        updated, action = insert_or_replace_block(original, asset)
    except ValueError as error:
        print(f"错误：{error}；未修改")
        return 1

    if updated == original:
        print("开发规范已包含正确的规模规则引用区块；未修改")
        return 0

    write_atomically(development_path, updated)
    action_text = "已插入" if action == "inserted" else "已更新"
    print(f"{action_text}开发规范的规模规则引用区块。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
