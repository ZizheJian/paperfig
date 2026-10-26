import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from .spec import DEFAULT_LEGEND_COLUMN_GAP_PT,DEFAULT_LEGEND_GAP_PT,DEFAULT_LEGEND_HANDLE_TEXT_GAP_PT,DEFAULT_LEGEND_ROW_GAP_PT,DEFAULT_PANEL_ASPECT_RATIO,DEFAULT_PANEL_CAPTION_GAP_PT,DEFAULT_X_LABEL_GAP_PT,MPL_POINTS_PER_INCH

def paper_subplots(spec,nrows=1,ncols=1,left_pt=0,right_pt=0,bottom_pt=0,top_pt=0,column_gap_pt=0,row_gap_pt=0,width_ratios=None,height_ratios=None,squeeze=True):
    axes_width_pt=spec.width_pt-left_pt-right_pt-(ncols-1)*column_gap_pt
    axes_height_pt=spec.height_pt-bottom_pt-top_pt-(nrows-1)*row_gap_pt
    if axes_width_pt<=0 or axes_height_pt<=0:raise ValueError("Figure margins and panel gaps leave no space for axes")
    gridspec_kw={}
    if width_ratios is not None:gridspec_kw["width_ratios"]=width_ratios
    if height_ratios is not None:gridspec_kw["height_ratios"]=height_ratios
    figure,axes=plt.subplots(nrows,ncols,figsize=spec.size_in,dpi=spec.dpi,squeeze=squeeze,gridspec_kw=gridspec_kw)
    # Matplotlib expresses wspace and hspace as fractions of an average axes size.
    wspace=column_gap_pt/(axes_width_pt/ncols) if ncols>1 else 0
    hspace=row_gap_pt/(axes_height_pt/nrows) if nrows>1 else 0
    figure.subplots_adjust(left=left_pt/spec.width_pt,right=1-right_pt/spec.width_pt,bottom=bottom_pt/spec.height_pt,top=1-top_pt/spec.height_pt,wspace=wspace,hspace=hspace)
    return figure,axes

def _legend_font_size_pt(kwargs):
    font_size=kwargs.get("fontsize",plt.rcParams["legend.fontsize"])
    return FontProperties(size=font_size).get_size_in_points()

def legend_spacing_kwargs(handle_width_pt,font_size_pt=None,handle_text_gap_pt=DEFAULT_LEGEND_HANDLE_TEXT_GAP_PT,column_gap_pt=DEFAULT_LEGEND_COLUMN_GAP_PT):
    if font_size_pt is None:font_size_pt=FontProperties(size=plt.rcParams["legend.fontsize"]).get_size_in_points()
    return {"handlelength":handle_width_pt/font_size_pt,"handletextpad":handle_text_gap_pt/font_size_pt,"columnspacing":column_gap_pt/font_size_pt}

def _visible_legend_row_gap_pt(legend):
    legend.figure.canvas.draw()
    renderer=legend.figure.canvas.get_renderer()
    bboxes=[text.get_window_extent(renderer) for text in legend.get_texts() if text.get_visible() and text.get_text()]
    rows=[]
    for bbox in sorted(bboxes,key=lambda item:item.y0,reverse=True):
        center=(bbox.y0+bbox.y1)/2
        if not rows or abs(center-rows[-1][0])>0.5:rows.append([center,[bbox]])
        else:rows[-1][1].append(bbox)
    if len(rows)<2:return None
    gaps=[min(bbox.y0 for bbox in upper[1])-max(bbox.y1 for bbox in lower[1]) for upper,lower in zip(rows,rows[1:])]
    return min(gaps)*MPL_POINTS_PER_INCH/legend.figure.dpi

def set_legend_row_gap(legend,row_gap_pt=DEFAULT_LEGEND_ROW_GAP_PT):
    # labelspacing is font-relative, so correct it from the rendered text bounds.
    visible_gap_pt=_visible_legend_row_gap_pt(legend)
    if visible_gap_pt is None:return legend
    correction_pt=row_gap_pt-visible_gap_pt
    for column in legend._legend_handle_box.get_children():
        if hasattr(column,"sep"):column.sep+=correction_pt
    legend.figure.canvas.draw()
    return legend

def legend_above(axis,*args,gap_pt=DEFAULT_LEGEND_GAP_PT,row_gap_pt=DEFAULT_LEGEND_ROW_GAP_PT,**kwargs):
    axes_height_pt=axis.get_position().height*axis.figure.get_figheight()*MPL_POINTS_PER_INCH
    kwargs.setdefault("loc","lower center")
    kwargs.setdefault("bbox_to_anchor",(0.5,1+gap_pt/axes_height_pt))
    kwargs.setdefault("borderaxespad",0)
    kwargs.setdefault("borderpad",0)
    font_size_pt=_legend_font_size_pt(kwargs)
    kwargs["labelspacing"]=row_gap_pt/font_size_pt
    legend=axis.legend(*args,**kwargs)
    return set_legend_row_gap(legend,row_gap_pt)

def _flatten_axes(axes):
    if hasattr(axes,"flat"):return list(axes.flat)
    if isinstance(axes,(list,tuple)):return [axis for item in axes for axis in _flatten_axes(item)]
    return [axes]

def _visible_bboxes(artists,renderer):
    return [artist.get_window_extent(renderer) for artist in artists if artist.get_visible() and artist.get_text()]

def _visible_tick_bboxes(axis,renderer,direction):
    axis_bbox=axis.get_window_extent(renderer)
    artists=axis.get_xticklabels(which="both") if direction=="x" else axis.get_yticklabels(which="both")
    bboxes=_visible_bboxes(artists,renderer)
    if direction=="x":return [bbox for bbox in bboxes if bbox.x1>=axis_bbox.x0 and bbox.x0<=axis_bbox.x1]
    return [bbox for bbox in bboxes if bbox.y1>=axis_bbox.y0 and bbox.y0<=axis_bbox.y1]

def panel_aspect_ratios(*spans,unit_aspect_ratio=DEFAULT_PANEL_ASPECT_RATIO):
    if not spans or any(span<=0 for span in spans):raise ValueError("Panel spans must be positive")
    return tuple(span*unit_aspect_ratio for span in spans)

def layout_panel_row(figure,axes,aspect_ratios,bottom_pt,panel_gap_pt,left_edge_gap_pt,right_edge_gap_pt):
    axes=_flatten_axes(axes)
    if len(axes)!=len(aspect_ratios):raise ValueError("Each panel needs exactly one plot-area aspect ratio")
    figure_width_pt=figure.get_figwidth()*MPL_POINTS_PER_INCH
    figure_height_pt=figure.get_figheight()*MPL_POINTS_PER_INCH
    # Re-measure because moving axes can change which edge tick labels are visible.
    for _ in range(3):
        figure.canvas.draw()
        renderer=figure.canvas.get_renderer()
        decoration_widths=[]
        right_decoration_width_pt=0
        for axis in axes:
            axis_bbox=axis.get_window_extent(renderer)
            candidates=_visible_tick_bboxes(axis,renderer,"x")+_visible_tick_bboxes(axis,renderer,"y")
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

def _axes_rows(axes):
    if hasattr(axes,"shape") and len(axes.shape)==2:return [[axes[row,column] for column in range(axes.shape[1])] for row in range(axes.shape[0])]
    rows=[list(row) for row in axes]
    if not rows or not rows[0] or any(len(row)!=len(rows[0]) for row in rows):raise ValueError("Panel grid must contain equally sized nonempty rows")
    return rows

def layout_panel_grid(figure,axes,aspect_ratios,bottom_pt,column_gap_pt,row_content_gap_pt,left_edge_gap_pt,right_edge_gap_pt):
    rows=_axes_rows(axes)
    if len(rows[0])!=len(aspect_ratios):raise ValueError("Each grid column needs exactly one plot-area aspect ratio")
    figure_width_pt=figure.get_figwidth()*MPL_POINTS_PER_INCH
    figure_height_pt=figure.get_figheight()*MPL_POINTS_PER_INCH
    # First solve the shared column geometry from every row's rendered decorations.
    for _ in range(3):
        figure.canvas.draw()
        renderer=figure.canvas.get_renderer()
        decoration_widths=[]
        right_decoration_width_pt=0
        for column in range(len(rows[0])):
            column_left_width_pt=0
            for row in rows:
                axis=row[column]
                axis_bbox=axis.get_window_extent(renderer)
                candidates=_visible_tick_bboxes(axis,renderer,"x")+_visible_tick_bboxes(axis,renderer,"y")
                if axis.yaxis.label.get_text():candidates.append(axis.yaxis.label.get_window_extent(renderer))
                leftmost=min((bbox.x0 for bbox in candidates),default=axis_bbox.x0)
                column_left_width_pt=max(column_left_width_pt,max(0,(axis_bbox.x0-leftmost)*MPL_POINTS_PER_INCH/figure.dpi))
                if column==len(rows[0])-1:
                    rightmost=max((bbox.x1 for bbox in candidates),default=axis_bbox.x1)
                    right_decoration_width_pt=max(right_decoration_width_pt,max(0,(rightmost-axis_bbox.x1)*MPL_POINTS_PER_INCH/figure.dpi))
            decoration_widths.append(column_left_width_pt)
        available_width_pt=figure_width_pt-left_edge_gap_pt-right_edge_gap_pt-sum(decoration_widths)-right_decoration_width_pt-(len(rows[0])-1)*column_gap_pt
        plot_height_pt=available_width_pt/sum(aspect_ratios)
        if plot_height_pt<=0:raise ValueError("Panel decorations and gaps leave no width for plot areas")
        left_pt=left_edge_gap_pt
        for column,(aspect_ratio,decoration_width_pt) in enumerate(zip(aspect_ratios,decoration_widths)):
            left_pt+=decoration_width_pt
            plot_width_pt=plot_height_pt*aspect_ratio
            for row_index,row in enumerate(rows):
                provisional_bottom_pt=bottom_pt+(len(rows)-1-row_index)*(plot_height_pt+40)
                row[column].set_position([left_pt/figure_width_pt,provisional_bottom_pt/figure_height_pt,plot_width_pt/figure_width_pt,plot_height_pt/figure_height_pt])
            left_pt+=plot_width_pt
            if column<len(rows[0])-1:left_pt+=column_gap_pt
    figure.canvas.draw()
    renderer=figure.canvas.get_renderer()
    # Then stack rows using the visible content below each plot area.
    # Measure every row independently because multiline panel captions extend farther below their plot areas.
    below_heights_pt=[]
    for row in rows:
        row_height_pt=0
        for axis in row:
            axis_bbox=axis.get_window_extent(renderer)
            candidates=_visible_tick_bboxes(axis,renderer,"x")
            if axis.xaxis.label.get_text():candidates.append(axis.xaxis.label.get_window_extent(renderer))
            bottom=min((bbox.y0 for bbox in candidates),default=axis_bbox.y0)
            row_height_pt=max(row_height_pt,(axis_bbox.y0-bottom)*MPL_POINTS_PER_INCH/figure.dpi)
        below_heights_pt.append(row_height_pt)
    # Keep the visible content gap fixed; plot-to-plot spacing then grows only for rows with taller captions.
    row_bottoms_pt=[0.0]*len(rows)
    row_bottoms_pt[-1]=bottom_pt
    for row_index in range(len(rows)-2,-1,-1):row_bottoms_pt[row_index]=row_bottoms_pt[row_index+1]+plot_height_pt+row_content_gap_pt+below_heights_pt[row_index]
    for row_index,row in enumerate(rows):
        for axis in row:
            position=axis.get_position()
            axis.set_position([position.x0,row_bottoms_pt[row_index]/figure_height_pt,position.width,plot_height_pt/figure_height_pt])
    figure.canvas.draw()
    return plot_height_pt

def _x_tick_bottom(axis,renderer):
    bboxes=_visible_tick_bboxes(axis,renderer,"x")
    if not bboxes:raise ValueError("Cannot place a bottom row below an axis without visible x tick labels")
    return min(bbox.y0 for bbox in bboxes)

def align_xlabels(figure,axes,gap_pt=DEFAULT_X_LABEL_GAP_PT):
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

def add_panel_captions(figure,axes,texts,gap_pt=DEFAULT_PANEL_CAPTION_GAP_PT,source="xlabel",**kwargs):
    axes=_flatten_axes(axes)
    if len(axes)!=len(texts):raise ValueError("Each panel needs exactly one caption")
    figure.canvas.draw()
    renderer=figure.canvas.get_renderer()
    if source=="xlabel":source_bboxes=[axis.xaxis.label.get_window_extent(renderer) for axis in axes]
    elif source=="ticks":source_bboxes=[min(_visible_tick_bboxes(axis,renderer,"x"),key=lambda bbox:bbox.y0) for axis in axes]
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
