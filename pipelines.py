from PyQt5 import QtWidgets, QtGui, QtCore
from studio_cgm import CgmModel


class PipelineDialog(QtWidgets.QWidget):
    def __init__(self, tree_widget=None):
        super(PipelineDialog, self).__init__(tree_widget)
        self.glb_pos = None
        self.pipelines_for_selection = []
        self.tree_widget = tree_widget

        layout = QtWidgets.QGridLayout(self)
        style = """ QPushButton::hover{
                             background-color: lightblue;
                             border: 2px solid lightblue;}
                            QPushButton::pressed{
                              border: none;
                              margin: 2px;
                              padding: 2px;}
                            QPushButton::flat{
                              border: none;
                              margin: 2px;
                              padding: 2px;}
                            QPushButton{
                              text-align: left;}"""

        # run = QtWidgets.QPushButton("Run operation")
        # run.setFlat(True)
        # run.setStyleSheet(style)
        remove = QtWidgets.QPushButton("Remove operation")
        remove.setFlat(True)
        remove.setStyleSheet(style)
        remove.clicked.connect(self.remove)
        # layout.addWidget(run)
        layout.addWidget(remove)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.adjustSize()
        self.setWindowFlags(QtCore.Qt.Popup)

    def init_window(self, glb_pos):
        glb_pos.setX(glb_pos.x() + 5)
        glb_pos.setY(glb_pos.y() + 10)
        self.move(glb_pos)

    def remove(self):
        item = self.tree_widget.selectedItems()
        pipeline = item[0].text(0)
        self.pipelines_for_selection.append(pipeline)
        root = self.tree_widget.invisibleRootItem()
        item[0].parent() or root.removeChild(item[0])
        self.close()


class Pipelines:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.dialog = None
        self.mainwindow.ui.pipelineSelectedWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainwindow.ui.pipelineSelectedWidget.customContextMenuRequested.connect(self.show_dialog)
        self.dialog = PipelineDialog(self.mainwindow.ui.pipelineSelectedWidget)
        self.populate_pipelines()
        self.filepath = None
        self.cgm_model = CgmModel(mainwindow)

    def set_loaded_filepath(self, filepath):
        self.filepath = filepath

    def show_dialog(self, pos):
        item = self.mainwindow.ui.pipelineSelectedWidget.selectedItems()
        if item:
            item_rect = self.mainwindow.ui.pipelineSelectedWidget.visualItemRect(item[0])
            if item_rect.contains(pos):
                glb_pos = self.mainwindow.ui.pipelineSelectedWidget.mapToGlobal(pos)
                self.dialog.init_window(glb_pos)
                self.dialog.show()

    def populate_pipelines(self):
        model_layer = QtWidgets.QTreeWidgetItem(["CGM Models"])
        font = QtGui.QFont()
        font.setBold(True)
        model_layer.setFont(0, font)
        self.mainwindow.ui.pipelineOperationsWidget.addTopLevelItem(model_layer)

        model_ops = ['Static cgm pipeline', 'Dynamic cgm pipeline']
        for model_op in model_ops:
            child = QtWidgets.QTreeWidgetItem([model_op])
            self.dialog.pipelines_for_selection.append(model_op)
            model_layer.addChild(child)

    def select_operation(self, item):
        pipeline = item.text(0)
        if pipeline in self.dialog.pipelines_for_selection:
            self.dialog.pipelines_for_selection.remove(pipeline)
            selected_layer = QtWidgets.QTreeWidgetItem([item.text(0)])
            selected_layer.setCheckState(0, QtCore.Qt.Unchecked)
            self.mainwindow.ui.pipelineSelectedWidget.addTopLevelItem(selected_layer)

    def run_pipelines(self):
        if self.mainwindow.playing:
            print("Please stop playback")
            return

        root = self.mainwindow.ui.pipelineSelectedWidget.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if item.checkState(0):
                self.cgm_model.scgm_run_model(item.text(0))
