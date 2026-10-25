# paperfig

`paperfig` provides deterministic Matplotlib layouts for publication figures. It keeps the final paper width and font size fixed, lays out panel rows and grids in physical points, renders to measure the actual text, and crops only the vertical whitespace when exporting a 300 dpi PNG.

The library handles publication geometry. A project still owns its data loading, plotting commands, colors, labels, and any figure-specific adjustments.

## Conventions

- Default font size: 8 pt.
- Default PNG resolution: 300 dpi.
- IEEE-style column width: 252 TeX pt.
- IEEE-style text width: 516 TeX pt.
- One panel slot has a plot-area width-to-height ratio of `sqrt(2)`.
- The default x- and y-tick-label gaps are 1.5 pt and 1 pt, respectively.
- The default axis-label gap is 1 pt, and the default panel-caption gap is 2 pt.
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

If the parent repository has already been cloned without submodules, initialize them with:

```bash
git submodule update --init --recursive
```

## Workflow

The intended order is:

1. Call `apply_paper_style` before creating the figure.
2. Select the final width with `PaperFigureSpec.column` or `PaperFigureSpec.text`.
3. Create the square provisional canvas and draw all data, ticks, and labels.
4. Call `style_plot_axis` for the shared tick, label, and spine geometry.
5. Call `layout_panel_row` or `layout_panel_grid` after the visible text exists. The layout functions measure that rendered text before placing the plot areas.
6. Add legends with `legend_above` after the plot areas have their final size, so its point-based gap is computed from the final geometry.
7. Align shared rows such as x-axis labels and panel captions.
8. Export with `save_paper_png_vertical_crop`. This keeps the exact paper width and removes only unused space above and below the content.

The provisional height is only workspace for Matplotlib. The exported height is determined by the measured content, while the width, font size, and 300 dpi resolution remain fixed.

## Minimal example

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from paperfig import PANEL_GAP_WITH_YLABEL_PT,PaperFigureSpec,add_panel_captions,align_xlabels,apply_paper_style,layout_panel_row,legend_above,legend_spacing_kwargs,panel_aspect_ratios,save_paper_png_vertical_crop,style_plot_axis

apply_paper_style()
spec=PaperFigureSpec.column()
figure,axes=plt.subplots(1,2,figsize=spec.size_in,dpi=spec.dpi)
for axis in axes:
    axis.plot([0,1,2],[0,1,0],label="Series")
    axis.set_xlabel("Input")
    axis.set_ylabel("Output")
    style_plot_axis(axis)
layout_panel_row(figure,axes,panel_aspect_ratios(1,1),bottom_pt=28,panel_gap_pt=PANEL_GAP_WITH_YLABEL_PT,left_edge_gap_pt=3,right_edge_gap_pt=3)
legend_above(axes[0],ncol=1,frameon=False,**legend_spacing_kwargs(8))
align_xlabels(figure,axes)
add_panel_captions(figure,axes,["(a) First","(b) Second"])
save_paper_png_vertical_crop(figure,"figure.png",spec,edge_gap_pt=3)
plt.close(figure)
```

The same code is available as the runnable [`examples/minimal`](examples/minimal) template. See [`examples/fdwz_tree_ablation`](examples/fdwz_tree_ablation) for a complete data-driven figure from the MRCZ paper.

## Choosing the layout helpers

| Helper | Use it for |
| --- | --- |
| `PaperFigureSpec.column(...)` | A figure measured from the 252 pt single-column width. |
| `PaperFigureSpec.text(...)` | A figure measured from the 516 pt full-text width. Use `width_fraction` for figures such as `5/6` of the text width. |
| `panel_aspect_ratios(...)` | Converting integer panel spans into plot-area aspect ratios based on the default `sqrt(2)` slot. Pass explicit ratios when a figure needs its own geometry. |
| `style_plot_axis(...)` | Applying physical tick-to-axis and label-to-tick gaps after scales and labels have been configured. Logarithmic x axes automatically use their separate default tick gap. |
| `layout_panel_row(...)` | Placing one row of panels while accounting for visible y-axis decorations and protruding edge ticks. |
| `layout_panel_grid(...)` | Placing a rectangular grid with measured gaps between the visible content of adjacent rows. |
| `legend_above(...)` | Placing a legend at a physical distance above one plot area. |
| `legend_spacing_kwargs(...)` | Expressing legend handle width, handle-to-text gap, and column gap in points. |
| `align_xlabels(...)` | Putting the x-axis labels of neighboring panels on one common row. |
| `add_panel_captions(...)` | Putting panel captions on one common row below x-axis labels or tick labels. |
| `add_shared_xlabel(...)` | Adding one x-axis label shared by several panels. |
| `save_paper_png_vertical_crop(...)` | Exporting a fixed-width 300 dpi PNG while cropping only vertical whitespace. |

All distance arguments ending in `_pt` are physical points in the final figure. Plot-area aspect ratios describe only the rectangle inside the axes spines. Tick labels, axis labels, legends, and captions do not count toward that ratio.

Choose the horizontal panel gap from the left-side decoration of the following panel: `PANEL_GAP_WITH_YLABEL_PT` is 8 pt when it has a y-axis label and tick labels, `PANEL_GAP_WITH_YTICKS_PT` is 4 pt when it has tick labels only, and `PANEL_GAP_WITHOUT_Y_DECORATION_PT` is 2 pt when it has neither. The layout helpers measure the decoration width separately, so these constants describe the visible clearance from the preceding plot boundary to that decoration.

## Shared defaults and figure-specific adjustments

Use the exported defaults for ordinary figures. Override a value in the project script when the data or labels create a special case. For example, a dense legend may need a smaller column gap, and a panel with two-line tick labels may need its caption row moved independently. Such adjustments belong in that figure's script unless they apply consistently across projects.

`paperfig` deliberately does not select tick locations, rewrite labels, choose colors, or infer semantic panel groupings. Keeping those choices in the parent project makes the shared geometry predictable.

Run the geometry checks with:

```bash
python -m unittest discover -s tests
```

## Using the instructions from a parent project

An `AGENTS.md` inside a submodule applies only to files in that submodule. Add this line to the parent project's root `AGENTS.md` if its plotting scripts should follow these conventions:

```text
For publication figures, follow third_party/paperfig/AGENTS.md and use the paperfig layout and output helpers.
```
