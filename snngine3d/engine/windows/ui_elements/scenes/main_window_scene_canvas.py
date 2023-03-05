from copy import copy
# from typing import Optional
import numpy as np

from vispy.visuals.transforms import STTransform
from vispy.util import keys
from vispy.scene import (Grid, TurntableCamera, ViewBox, XYZAxis)

# from network import SpikingNeuralNetwork
# from rendering import RenderedObject
from .widgets import (
    BaseEngineSceneCanvas,
    BasePlotWidget,
    GroupFiringsPlotWidget,
    GroupInfoColorBar,
    ScatterPlotWidget,
    TextTableWidget,
    VoltagePlotWidget,
)
from .canvas_config import CanvasConfig

from snngine3d.config_models import PlottingConfig
from snngine3d.geometry.vector import LineSegment
from snngine3d.vispy_torch_interop import RenderedObject


class MainSceneCanvas(BaseEngineSceneCanvas):

    # noinspection PyTypeChecker
    def __init__(self,
                 conf: CanvasConfig,
                 app,
                 ):

        super().__init__(conf, app)

        self.unfreeze()

        # self.network: Optional[SpikingNeuralNetwork] = None

        self.n_voltage_plots = None
        self.voltage_plot_length = None
        self.n_scatter_plots = None
        self.scatter_plot_length = None

        self.voltage_plot = None
        self.scatter_plot = None
        self.group_firings_multiplot = None
        self.color_bar = None
        self.group_firings_plot_single0 = None
        self.group_firings_plot_single1 = None

        self.network_view: ViewBox = self.central_widget.add_view()

        self.grid: Grid = self.network_view.add_grid()

        self.network_view.camera = TurntableCamera(name='Camera0')
        axis = XYZAxis(parent=self.network_view.scene)
        axis.transform = STTransform()
        axis.transform.move((-0.1, -0.1, -0.1))

        self._row_span_0 = 2
        self._col_span0 = 2
        self._plot_row0 = 0
        self._plot_col0 = 0
        self._plot_col1 = 4
        self._plot_col2 = self._plot_col1 + self._col_span0
        self._plot_row1 = self._plot_row0 + self._row_span_0
        self._row_span10 = 2
        self._row_span_11 = 1
        self._height_min0 = 350
        self._height_max1 = 500

        self.table = TextTableWidget(labels=['t', 'update_duration'])
        self.grid.add_widget(self.table, 0, self._plot_col2+1)

        self._clicked_obj = None
        self._selected_objects = []
        self._last_selected_obj = None

        self._click_pos = np.zeros(2)
        self._last_cursor_pos = np.zeros(2)
        self._last_mouse_drag = LineSegment(
            p_start=self._click_pos,
            p_end=self._last_cursor_pos)

        self.mouse_pressed = True

        self.grid_transform = self.scene.node_transform(self.grid)

        self.network = None

        self.freeze()

    def add_plot_widgets(self, plotting_config: PlottingConfig):

        self.n_voltage_plots = plotting_config.n_voltage_plots
        self.voltage_plot_length = plotting_config.voltage_plot_length
        self.n_scatter_plots = plotting_config.n_scatter_plots
        self.scatter_plot_length = plotting_config.scatter_plot_length

        if plotting_config.windowed_multi_neuron_plots is False:
            if plotting_config.has_voltage_multiplot is True:
                self.voltage_plot = VoltagePlotWidget(plotting_confing=plotting_config,
                                                      width_max=600, height_min=self._height_min0)
                self.grid.add_widget(self.voltage_plot, self._plot_row0, self._plot_col0, row_span=self._row_span_0,
                                     col_span=self._col_span0)
            if plotting_config.has_firing_scatterplot is True:
                self.scatter_plot = ScatterPlotWidget(plotting_confing=plotting_config,
                                                      width_max=600, height_max=self._height_max1)
                self.grid.add_widget(self.scatter_plot, self._plot_row1, self._plot_col0, row_span=self._row_span10,
                                     col_span=self._col_span0)

        if plotting_config.group_info_view_mode.scene is True:
            if plotting_config.has_group_firings_multiplot is True:
                self.group_firings_multiplot = GroupFiringsPlotWidget(plotting_confing=plotting_config)
                self.grid.add_widget(self.group_firings_multiplot, self._plot_row1, self._plot_col1,
                                     col_span=self._col_span0, row_span=self._row_span10)
            self.color_bar = GroupInfoColorBar()
            self.grid.add_widget(self.color_bar, self._plot_row1, self._plot_col0 + self._col_span0,
                                 self._row_span10, 1)
        if plotting_config.has_group_firings_plot0:
            self.group_firings_plot_single0 = BasePlotWidget(
                title="Group Firings 0:",
                plot_height=1, plot_length=self.scatter_plot_length,
                cam_yscale=1)
            self.grid.add_widget(self.group_firings_plot_single0, self._plot_row1, self._plot_col2,
                                 col_span=self._col_span0, row_span=self._row_span_11)
        if plotting_config.has_group_firings_plot1:
            self.group_firings_plot_single1 = BasePlotWidget(
                title="Group Firings 1:",
                plot_height=1, plot_length=self.scatter_plot_length)
            self.grid.add_widget(self.group_firings_plot_single1, self._plot_row1 + self._row_span_11, self._plot_col2,
                                 col_span=2, row_span=self._row_span_11)

    def set_keys(self, keys_):
        self.unfreeze()
        # noinspection PyProtectedMember
        self._set_keys(keys_)
        self.freeze()

    def mouse_pos(self, event):
        return self.grid_transform.map(event.pos)[:2]

    def _select_clicked_obj(self):

        if self._clicked_obj is not self._last_selected_obj:
            # TODO: uncomment
            # self.network.neurons._neuron_visual.face_color[:, 3] = 0.05
            # self.network.neurons._neuron_visual.edge_color[:, 3] = 0.05
            # self.network.neurons._neuron_visual.set_gl_state(depth_test=False)

            for o in copy(self._selected_objects):
                if ((not (o is self._clicked_obj))
                        and ((self._clicked_obj is None) or (not o.is_select_child(self._clicked_obj)))):
                    self._select(o, False)

            if isinstance(self._clicked_obj, RenderedObject):
                if self._clicked_obj.selected:
                    # self.clicked_obj.on_select_callback(self.clicked_obj.selected)
                    self._clicked_obj.update()
                    self._last_selected_obj = self._clicked_obj
                else:
                    # print('\nSELECTED:', self._clicked_obj)
                    self._select(self._clicked_obj, True)

    def on_mouse_press(self, event):

        if event.button == 1:
            self.network_view.camera.interactive = False
            self.network_view.interactive = False
            self._clicked_obj = self.visual_at(event.pos)

            self.network_view.interactive = True
            self._click_pos[:2] = event.pos

            import vispy
            # pos = self.mouse_pos(event)
            o: vispy.visuals.Visual = self.visual_at(event.pos)
            v = self.network_view
            c = v.camera
            try:
                verts = np.array([[-.25, -.25, -.25], [.25, -.25, -.25], [-.25, .25, -.25], [-.25, -.25, .25]])

                dir0x_3d = verts[0] + (verts[1] - verts[0]) / 2
                dir0y_3d = verts[0] + (verts[2] - verts[0]) / 2
                dir0z_3d = verts[0] + (verts[3] - verts[0]) / 2

                vert0_canvas = o.get_transform('visual', 'canvas').map(verts)
                dir0x_3d_canvas = o.get_transform('visual', 'canvas').map(dir0x_3d)
                dir0y_3d_canvas = o.get_transform('visual', 'canvas').map(dir0y_3d)
                dir0z_3d_canvas = o.get_transform('visual', 'canvas').map(dir0z_3d)

                vert0_canvas2d = vert0_canvas[:, :2]/vert0_canvas[:, 3][:, None]

                dir0x_2d_0 = dir0x_3d_canvas[:2]/dir0x_3d_canvas[3]
                dir0x_2d_1 = vert0_canvas2d[0] + (vert0_canvas2d[1] - vert0_canvas2d[0])/2

                dir0y_2d_0 = dir0y_3d_canvas[:2]/dir0y_3d_canvas[3]
                dir0y_2d_1 = vert0_canvas2d[0] + (vert0_canvas2d[2] - vert0_canvas2d[0])/2

                dir0z_2d_0 = dir0z_3d_canvas[:2]/dir0z_3d_canvas[3]
                dir0z_2d_1 = vert0_canvas2d[0] + (vert0_canvas2d[3] - vert0_canvas2d[0])/2
            except:
                pass
            if isinstance(self._clicked_obj, RenderedObject) and self._clicked_obj.draggable:
                self._select_clicked_obj()

    def _mouse_moved(self, event):
        # self._last_mouse_pos[:2] = self.mouse_pos(event)
        self._last_cursor_pos[:2] = event.pos
        return (self._last_cursor_pos[:2] - self._click_pos[:2]).any()

    def _select(self, obj: RenderedObject, v: bool):
        obj.select(v)
        if v is True:
            self._selected_objects.append(obj)
            self._last_selected_obj = obj
        else:
            self._selected_objects.remove(obj)
            if obj is self._last_selected_obj:
                self._last_selected_obj = None
        return obj

    def on_mouse_release(self, event):
        self.network_view.camera.interactive = True
        if event.button == 1:
            if (not self._mouse_moved(event)) or (self._clicked_obj is self.visual_at(event.pos)):
                self._select_clicked_obj()
            if isinstance(self._last_selected_obj, RenderedObject) and self._last_selected_obj.draggable:
                self._select(self._last_selected_obj, False).update()
                self._last_selected_obj = self._selected_objects[-1]

            print(f'currently selected ({len(self._selected_objects)}):', self._selected_objects)
            # TODO: uncomment
            # if len(self._selected_objects) == 0:
            #     self.network.neurons._neuron_visual.face_color[:, 3] = 0.3
            #     self.network.neurons._neuron_visual.edge_color[:, 3] = 0.5
            #     self.network.neurons._neuron_visual.set_gl_state(depth_test=True)

    def on_mouse_move(self, event):
        self.network_view.camera.interactive = True
        if event.button == 1:
            if isinstance(self._clicked_obj, RenderedObject) and self._clicked_obj.draggable:
                self.network_view.camera.interactive = False
                self._last_cursor_pos[:2] = event.pos

                cursor_pos_diff = self._last_cursor_pos - self._click_pos
                if keys.SHIFT in event.modifiers:
                    mode = 0
                elif keys.CONTROL in event.modifiers:
                    mode = 1
                else:
                    mode = 2
                self._last_mouse_drag.set_p_start(self._click_pos)
                self._last_mouse_drag.set_p_start(self._last_cursor_pos)
                self._clicked_obj.on_drag_callback(drag=self._last_mouse_drag, mode=mode)
