#!/usr/bin/env python3
"""Generate full LC100 题解文档 and upload to Feishu.

Reads PROGRESS.md to determine completed problems, then generates a full
markdown document from problems/*.md + code/*.py and uploads to Feishu doc
EZfodeviXosNJLxuZWFcKCwonyg via lark-cli.

Usage:
    python3 scripts/gen_doc.py          # Generate + upload
    python3 scripts/gen_doc.py --local  # Generate only (write to /tmp/lc100_doc.md)

Pitfalls:
    - PROGRESS.md regex must skip 序号 (col 1) and match 题号 (col 2)
    - lark-cli docs +update requires relative path: @./lc100_doc.md not @/tmp/lc100_doc.md
    - Must cd /tmp before running lark-cli (relative path requirement)
    - HTML tags in problem files must be cleaned before upload
    - SLUGS dict must be maintained for LeetCode URLs
"""
import os, re, glob, sys, subprocess

PROBLEMS_DIR = "/root/projects/leetcode-hot100/problems"
CODE_DIR = "/root/projects/leetcode-hot100/code"
PROGRESS_FILE = "/root/projects/leetcode-hot100/PROGRESS.md"

# Problem slugs for LeetCode URLs — add new problems as they appear
SLUGS = {
    1: "two-sum", 49: "group-anagrams", 128: "longest-consecutive-sequence",
    283: "move-zeroes", 11: "container-with-most-water", 15: "3sum",
    42: "trapping-rain-water", 3: "longest-substring-without-repeating-characters",
    438: "find-all-anagrams-in-a-string", 560: "subarray-sum-equals-k",
    239: "sliding-window-maximum", 76: "minimum-window-substring",
    347: "top-k-frequent-elements", 136: "single-number",
    169: "majority-element", 75: "sort-colors",
    206: "reverse-linked-list", 234: "palindrome-linked-list",
    141: "linked-list-cycle", 142: "linked-list-cycle-ii",
    160: "intersection-of-two-linked-lists", 21: "merge-two-sorted-lists",
    2: "add-two-numbers", 19: "remove-nth-node-from-end-of-list",
    24: "swap-nodes-in-pairs", 25: "reverse-nodes-in-k-group",
    138: "copy-list-with-random-pointer", 148: "sort-list",
    146: "lru-cache", 94: "binary-tree-inorder-traversal",
    104: "maximum-depth-of-binary-tree", 226: "invert-binary-tree",
    101: "symmetric-tree", 543: "diameter-of-binary-tree",
    102: "binary-tree-level-order-traversal", 108: "convert-sorted-array-to-binary-search-tree",
    98: "validate-binary-search-tree", 230: "kth-smallest-element-in-a-bst",
    199: "binary-tree-right-side-view", 114: "flatten-binary-tree-to-linked-list",
    105: "construct-binary-tree-from-preorder-and-inorder-traversal",
    437: "path-sum-iii", 236: "lowest-common-ancestor-of-a-binary-tree",
    124: "binary-tree-maximum-path-sum", 200: "number-of-islands",
    994: "rotting-oranges", 207: "course-schedule",
    208: "implement-trie-prefix-tree", 46: "permutations",
    78: "subsets", 17: "letter-combinations-of-a-phone-number",
    39: "combination-sum", 22: "generate-parentheses",
    79: "word-search", 131: "palindrome-partitioning",
    51: "n-queens", 70: "climbing-stairs",
    118: "pascals-triangle", 198: "house-robber",
    279: "perfect-squares", 322: "coin-change",
    139: "word-break", 300: "longest-increasing-subsequence",
    152: "maximum-product-subarray", 416: "partition-equal-subset-sum",
    32: "longest-valid-parentheses", 62: "unique-paths",
    64: "minimum-path-sum", 5: "longest-palindromic-substring",
    1143: "longest-common-subsequence", 72: "edit-distance",
    53: "maximum-subarray", 56: "merge-intervals",
}

DIFF_MAP = {"E": "Easy", "M": "Medium", "H": "Hard"}


def get_completed():
    """Read PROGRESS.md and return set of completed problem IDs.
    
    CRITICAL: regex must skip 序号 (col 1) and match 题号 (col 2).
    PROGRESS.md has 7 columns: | 序号 | 题号 | 题名 | 难度 | 状态 | 完成日期 | 备注 |
    """
    with open(PROGRESS_FILE) as f:
        content = f.read()
    return set(int(m.group(1)) for m in re.finditer(
        r'\| \d+ \| (\d+) \| .+? \| .+? \| ✅ 已完成', content))


def get_problems_order():
    """Read PROBLEMS.txt to get the correct display order."""
    order = []
    with open("/root/projects/leetcode-hot100/PROBLEMS.txt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) >= 3:
                order.append(int(parts[1]))
    return order


def find_problem_file(prob_id):
    prefix = f"{prob_id:04d}_"
    matches = glob.glob(os.path.join(PROBLEMS_DIR, prefix + "*.md"))
    return matches[0] if matches else None


def find_code_file(prob_id):
    prefix = f"{prob_id:04d}_"
    matches = glob.glob(os.path.join(CODE_DIR, prefix + "*.py"))
    return matches[0] if matches else None


def clean_html(content):
    """Remove HTML tags from LeetCode problem descriptions."""
    content = re.sub(r'<strong\s+class="[^"]*">', '**', content)
    content = re.sub(r'</strong>', '**', content)
    content = re.sub(r'<span[^>]*>', '', content)
    content = re.sub(r'</span>', '', content)
    content = re.sub(r'<meta[^>]*/?>', '', content)
    content = re.sub(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*>', '', content)
    return content


def read_problem_body(filepath):
    with open(filepath) as f:
        content = f.read()
    content = clean_html(content)
    m = re.search(r"## 题目描述\s*\n(.+)", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = content.split("\n")
    return "\n".join(lines[1:]).strip()


def read_code(filepath):
    with open(filepath) as f:
        content = f.read()
    m = re.search(r"(class Solution:.+?)(?=\n# ----|\ndef test|\nif __name__)", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return content.split("# ===")[0].strip()


def get_difficulty(prob_id):
    """Read difficulty from PROGRESS.md for a given problem ID."""
    with open(PROGRESS_FILE) as f:
        for line in f:
            if f'| {prob_id} |' in line:
                if 'Easy' in line: return "Easy"
                elif 'Hard' in line: return "Hard"
                else: return "Medium"
    return "Medium"


def get_notes():
    """Extract notes from PROGRESS.md for completed problems."""
    notes = {}
    with open(PROGRESS_FILE) as f:
        for line in f:
            m = re.match(r'\| \d+ \| (\d+) \| .+? \| .+? \| .+? \| .+? \| (.+?) \|', line)
            if m:
                notes[int(m.group(1))] = m.group(2).strip()
    return notes


def main():
    completed = get_completed()
    order = get_problems_order()
    notes = get_notes()

    sections = ["LC100 题解笔记\n"]
    sections.append("📋 配合多维表格「LC100 进度追踪」使用\n")
    sections.append("📊 多维表格: LC100 进度追踪\n")

    for prob_id in order:
        prob_file = find_problem_file(prob_id)
        if not prob_file:
            continue

        basename = os.path.basename(prob_file)
        name_match = re.match(r'\d+_(.+)\.md', basename)
        name = name_match.group(1) if name_match else f"Problem {prob_id}"

        is_done = prob_id in completed
        diff = get_difficulty(prob_id)
        status = "✅" if is_done else "⏳"
        slug = SLUGS.get(prob_id, "")
        url = f"https://leetcode.cn/problems/{slug}/" if slug else ""

        header = f"## {prob_id}. {name} ({diff}) {status}"
        if is_done and url:
            header += f"\n\n🔗 [原题链接]({url}) ｜ 📊 进度记录"
        elif url:
            header += f"\n\n🔗 [原题链接]({url})"

        body = read_problem_body(prob_file)
        section = f"{header}\n\n{body}"

        if is_done:
            code_file = find_code_file(prob_id)
            if code_file:
                code = read_code(code_file)
                note = notes.get(prob_id, "")
                if note:
                    section += f"\n\n**思路**：{note}"
                section += f"\n```python\n{code}\n```"

        sections.append(section)

    doc_content = "\n\n".join(sections)

    tmpfile = "/tmp/lc100_doc.md"
    with open(tmpfile, "w") as f:
        f.write(doc_content)

    print(f"Generated {len(sections)} sections, {len(doc_content)} chars")
    print(f"Written to {tmpfile}")

    if "--local" in sys.argv:
        print("Local mode — skipping upload")
        return

    # Upload to Feishu — must use relative path from cwd=/tmp
    result = subprocess.run(
        ["lark-cli", "docs", "+update", "--doc", "EZfodeviXosNJLxuZWFcKCwonyg",
         "--mode", "overwrite", "--markdown", "@./lc100_doc.md", "--as", "bot"],
        capture_output=True, text=True, cwd="/tmp"
    )
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print(result.stdout[:500])
    if result.stderr:
        print(f"STDERR: {result.stderr[:500]}")


if __name__ == "__main__":
    main()
