from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np


def custom_handle(splitter, direction):
    handle = splitter.handle(1)
    layout = QtWidgets.QVBoxLayout(handle)
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)

    line = QtWidgets.QFrame(handle)
    if direction == 'Horizontal':
        line.setFrameShape(QtWidgets.QFrame.HLine)
    elif direction == 'Vertical':
        line.setFrameShape(QtWidgets.QFrame.VLine)

    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(line)


def tree_find(tree, marker):
    return tree.findItems(marker, QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive, 0)


class ExplorerWidget:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        selmodel = self.mainwindow.ui.explorerTree.selectionModel()
        selmodel.selectionChanged.connect(self.explorer_selected)
        self.mainwindow.ui.explorerTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.highlighter = None
        self.marker_names = None
        self.model_names = None
        self.channel_names = None
        self.setup_splitter()

    def clear(self):
        self.mainwindow.ui.explorerTree.clear()

    def set_highlighter(self, highlighter):
        self.highlighter = highlighter

    def populate_tree(self):
        self.marker_names = [*self.mainwindow.pycgm_data.Data['Markers']]
        self.channel_names = [*self.mainwindow.pycgm_data.Data['Analogs']]

        # markers
        markers_name = "Markers [" + str(self.mainwindow.pycgm_data.Gen['Vid_SampRate']) + "Hz]"
        marker_layer = QtWidgets.QTreeWidgetItem([markers_name])
        marker_layer.setIcon(0, QtGui.QIcon("./Resources/Images/markerballs.png"))
        self.mainwindow.ui.explorerTree.addTopLevelItem(marker_layer)

        # analog channels
        analog_sfreq = self.mainwindow.pycgm_data.Gen['Analog_SampRate']
        if analog_sfreq > 0:
            devices_name = "Devices [" + str(analog_sfreq) + "Hz]"
        else:
            devices_name = "Devices"
        analog_layer = QtWidgets.QTreeWidgetItem([devices_name])
        analog_layer.setIcon(0, QtGui.QIcon("./Resources/Images/devices.png"))
        self.mainwindow.ui.explorerTree.addTopLevelItem(analog_layer)

        # model outputs
        model_layer = QtWidgets.QTreeWidgetItem(["Model Outputs"])
        model_layer.setIcon(0, QtGui.QIcon("./Resources/Images/models.png"))
        self.mainwindow.ui.explorerTree.addTopLevelItem(model_layer)

        # add marker source
        for marker in [*self.mainwindow.pycgm_data.Data['Markers']]:
            if marker[0] != '*':
                marker_child = QtWidgets.QTreeWidgetItem([marker])
                marker_child.setIcon(0, QtGui.QIcon("./Resources/Images/shinyball.png"))
                marker_layer.addChild(marker_child)

        # add analog source
        # find and add force platforms
        # possible names for force platform channels
        fp_targets = ['Force.Fx', 'Fx', 'ForceFx', 'Force.Fx.', 'Fx.', 'ForceFx.',
                      'Force.Fy', 'Fy', 'ForceFy', 'Force.Fy.', 'Fy.', 'ForceFy.',
                      'Force.Fz', 'Fz', 'ForceFz', 'Force.Fz.', 'Fz.', 'ForceFz.',
                      'Moment.Mx', 'Mx', 'MomentMx', 'Moment.Mx.', 'Mx.', 'MomentMx.',
                      'Moment.My', 'My', 'MomentMy', 'Moment.My.', 'My.', 'MomentMy.',
                      'Moment.Mz', 'Mz', 'MomentMz', 'Moment.Mz.', 'Mz.', 'MomentMz.']

        force_targets = ['Fx', 'Fy', 'Fz']
        moment_targets = ['Mx', 'My', 'Mz']
        cop_targets = ['Cx', 'Cy', 'Cz']
        fp_count = 1

        for analog in [*self.mainwindow.pycgm_data.Data['Analogs']]:
            fp_targs = [s + str(fp_count) for s in fp_targets]

            if analog in fp_targs:
                fp_name = "#" + str(fp_count) + " Force platform"

                analog_child = QtWidgets.QTreeWidgetItem([fp_name])
                analog_child.setIcon(0, QtGui.QIcon("./Resources/Images/play.png"))
                analog_layer.addChild(analog_child)

                force_child = QtWidgets.QTreeWidgetItem(["Force"])
                force_child.setIcon(0, QtGui.QIcon("./Resources/Images/subplay.png"))
                moment_child = QtWidgets.QTreeWidgetItem(["Moment"])
                moment_child.setIcon(0, QtGui.QIcon("./Resources/Images/subplay.png"))
                cop_child = QtWidgets.QTreeWidgetItem(["CoP"])
                cop_child.setIcon(0, QtGui.QIcon("./Resources/Images/subplay.png"))

                analog_child.addChild(force_child)
                analog_child.addChild(moment_child)
                analog_child.addChild(cop_child)

                for f_targ, m_targ, c_targ in zip(force_targets, moment_targets, cop_targets):
                    f_child = QtWidgets.QTreeWidgetItem([f_targ])
                    f_child.setIcon(0, QtGui.QIcon("./Resources/Images/subsubplay.png"))
                    force_child.addChild(f_child)

                    m_child = QtWidgets.QTreeWidgetItem([m_targ])
                    m_child.setIcon(0, QtGui.QIcon("./Resources/Images/subsubplay.png"))
                    moment_child.addChild(m_child)

                    cp = QtWidgets.QTreeWidgetItem([c_targ])
                    cp.setIcon(0, QtGui.QIcon("./Resources/Images/subsubplay.png"))
                    cop_child.addChild(cp)

                fp_count += 1

        # display other analog channels
        if len([*self.mainwindow.pycgm_data.Data['Analogs']]) > 0:
            analog_child = QtWidgets.QTreeWidgetItem(["Analog channels"])
            analog_child.setIcon(0, QtGui.QIcon("./Resources/Images/play.png"))
            analog_layer.addChild(analog_child)

            ch_count = 1
            for analog in [*self.mainwindow.pycgm_data.Data['Analogs']]:
                raw_child = QtWidgets.QTreeWidgetItem([analog])
                raw_child.setIcon(0, QtGui.QIcon("./Resources/Images/subsubplay.png"))
                analog_child.addChild(raw_child)
                ch_count += 1

        # add model outputs
        outputs = 'Angles,Forces,Moments,Bones,Powers'
        outputs = outputs.split(',')

        for output in outputs:
            if output in [*self.mainwindow.pycgm_data.Data] and len(self.mainwindow.pycgm_data.Data[output]) > 0:
                output_child = QtWidgets.QTreeWidgetItem([output])
                output_child.setIcon(0, QtGui.QIcon("./Resources/Images/modelchild1.png"))
                model_layer.addChild(output_child)

                for variable in [*self.mainwindow.pycgm_data.Data[output]]:
                    output_child2 = QtWidgets.QTreeWidgetItem([variable])
                    output_child2.setIcon(0, QtGui.QIcon("./Resources/Images/modelchild2.png"))
                    output_child.addChild(output_child2)

    def update_cgm_model_outputs(self):
        # remove present layer
        root = self.mainwindow.ui.explorerTree.invisibleRootItem()
        count = root.childCount()
        for i in range(count):
            item = root.child(i)
            if item.text(0) == 'PyCGM Model Outputs':
                to_delete = self.mainwindow.ui.explorerTree.takeTopLevelItem(i)
                del to_delete

        pycgm_model_layer = QtWidgets.QTreeWidgetItem(['PyCGM Model Outputs'])
        pycgm_model_layer.setIcon(0, QtGui.QIcon("./Resources/Images/models.png"))
        pycgm_model_layer.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)
        self.mainwindow.ui.explorerTree.addTopLevelItem(pycgm_model_layer)

        for variable in [*self.mainwindow.pycgm_data.Data['PyCGM Model Outputs']]:
            output_child = QtWidgets.QTreeWidgetItem([variable])
            output_child.setIcon(0, QtGui.QIcon("./Resources/Images/modelchild2.png"))
            pycgm_model_layer.addChild(output_child)

    def explorer_selected(self, selected, deselected):
        if selected:
            count = len(selected.indexes())
            for index in selected.indexes():
                item = self.mainwindow.ui.explorerTree.itemFromIndex(index)
                marker_name = item.text(0)
                if marker_name in self.marker_names:
                    self.highlighter.highlighter_picked_handler(marker_name, from_explorer=True, selected=True)
                else:
                    self.mainwindow.plotter.plotter_picked_handler(item, selected=True, count=count)

        if deselected:
            count = len(deselected.indexes())
            for index in deselected.indexes():
                item = self.mainwindow.ui.explorerTree.itemFromIndex(index)
                marker_name = item.text(0)
                if marker_name in self.marker_names:
                    self.highlighter.highlighter_picked_handler(marker_name, from_explorer=True, deselected=True)
                else:
                    self.mainwindow.plotter.plotter_picked_handler(item, deselected=True, count=count)

    def highlight_marker_tree(self, marker, highlight=None, dehighlight=None):
        items = tree_find(self.mainwindow.ui.explorerTree, marker)
        if items:
            if highlight:
                items[0].setSelected(True)

            if dehighlight:
                items[0].setSelected(False)

    def highlight_marker_label(self, frame):
        for marker, coord in self.mainwindow.pycgm_data.Data['Markers'].items():
            if np.isnan(coord[0, frame]):
                items = tree_find(self.mainwindow.ui.explorerTree, marker)
                if items:
                    items[0].setForeground(0, QtGui.QBrush(QtGui.QColor(220, 220, 220)))
            else:
                items = tree_find(self.mainwindow.ui.explorerTree, marker)
                if items:
                    items[0].setForeground(0, QtGui.QBrush(QtGui.QColor(0, 0, 0)))

    def populate_vsk_form(self, filepath, vsk):
        filename = []
        for c in reversed(filepath):
            if c != '/':
                filename.append(c)
            else:
                break
        s = ''
        filename = filename[::-1]
        self.mainwindow.ui.nameLineEdit.setText(str(s.join(filename[:-4])))

        for key, val in vsk.items():
            line_edit = self.mainwindow.ui.vskWidget.findChild(QtWidgets.QLineEdit, key)
            if line_edit:
                line_edit.setText(str("%.2f" % round(val, 2)))

        self.mainwindow.ui.vskScrollArea.setVisible(True)

    def setup_splitter(self):
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.mainwindow.ui.explorerTree)
        splitter.addWidget(self.mainwindow.ui.vskScrollArea)
        self.mainwindow.ui.vskScrollArea.setVisible(False)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        custom_handle(splitter, direction='Horizontal')
        self.mainwindow.ui.splitterLayout.addWidget(splitter)

