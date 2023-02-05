from snngine3d.engine.widgets import (
    AllButtonMenuActions,
    ComboBoxFrame,
    G2GInfoDualComboBoxFrame
)

from .base_panel import BasePanel
from snngine3d.engine.widgets.collapsibles import CollapsibleWidget


class LocationGroupInfoPanel(BasePanel):

    def __init__(self, window, buttons: AllButtonMenuActions):

        super().__init__(window)

        self.combo_boxes_collapsible0 = CollapsibleWidget(title='Group Info Display 0')

        self.combo_boxes = []

        self.group_ids_combobox = ComboBoxFrame('Group IDs')
        self.add_combo_box(self.group_ids_combobox)

        self.g_flags_combobox = ComboBoxFrame(
            'G_flags', buttons.ACTUALIZE_G_FLAGS_TEXT.button())
        self.add_combo_box(self.g_flags_combobox)

        self.g_props_combobox = ComboBoxFrame(
            'G_props', buttons.ACTUALIZE_G_PROPS_TEXT.button())
        self.add_combo_box(self.g_props_combobox)

        self.combo_boxes_collapsible1 = CollapsibleWidget(title='Group Info Display 1')
        self.g2g_info_combo_box = G2GInfoDualComboBoxFrame(
            'G2G_info', buttons.ACTUALIZE_G2G_INFO_TEXT.button())
        self.combo_boxes_collapsible1.add(self.g2g_info_combo_box)

        self.addWidget(self.combo_boxes_collapsible0)
        self.addWidget(self.combo_boxes_collapsible1)

    def add_combo_box(self, combo_box):

        self.combo_boxes_collapsible0.add(combo_box)
        # self.addWidget(combo_box)
        self.combo_boxes.append(combo_box)
