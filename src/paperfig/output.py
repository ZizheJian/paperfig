import math
from matplotlib.transforms import Bbox
from .spec import MPL_POINTS_PER_INCH

def _visible_tick_labels(axis,renderer,direction):
    axis_bbox=axis.get_window_extent(renderer)
    artists=axis.get_xticklabels(which="both") if direction=="x" else axis.get_yticklabels(which="both")
    visible=[]
    for artist in artists:
        if not artist.get_visible() or not artist.get_text():continue
        bbox=artist.get_window_extent(renderer)
        intersects=bbox.x1>=axis_bbox.x0 and bbox.x0<=axis_bbox.x1 if direction=="x" else bbox.y1>=axis_bbox.y0 and bbox.y0<=axis_bbox.y1
        if intersects:visible.append(artist)
    return visible

def validate_figure_bounds(figure,tolerance_px=0.5):
    figure.canvas.draw()
    renderer=figure.canvas.get_renderer()
    artists=list(figure.texts)+list(figure.legends)
    for axis in figure.axes:
        artists.extend([axis.xaxis.label,axis.yaxis.label,axis.title])
        artists.extend(_visible_tick_labels(axis,renderer,"x"))
        artists.extend(_visible_tick_labels(axis,renderer,"y"))
        if axis.get_legend() is not None:artists.append(axis.get_legend())
    for artist in artists:
        if not artist.get_visible():continue
        bbox=artist.get_window_extent(renderer)
        if bbox.x0<-tolerance_px or bbox.y0<-tolerance_px or bbox.x1>figure.bbox.x1+tolerance_px or bbox.y1>figure.bbox.y1+tolerance_px:
            description=artist.get_text() if hasattr(artist,"get_text") else artist.__class__.__name__
            raise ValueError(f"Figure decoration exceeds canvas: {description}; artist=({bbox.x0},{bbox.y0},{bbox.x1},{bbox.y1}); figure=({figure.bbox.x0},{figure.bbox.y0},{figure.bbox.x1},{figure.bbox.y1})")

def save_paper_png(figure,path,spec):
    figure.set_size_inches(*spec.size_in,forward=True)
    validate_figure_bounds(figure)
    figure.savefig(path,format="png",dpi=spec.dpi,bbox_inches=None,pad_inches=0,facecolor="white")

def save_paper_png_vertical_crop(figure,path,spec,edge_gap_pt=0):
    figure.set_size_inches(*spec.size_in,forward=True)
    validate_figure_bounds(figure)
    renderer=figure.canvas.get_renderer()
    content_bboxes=[axis.get_tightbbox(renderer) for axis in figure.axes]
    for axis in figure.axes:
        content_bboxes.extend([axis.get_window_extent(renderer),axis.xaxis.label.get_window_extent(renderer),axis.yaxis.label.get_window_extent(renderer),axis.title.get_window_extent(renderer)])
        content_bboxes.extend(label.get_window_extent(renderer) for label in _visible_tick_labels(axis,renderer,"x"))
        content_bboxes.extend(label.get_window_extent(renderer) for label in _visible_tick_labels(axis,renderer,"y"))
        if axis.get_legend() is not None:content_bboxes.append(axis.get_legend().get_window_extent(renderer))
    content_bboxes.extend(text.get_window_extent(renderer) for text in figure.texts if text.get_visible() and text.get_text())
    content_bboxes.extend(legend.get_window_extent(renderer) for legend in figure.legends if legend.get_visible())
    content_bbox=Bbox.union([bbox for bbox in content_bboxes if bbox is not None and bbox.width>0 and bbox.height>0])
    edge_gap_px=edge_gap_pt*spec.dpi/MPL_POINTS_PER_INCH
    bottom_px=max(0,math.floor(content_bbox.y0-edge_gap_px))
    top_px=min(figure.bbox.y1,math.ceil(content_bbox.y1+edge_gap_px))
    crop_bbox=Bbox.from_extents(0,bottom_px/spec.dpi,figure.get_figwidth(),top_px/spec.dpi)
    figure.savefig(path,format="png",dpi=spec.dpi,bbox_inches=crop_bbox,pad_inches=0,facecolor="white")
