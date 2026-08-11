#!/usr/bin/env python3
"""
Convert a GitBook-style SUMMARY.md (nested "* [Title](path.md)" bullets,
2-space indentation per level) into an MkDocs `nav:` YAML block.

This exists so each language's table of contents stays hand-edited in the
familiar SUMMARY.md format (translators/reviewers already know it), while
mkdocs.yml's nav is regenerated from it mechanically rather than by hand.

Usage:
    python tools/summary_to_nav.py french/SUMMARY.md > french_nav.yml

Then paste/merge the emitted `nav:` block into mkdocs.yml, or (once we
adopt mkdocs-static-i18n per-language configs) have the build pull it in
directly. Kept as a standalone script for now rather than a build-time
dependency, so the mkdocs build stays simple and reviewable.
"""

import re
import sys

BULLET_RE = re.compile(r"^(?P<indent>\s*)\*\s+\[(?P<title>.+?)\]\((?P<path>.+?)\)\s*$")


def parse_summary(lines):
    """Return a nested list of (title, path, children) tuples."""
    root = []
    # stack of (indent_width, children_list)
    stack = [(-1, root)]

    for raw_line in lines:
        m = BULLET_RE.match(raw_line.rstrip("\n"))
        if not m:
            continue  # skip headings, blank lines, prose
        indent = len(m.group("indent"))
        title = m.group("title")
        path = m.group("path")

        while stack and indent <= stack[-1][0]:
            stack.pop()

        node = {"title": title, "path": path, "children": []}
        stack[-1][1].append(node)
        stack.append((indent, node["children"]))

    return root


def to_yaml(nodes, depth=0):
    """Emit MkDocs nav YAML (list of {Title: path} or {Title: [...]})."""
    out = []
    pad = "  " * depth
    for node in nodes:
        title = node["title"].replace("'", "''")
        if node["children"]:
            out.append(f"{pad}- '{title}':")
            out.append(f"{pad}  - {node['path']}")
            out.extend(to_yaml(node["children"], depth + 1))
        else:
            out.append(f"{pad}- '{title}': {node['path']}")
    return out


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path/to/SUMMARY.md>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        lines = f.readlines()

    tree = parse_summary(lines)
    print("nav:")
    for line in to_yaml(tree, depth=1):
        print(line)


if __name__ == "__main__":
    main()
