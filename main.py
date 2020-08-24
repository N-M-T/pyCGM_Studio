from PyQt5 import QtWidgets, QtCore, QtGui, uic
import sys
import os
from ui.gui import Ui_mainWindow
from vis_support.vtkWidgets import VTK3d
from vis_support.highlighter import Highlighter
from vis_support.picker import Picker
from vis_support.player_handler import Player
from vis_support.emitter import Emitter
from explorer.explorer_widget import ExplorerWidget
from ui.multiview import MultiView
from vis_support.plotter import Plotter
from operations.gaps import Gaps
from vis_support.pycgm_interactor_styles import ChangeStyles
from core.history import Handler, SaveSplineCommand, GapReceiver
from files.files_widget import Files
from operations.pipelines import Pipelines
from files.studio_io import StudioIo
from vis_support.plotter import GraphicsLayoutWidget
from vis_support.force_platforms import ForcePlatforms
from vis_support.trajectories import Trajectories
from vis_support.segments import Segments
from files.vtk_title import VtkTitle
import resources_rc


class MainWindow(QtWidgets.QMainWindow):
    ui: Ui_mainWindow

    def __init__(self):
        super(MainWindow, self).__init__()
        self.playing = False
        self.pycgm_data = None
        self.markers = None
        self.vsk = None

        print("Starting PyCGM Studio")

        from ui import gui
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

        # pass methods to vis_toolkit styles enabling picking and highlighting etc.
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
        # save = QtWidgets.QAction(QtGui.QIcon(self.current_dir + "/resources/images/save.png"), "save", self)
        save = QtWidgets.QAction(QtGui.QIcon(":images/save.png"), "save", self)
        toolbar.addAction(save)
        toolbar.actionTriggered.connect(self.studio_io_ops.save_project)

        # tabify dockwidgets
        self.tabifyDockWidget(self.ui.filesDock, self.ui.toolDock)
        self.tabifyDockWidget(self.ui.toolDock, self.ui.cgmPipelinesDock)
        self.ui.toolDock.setVisible(False)
        self.ui.cgmPipelinesDock.setVisible(False)

        self.read_settings()

    def set_data(self, data):
        # called by setup helper when new data is loaded. This is the main data store
        self.pycgm_data = data

    def set_markers(self, markers):
        # Contains all information about marker sources, colours etc.
        self.markers = markers

    def set_vsk(self, vsk):
        # vsk are Vicon way of storing subject parameters (e.g. leg length, bodymass etc.)
        self.vsk = vsk

    def closeEvent(self, event):
        self.studio_io_ops.save_dialog()
        settings = QtCore.QSettings()
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        settings.setValue('pipeline', self.pipelines.tree_state)
        self.pipelines.update_pipeline_order()
        settings.setValue('pipeline_order', self.pipelines.key_order)
        settings.setValue('tree_last_index', self.files.save_state())
        settings.sync()
        super(MainWindow, self).closeEvent(event)

    def read_settings(self):
        settings = QtCore.QSettings()
        geometry_state = settings.value("geometry")
        window_state = settings.value("windowState")
        if geometry_state:
            self.restoreGeometry(geometry_state)
            self.restoreState(window_state)

        pipeline = settings.value("pipeline")
        pipeline_order = settings.value("pipeline_order")
        if pipeline and pipeline_order:
            self.pipelines.restore_pipeline_order(pipeline_order, pipeline)
            self.pipelines.restore_pipeline()

        last_dir = settings.value('tree_last_index')
        if last_dir:
            self.files.load_state(last_dir)


def userinput():
    print('Press enter to exit')
    input()


if __name__ == "__main__":
    try:
        '''if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
            base_dir, end = os.path.split(application_path)
            ui_path = base_dir + '/ui/gui'
        else:
            application_path = os.path.dirname(__file__)
            ui_path = 'ui/gui'

        with open(ui_path + '.ui') as ui_file:
            with open(ui_path + '.py', "w") as py_ui_file:
                uic.compileUi(ui_file, py_ui_file)'''

        app = QtCore.QCoreApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
            app.setOrganizationDomain('ltd')
            app.setOrganizationName('alg')

        mainWindow = MainWindow()
        mainWindow.show()
        app.exec_()

    except Exception as err:
        print(err)
        userinput()

