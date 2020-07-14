from PyQt5 import QtWidgets, QtCore, uic
import sys
import os
from gui import Ui_mainWindow
from vtkWidgets import VTK3d, VTK2d
from highlighter import Highlighter
from picker import Picker
from player_handler import Player
from emitter import Emitter
from explorer_widget import ExplorerWidget
from multiview import MultiView
from plotter import Plotter
from gaps import Gaps
from functools import partial
from pycgm_interactor_styles import ChangeStyles
from history import Handler, SaveSplineCommand, GapReceiver
from files_widget import Files
from studio_io import StudioLoader
from pipelines import Pipelines


class MainWindow(QtWidgets.QMainWindow):
    ui: Ui_mainWindow

    def __init__(self):
        super(MainWindow, self).__init__()
        self.playing = False
        self.pycgm_data = None
        self.markers = None
        self.trajectories = None
        self.vsk = None

        import gui
        self.ui = gui.Ui_mainWindow()
        self.ui.setupUi(self)

        # setup vtk widgets
        # 3d
        qwidget3d = QtWidgets.QWidget()
        self.vtk3d_widget = VTK3d(qwidget3d)
        vtk_layout3d = QtWidgets.QHBoxLayout()
        vtk_layout3d.addWidget(self.vtk3d_widget)
        self.vtk3d_widget.setLayout(vtk_layout3d)

        # 2d
        qwidget2d = QtWidgets.QWidget()
        self.vtk2d_widget = VTK2d(qwidget2d)
        vtk_layout2d = QtWidgets.QHBoxLayout()
        vtk_layout2d.addWidget(self.vtk2d_widget)
        self.vtk2d_widget.setLayout(vtk_layout2d)

        # plotter
        self.plotter = Plotter(self)

        # central area multiview
        self.multiview = MultiView(self.ui, self.vtk3d_widget, self.vtk2d_widget)

        # player handler
        self.player = Player(self)

        # explorer widget
        self.explorer_widget = ExplorerWidget(self)
        selmodel = self.ui.explorerTree.selectionModel()
        selmodel.selectionChanged.connect(self.explorer_widget.explorer_selected)
        self.ui.explorerTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # highlighting
        self.highlighter = Highlighter(self)
        self.explorer_widget.set_highlighter(self.highlighter)

        # emitter
        self.emitter = Emitter(self)

        # undo/redo operations
        self.gap_receiver = GapReceiver(self)
        save_spline = SaveSplineCommand(self.gap_receiver)
        self.handler = Handler()
        self.handler.register("save_spline", save_spline)

        # gaps
        self.gaps = Gaps(self)
        self.ui.gapTable.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ui.gapTable.itemClicked.connect(self.gaps.gap_table_selected)
        self.ui.gapTable.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        style = """QTableView::item:selected { 
                       color:white; 
                       background:blue;}
                   QTableCornerButton::section{
                       background-color:#232326;}
                   QHeaderView::section {
                       color:black; 
                       background-color:#f6f6f6;
                       padding:2px;}"""

        self.ui.gapTable.setStyleSheet(style)
        self.ui.gapTable.setColumnCount(2)
        self.ui.gapTable.setHorizontalHeaderLabels(['Trajectory', 'Gaps'])
        header = self.ui.gapTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.ui.gapTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # changing styles
        self.change_styles = ChangeStyles(self.vtk3d_widget)

        # picking glyphs
        self.picker = Picker(self, self.change_styles)

        self.vtk3d_widget.pycgm_trackball_style.set_picker(self.picker)
        self.vtk3d_widget.pycgm_drag_actor_style.set_picker(self.picker)
        self.vtk3d_widget.pycgm_drag_actor_style.set_gaps(self.gaps)

        # pipelines
        self.pipelines = Pipelines(self)
        self.ui.pipelineOperationsWidget.itemDoubleClicked.connect(self.pipelines.select_operation)

        # connect slots and setup buttons/scrollslider
        self.ui.gapFillToolButton.clicked.connect(self.gaps.show_gap_filling)  # show/hide widget
        self.ui.gapLeftButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
        self.ui.gapRightButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
        self.ui.gapRightButton.clicked.connect(partial(self.gaps.gap_shift, 'forward'))
        self.ui.gapLeftButton.clicked.connect(partial(self.gaps.gap_shift, 'backward'))
        self.ui.splineButton.clicked.connect(self.gaps.spline)
        self.ui.undo.clicked.connect(self.gaps.undo_operation)
        self.ui.playOperations.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.ui.playOperations.clicked.connect(self.pipelines.run_pipelines)
        self.ui.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.ui.playButton.clicked.connect(self.player.play)
        self.ui.playButton.setEnabled(False)
        self.ui.vtkScrollSlider.valueChanged[int].connect(self.emitter.emit)
        self.ui.vtkScrollSlider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.ui.vtkScrollSlider.setEnabled(False)
        self.ui.vtkScrollSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)

        # tabify dockwidgets
        self.tabifyDockWidget(self.ui.filesDock, self.ui.toolDock)
        self.tabifyDockWidget(self.ui.toolDock, self.ui.cgmPipelinesDock)
        self.ui.toolDock.setVisible(False)
        self.ui.cgmPipelinesDock.setVisible(False)

        # files browser
        self.files = Files(self, self.ui)

        # loader
        self.studio_loader = StudioLoader(self)

    def set_data(self, data):
        self.pycgm_data = data

    def set_markers(self, markers):
        self.markers = markers

    def set_trajectories(self, trajectories):
        self.trajectories = trajectories

    def set_vsk(self, vsk):
        self.vsk = vsk


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    # recompile ui
    with open("Gui.ui") as ui_file:
        with open("Gui.py", "w") as py_ui_file:
            uic.compileUi(ui_file, py_ui_file)

    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()
    # mainWindow.showMaximized() #turned off for development
    app.exec_()
