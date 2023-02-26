from typing import Optional, Union

from PyQt6 import QtCore
from PyQt6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


from vispy.scene import BaseCamera, TurntableCamera
from vispy.scene.cameras.perspective import PerspectiveCamera


from .base_collapsible_widget import CollapsibleWidget, SubCollapsibleFrame
from snngine3d.engine.widgets import SpinBoxSlider


slider_intervals = {
    'scale_factor': (0, 100),
    'fov': (0, 100),

    'elevation': (0, 360),
    'azimuth': (0, 360),
    'roll': (0, 360),

    'distance': (0, 100),
    'translate_speed': (0, 10),
}


class CameraPropertyFrame(SubCollapsibleFrame):

    class Sliders:
        pass
        # scale_factor: SpinBoxSlider = None
        # center: SpinBoxSlider = None
        # fov: SpinBoxSlider = None
        # elevation: SpinBoxSlider = None
        # azimuth: SpinBoxSlider = None
        # roll: SpinBoxSlider = None
        # distance: SpinBoxSlider = None
        # translate_speed: SpinBoxSlider = None

    def __init__(self, parent, window: QMainWindow, camera: BaseCamera,
                 prop_id: str, slider_names: Union[list[str], tuple[str, ...]], label=None,
                 # min_value: Optional[int] = None,
                 # max_value=10
                 ):

        super().__init__(parent)

        if label is None:
            label = prop_id
            label = label[0].upper() + label[1:]
        self.layout().addWidget(QLabel(label))

        self.sliders = self.Sliders()

        sliders_widget = QWidget()

        sliders_layout = QVBoxLayout(sliders_widget)
        sliders_layout.setContentsMargins(0, 0, 0, 0)
        # slider_names = TurntableCamera._state_props + ('distance', 'translate_speed')

        for i in slider_names:

            sbs = SpinBoxSlider(name=i + ':',
                                window=window,
                                _min_value=slider_intervals[i][0],
                                _max_value=slider_intervals[i][1],
                                boxlayout_orientation=QtCore.Qt.Orientation.Horizontal,
                                status_tip=f"{camera.name}.{prop_id}.{i}",
                                prop_id=i,
                                single_step_spin_box=0.1,
                                single_step_slider=10)

            setattr(self.sliders, i, sbs)
            # sbs.widget.setFixedHeight(35)
            sliders_layout.addWidget(sbs.widget)
            sbs.connect_property(camera)

        max_height = 25 + 35 * len(slider_names)
        self.setFixedHeight(max_height)
        sliders_widget.setMaximumHeight(max_height-5)

        self.layout().addWidget(sliders_widget)


class TurntableCameraCollapsible(CollapsibleWidget):

    def __init__(self, camera: TurntableCamera, window, parent=None):

        super().__init__(parent=parent, title=camera.name)

        self.perspective = CameraPropertyFrame(parent=self, window=window, camera=camera,
                                               slider_names=('scale_factor', 'fov'),
                                               prop_id='perspective')

        self.rotation = CameraPropertyFrame(parent=self, window=window, camera=camera,
                                            slider_names=("elevation", "azimuth", "roll"),
                                            prop_id='rotation')
        self.movement = CameraPropertyFrame(parent=self, window=window, camera=camera,
                                            slider_names=(
                                                # "distance",
                                                "translate_speed",),
                                            prop_id='movement')

        self.add(self.perspective)
        self.add(self.rotation)
        self.add(self.movement)


class CameraCollectionCollapsible(CollapsibleWidget):

    def __init__(self, parent):

        super().__init__(parent=parent, title='Cameras')

    def add_camera(self, camera: TurntableCamera, name=None):
        if (not hasattr(camera, 'name')) or (camera.name is None):
            if name is None:
                raise ValueError
            else:
                camera.name = name
        if isinstance(camera, TurntableCamera):
            collapsible = TurntableCameraCollapsible(camera=camera, window=self.window(), parent=self)
        else:
            raise TypeError(f'isinstance(camera, TurntableCamera) = {isinstance(camera, TurntableCamera):}')
        self.add(collapsible)
        return collapsible
