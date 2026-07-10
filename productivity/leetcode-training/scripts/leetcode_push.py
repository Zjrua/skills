#!/usr/bin/env python3
"""
LeetCode Hot 100 - 早间推送 (09:00)
每天推送5道新题，闪击战模式
"""
import re, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROGRESS_FILE = os.path.join(BASE_DIR, "PROGRESS.md")
PROBLEMS_FILE = os.path.join(BASE_DIR, "PROBLEMS.txt")

DAILY_COUNT = 5  # 每天题目数

HINTS = {
    1: "哈希表空间换时间",
    49: "把字符串「标准化」成统一形式",
    128: "Set + 只看序列起点",
    283: "双指针，慢指针跟踪填入位置",
    11: "两端收缩，短板移动",
    15: "排序 + 双指针，注意去重",
    42: "单调栈 or 双指针，想清楚每根柱子接多少水",
    3: "滑动窗口维护无重复字符",
    438: "固定长度滑动窗口 + 频率统计",
    560: "前缀和 + 哈希表",
    239: "单调队列入门",
    76: "滑动窗口终极版，维护满足条件的最小窗口",
    53: "经典 DP，也能用贪心理解",
    56: "排序后贪心合并",
    189: "翻转法最优雅",
    73: "O(1) 空间：用矩阵自身第一行第一列标记",
    54: "模拟转圈，注意边界",
    48: "旋转 = 转置 + 水平翻转",
    240: "从右上角出发，每次排除一行或一列",
    121: "一遍遍历维护最小买入价",
    55: "贪心维护最远可达位置",
    45: "想清楚「跳几步能到最远」",
    763: "预处理每个字母最后出现的位置",
    70: "经典 DP / 矩阵快速幂",
    118: "杨辉三角规律",
    198: "偷 or 不偷",
    279: "BFS 视角更直观",
    322: "完全背包，初始化为无穷大",
    139: "s[i] = s[j] + word?",
    300: "O(n²) DP 或 O(n log n) 贪心+二分",
    152: "同时维护最大值和最小值（负负得正）",
    416: "01背包，目标和 = sum/2",
    62: "经典网格 DP",
    64: "网格 DP + 权重",
    5: "中心扩展 or Manacher",
    1143: "经典 LCS 二维 DP",
    72: "插入/删除/替换三选一",
    32: "栈 or DP，栈更巧妙",
    200: "BFS/DFS 岛屿遍历",
    994: "多源 BFS 同时扩散",
    207: "拓扑排序 / 环检测",
    210: "207 加强版，记录顺序",
    17: "回溯 + 字母映射",
    22: "回溯生成合法括号",
    39: "回溯 + 排序剪枝",
    46: "回溯排列 + used 数组",
    78: "回溯 or 位运算枚举",
    131: "回溯 + 判断回文",
    51: "经典 N 皇后回溯",
    35: "二分查找变体",
    74: "二维转一维 or 右上角搜索",
    34: "两次二分找左右边界",
    33: "旋转数组二分，判断哪半边有序",
    153: "二分，比较 mid 和 right",
    4: "二分第 k 小",
    20: "栈匹配括号",
    155: "辅助栈 or 一个栈存差值",
    394: "嵌套结构栈解析",
    739: "单调栈找右边第一个更大",
    84: "单调栈求最大矩形",
    215: "堆 or QuickSelect",
    347: "频率统计 + 堆/桶排序",
    295: "双堆：大顶堆 + 小顶堆",
    21: "归并排序合并步骤",
    206: "迭代和递归都要会",
    141: "快慢指针判环",
    160: "双指针走两遍",
    92: "局部反转，注意边界",
    19: "快指针先走 n 步",
    82: "dummy node + 连续重复",
    25: "k 个一组反转，递归/迭代",
    143: "找中点→反转后半→交替合并",
    23: "堆优化 K 路归并",
    146: "哈希表 + 双向链表",
    94: "递归/迭代/Morris",
    104: "DFS 最大深度",
    226: "递归交换左右子树",
    101: "递归比较镜像",
    543: "DFS 深度 + 全局最大直径",
    102: "BFS 层序",
    108: "二分构造平衡 BST",
    98: "中序遍历严格递增",
    230: "中序第 k 个",
    199: "BFS 每层最后节点",
    114: "前序遍历逐步展开",
    105: "前序定根，中序分左右",
    437: "前缀和 + 哈希表，路径不必从根开始",
    236: "递归，p q 分布在哪棵子树",
    124: "DFS 返回单条路径最大贡献",
    130: "边界 DFS 标记不被包围的 O",
    133: "图深拷贝 + 哈希表",
    399: "图 + DFS/BFS 带权重",
    208: "字典树",
    136: "异或运算",
    169: "Boyer-Moore 投票",
    75: "三指针/计数排序",
    148: "链表归并排序",
}


def get_completed_count():
    with open(PROGRESS_FILE, "r") as f:
        return len(re.findall(r'\| ✅ 已完成', f.read()))


def get_problems(start, count):
    with open(PROBLEMS_FILE, "r") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    results = []
    for i in range(start, min(start + count, len(lines))):
        parts = lines[i].split("|")
        if len(parts) >= 6:
            results.append({
                "seq": int(parts[0]), "id": int(parts[1]), "name": parts[2],
                "difficulty": parts[3], "category": parts[4], "url": parts[5],
            })
    return results


def main():
    completed = get_completed_count()
    problems = get_problems(completed, DAILY_COUNT)

    if not problems:
        print("🎉🎉🎉 **LeetCode Hot 100 全部刷完！传奇！**")
        return

    diff_map = {"E": "🟢", "M": "🟡", "H": "🔴"}
    today_num = len(problems)

    print(f"⚡ **LeetCode Hot 100 · 闪击战 · 今日 {today_num} 题**")
    print()
    print(f"📊 当前进度: {completed}/100 → 目标 {completed + today_num}/100")
    print()
    print("---")
    print()

    for i, p in enumerate(problems, 1):
        diff = diff_map.get(p["difficulty"], "")
        hint = HINTS.get(p["id"], "先想暴力再优化")
        print(f"**{i}. {p['name']}** ({p['id']}) {diff} · {p['category']}")
        print(f"   🔗 {p['url']}")
        print(f"   💡 {hint}")
        print()

    print("---")
    print()
    remaining = 100 - completed
    days_left = (remaining + DAILY_COUNT - 1) // DAILY_COUNT
    print(f"🔥 剩余 {remaining} 题，预计 {days_left} 天刷完！冲！")


if __name__ == "__main__":
    main()
