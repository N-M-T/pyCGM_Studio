from PyQt5 import QtWidgets, QtCore
from sub_windows import gen_sub


class MultiView:
    def __init__(self, ui, vtk3d_widget, vtk2d_widget):
        self.ui = ui
        self.vtk3d_widget = vtk3d_widget
        self.vtk2d_widget = vtk2d_widget

        self.sub_window = gen_sub(widget=self.vtk3d_widget, kind='main')
        self.plot_window = gen_sub(widget=vtk2d_widget, kind='plot')

        self.sub_window.CustomBar.handle_split = self.handle_split
        self.plot_window.CustomBar.handle_split = self.handle_split

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.sub_window)
        self.splitter.addWidget(self.plot_window)
        self.splitter.setSizes([1, 0])
        ui.centralLayout.addWidget(self.splitter)
        self.splitter.handle(1).setEnabled(False)

        self.plot_showing = False
        self.split = False
        self.current_view = "     3D Perspective"
        self.reset_combo()

    def handle_split(self, direction=None, action=None, kind=None, new_view=None):
        if direction == 'horizontal':
            self.splitter.setSizes([1, 1])
            self.splitter.handle(1).setEnabled(True)
            self.split = True
            self.plot_showing = True
            self.splitter.setCollapsible(0, False)
            self.splitter.setCollapsible(1, False)
            # ensure minimum required y axis is always visible
            self.vtk2d_widget.setMinimumHeight(100)

        elif action == 'close':  # we are hiding
            self.splitter.setCollapsible(0, True)
            self.splitter.setCollapsible(1, True)
            self.vtk2d_widget.setMinimumHeight(0)

            if kind == 'main':
                if self.split:
                    self.splitter.setSizes([0, 1])
                    self.split = False
                    self.splitter.handle(1).setEnabled(False)
                    self.current_view = "     Graph"

            elif kind == 'plot':
                if self.split:
                    self.splitter.setSizes([1, 0])
                    self.split = False
                    self.plot_showing = False
                    self.splitter.handle(1).setEnabled(False)
                    self.current_view = "     3D Perspective"

        elif new_view:
            if new_view == self.current_view or self.split:
                self.reset_combo()

            elif not self.split and new_view == "     Graph":
                self.splitter.setSizes([0, 1])
                self.current_view = new_view
                self.splitter.handle(1).setEnabled(False)
                self.plot_showing = True
                self.reset_combo()

            elif not self.split and new_view == "     3D Perspective":
                self.splitter.setSizes([1, 0])
                self.current_view = new_view
                self.splitter.handle(1).setEnabled(False)
                self.plot_showing = False
                self.reset_combo()

    def reset_combo(self):
        self.plot_window.set_combo_box("     Graph", "     3D Perspective")
        self.sub_window.set_combo_box("     3D Perspective", "     Graph")
