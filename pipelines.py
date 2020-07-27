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
        self.model_ops = ['Static cgm pipeline', 'Dynamic cgm pipeline']
        self.export_ops = ['Export spreadsheet (.csv)']
        self.mainwindow.ui.pipelineSelectedWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainwindow.ui.pipelineSelectedWidget.customContextMenuRequested.connect(self.show_dialog)
        self.mainwindow.ui.pipelineOperationsWidget.itemDoubleClicked.connect(self.select_operation)
        self.mainwindow.ui.pipelineSelectedWidget.itemClicked.connect(self.static_or_dynamic_check)
        self.dialog = PipelineDialog(self.mainwindow.ui.pipelineSelectedWidget)
        self.populate_pipelines()
        self.cgm_model = CgmModel(mainwindow)
        self.operation_stack = []

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

        file_io_layer = QtWidgets.QTreeWidgetItem(["Export"])
        file_io_layer.setFont(0, font)
        self.mainwindow.ui.pipelineOperationsWidget.addTopLevelItem(file_io_layer)

        for model_op in self.model_ops:
            child = QtWidgets.QTreeWidgetItem([model_op])
            self.dialog.pipelines_for_selection.append(model_op)
            model_layer.addChild(child)

        for export_op in self.export_ops:
            child = QtWidgets.QTreeWidgetItem([export_op])
            self.dialog.pipelines_for_selection.append(export_op)
            file_io_layer.addChild(child)

    def select_operation(self, item):
        pipeline = item.text(0)
        if pipeline in self.dialog.pipelines_for_selection:
            self.dialog.pipelines_for_selection.remove(pipeline)
            selected_layer = QtWidgets.QTreeWidgetItem([item.text(0)])
            selected_layer.setCheckState(0, QtCore.Qt.Unchecked)
            self.mainwindow.ui.pipelineSelectedWidget.addTopLevelItem(selected_layer)

    def get_pipeline_root_child_count(self):
        root = self.mainwindow.ui.pipelineSelectedWidget.invisibleRootItem()
        count = root.childCount()
        return root, count

    def set_operations(self):
        self.operation_stack = []
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)
            if item.checkState(0):
                operation_name = item.text(0)
                self.operation_stack.append(operation_name)

    def run_pipelines(self, from_operation=None):
        if self.mainwindow.playing:
            print("Please stop playback before running pipeline")
            return

        if not from_operation:
            self.set_operations()

        for op in self.operation_stack:
            if op in self.model_ops:
                op_running = self.cgm_model.scgm_run_model(op)
                self.status_handler(op, op_running)
                break

            if op in self.export_ops:
                op_running = self.mainwindow.studio_io_ops.studio_exporter(op, self.cgm_model.current_angles)
                self.status_handler(op, op_running)
                break

    def remove_operation(self, operation):
        self.operation_stack.remove(operation)

    def status_handler(self, op, op_running):
        if op_running:
            self.update_status(op, status='running')
        else:
            self.update_status(op, status='failed')

    def update_status(self, kind, status):
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)
            if item.text(0) == kind:
                if status == 'running':
                    item.setIcon(0, QtGui.QIcon("./Resources/Images/running.png"))
                elif status == 'failed':
                    item.setIcon(0, QtGui.QIcon("./Resources/Images/failed.png"))
                    self.update_progress_bar(0)
                elif status == 'success':
                    item.setIcon(0, QtGui.QIcon("./Resources/Images/success.png"))

    def clear_pipelines(self):
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)
            if item.text(0) != 'Static cgm pipeline':
                item.setIcon(0, QtGui.QIcon())

    def static_or_dynamic_check(self, item, column):
        # only allow either static or dynamic pipeline to be checked
        if item.checkState(column):
            root, child_count = self.get_pipeline_root_child_count()
            operation = item.text(column)
            if operation in self.model_ops:
                for i in range(child_count):
                    item2 = root.child(i)
                    if item2.checkState(column):
                        to_uncheck = item2.text(column)
                        if to_uncheck != operation and to_uncheck in self.model_ops:
                            item2.setCheckState(column, QtCore.Qt.Unchecked)

    def update_progress_bar(self, percentage):
        self.mainwindow.ui.pipelineBar.setValue(percentage)
