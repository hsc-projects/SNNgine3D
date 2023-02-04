from PyQt6.QtCore import QRect
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMenuBar,
)

from .all_button_menu_actions import AllButtonMenuActions


class MenuBar(QMenuBar):

    class MenuActions:

        def __init__(self, actions: AllButtonMenuActions):

            self.start: QAction = actions.START_SIMULATION.action()
            self.pause: QAction = actions.PAUSE_SIMULATION.action()
            self.toggle_outergrid: QAction = actions.TOGGLE_OUTERGRID.action()
            self.exit: QAction = actions.EXIT_APP.action()

            self.add_selector_box: QAction = actions.ADD_SELECTOR_BOX.action()
            self.add_synapsevisual: QAction = actions.ADD_SYNAPSEVISUAL.action()

            self.toggle_groups_ids: QAction = actions.TOGGLE_GROUP_IDS_TEXT.action()
            self.toggle_g_flags: QAction = actions.TOGGLE_G_FLAGS_TEXT.action()
            self.toggle_g_props: QAction = actions.TOGGLE_G_PROPS_TEXT.action()
            self.toggle_g2g_info: QAction = actions.TOGGLE_G2G_INFO_TEXT.action()

            self.actualize_g_flags: QAction = actions.ACTUALIZE_G_FLAGS_TEXT.action()
            self.actualize_g_props: QAction = actions.ACTUALIZE_G_PROPS_TEXT.action()
            self.actualize_g2g_info: QAction = actions.ACTUALIZE_G2G_INFO_TEXT.action()

    def __init__(self, window, actions: AllButtonMenuActions):

        super().__init__(window)
        self.actions = self.MenuActions(actions=actions)

        self.setGeometry(QRect(0, 0, 440, 130))
        self.setObjectName("menubar")

        self.file_menu = self.addMenu('&File')
        self.file_menu.addAction(self.actions.start)
        self.file_menu.addAction(self.actions.pause)
        self.file_menu.addAction(self.actions.exit)

        self.objects_menu = self.addMenu('&Objects')
        self.objects_menu.addAction(self.actions.add_selector_box)
        self.objects_menu.addAction(self.actions.add_synapsevisual)

        self.view_menu = self.addMenu('&View')
        self.view_menu.addAction(self.actions.toggle_outergrid)

        self.view_menu.addAction(self.actions.toggle_groups_ids)

        self.view_menu.addAction(self.actions.toggle_g_flags)
        self.view_menu.addAction(self.actions.actualize_g_flags)
        self.view_menu.addAction(self.actions.toggle_g_props)
        self.view_menu.addAction(self.actions.actualize_g_props)
        self.view_menu.addAction(self.actions.toggle_g2g_info)
        self.view_menu.addAction(self.actions.actualize_g2g_info)
