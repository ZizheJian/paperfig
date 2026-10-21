# paperfig

`paperfig` provides deterministic Matplotlib layouts for publication figures. It keeps the final paper width and font size fixed, lays out panel rows and grids in physical points, renders once to measure the actual text, and crops only the vertical whitespace when exporting a 300 dpi PNG.

## Conventions

- Default font size: 8 pt.
- Default PNG resolution: 300 dpi.
- IEEE-style column width: 252 TeX pt.
- IEEE-style text width: 516 TeX pt.
- One panel slot has a plot-area width-to-height ratio of `sqrt(2)`.
- The default x- and y-tick-label gaps are 1.5 pt and 1 pt, respectively.
- The default gap from a legend to its plot area is 1 pt, and the default gap between legend rows is 1 pt.
- A normal three-panel row uses spans `(1,1,1)`.
- A panel occupying two slots beside a one-slot panel uses spans `(2,1)`, producing aspect ratios `(2*sqrt(2),sqrt(2))`.
- The provisional canvas is square. Export keeps its full fixed width and crops only the top and bottom.
- Distances are measured from rendered artist bounding boxes, so ordinary decimals and math-text tick labels are handled consistently.
- `set_legend_row_gap` applies the same measured row spacing to legends created directly with Matplotlib.

## Installation

For standalone development:

```bash
python -m pip install -e .
```

To pin the helper to an exact commit inside another project:

```bash
git submodule add git@github.com:ZizheJian/paperfig.git third_party/paperfig
python -m pip install -e third_party/paperfig
```

Clone a parent project and its pinned helper with:

```bash
git clone --recurse-submodules <parent-repository>
```

## Example

```python
import matplotlib.pyplot as plt
from paperfig import PaperFigureSpec,layout_panel_row,panel_aspect_ratios,save_paper_png_vertical_crop

spec=PaperFigureSpec.column(1)
figure,axes=plt.subplots(1,2,figsize=spec.size_in,dpi=spec.dpi)
layout_panel_row(figure,axes,panel_aspect_ratios(2,1),bottom_pt=30,panel_gap_pt=9,left_edge_gap_pt=3,right_edge_gap_pt=3)
save_paper_png_vertical_crop(figure,"figure.png",spec,edge_gap_pt=3)
```

See [`examples/fdwz_tree_ablation`](examples/fdwz_tree_ablation) for the data and code that reproduce a two-slot plus one-slot panel figure from the MRCZ paper.

Run the geometry checks with:

```bash
python -m unittest discover -s tests
```

## Using the instructions from a parent project

An `AGENTS.md` inside a submodule applies only to files in that submodule. Add this line to the parent project's root `AGENTS.md` if its plotting scripts should follow these conventions:

```text
For publication figures, follow third_party/paperfig/AGENTS.md and use the paperfig layout and output helpers.
```
