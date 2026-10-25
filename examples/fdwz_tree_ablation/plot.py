import csv,os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedFormatter,FixedLocator
from paperfig import PANEL_GAP_WITH_YLABEL_PT,PaperFigureSpec,add_panel_captions,align_xlabels,apply_paper_style,layout_panel_row,legend_above,legend_spacing_kwargs,save_paper_png_vertical_crop,style_plot_axis

example_directory=os.path.dirname(os.path.abspath(__file__))
tree_count_path=os.path.join(example_directory,"data/tree_count.csv")
prediction_error_distribution_path=os.path.join(example_directory,"data/prediction_error_distribution.csv")
output_path=os.path.join(example_directory,"fdwz-tree-ablation.png")

X_TICK_GAP_PT=1.5
Y_TICK_GAP_PT=1.0
X_LABEL_GAP_PT=1.0
Y_LABEL_GAP_PT=1.0
LEFT_EDGE_GAP_PT=3.0
RIGHT_EDGE_GAP_PT=3.0
PANEL_CAPTION_GAP_PT=2.0
VERTICAL_EDGE_GAP_PT=3.0

tree_colors=["#000000","#0072B2","#D55E00","#009E73","#CC79A7"]
tree_styles=["-","--","-.",":",(0,(3,1,1,1))]

def read_tree_counts(path):
    with open(path,encoding="utf-8") as csv_file:return [(int(row["Tree Count"]),float(row["BR"])) for row in csv.DictReader(csv_file)]

def read_prediction_error_distributions(path):
    distributions=defaultdict(dict)
    totals={}
    bin_width=None
    with open(path,encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            tree_id=int(row["Tree ID"])
            distributions[tree_id][int(row["Bin ID"])]=int(row["Count"])
            totals[tree_id]=int(row["Total"])
            bin_width=float(row["Bin Width"])
    return distributions,totals,bin_width

def configure_common_axes(axis):
    style_plot_axis(axis,tick_length=2.5,tick_width=0.6,x_tick_pad=X_TICK_GAP_PT,y_tick_pad=Y_TICK_GAP_PT,x_label_pad=X_LABEL_GAP_PT,y_label_pad=Y_LABEL_GAP_PT,spine_width=0.6,minor_tick_length=1.5,minor_tick_width=0.5)

def draw_tree_count_bars(axis):
    points=read_tree_counts(tree_count_path)
    tree_nums=[point[0] for point in points]
    bit_rates=[point[1] for point in points]
    axis.bar(tree_nums,bit_rates,width=0.68,color=["#9ecae1","#6baed6","#4292c6","#2171b5","#08519c"],edgecolor="black",linewidth=0.45)
    axis.set_xlim(0.45,5.55)
    axis.set_ylim(0,0.27)
    axis.xaxis.set_major_locator(FixedLocator(tree_nums))
    axis.yaxis.set_major_locator(FixedLocator([0,0.1,0.2]))
    axis.yaxis.set_major_formatter(FixedFormatter(["0","0.1","0.2"]))
    axis.set_xlabel("Number of Trees")
    axis.set_ylabel("BR")
    configure_common_axes(axis)

def draw_prediction_error_density(axis,distributions,totals,bin_width):
    maximum_density=0
    for tree_id,counts in sorted(distributions.items()):
        bins=range(min(counts),max(counts)+1)
        densities=[counts[bin_id]/(totals[tree_id]*bin_width) for bin_id in bins]
        maximum_density=max(maximum_density,max(densities))
        axis.plot([bin_id*bin_width for bin_id in bins],densities,label=f"Tree{tree_id}",color=tree_colors[tree_id],linestyle=tree_styles[tree_id],linewidth=0.9,drawstyle="steps-mid")
    axis.set_xlim(-0.15,0.15)
    axis.set_ylim(0,maximum_density*1.08)
    axis.xaxis.set_major_locator(FixedLocator([-0.15,0,0.15]))
    axis.xaxis.set_major_formatter(FixedFormatter(["-0.15","0","0.15"]))
    axis.yaxis.set_major_locator(FixedLocator([0,5,10]))
    axis.set_xlabel("Prediction Error")
    axis.set_ylabel("Probability Density")
    handles,labels=axis.get_legend_handles_labels()
    order=[0,3,1,4,2]
    configure_common_axes(axis)
    return [handles[index] for index in order],[labels[index] for index in order]

def make_figure():
    distributions,totals,bin_width=read_prediction_error_distributions(prediction_error_distribution_path)
    spec=PaperFigureSpec.column(1)
    figure,axes=plt.subplots(1,2,figsize=spec.size_in,dpi=spec.dpi)
    left_axis,right_axis=axes
    legend_handles,legend_labels=draw_prediction_error_density(left_axis,distributions,totals,bin_width)
    left_axis.get_xticklabels()[0].set_horizontalalignment("left")
    left_axis.get_xticklabels()[-1].set_horizontalalignment("right")
    draw_tree_count_bars(right_axis)
    layout_panel_row(figure,axes,(2.4,1.2),bottom_pt=30,panel_gap_pt=PANEL_GAP_WITH_YLABEL_PT,left_edge_gap_pt=LEFT_EDGE_GAP_PT,right_edge_gap_pt=RIGHT_EDGE_GAP_PT)
    legend_above(left_axis,legend_handles,legend_labels,ncol=3,frameon=False,**legend_spacing_kwargs(8))
    for axis in axes:
        axis.set_axisbelow(True)
        axis.grid(True,linestyle="--",linewidth=0.45,alpha=0.35)
    align_xlabels(figure,axes,gap_pt=X_LABEL_GAP_PT)
    add_panel_captions(figure,axes,["(a) Prediction-Error Density","(b) Tree Count"],gap_pt=PANEL_CAPTION_GAP_PT)
    save_paper_png_vertical_crop(figure,output_path,spec,edge_gap_pt=VERTICAL_EDGE_GAP_PT)
    plt.close(figure)

if __name__=="__main__":
    apply_paper_style(serif_fonts=["STIXGeneral"])
    make_figure()
