#!/usr/bin/env python3
"""Update the STATUS-controlled managed block in CONTRIBUTING.md."""

from __future__ import annotations

import argparse
import os
import stat
import tempfile
from pathlib import Path

from canonical_paths import (
    add_language_argument,
    requested_language,
    resolve_project_docs,
)
from contributing_blocks import (
    compose_contributing_block,
    mvp_heading_positions,
    parse_mvp_mode,
    render_contributing_assets,
)
from doc_anchors import LanguageProfile, profile_for
from managed_blocks import (
    ManagedBlockError,
    locate_managed_block,
    visible_atx_headings,
    visible_section_titles,
)


START_MARKER = "<!-- write-project-docs:shared-contributing:start -->"
END_MARKER = "<!-- write-project-docs:shared-contributing:end -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="按 STATUS.md 的 MVP 快速验证模式更新 CONTRIBUTING.md 托管区块。"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="项目根目录，默认为当前目录。",
    )
    add_language_argument(parser)
    return parser.parse_args()


def complete_asset_issue(asset: str) -> str | None:
    if "\r" in asset or not asset.endswith("\n") or asset.endswith("\n\n"):
        return "CONTRIBUTING 组合 asset 必须使用 LF，并仅保留一个尾随换行"
    try:
        span = locate_managed_block(
            asset, START_MARKER, END_MARKER, "CONTRIBUTING 组合 asset"
        )
    except ManagedBlockError as error:
        return str(error)
    if span is None or span.start != 0 or span.end != len(asset):
        return "CONTRIBUTING 组合 asset 的 marker 必须包围整个 asset"
    return None


def insert_or_replace_block(
    text: str, asset: str, profile: LanguageProfile
) -> tuple[str, str]:
    try:
        span = locate_managed_block(
            text, START_MARKER, END_MARKER, "CONTRIBUTING.md 的共享区块"
        )
    except ManagedBlockError as error:
        raise ValueError(str(error)) from error

    mvp_positions = mvp_heading_positions(text, profile)
    if span is None:
        if mvp_positions:
            raise ValueError(
                f"CONTRIBUTING.md 在托管区块外包含“{profile.mvp_heading}”"
            )
        existing_titles = visible_section_titles(
            text, profile.contributing_section_titles
        )
        if existing_titles:
            titles = "、".join(f"## {title}" for title in sorted(existing_titles))
            raise ValueError(f"CONTRIBUTING.md 的共享区块已漂移：{titles}")
        newline = "\r\n" if "\r\n" in text else "\n"
        prefix = text
        if prefix and not prefix.endswith(newline):
            prefix += newline
        if prefix and not prefix.endswith(newline * 2):
            prefix += newline
        return prefix + asset, "inserted"

    outside_positions = [
        position
        for position in mvp_positions
        if not (span.start <= position < span.end)
    ]
    if outside_positions:
        raise ValueError(
            f"CONTRIBUTING.md 在托管区块外包含“{profile.mvp_heading}”"
        )
    inside_positions = [
        position for position in mvp_positions if span.start <= position < span.end
    ]
    if len(inside_positions) > 1:
        raise ValueError(
            f"CONTRIBUTING.md 的共享区块包含重复“{profile.mvp_title}”标题"
        )
    outside_titles = visible_section_titles(
        text[: span.start] + text[span.end :],
        profile.contributing_section_titles,
    )
    if outside_titles:
        titles = "、".join(f"## {title}" for title in sorted(outside_titles))
        raise ValueError(f"CONTRIBUTING.md 在共享区块外包含托管标题：{titles}")
    h2_titles = [
        title
        for level, title, _ in visible_atx_headings(text[span.start : span.end])
        if level == 2
    ]
    if h2_titles != list(profile.contributing_section_titles):
        raise ValueError("CONTRIBUTING.md 的共享区块标题顺序错误")
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
    status_path = root / "STATUS.md"
    contributing_path = root / "CONTRIBUTING.md"

    if not root.is_dir():
        print(f"错误：项目根目录不存在或不是目录：{root}")
        return 2

    context = resolve_project_docs(root, language=requested_language(args.language))
    if context.errors:
        print("错误：")
        for error in context.errors:
            print(f"- {error}")
        print("未修改 CONTRIBUTING.md")
        return 1
    selected = context.selected
    profile = profile_for(context.language)

    base_asset_path = profile.asset_path(
        skill_root, profile.contributing_base_asset_name
    )
    mvp_asset_path = profile.asset_path(
        skill_root, profile.contributing_mvp_asset_name
    )

    for label, path in (
        ("STATUS.md", status_path),
        ("CONTRIBUTING.md", contributing_path),
    ):
        if path.is_symlink():
            print(f"错误：{label} 是符号链接；未修改")
            return 1
        if not path.is_file():
            print(f"错误：{label} 不存在或不是普通文件；未修改")
            return 1
    for label, path in (
        ("CONTRIBUTING 基础 asset", base_asset_path),
        ("CONTRIBUTING MVP asset", mvp_asset_path),
    ):
        if path.is_symlink() or not path.is_file():
            print(
                "错误：skill 缺少普通文件 "
                + f"{profile.asset_display(path.name)}（{label}）"
            )
            return 2

    try:
        with status_path.open("r", encoding="utf-8", newline="") as handle:
            status_text = handle.read()
        with contributing_path.open("r", encoding="utf-8", newline="") as handle:
            original = handle.read()
    except UnicodeDecodeError:
        print("错误：STATUS.md 或 CONTRIBUTING.md 不是有效 UTF-8；未修改")
        return 1

    try:
        base_asset, mvp_asset = render_contributing_assets(
            base_asset_path.read_bytes(),
            mvp_asset_path.read_bytes(),
            selected,
            context.language,
        )
    except ValueError as error:
        print(f"错误：skill 共享资源无效：{error}；未修改")
        return 2

    try:
        mvp_mode = parse_mvp_mode(status_text, context.language)
    except ValueError as error:
        print(f"错误：{error}；未修改")
        return 1

    try:
        asset = compose_contributing_block(
            base_asset,
            mvp_asset,
            mvp_mode=mvp_mode,
            language=context.language,
        )
    except (TypeError, ValueError) as error:
        print(f"错误：skill 共享资源无效：{error}；未修改")
        return 2

    asset_issue = complete_asset_issue(asset)
    if asset_issue:
        print(f"错误：{asset_issue}；未修改")
        return 2

    try:
        updated, action = insert_or_replace_block(original, asset, profile)
    except ValueError as error:
        print(f"错误：{error}；未修改")
        return 1

    if updated == original:
        print(
            "CONTRIBUTING.md 已符合 MVP 快速验证模式"
            f"（{mvp_mode.display}）；未修改"
        )
        return 0

    write_atomically(contributing_path, updated)
    action_text = "已插入" if action == "inserted" else "已更新"
    print(
        f"{action_text} CONTRIBUTING.md 共享区块；"
        f"文档语言：{profile.language.label}；"
        f"MVP 快速验证模式：{mvp_mode.display}。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
