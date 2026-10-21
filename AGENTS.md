# Publication figure rules

- Use a fixed paper width and 8 pt final text.
- Export final figures as 300 dpi PNG files.
- Use `sqrt(2)` as the plot-area width-to-height ratio for one panel slot.
- Express row layouts through integer spans. Use `(1,1,1)` for three equal panels and `(2,1)` when the first panel occupies two slots.
- Start from a fixed-width square provisional canvas.
- Measure rendered artists before export.
- Preserve the full horizontal canvas so LaTeX scaling does not change the font size.
- Crop only vertical whitespace with `save_paper_png_vertical_crop`.
- Specify tick, label, caption, legend, panel, and outer-edge distances in points.
- Use 1 pt for the default legend-to-plot and legend-row gaps.
- Keep data loading and domain-specific labels, colors, and plotting logic in the parent project.
- Do not use `bbox_inches="tight"` for final paper figures because it can change the exported width.
- Run the geometry tests after changing layout code.
