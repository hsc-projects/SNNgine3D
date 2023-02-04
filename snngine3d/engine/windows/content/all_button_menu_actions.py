from PyQt6.QtWidgets import QMainWindow

from snngine3d.utils import boxed_string
from .ui_widgets import ButtonMenuAction


class AllButtonMenuActions:

    def __init__(self, window):

        print('\n', boxed_string("Shortcuts"))

        self.window: QMainWindow = window

        self.START_SIMULATION: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Start Simulation',
            menu_short_cut='F9',
            status_tip='Start Simulation',
            icon_name='control.png',
            window=self.window)

        self.PAUSE_SIMULATION: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Pause Simulation',
            menu_short_cut='F10',
            status_tip='Pause Simulation',
            icon_name='control-pause.png',
            disabled=True,
            window=self.window)

        self.EXIT_APP: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Exit',
            name='Exit',
            status_tip='Close Application',
            menu_short_cut='Ctrl+Q',
            window=self.window)

        self.TOGGLE_OUTERGRID: ButtonMenuAction = ButtonMenuAction(
            menu_name='&OuterGrid',
            name='Show OuterGrid',
            status_tip='Show/Hide OuterGrid',
            menu_short_cut='Ctrl+G',
            checkable=True, window=self.window)

        self.ADD_SELECTOR_BOX: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Add SelectorBox',
            name='Add SelectorBox',
            status_tip='Add SelectorBox',
            window=self.window)

        self.ADD_SYNAPSEVISUAL: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Add SynapseVisual',
            name='Add SynapseVisual',
            status_tip='Add SynapseVisual',
            window=self.window)

        self.ACTUALIZE_G_FLAGS_TEXT: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Refresh displayed G_flags',
            menu_short_cut='F7',
            icon_name='arrow-circle.png',
            status_tip='Refresh displayed G_flags values',
            window=self.window)

        self.ACTUALIZE_G_PROPS_TEXT: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Refresh displayed G2G_info',
            menu_short_cut='F6',
            icon_name='arrow-circle.png',
            status_tip='Refresh displayed G2G_info values',
            window=self.window)

        self.ACTUALIZE_G2G_INFO_TEXT: ButtonMenuAction = ButtonMenuAction(
            menu_short_cut='F5',
            menu_name='&Refresh displayed G2G_flags ',
            icon_name='arrow-circle.png',
            status_tip='Refresh displayed G2G_flags values',
            window=self.window)

        self.TOGGLE_GROUP_IDS_TEXT: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Group IDs',
            menu_short_cut='Ctrl+F8',
            checkable=True,
            status_tip='Show/Hide Group IDs',
            window=self.window)

        self.TOGGLE_G_FLAGS_TEXT: ButtonMenuAction = ButtonMenuAction(
            menu_name='&G_flags Text',
            checkable=True,
            menu_short_cut='Ctrl+F7',
            status_tip='Show/Hide G_flags values',
            window=self.window)

        self.TOGGLE_G_PROPS_TEXT: ButtonMenuAction = ButtonMenuAction(
            menu_name='&G_Props Text',
            checkable=True,
            menu_short_cut='Ctrl+F6',
            status_tip='Show/Hide G_props values',
            window=self.window)

        self.TOGGLE_G2G_INFO_TEXT: ButtonMenuAction = ButtonMenuAction(
            menu_name='&G2G_info Text',
            checkable=True,
            menu_short_cut='Ctrl+F5',
            status_tip='Show/Hide G2G_info values',
            window=self.window)


