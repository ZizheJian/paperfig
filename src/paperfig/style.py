import matplotlib.pyplot as plt
from .spec import DEFAULT_X_TICK_GAP_PT,DEFAULT_Y_TICK_GAP_PT,PAPER_FONT_SIZE

def apply_paper_style(svg_hashsalt=None,font_size=PAPER_FONT_SIZE,tick_size=None,legend_size=None,serif_fonts=None):
    if tick_size is None:tick_size=font_size
    if legend_size is None:legend_size=font_size
    if serif_fonts is None:serif_fonts=["STIXGeneral"]
    if svg_hashsalt is not None:plt.rcParams["svg.hashsalt"]=svg_hashsalt
    plt.rcParams.update({"font.family":"serif","font.serif":serif_fonts,"mathtext.fontset":"stix","font.size":font_size,"axes.labelsize":font_size,"axes.titlesize":font_size,"xtick.labelsize":tick_size,"ytick.labelsize":tick_size,"legend.fontsize":legend_size,"pdf.fonttype":42,"ps.fonttype":42})

def style_plot_axis(axis,tick_length=1.8,tick_width=0.45,tick_pad=None,x_tick_pad=None,y_tick_pad=None,x_label_pad=None,y_label_pad=None,spine_width=0.5,minor_tick_length=None,minor_tick_width=None):
    if x_tick_pad is None:x_tick_pad=DEFAULT_X_TICK_GAP_PT if tick_pad is None else tick_pad
    if y_tick_pad is None:y_tick_pad=DEFAULT_Y_TICK_GAP_PT if tick_pad is None else tick_pad
    axis.tick_params(axis="x",direction="in",length=tick_length,width=tick_width,pad=x_tick_pad)
    axis.tick_params(axis="y",direction="in",length=tick_length,width=tick_width,pad=y_tick_pad)
    if x_label_pad is not None:axis.xaxis.labelpad=x_label_pad
    if y_label_pad is not None:axis.yaxis.labelpad=y_label_pad
    if minor_tick_length is not None:axis.tick_params(axis="both",which="minor",direction="in",length=minor_tick_length,width=minor_tick_width if minor_tick_width is not None else tick_width)
    for spine in axis.spines.values():spine.set_linewidth(spine_width)
