import matplotlib.pyplot as plt
from .spec import DEFAULT_PANEL_ASPECT_RATIO,MPL_POINTS_PER_INCH

def paper_subplots(spec,nrows=1,ncols=1,left_pt=0,right_pt=0,bottom_pt=0,top_pt=0,column_gap_pt=0,row_gap_pt=0,width_ratios=None,height_ratios=None,squeeze=True):
    axes_width_pt=spec.width_pt-left_pt-right_pt-(ncols-1)*column_gap_pt
    axes_height_pt=spec.height_pt-bottom_pt-top_pt-(nrows-1)*row_gap_pt
    if axes_width_pt<=0 or axes_height_pt<=0:raise ValueError("Figure margins and panel gaps leave no space for axes")
    gridspec_kw={}
    if width_ratios is not None:gridspec_kw["width_ratios"]=width_ratios
    if height_ratios is not None:gridspec_kw["height_ratios"]=height_ratios
    figure,axes=plt.subplots(nrows,ncols,figsize=spec.size_in,dpi=spec.dpi,squeeze=squeeze,gridspec_kw=gridspec_kw)
    wspace=column_gap_pt/(axes_width_pt/ncols) if ncols>1 else 0
    hspace=row_gap_pt/(axes_height_pt/nrows) if nrows>1 else 0
    figure.subplots_adjust(left=left_pt/spec.width_pt,right=1-right_pt/spec.width_pt,bottom=bottom_pt/spec.height_pt,top=1-top_pt/spec.height_pt,wspace=wspace,hspace=hspace)
    return figure,axes

def legend_above(axis,*args,gap_pt=2,**kwargs):
    axes_height_pt=axis.get_position().height*axis.figure.get_figheight()*MPL_POINTS_PER_INCH
    kwargs.setdefault("loc","lower center")
    kwargs.setdefault("bbox_to_anchor",(0.5,1+gap_pt/axes_height_pt))
    kwargs.setdefault("borderaxespad",0)
    return axis.legend(*args,**kwargs)

def _flatten_axes(axes):
    if hasattr(axes,"flat"):return list(axes.flat)
    if isinstance(axes,(list,tuple)):return [axis for item in axes for axis in _flatten_axes(item)]
    return [axes]

def _visible_bboxes(artists,renderer):
    return [artist.get_window_extent(renderer) for artist in artists if artist.get_visible() and artist.get_text()]

def panel_aspect_ratios(*spans,unit_aspect_ratio=DEFAULT_PANEL_ASPECT_RATIO):
    if not spans or any(span<=0 for span in spans):raise ValueError("Panel spans must be positive")
    return tuple(span*unit_aspect_ratio for span in spans)

def layout_panel_row(figure,axes,aspect_ratios,bottom_pt,panel_gap_pt,left_edge_gap_pt,right_edge_gap_pt):
    axes=_flatten_axes(axes)
    if len(axes)!=len(aspect_ratios):raise ValueError("Each panel needs exactly one plot-area aspect ratio")
    figure_width_pt=figure.get_figwidth()*MPL_POINTS_PER_INCH
    figure_height_pt=figure.get_figheight()*MPL_POINTS_PER_INCH
    for _ in range(2):
        figure.canvas.draw()
        renderer=figure.canvas.get_renderer()
        decoration_widths=[]
        right_decoration_width_pt=0
        for axis in axes:
            axis_bbox=axis.get_window_extent(renderer)
            candidates=_visible_bboxes(axis.get_xticklabels(which="both"),renderer)+_visible_bboxes(axis.get_yticklabels(which="both"),renderer)
            if axis.xaxis.label.get_text():candidates.append(axis.xaxis.label.get_window_extent(renderer))
            if axis.yaxis.label.get_text():candidates.append(axis.yaxis.label.get_window_extent(renderer))
            leftmost=min((bbox.x0 for bbox in candidates),default=axis_bbox.x0)
            decoration_widths.append(max(0,(axis_bbox.x0-leftmost)*MPL_POINTS_PER_INCH/figure.dpi))
            if axis is axes[-1]:right_decoration_width_pt=max(0,(max((bbox.x1 for bbox in candidates),default=axis_bbox.x1)-axis_bbox.x1)*MPL_POINTS_PER_INCH/figure.dpi)
        available_width_pt=figure_width_pt-left_edge_gap_pt-right_edge_gap_pt-sum(decoration_widths)-right_decoration_width_pt-(len(axes)-1)*panel_gap_pt
        plot_height_pt=available_width_pt/sum(aspect_ratios)
        if plot_height_pt<=0:raise ValueError("Panel decorations and gaps leave no width for plot areas")
        left_pt=left_edge_gap_pt
        for index,(axis,aspect_ratio,decoration_width_pt) in enumerate(zip(axes,aspect_ratios,decoration_widths)):
            left_pt+=decoration_width_pt
            width_pt=plot_height_pt*aspect_ratio
            axis.set_position([left_pt/figure_width_pt,bottom_pt/figure_height_pt,width_pt/figure_width_pt,plot_height_pt/figure_height_pt])
            left_pt+=width_pt
            if index<len(axes)-1:left_pt+=panel_gap_pt
    return plot_height_pt

def _x_tick_bottom(axis,renderer):
    bboxes=_visible_bboxes(axis.get_xticklabels(which="both"),renderer)
    if not bboxes:raise ValueError("Cannot place a bottom row below an axis without visible x tick labels")
    return min(bbox.y0 for bbox in bboxes)

def align_xlabels(figure,axes,gap_pt=2):
    axes=_flatten_axes(axes)
    figure.canvas.draw()
    renderer=figure.canvas.get_renderer()
    row_top=min(_x_tick_bottom(axis,renderer) for axis in axes)-gap_pt*figure.dpi/MPL_POINTS_PER_INCH
    row_top_figure=figure.transFigure.inverted().transform((0,row_top))[1]
    for axis in axes:
        position=axis.get_position()
        label=axis.xaxis.label
        label.set_horizontalalignment("center")
        label.set_verticalalignment("top")
        axis.xaxis.set_label_coords((position.x0+position.x1)/2,row_top_figure,transform=figure.transFigure)
    figure.canvas.draw()

def add_panel_captions(figure,axes,texts,gap_pt=2,source="xlabel",**kwargs):
    axes=_flatten_axes(axes)
    if len(axes)!=len(texts):raise ValueError("Each panel needs exactly one caption")
    figure.canvas.draw()
    renderer=figure.canvas.get_renderer()
    if source=="xlabel":source_bboxes=[axis.xaxis.label.get_window_extent(renderer) for axis in axes]
    elif source=="ticks":source_bboxes=[min(_visible_bboxes(axis.get_xticklabels(which="both"),renderer),key=lambda bbox:bbox.y0) for axis in axes]
    else:raise ValueError(f"Unknown panel-caption source: {source}")
    row_top=min(bbox.y0 for bbox in source_bboxes)-gap_pt*figure.dpi/MPL_POINTS_PER_INCH
    row_top_figure=figure.transFigure.inverted().transform((0,row_top))[1]
    defaults={"ha":"center","va":"top"}
    defaults.update(kwargs)
    captions=[]
    for axis,text in zip(axes,texts):
        position=axis.get_position()
        captions.append(figure.text((position.x0+position.x1)/2,row_top_figure,text,**defaults))
    figure.canvas.draw()
    return captions

def add_shared_xlabel(figure,axes,text,gap_pt=2,source_artists=None,**kwargs):
    axes=_flatten_axes(axes)
    figure.canvas.draw()
    renderer=figure.canvas.get_renderer()
    if source_artists is None:source_bottom=min(_x_tick_bottom(axis,renderer) for axis in axes)
    else:source_bottom=min(artist.get_window_extent(renderer).y0 for artist in source_artists)
    row_top=source_bottom-gap_pt*figure.dpi/MPL_POINTS_PER_INCH
    row_top_figure=figure.transFigure.inverted().transform((0,row_top))[1]
    left=min(axis.get_position().x0 for axis in axes)
    right=max(axis.get_position().x1 for axis in axes)
    defaults={"ha":"center","va":"top"}
    defaults.update(kwargs)
    label=figure.text((left+right)/2,row_top_figure,text,**defaults)
    figure.canvas.draw()
    return label
