import math
import os
import tempfile
import unittest
import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from paperfig import DEFAULT_LEGEND_GAP_PT,DEFAULT_LEGEND_ROW_GAP_PT,DEFAULT_X_LABEL_GAP_PT,DEFAULT_X_TICK_GAP_PT,DEFAULT_Y_LABEL_GAP_PT,DEFAULT_Y_TICK_GAP_PT,MPL_POINTS_PER_INCH,PaperFigureSpec,apply_paper_style,layout_panel_grid,layout_panel_row,legend_above,panel_aspect_ratios,save_paper_png_vertical_crop,style_plot_axis

class GeometryTest(unittest.TestCase):
    def test_default_panel_spans(self):
        self.assertEqual(panel_aspect_ratios(1,1,1),(math.sqrt(2),)*3)
        self.assertEqual(panel_aspect_ratios(2,1),(2*math.sqrt(2),math.sqrt(2)))
        with self.assertRaises(ValueError):panel_aspect_ratios(1,0)

    def test_layout_and_vertical_crop_preserve_width(self):
        apply_paper_style()
        spec=PaperFigureSpec.column(1)
        figure,axes=plt.subplots(1,2,figsize=spec.size_in,dpi=spec.dpi)
        for axis in axes:
            axis.plot([0,1],[0,1])
            axis.set_xticks([-1,0,1,2])
            axis.set_xlim(0,1)
            axis.set_xlabel("x")
            axis.set_ylabel("y")
            style_plot_axis(axis,x_tick_pad=1.5,y_tick_pad=1,x_label_pad=1,y_label_pad=1)
        ratios=panel_aspect_ratios(2,1)
        layout_panel_row(figure,axes,ratios,bottom_pt=30,panel_gap_pt=9,left_edge_gap_pt=3,right_edge_gap_pt=3)
        figure.canvas.draw()
        renderer=figure.canvas.get_renderer()
        for axis,ratio in zip(axes,ratios):
            bbox=axis.get_window_extent(renderer)
            self.assertAlmostEqual(bbox.width/bbox.height,ratio,places=10)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path=os.path.join(temporary_directory,"figure.png")
            save_paper_png_vertical_crop(figure,output_path,spec,edge_gap_pt=3)
            image=mpimg.imread(output_path)
            self.assertEqual(image.shape[1],spec.pixel_size[0])
            self.assertLess(image.shape[0],image.shape[1])
            self.assertGreater(image.shape[0],0)
            visible_rows=(image[:,:,:3]<0.98).any(axis=2).any(axis=1).nonzero()[0]
            self.assertGreaterEqual(visible_rows[0],8)
            self.assertLessEqual(visible_rows[-1],image.shape[0]-9)
        plt.close(figure)

    def test_default_legend_gaps_use_physical_points(self):
        apply_paper_style()
        figure,axis=plt.subplots(figsize=(4,4),dpi=300)
        axis.plot([0,1],[0,1],label="First")
        axis.plot([0,1],[1,0],label="Second")
        legend=legend_above(axis,ncol=1,frameon=False)
        figure.canvas.draw()
        renderer=figure.canvas.get_renderer()
        axis_bbox=axis.get_window_extent(renderer)
        legend_bbox=legend.get_window_extent(renderer)
        legend_gap_pt=(legend_bbox.y0-axis_bbox.y1)*MPL_POINTS_PER_INCH/figure.dpi
        text_bboxes=[text.get_window_extent(renderer) for text in legend.get_texts()]
        row_gap_pt=(text_bboxes[0].y0-text_bboxes[1].y1)*MPL_POINTS_PER_INCH/figure.dpi
        self.assertAlmostEqual(legend_gap_pt,DEFAULT_LEGEND_GAP_PT,places=10)
        self.assertAlmostEqual(row_gap_pt,DEFAULT_LEGEND_ROW_GAP_PT,places=10)
        plt.close(figure)

    def test_default_tick_gaps_use_physical_points(self):
        apply_paper_style()
        figure,axis=plt.subplots(figsize=(4,4),dpi=300)
        axis.plot([0,1],[0,1])
        axis.set_xticks([0,0.5,1])
        axis.set_yticks([0,0.5,1])
        axis.set_xlabel("X label")
        axis.set_ylabel("Y label")
        style_plot_axis(axis)
        figure.canvas.draw()
        renderer=figure.canvas.get_renderer()
        axis_bbox=axis.get_window_extent(renderer)
        x_bboxes=[label.get_window_extent(renderer) for label in axis.get_xticklabels() if label.get_visible() and label.get_text()]
        y_bboxes=[label.get_window_extent(renderer) for label in axis.get_yticklabels() if label.get_visible() and label.get_text()]
        x_gap_pt=(axis_bbox.y0-max(bbox.y1 for bbox in x_bboxes))*MPL_POINTS_PER_INCH/figure.dpi
        y_gap_pt=(axis_bbox.x0-max(bbox.x1 for bbox in y_bboxes))*MPL_POINTS_PER_INCH/figure.dpi
        self.assertAlmostEqual(x_gap_pt,DEFAULT_X_TICK_GAP_PT,places=10)
        self.assertAlmostEqual(y_gap_pt,DEFAULT_Y_TICK_GAP_PT,places=10)
        x_label_bbox=axis.xaxis.label.get_window_extent(renderer)
        y_label_bbox=axis.yaxis.label.get_window_extent(renderer)
        x_label_gap_pt=(min(bbox.y0 for bbox in x_bboxes)-x_label_bbox.y1)*MPL_POINTS_PER_INCH/figure.dpi
        y_label_gap_pt=(min(bbox.x0 for bbox in y_bboxes)-y_label_bbox.x1)*MPL_POINTS_PER_INCH/figure.dpi
        self.assertAlmostEqual(x_label_gap_pt,DEFAULT_X_LABEL_GAP_PT,places=10)
        self.assertAlmostEqual(y_label_gap_pt,DEFAULT_Y_LABEL_GAP_PT,places=10)
        plt.close(figure)

    def test_grid_layout_preserves_every_panel_ratio(self):
        apply_paper_style()
        spec=PaperFigureSpec.text(1,width_fraction=5/6)
        figure,axes=plt.subplots(2,5,figsize=spec.size_in,dpi=spec.dpi)
        for index,axis in enumerate(axes.flat):
            axis.plot([0,1],[0,1])
            axis.set_xlabel(f"({chr(ord('a')+index)}) Panel")
            style_plot_axis(axis,x_tick_pad=1.5,y_tick_pad=1,x_label_pad=1)
        ratios=panel_aspect_ratios(1,1,1,1,1)
        layout_panel_grid(figure,axes,ratios,bottom_pt=30,column_gap_pt=4,row_content_gap_pt=6,left_edge_gap_pt=12,right_edge_gap_pt=3)
        figure.canvas.draw()
        renderer=figure.canvas.get_renderer()
        for axis in axes.flat:
            bbox=axis.get_window_extent(renderer)
            self.assertAlmostEqual(bbox.width/bbox.height,math.sqrt(2),places=10)
        top_caption_bottom=min(axis.xaxis.label.get_window_extent(renderer).y0 for axis in axes[0,:])
        lower_plot_top=max(axis.get_window_extent(renderer).y1 for axis in axes[1,:])
        content_gap_pt=(top_caption_bottom-lower_plot_top)*MPL_POINTS_PER_INCH/figure.dpi
        self.assertAlmostEqual(content_gap_pt,6,places=10)
        plt.close(figure)

if __name__=="__main__":unittest.main()
