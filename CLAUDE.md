# paperfig使用规则

画论文图（Matplotlib）时，用paperfig处理版面：固定纸面宽度和字号，按物理尺寸（pt）摆放面板，渲染后测量文字再定位，导出时只裁掉上下空白。数据读取、画图命令、颜色、标签和单张图的特殊调整都留在各自的项目里。

## 必须遵守

- 最终字号8 pt，导出300 dpi的PNG。
- 宽度用`PaperFigureSpec.column()`（单栏252 pt）或`PaperFigureSpec.text()`（通栏516 pt，可以用`width_fraction`取一部分，例如`5/6`）。导出时保持完整宽度，LaTeX里按原宽度插入，字号才不会被缩放。
- 只用`save_paper_png_vertical_crop`导出。不要用`bbox_inches="tight"`，它会改变导出宽度。
- 所有间距都用pt表示。参数名以`_pt`结尾的，都是最终图里的物理pt。
- 一个面板槽位的绘图区宽高比是`sqrt(2)`。一行面板用整数跨度表示：三个等宽面板用`panel_aspect_ratios(1,1,1)`，第一个占两格用`panel_aspect_ratios(2,1)`。宽高比只算坐标轴边框以内的矩形，不含刻度标签、轴标签、图例和子图标题。确实需要别的比例时，直接传宽高比，例如`(2.4,1.2)`。
- 默认间距：x刻度标签1.5 pt（对数x轴2.5 pt），y刻度标签1 pt，轴标签1 pt，子图标题2 pt，图例到绘图区1 pt，图例行间1 pt。没有特殊原因就用默认值。左右边缘和上下裁剪的留白一般用3 pt。
- paperfig不选刻度位置、不改标签文字、不选颜色，也不判断哪些面板属于一组。这些都在项目脚本里决定。只对某一张图成立的调整写在那张图的脚本里，对所有项目都适用的规则才放进paperfig。

## 在项目里引入

各项目把paperfig作为子模块放在`third_party/paperfig`，画图脚本里把源码目录加进`sys.path`：

```python
paperfig_source=os.path.join(project_root,"third_party/paperfig/src")
if paperfig_source not in sys.path:sys.path.insert(0,paperfig_source)
from paperfig import PaperFigureSpec,apply_paper_style,layout_panel_row,save_paper_png_vertical_crop,style_plot_axis
```

## 调用顺序

1. 创建figure之前调用`apply_paper_style()`。
2. `spec=PaperFigureSpec.column()`或`PaperFigureSpec.text(...)`。
3. `figure,axes=plt.subplots(nrows,ncols,figsize=spec.size_in,dpi=spec.dpi)`。画布先是正方形，这个高度只是临时工作区，导出高度由内容决定。
4. 画数据，设好刻度位置、刻度标签和轴标签。
5. 对每个坐标轴调用`style_plot_axis(axis)`。
6. 所有文字都设好之后，调用`layout_panel_row`或`layout_panel_grid`。它们会测量渲染出的文字，再摆放绘图区。之后如果又改了刻度或标签，要重新调用。
7. 绘图区尺寸定下来之后，用`legend_above`加图例。
8. 用`align_xlabels`把相邻面板的x轴标签对齐到同一行，用`add_panel_captions`加`(a)`、`(b)`这样的子图标题。
9. `save_paper_png_vertical_crop(figure,path,spec,edge_gap_pt=3)`导出，然后`plt.close(figure)`。

## 函数速查

| 函数 | 用途 |
|---|---|
| `apply_paper_style(svg_hashsalt=None,font_size=8,tick_size=None,legend_size=None,serif_fonts=None)` | 设置字体（STIX衬线）和字号。第一个参数不是字号，改字号要写`font_size=` |
| `PaperFigureSpec.column(height_width_ratio=1,width_fraction=1)`、`PaperFigureSpec.text(...)` | 图的宽度和临时高度。`spec.size_in`给`figsize`用 |
| `panel_aspect_ratios(*spans)` | 把整数跨度换成绘图区宽高比 |
| `style_plot_axis(axis,tick_length=1.8,tick_width=0.45,...)` | 刻度朝内，按pt设刻度标签和轴标签的间距、边框线宽 |
| `layout_panel_row(figure,axes,aspect_ratios,bottom_pt,panel_gap_pt,left_edge_gap_pt,right_edge_gap_pt)` | 摆放一行面板，返回绘图区高度（pt） |
| `layout_panel_grid(figure,axes,aspect_ratios,bottom_pt,column_gap_pt,row_content_gap_pt,left_edge_gap_pt,right_edge_gap_pt)` | 摆放多行多列的网格 |
| `legend_above(axis,*args,gap_pt=1,row_gap_pt=1,**kwargs)` | 在某个绘图区上方指定距离处放图例，其余参数传给`axis.legend` |
| `legend_spacing_kwargs(handle_width_pt,font_size_pt=None,handle_text_gap_pt=1.5,column_gap_pt=5)` | 用pt表示图例的线段长度、线段到文字、列间距，结果用`**`展开传给图例。第二个参数是字号，其余间距要用关键字传 |
| `set_legend_row_gap(legend,row_gap_pt=1)` | 把直接用Matplotlib创建的图例行距调成指定pt |
| `align_xlabels(figure,axes,gap_pt=1)` | 把几个面板的x轴标签放到同一行 |
| `add_panel_captions(figure,axes,texts,gap_pt=2,source="xlabel")` | 在x轴标签下方加子图标题。没有x轴标签时用`source="ticks"`，放在刻度标签下方 |
| `add_shared_xlabel(figure,axes,text,gap_pt=2)` | 给几个面板加一个共用的x轴标签 |
| `save_paper_png_vertical_crop(figure,path,spec,edge_gap_pt=0)` | 保持宽度不变，只裁上下空白，导出300 dpi PNG |
| `validate_figure_bounds(figure)` | 检查文字和图例有没有超出画布，导出函数会自动调用 |

## 面板间距

一行里相邻面板的水平间距，按后一个面板左侧有什么来选：

- `PANEL_GAP_WITH_YLABEL_PT`（8 pt）：有y轴标签和刻度标签
- `PANEL_GAP_WITH_YTICKS_PT`（4 pt）：只有刻度标签
- `PANEL_GAP_WITHOUT_Y_DECORATION_PT`（2 pt）：都没有

这些常量是前一个绘图区边框到后一个面板左侧文字的可见距离，文字本身的宽度由layout函数另外测量。

网格里的`row_content_gap_pt`，是上一行刻度标签或x轴标签的底部，到下一行绘图区上边框的可见距离，每一行单独测量。网格的子图标题要先写进各坐标轴的x轴标签，再调用`layout_panel_grid`，这样标题的高度才会算进去，两行的标题也不会挤在一起。

## 常见问题

- `bottom_pt`是最下面一行绘图区到画布底部的距离，要留够x轴标签和子图标题的空间。一行面板加子图标题时，通常28到30 pt。
- 首尾的x刻度标签伸出绘图区时，可以把第一个改成左对齐、最后一个改成右对齐，见`examples/fdwz_tree_ablation/plot.py`。
- 文字超出画布时，导出会报错。这时调整边缘留白或`bottom_pt`，不要绕过检查。
- 图例很密时，可以在那张图的脚本里减小列间距。某个面板的刻度标签有两行时，可以单独调整它的子图标题位置。

## 示例

- `examples/minimal/plot.py`：不需要数据的两面板单栏图，包含完整的调用顺序。
- `examples/fdwz_tree_ablation/plot.py`：用真实数据画的完整例子，包括自定义宽高比、图例顺序和首尾刻度对齐。

## 修改paperfig本身时

- 改动会影响所有用它的项目，只有对所有项目都适用的规则才放进来。
- 改完版面代码后运行`python -m unittest discover -s tests`。
- 改了默认值或函数参数时，同步修改这份说明。
