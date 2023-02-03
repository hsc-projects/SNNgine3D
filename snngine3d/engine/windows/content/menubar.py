from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMenuBar,
)


class MenuBar(QMenuBar):
    class MenuActions:
        def __init__(self):
            # self.start: QAction = ButtonMenuActions.START_SIMULATION.action()
            # self.pause: QAction = ButtonMenuActions.PAUSE_SIMULATION.action()
            # self.toggle_outergrid: QAction = ButtonMenuActions.TOGGLE_OUTERGRID.action()
            # self.exit: QAction = ButtonMenuActions.EXIT_APP.action()
            self.exit: QAction = ButtonMenuActions.EXIT_APP.action()
            #
            # self.add_selector_box: QAction = ButtonMenuActions.ADD_SELECTOR_BOX.action()
            # self.add_synapsevisual: QAction = ButtonMenuActions.ADD_SYNAPSEVISUAL.action()
            #
            # self.toggle_groups_ids: QAction = ButtonMenuActions.TOGGLE_GROUP_IDS_TEXT.action()
            # self.toggle_g_flags: QAction = ButtonMenuActions.TOGGLE_G_FLAGS_TEXT.action()
            # self.toggle_g_props: QAction = ButtonMenuActions.TOGGLE_G_PROPS_TEXT.action()
            # self.toggle_g2g_info: QAction = ButtonMenuActions.TOGGLE_G2G_INFO_TEXT.action()
            #
            # self.actualize_g_flags: QAction = ButtonMenuActions.ACTUALIZE_G_FLAGS_TEXT.action()
            # self.actualize_g_props: QAction = ButtonMenuActions.ACTUALIZE_G_PROPS_TEXT.action()
            # self.actualize_g2g_info: QAction = ButtonMenuActions.ACTUALIZE_G2G_INFO_TEXT.action()
