#!/usr/bin/env python3
"""列出 Issue 纪要的 idea，或原样提取公共部分与一个 idea 章节。"""

import argparse
import re
from pathlib import Path

ISSUE = re.compile(r"# Issue #([1-9][0-9]*)(?:[ \t]+.*)?")
IDEA = re.compile(r"(I([0-9]+)-N([0-9]+))[ \t]+(.+)")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")


def parse_document(text):
    lines = text.splitlines(keepends=True)
    issue = None
    common = None
    sections = []
    seen = set()
    fence = None
    for position, line in enumerate(lines):
        content = line.rstrip("\r\n")
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) +
                            "{" + str(len(fence)) + r",}[ \t]*", content):
                fence = None
            continue
        opening = FENCE.fullmatch(content)
        if opening:
            fence, info = opening.groups()
            if fence[0] == "`" and "`" in info:
                raise ValueError(f"第 {position + 1} 行：代码围栏信息不能包含反引号")
            continue
        title = ISSUE.fullmatch(content)
        if title:
            if issue is not None or common is not None or sections:
                raise ValueError("Issue 标题只能在公共部分之前出现一次")
            issue = int(title[1])
        elif re.match(r" {0,3}##(?:[ \t]|$)", content):
            if not content.startswith("## "):
                raise ValueError(f"第 {position + 1} 行：二级标题必须从行首以 '## ' 开始")
            heading = content[3:].strip()
            if heading == "统一信息":
                if issue is None or common is not None or sections:
                    raise ValueError("统一信息必须在 Issue 标题之后、所有 idea 之前，且只出现一次")
                common = position
                continue
            match = IDEA.fullmatch(heading)
            if not match:
                raise ValueError(f"第 {position + 1} 行：二级标题只能是统一信息或 idea ID 加标题")
            if common is None:
                raise ValueError("idea 之前缺少统一信息")
            identity = (int(match[2]), int(match[3]))
            if identity[0] != issue or identity[1] == 0:
                raise ValueError(f"{match[1]} 必须属于本 Issue，且节点编号大于零")
            if identity in seen:
                raise ValueError(f"idea 编号重复：{match[1]}")
            seen.add(identity)
            sections.append((match[1], match[4], position))
    if fence:
        raise ValueError("代码围栏未闭合，无法安全确定章节边界")
    if not sections:
        raise ValueError("文档必须包含 Issue 标题、统一信息和至少一个 idea")
    if not any(line.strip() for line in lines[common + 1:sections[0][2]]):
        raise ValueError("统一信息不能为空")
    shared = "".join(lines[:sections[0][2]])
    ideas = {}
    for index, (node_id, title, start) in enumerate(sections):
        end = sections[index + 1][2] if index + 1 < len(sections) else len(lines)
        if not any(line.strip() for line in lines[start + 1:end]):
            raise ValueError(f"{node_id} 章节不能为空")
        ideas[node_id] = (title, "".join(lines[start:end]))
    return shared, ideas


def extract_idea(text, idea_id):
    shared, ideas = parse_document(text)
    if idea_id not in ideas:
        raise ValueError(f"未找到 {idea_id}；可选：{', '.join(ideas)}")
    return shared + ideas[idea_id][1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("idea", nargs="?", help="省略时仅列出 idea ID 和标题")
    args = parser.parse_args()
    try:
        text = args.document.read_text(encoding="utf-8")
        if args.idea:
            print(extract_idea(text, args.idea), end="")
        else:
            _, ideas = parse_document(text)
            for node_id, (title, _) in ideas.items():
                print(f"{node_id}\t{title}")
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
