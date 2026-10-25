import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from paperfig import PANEL_GAP_WITH_YLABEL_PT,PaperFigureSpec,add_panel_captions,align_xlabels,apply_paper_style,layout_panel_row,legend_above,legend_spacing_kwargs,panel_aspect_ratios,save_paper_png_vertical_crop,style_plot_axis

example_directory=os.path.dirname(os.path.abspath(__file__))
output_path=os.path.join(example_directory,"minimal.png")

def make_figure():
    apply_paper_style()
    spec=PaperFigureSpec.column()
    figure,axes=plt.subplots(1,2,figsize=spec.size_in,dpi=spec.dpi)
    for index,axis in enumerate(axes):
        axis.plot([0,1,2],[index,1+index,index],marker="o",label="Series")
        axis.set_xlabel("Input")
        axis.set_ylabel("Output")
        style_plot_axis(axis)
    layout_panel_row(figure,axes,panel_aspect_ratios(1,1),bottom_pt=28,panel_gap_pt=PANEL_GAP_WITH_YLABEL_PT,left_edge_gap_pt=3,right_edge_gap_pt=3)
    legend_above(axes[0],ncol=1,frameon=False,**legend_spacing_kwargs(8))
    align_xlabels(figure,axes)
    add_panel_captions(figure,axes,["(a) First","(b) Second"])
    save_paper_png_vertical_crop(figure,output_path,spec,edge_gap_pt=3)
    plt.close(figure)

if __name__=="__main__":make_figure()
