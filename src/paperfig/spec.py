from dataclasses import dataclass
import math

MPL_POINTS_PER_INCH=72.0
TEX_POINTS_PER_INCH=72.27
PAPER_COLUMN_WIDTH_PT=252.0
PAPER_TEXT_WIDTH_PT=516.0
PAPER_TEXT_WIDTH_IN=PAPER_TEXT_WIDTH_PT/TEX_POINTS_PER_INCH
RASTER_DPI=300
PAPER_FONT_SIZE=8.0
DEFAULT_PANEL_ASPECT_RATIO=math.sqrt(2)
DEFAULT_X_TICK_GAP_PT=1.5
DEFAULT_LOG_X_TICK_GAP_PT=2.5
DEFAULT_Y_TICK_GAP_PT=1.0
DEFAULT_X_LABEL_GAP_PT=1.0
DEFAULT_Y_LABEL_GAP_PT=1.0
DEFAULT_PANEL_CAPTION_GAP_PT=2.0
DEFAULT_LEGEND_GAP_PT=1.0
DEFAULT_LEGEND_ROW_GAP_PT=1.0
DEFAULT_LEGEND_HANDLE_TEXT_GAP_PT=1.5
DEFAULT_LEGEND_COLUMN_GAP_PT=5.0

@dataclass(frozen=True)
class PaperFigureSpec:
    width_pt:float
    height_pt:float
    dpi:int=RASTER_DPI

    @classmethod
    def column(cls,height_width_ratio=1,width_fraction=1,dpi=RASTER_DPI):
        width_pt=PAPER_COLUMN_WIDTH_PT*width_fraction
        return cls(width_pt,width_pt*height_width_ratio,dpi)

    @classmethod
    def text(cls,height_width_ratio=1,width_fraction=1,dpi=RASTER_DPI):
        width_pt=PAPER_TEXT_WIDTH_PT*width_fraction
        return cls(width_pt,width_pt*height_width_ratio,dpi)

    @property
    def size_in(self):
        return self.width_pt/TEX_POINTS_PER_INCH,self.height_pt/TEX_POINTS_PER_INCH

    @property
    def pixel_size(self):
        width_in,height_in=self.size_in
        return round(width_in*self.dpi),round(height_in*self.dpi)
