from .base_collapsible_widget import CollapsibleWidget
from snngine3d.engine.widgets import SpinBoxSlider


class ThalamicInputCollapsible(CollapsibleWidget):

    class Sliders:
        def __init__(self, window):

            self.thalamic_inh_input_current = SpinBoxSlider(name='Inhibitory Current [I]',
                                                            window=window,
                                                            status_tip='Thalamic Inhibitory Input Current [I]',
                                                            prop_id='thalamic_inh_input_current',
                                                            maximum_width=300,
                                                            _min_value=0, _max_value=250)

            self.thalamic_exc_input_current = SpinBoxSlider(name='Excitatory Current [I]',
                                                            window=window,
                                                            status_tip='Thalamic Excitatory Input Current [I]',
                                                            prop_id='thalamic_exc_input_current',
                                                            maximum_width=300,
                                                            _min_value=0, _max_value=250)

    def __init__(self, parent, window):

        super().__init__(parent=parent, title='Thalamic Input')

        self.sliders = self.Sliders(window)
        self.add(self.sliders.thalamic_inh_input_current.widget)
        self.add(self.sliders.thalamic_exc_input_current.widget)
