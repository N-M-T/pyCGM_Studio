from PyQt5 import QtWidgets, QtCore, QtGui, uic
import sys
import os
from gui import Ui_mainWindow
from vtkWidgets import VTK3d
from highlighter import Highlighter
from picker import Picker
from player_handler import Player
from emitter import Emitter
from explorer_widget import ExplorerWidget
from multiview import MultiView
from plotter import Plotter
from gaps import Gaps
from pycgm_interactor_styles import ChangeStyles
from history import Handler, SaveSplineCommand, GapReceiver
from files_widget import Files
from pipelines import Pipelines
from studio_io import StudioIo
from plotter import GraphicsLayoutWidget
from force_platforms import ForcePlatforms
from trajectories import Trajectories
from segments import Segments
from vtk_title import VtkTitle


class MainWindow(QtWidgets.QMainWindow):
    ui: Ui_mainWindow

    def __init__(self):
        super(MainWindow, self).__init__()
        self.playing = False
        self.pycgm_data = None
        self.markers = None
        self.vsk = None

        import gui
        self.ui = gui.Ui_mainWindow()
        self.ui.setupUi(self)

        # setup vtk3d widget
        qwidget3d = QtWidgets.QWidget()  # 3d
        self.vtk3d_widget = VTK3d(qwidget3d)
        self.vtk_title = VtkTitle(self)

        # pyqtgraph widget (formally vtk2d)
        self.pyqtgraph2d_widget = GraphicsLayoutWidget()

        # pycgm classes
        self.plotter = Plotter(self)
        self.multiview = MultiView(self.ui, self.vtk3d_widget, self.pyqtgraph2d_widget)

        self.player = Player(self)
        self.explorer_widget = ExplorerWidget(self)
        self.highlighter = Highlighter(self)
        self.trajectories = Trajectories(self)
        self.explorer_widget.set_highlighter(self.highlighter)
        self.emitter = Emitter(self)
        self.gap_receiver = GapReceiver(self)
        self.handler = Handler("save_spline", SaveSplineCommand(self.gap_receiver))
        self.gaps = Gaps(self)
        self.change_styles = ChangeStyles(self.vtk3d_widget)
        self.picker = Picker(self, self.change_styles)
        self.pipelines = Pipelines(self)
        self.files = Files(self)
        self.studio_io_ops = StudioIo(self)
        self.force_platforms = ForcePlatforms(self)
        self.segments = Segments(self)

        # pass methods to vtk styles enabling picking and highlighting etc.
        self.vtk3d_widget.pycgm_trackball_style.set_picker(self.picker)
        self.vtk3d_widget.pycgm_drag_actor_style.set_picker(self.picker)
        self.vtk3d_widget.pycgm_drag_actor_style.set_gaps(self.gaps)

        # connect slots/setup scrollslider
        self.ui.playOperations.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.ui.playOperations.clicked.connect(self.pipelines.run_pipelines)
        self.ui.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.ui.playButton.clicked.connect(self.player.play)
        self.ui.playButton.setEnabled(False)
        self.ui.vtkScrollSlider.valueChanged[int].connect(self.emitter.emit)
        self.ui.vtkScrollSlider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.ui.vtkScrollSlider.setEnabled(False)
        self.ui.vtkScrollSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)

        # setup toolbar
        toolbar = self.addToolBar("File")
        save = QtWidgets.QAction(QtGui.QIcon("./Resources/Images/save.png"), "save", self)
        toolbar.addAction(save)
        toolbar.actionTriggered.connect(self.studio_io_ops.save_project)

        # tabify dockwidgets
        self.tabifyDockWidget(self.ui.filesDock, self.ui.toolDock)
        self.tabifyDockWidget(self.ui.toolDock, self.ui.cgmPipelinesDock)
        self.ui.toolDock.setVisible(False)
        self.ui.cgmPipelinesDock.setVisible(False)

    def set_data(self, data):
        # called by setup helper when new data is loaded. This is the main data store
        self.pycgm_data = data

    def set_markers(self, markers):
        # Contains all information about marker sources, colours etc.
        self.markers = markers

    def set_vsk(self, vsk):
        # vsk are Vicon way of storing subject parameters (e.g. leg length, bodymass etc.)
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
