---
name: image-pdf-to-latex-cheatsheet
version: 1.0.0
description: "将图片型PDF（扫描件/截图）通过视觉识别转为A3横向LaTeX速查表，编译后发送。适用于开卷考试材料整理。"
---

# Image PDF → A3 LaTeX Cheat Sheet 工作流

## 适用场景
- 原始PDF是图片型（扫描件、截图），`fitz.get_text()` 返回空
- 需要把参考材料压缩成A3两页的速查表带去开卷考试

## 步骤

### 1. 检查PDF是否为图片型
```python
import fitz
doc = fitz.open("input.pdf")
for page in doc:
    text = page.get_text().strip()
    if not text:
        print("图片型PDF，需用视觉识别")
```

### 2. 渲染为图片（视觉识别用）
```python
import fitz
doc = fitz.open("input.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)  # 200 DPI 足够视觉识别
    pix.save(f"/tmp/page_{i+1}.png")
```

> **坑：不要用 clip 分块**，pymupdf 的 `get_pixmap(dpi=高DPI, clip=...)` 在某些DPI下会报 `Invalid bandwriter header dimensions/setup`。直接渲染整页更稳定。

### 3. 视觉识别
对每页图片调用 `vision_analyze`，提问示例：
- "请从上到下、从左到右，逐块识别所有代码和文字。每个代码块用 ```latex``` 包裹。不要省略任何内容。"
- 对内容密集的页面可能需要多次识别不同区域，或换不同提问角度获取更完整内容

### 4. 编写A3 LaTeX速查表模板

> **坑：`a3paper` 不要放在 `\documentclass` 选项里**（会被忽略），必须放在 `geometry` 包选项中。

#### 方案A：minipage 多栏布局（推荐，精确控制每页栏数）

> **关键：不要用 `multicols*` 跨页！** `multicols*` 跨页后第二页不再维持多栏布局，导致大片空白。用 `minipage` 手动控制每页的栏数和内容分布。

用并排 `minipage` 实现精确的4栏/2栏布局，每页独立设计：

```latex
\documentclass[9pt]{article}
\usepackage[a3paper,landscape,margin=0.6cm]{geometry}
\usepackage[UTF8,scheme=plain]{ctex}
\usepackage{amsmath,amssymb}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{titlesec}

\titleformat{\section}{\bfseries\fontsize{7}{8}\selectfont\color{blue!70!black}}{}{0pt}{}

\lstset{
  basicstyle=\ttfamily\fontsize{6.5}{8}\selectfont,
  keywordstyle=\color{black},      % 不要蓝色，保持干净
  commentstyle=\color{black},
  breaklines=true,
  frame=none,
  backgroundcolor=\color{white},   % 纯白底，不要灰色！
  xleftmargin=0pt, xrightmargin=0pt,
  aboveskip=1pt, belowskip=1pt,
  columns=fullflexible,
  keepspaces=true,
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5pt}
\pagestyle{empty}

\newcommand{\code}[1]{{\ttfamily\fontsize{6.5}{8}\selectfont #1}}
\newcommand{\mysec}[1]{\vspace{3pt}{\bfseries\fontsize{7}{8}\selectfont\color{blue!70!black} #1}\vspace{1pt}}
\newcommand{\mysubsec}[1]{\vspace{2pt}{\bfseries\fontsize{6}{7}\selectfont #1}\vspace{0.5pt}}
\newcommand{\hl}[1]{\colorbox{yellow!40}{#1}}  % 黄色高亮关键词

\begin{document}
\fontsize{7.5}{9.5}\selectfont

% ===== PAGE 1: 4栏 =====
\noindent
\begin{minipage}[t]{0.24\textwidth}
% 栏1内容
\end{minipage}%
\hfill
\begin{minipage}[t]{0.24\textwidth}
% 栏2内容
\end{minipage}%
\hfill
\begin{minipage}[t]{0.24\textwidth}
% 栏3内容
\end{minipage}%
\hfill
\begin{minipage}[t]{0.24\textwidth}
% 栏4内容
\end{minipage}

\newpage
% ===== PAGE 2: 2栏 =====
\noindent
\begin{minipage}[t]{0.48\textwidth}
% 栏1内容
\end{minipage}%
\hfill
\begin{minipage}[t]{0.48\textwidth}
% 栏2内容
\end{minipage}

\end{document}
```

**设计风格建议（用户验证过的）：**
- 大标题用 `\color{blue!70!black}` 蓝色，层级清晰
- 代码块纯白底无框，等宽黑色字体（不要灰底！用户不喜欢）
- 关键概念用 `\colorbox{yellow!40}{...}` 黄色高亮点缀
- 数学符号表用 `tabular` + `\code{}` 对齐

#### 方案B：标准2栏布局（更宽松）

```latex
\documentclass[7pt,twocolumn]{article}
\usepackage[a3paper,landscape,margin=0.8cm]{geometry}
\usepackage[UTF8,scheme=plain]{ctex}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{booktabs}

\titlespacing*{\section}{0pt}{4pt}{2pt}
\lstset{
  basicstyle=\ttfamily\fontsize{5.5}{6.5}\selectfont,
  keywordstyle=\color{blue},
  commentstyle=\color{gray},
  breaklines=true,
  frame=single,
  backgroundcolor=\color{gray!8},
  rulecolor=\color{gray!40},
  columns=fullflexible,
  language=[LaTeX]TeX,
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{1pt}
\pagestyle{empty}

\begin{document}
\fontsize{6.8}{8.2}\selectfont
% ... 内容 ...
\end{document}
```

### 5. 编译
```bash
cd /tmp && xelatex -interaction=nonstopmode output.tex
```

### 6. 发送
```bash
cd /tmp && lark-cli im +messages-send --chat-id <oc_xxx> --file ./output.pdf --as bot
```

> **坑：`--file` 必须用相对路径**（当前目录下的文件），绝对路径会报错。先 `cd` 到文件所在目录。

## 排版调参经验

### 迭代调页数的方法
1. 先用较大字号（9pt）写完所有内容
2. 编译检查页数：`xelatex ... | grep "Output"`
3. **页数不够（如1页）**：增大字号、增大边距、增大行距、减少栏数（4栏→3栏→2栏）
4. **页数太多**：缩小字号、减小边距、增加栏数、减少 aboveskip/belowskip
5. 每次调整 `documentclass` 基础字号 + `\fontsize` + lstset basicstyle + `\code` 命令字号，保持比例一致
6. 重复直到恰好 N 页

### 视觉审查（必须做！）
用户要求编译后必须用视觉审查确认排版质量：
```python
import fitz
doc = fitz.open("/tmp/output.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    pix.save(f"/tmp/check_p{i+1}.png")
```
然后用 `vision_analyze` 逐页审查，重点检查：
1. 每栏/每页内容是否填满（底部有无大片空白）
2. 代码块是否干净无灰底
3. 标题层级是否清晰
4. 数学符号表是否整齐
5. 黄色高亮是否适度（点缀关键词，不要滥用）

**审查不通过就修改再编译再审查，循环直到通过。**

## Pitfalls
1. **pymupdf clip+高DPI 组合可能报错** → 直接用整页渲染，不要分块
2. **`\documentclass` 的 `a3paper` 选项被 geometry 覆盖时可能无效** → 只在 geometry 中指定
3. **lark-cli `--file` 不接受绝对路径** → 先 cd 再用相对路径
4. **图片型PDF的 `fitz.get_text()` 返回空** → 不浪费时间去试，直接用视觉识别
5. **lstlisting 不能嵌套** → 如果代码示例本身包含 `\begin{lstlisting}`，不能用 lstlisting 环境包裹，改用 `\code{}` 命令手动转义输出（用 `\textbackslash` 代替 `\`）
6. **`multicols*` 跨页后第二页不再分栏** → 这是最大坑！用 `minipage` 手动控制每页布局
7. **python3 执行器(sandbox)没有 fitz/pymupdf** → 写到临时 .py 文件再用 `terminal("python3 /tmp/script.py")` 执行
8. **代码块不要用灰底背景** → 用户不喜欢 `backgroundcolor=\color{gray!5}`，用纯白底 `\color{white}`
9. **A3纸4栏太多可能1页就塞下** → 如果内容不多，第一页用4栏 minipage（24%宽度），第二页用2栏 minipage（48%宽度），根据内容量灵活调整
