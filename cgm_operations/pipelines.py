from PyQt5 import QtWidgets, QtGui, QtCore
from cgm_operations.studio_cgm import CgmModel
from functools import partial


class PipelineDialog(QtWidgets.QWidget):
    def __init__(self, pipelines=None):
        super(PipelineDialog, self).__init__(pipelines)
        self.glb_pos = None
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

        move_up = QtWidgets.QPushButton("Move up")
        move_up.setFlat(True)
        move_up.setStyleSheet(style)
        move_up.clicked.connect(partial(pipelines.move_operation, 'up'))
        move_down = QtWidgets.QPushButton("Move down")
        move_down.setFlat(True)
        move_down.setStyleSheet(style)
        move_down.clicked.connect(partial(pipelines.move_operation, 'down'))
        remove = QtWidgets.QPushButton("Remove")
        remove.setFlat(True)
        remove.setStyleSheet(style)
        remove.clicked.connect(pipelines.remove)
        layout.addWidget(move_up)
        layout.addWidget(move_down)
        layout.addWidget(remove)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        self.setLayout(layout)
        self.adjustSize()
        self.setWindowFlags(QtCore.Qt.Popup)

    def init_window(self, glb_pos):
        glb_pos.setX(glb_pos.x() + 5)
        glb_pos.setY(glb_pos.y() + 10)
        self.move(glb_pos)


class Pipelines(QtWidgets.QWidget):
    def __init__(self, mainwindow):
        super(Pipelines, self).__init__(mainwindow)
        self.mainwindow = mainwindow
        self.pipelines_for_selection = []
        self.model_ops = ['Static cgm pipeline', 'Dynamic cgm pipeline']
        self.export_ops = ['Export spreadsheet (.csv)']
        self.mainwindow.ui.pipelineSelectedWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainwindow.ui.pipelineSelectedWidget.customContextMenuRequested.connect(self.show_dialog)
        self.mainwindow.ui.pipelineOperationsWidget.itemDoubleClicked.connect(self.select_operation)
        self.mainwindow.ui.pipelineSelectedWidget.itemClicked.connect(self.static_or_dynamic_check)
        self.mainwindow.ui.pipelineSelectedWidget.itemClicked.connect(self.update_checked_status)
        self.dialog = PipelineDialog(self)
        self.populate_pipelines()
        self.cgm_model = CgmModel(mainwindow)
        self.operation_stack = []
        self.tree_state = dict()
        self.key_order = []

    def show_dialog(self, pos):
        item = self.mainwindow.ui.pipelineSelectedWidget.selectedItems()
        if item:
            item_rect = self.mainwindow.ui.pipelineSelectedWidget.visualItemRect(item[0])
            if item_rect.contains(pos):
                glb_pos = self.mainwindow.ui.pipelineSelectedWidget.mapToGlobal(pos)
                self.dialog.init_window(glb_pos)
                self.dialog.show()

    def populate_pipelines(self):
        # available operations
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
            self.pipelines_for_selection.append(model_op)
            model_layer.addChild(child)

        for export_op in self.export_ops:
            child = QtWidgets.QTreeWidgetItem([export_op])
            self.pipelines_for_selection.append(export_op)
            file_io_layer.addChild(child)

    def select_operation(self, pipeline):
        # either when double clicked on available operations or when restoring from save state
        if not isinstance(pipeline, str):
            pipeline = pipeline.text(0)

        if pipeline in self.pipelines_for_selection:
            self.pipelines_for_selection.remove(pipeline)
            selected_layer = QtWidgets.QTreeWidgetItem([pipeline])

            if pipeline in [*self.tree_state]:  # restore from saved state
                if self.tree_state[pipeline]['checked']:
                    selected_layer.setCheckState(0, QtCore.Qt.Checked)
                else:
                    selected_layer.setCheckState(0, QtCore.Qt.Unchecked)
            else:  # add as new
                self.tree_state[pipeline] = {'checked': False}
                selected_layer.setCheckState(0, QtCore.Qt.Unchecked)
            self.mainwindow.ui.pipelineSelectedWidget.addTopLevelItem(selected_layer)

    def get_pipeline_root_child_count(self):
        root = self.mainwindow.ui.pipelineSelectedWidget.invisibleRootItem()
        count = root.childCount()
        return root, count

    def set_operations(self):
        # add ticked operations to operation stack, which is iterated when pipeline is run
        self.operation_stack = []
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)
            if item.checkState(0):
                operation_name = item.text(0)
                self.operation_stack.append(operation_name)

    def run_pipelines(self, from_operation=None):
        self.mainwindow.emitter.emit('current')
        if self.mainwindow.playing:
            self.mainwindow.messages.set_text('Stop playback before running pipeline')
            return

        if not from_operation:
            self.set_operations()

        for op in self.operation_stack:
            if op in self.model_ops:
                # self.mainwindow.segments.clear()
                # self.mainwindow.plotter.remove_plots()
                op_running = self.cgm_model.scgm_run_model(op)
                self.status_handler(op, op_running)
                if op_running:
                    break

            if op in self.export_ops:
                op_running = self.mainwindow.studio_io_ops.studio_exporter(op, self.cgm_model.current_angles)
                self.status_handler(op, op_running)
                if op_running:
                    break

    def remove_operation(self, operation):
        # this is called from modules when operation is complete (e.g. studio_cgm)
        self.operation_stack.remove(operation)

    def status_handler(self, op, op_running):
        if op_running:
            self.update_status(op, status='running')
        else:
            self.update_status(op, status='failed')

    def update_status(self, op, status):
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)
            if item.text(0) == op:
                if status == 'running':
                    self.mainwindow.ui.playOperations.setEnabled(False)
                    item.setIcon(0, QtGui.QIcon("./Resources/Images/running.png"))
                elif status == 'failed':
                    self.mainwindow.ui.playOperations.setEnabled(True)
                    item.setIcon(0, QtGui.QIcon("./Resources/Images/failed.png"))
                    self.update_progress_bar(0)
                    self.remove_operation(op)
                    self.run_pipelines(from_operation=True)  # move to next operation
                elif status == 'success':
                    self.mainwindow.ui.playOperations.setEnabled(True)
                    item.setIcon(0, QtGui.QIcon("./Resources/Images/success.png"))

    def clear_pipelines(self):
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)
            if item.text(0) != 'Static cgm pipeline':
                item.setIcon(0, QtGui.QIcon())

    def update_pipeline_order(self):
        self.key_order = []
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)
            self.key_order.append(item.text(0))

    def restore_pipeline_order(self, order, pipeline):
        self.key_order = order
        self.tree_state = {k: pipeline[k] for k in self.key_order}

    def restore_pipeline(self):
        for op in [*self.tree_state]:
            self.select_operation(op)

    def update_checked_status(self, initem, column):
        root, child_count = self.get_pipeline_root_child_count()
        for i in range(child_count):
            item = root.child(i)

            if item.checkState(column):
                self.tree_state[item.text(0)]['checked'] = True
            else:
                self.tree_state[item.text(0)]['checked'] = False

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
                            # if modified we need to check status and update accordingly
                            # self.update_checked_status(item, column)

    def update_progress_bar(self, percentage):
        self.mainwindow.ui.pipelineBar.setValue(percentage)

    def move_operation(self, direction):
        count = self.mainwindow.ui.pipelineSelectedWidget.topLevelItemCount()
        if count > 1:
            item = self.mainwindow.ui.pipelineSelectedWidget.currentItem()
            row = self.mainwindow.ui.pipelineSelectedWidget.currentIndex().row()

            if direction == 'up' and row > 0:
                self.mainwindow.ui.pipelineSelectedWidget.takeTopLevelItem(row)
                self.mainwindow.ui.pipelineSelectedWidget.insertTopLevelItem(row - 1, item)
                self.mainwindow.ui.pipelineSelectedWidget.setCurrentItem(item)

            elif direction == 'down' and row < count - 1:
                self.mainwindow.ui.pipelineSelectedWidget.takeTopLevelItem(row)
                self.mainwindow.ui.pipelineSelectedWidget.insertTopLevelItem(row + 1, item)
                self.mainwindow.ui.pipelineSelectedWidget.setCurrentItem(item)

        self.dialog.close()

    def remove(self):
        item = self.mainwindow.ui.pipelineSelectedWidget.currentItem()
        pipeline = item.text(0)
        self.pipelines_for_selection.append(pipeline)
        del self.tree_state[pipeline]
        root = self.mainwindow.ui.pipelineSelectedWidget.invisibleRootItem()
        item.parent() or root.removeChild(item)
        self.dialog.close()


