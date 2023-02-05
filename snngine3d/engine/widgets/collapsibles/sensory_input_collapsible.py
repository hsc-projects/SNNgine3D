from .base_collapsible_widget import CollapsibleWidget
from snngine3d.engine.widgets import SpinBoxSlider


class SensoryInputCollapsible(CollapsibleWidget):

    class Sliders:
        def __init__(self, window):

            self.sensory_input_current0 = SpinBoxSlider(name='Input Current 0 [I]',
                                                        window=window,
                                                        status_tip='Sensory Input Current 0 [I]',
                                                        prop_id='sensory_input_current0',
                                                        maximum_width=300,
                                                        _min_value=0, _max_value=200)

            self.sensory_input_current1 = SpinBoxSlider(name='Input Current 1 [I]',
                                                        window=window,
                                                        status_tip='Sensory Input Current 1 [I]',
                                                        prop_id='sensory_input_current1',
                                                        maximum_width=300,
                                                        _min_value=0, _max_value=200)

    def __init__(self, parent, window):

        super().__init__(parent=parent, title='Sensory Input')

        self.sliders = self.Sliders(window)
        self.add(self.sliders.sensory_input_current0.widget)
        self.add(self.sliders.sensory_input_current1.widget)
