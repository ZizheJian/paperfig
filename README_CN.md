# paperfig

[English](README.md) | **中文**

`paperfig`按固定的纸面宽度和字号排布论文里的Matplotlib图，导出只裁掉上下空白的300 dpi PNG。它主要由AI编程助手在写画图脚本时使用，它们遵守的规则和函数说明在[CLAUDE.md](CLAUDE.md)里。

## 在项目里使用

把仓库加为子模块：

```bash
git submodule add git@github.com:ZizheJian/paperfig.git third_party/paperfig
```

再在项目的`CLAUDE.md`里加上这一句，Claude Code在这个项目里工作时就会读到paperfig的规则：

```text
画论文图时，按照 @third_party/paperfig/CLAUDE.md 使用paperfig。
```

## 示例

- [`examples/minimal`](examples/minimal)：不需要数据的两面板单栏图。
- [`examples/fdwz_tree_ablation`](examples/fdwz_tree_ablation)：用实验数据画的完整例子。
