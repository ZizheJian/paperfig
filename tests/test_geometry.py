import math
import os
import tempfile
import unittest
import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from paperfig import PaperFigureSpec,apply_paper_style,layout_panel_row,panel_aspect_ratios,save_paper_png_vertical_crop,style_plot_axis

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

if __name__=="__main__":unittest.main()
