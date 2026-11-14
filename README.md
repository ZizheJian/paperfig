# paperfig

**English** | [中文](README_CN.md)

`paperfig` lays out Matplotlib figures for papers at a fixed paper width and font size, and exports 300 dpi PNG files that crop only the vertical whitespace. It is mainly used by AI coding assistants when they write plotting scripts. The rules and function summary they follow are in [CLAUDE.md](CLAUDE.md).

## Using it in a project

Add the repository as a submodule:

```bash
git submodule add git@github.com:ZizheJian/paperfig.git third_party/paperfig
```

Then add this line to the project's `CLAUDE.md`, so that Claude Code loads the paperfig rules when working in the project:

```text
画论文图时，按照 @third_party/paperfig/CLAUDE.md 使用paperfig。
```

## Examples

- [`examples/minimal`](examples/minimal): a two-panel single-column figure without data.
- [`examples/fdwz_tree_ablation`](examples/fdwz_tree_ablation): a complete figure drawn from experiment data.
