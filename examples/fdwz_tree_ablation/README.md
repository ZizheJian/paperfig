# FDWZ tree ablation example

This example reproduces the MRCZ paper's FDWZ tree-ablation figure with one two-slot panel and one one-slot panel. The plot-area spans `(2,1)` map to aspect ratios `(2*sqrt(2),sqrt(2))`.

The figure-ready CSV files are compact extracts of the original experiment results:

- `data/prediction_error_distribution.csv` stores the visible prediction-error bins, counts, and full-tree totals needed to reproduce the density curves.
- `data/tree_count.csv` stores the bitrate measured for one through five trees at relative error bound `1e-3`.

Generate the tracked example image from the repository root:

```bash
python examples/fdwz_tree_ablation/plot.py
```

The output is `examples/fdwz_tree_ablation/fdwz-tree-ablation.png`.
