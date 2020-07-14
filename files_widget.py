from PyQt5 import QtWidgets, QtCore, QtGui
import os
from functools import partial
from xml.dom import minidom

# store directories so we can share with IconProvider
global patient_dirs
global session_dirs
global trials
global c3ds
global vsks

patient_dirs = list()
session_dirs = list()
trials = list()
c3ds = list()
vsks = list()


def update_all(path):
    global patient_dirs
    global session_dirs
    global trials
    global vsks

    patient_dirs = list()
    session_dirs = list()
    trials = list()
    vsks = list()

    # this finds all Vicon files and assigns icons
    for current_dir, dirnames, filenames in os.walk(path):
        current_dir = current_dir.replace(os.sep, '/')
        for filename in filenames:
            ext = filename[-3:]
            if filename[-11:-4] == 'Patient':
                if current_dir not in patient_dirs:
                    patient_dirs.append(current_dir)

            elif filename[-11:-4] == 'Session':
                if current_dir not in session_dirs:
                    session_dirs.append(current_dir)

            elif ext == 'c3d':
                trial_name = current_dir + '/' + filename
                if trial_name not in trials:
                    trials.append(trial_name)

            elif ext == 'vsk':
                vsk_name = current_dir + '/' + filename
                if vsk_name not in vsks:
                    vsks.append(vsk_name)


class IconProvider(QtWidgets.QFileIconProvider):
    def icon(self, file_info):
        if file_info.isDir():
            path = file_info.absoluteFilePath()
            if path in patient_dirs:
                return QtGui.QIcon("./Resources/Images/patientball.png")
            if path in session_dirs:
                return QtGui.QIcon("./Resources/Images/sessionball.png")

        if file_info.isFile():
            file_dir = file_info.absolutePath()
            file_base = file_info.completeBaseName()
            file_ext = file_info.suffix()
            file_name = file_dir + "/" + file_base + '.' + file_ext
            if file_name in trials:
                return QtGui.QIcon("./Resources/Images/trialball.png")
            elif file_name in vsks:
                return QtGui.QIcon("./Resources/Images/vskball.png")

        return QtWidgets.QFileIconProvider.icon(self, file_info)


class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.decorationPosition = QtWidgets.QStyleOptionViewItem.Left


class Files:
    def __init__(self, mainwindow, ui):
        self.mainwindow = mainwindow
        self.ui = ui
        header_style = """QTableView::item:selected { 
                            color:black; 
                            background:#f6f6f6;}
                        QTableCornerButton::section{
                            background-color:#232326;}
                        QHeaderView::section {
                            color:black; 
                            background-color:#f6f6f6;
                            padding:2px;}"""

        # file browser model tree
        # self.path = ''
        self.path = 'C:/Users/M.Hollands/Desktop/Example_c3d/'
        # self.path = "C:/Users/M.Hollands/Desktop/pyCGM-master/SampleData/Sample_2"
        # self.path = QtCore.QDir.currentPath()
        # self.path = "C:/Users/M.Hollands/Desktop/Dunhill project/Decor/Decor_staircase_Vicon_Processed/"

        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(self.path)
        self.model.setIconProvider(IconProvider())

        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.path))
        self.tree.clicked.connect(partial(self.tree_clicked, 'single'))
        self.tree.doubleClicked.connect(partial(self.tree_clicked, 'double'))
        self.tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tree.header().setStyleSheet(header_style)

        # info display table
        self.files_table = QtWidgets.QTableWidget()
        self.files_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.files_table.resize(10, 10)
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels((['Name', 'Type', 'Created', '', '']))
        self.files_table.setColumnHidden(4, True)
        self.files_table.verticalHeader().setVisible(False)
        self.files_table.setStyleSheet(header_style)
        delegate = AlignDelegate(self.files_table)
        self.files_table.setItemDelegate(delegate)
        self.files_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.files_table.setFocusPolicy(QtCore.Qt.NoFocus)

        self.files_table.clicked.connect(partial(self.table_clicked, 'single'))
        self.files_table.doubleClicked.connect(partial(self.table_clicked, 'double'))

        # splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.files_table)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        splitter.setSizePolicy(size_policy)
        self.ui.filesLayout.addWidget(splitter)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        update_all(self.path)

    def update_trials(self, path):
        # populates tableview with trials and icons once a tree item (session) is clicked
        self.files_table.setRowCount(0)
        for current_dir, dirnames, filenames in os.walk(path):
            current_dir = current_dir.replace(os.sep, '/')
            for filename in filenames:
                ext = filename[-3:]
                if ext == 'c3d' or ext == 'vsk':
                    name = filename[:-4]
                    self.files_table.insertRow(self.files_table.rowCount())
                    item = QtWidgets.QTableWidgetItem(name)
                    if ext == 'c3d':
                        icon = QtGui.QIcon("./Resources/Images/trialball.png")
                    else:
                        icon = QtGui.QIcon("./Resources/Images/vskball.png")
                    item.setIcon(icon)
                    self.files_table.setItem(self.files_table.rowCount() - 1, 0, item)
                    self.files_table.setItem(self.files_table.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(ext))
                    self.files_table.setItem(self.files_table.rowCount() - 1, 4,
                                             QtWidgets.QTableWidgetItem(current_dir + '/' + filename))

                    history = filename[:-3]
                    history = history + 'history'
                    history_path = current_dir + '/' + history

                    if os.path.exists(history_path):
                        xmldoc = minidom.parse(history_path)
                        itemlist = xmldoc.getElementsByTagName('Param')
                        created = itemlist[0].attributes['value'].value
                    else:
                        created = 'No history'

                    self.files_table.setItem(self.files_table.rowCount() - 1, 2,
                                             QtWidgets.QTableWidgetItem(created))

        [self.files_table.resizeColumnToContents(i) for i in range(3)]

    def update_sessions(self, path):
        # populates tableview with sessions and icons once a tree item (patient) is clicked
        self.files_table.setRowCount(0)
        for current_dir, dirnames, filenames in os.walk(path):
            current_dir = current_dir.replace(os.sep, '/')
            for filename in filenames:
                if filename[-11:-4] == 'Session':
                    self.files_table.insertRow(self.files_table.rowCount())
                    item = QtWidgets.QTableWidgetItem(filename[:-12])
                    icon = QtGui.QIcon("./Resources/Images/sessionball.png")
                    item.setIcon(icon)
                    self.files_table.setItem(self.files_table.rowCount() - 1, 0, item)
                    self.files_table.setItem(self.files_table.rowCount() - 1, 4,
                                             QtWidgets.QTableWidgetItem(current_dir))

        self.files_table.resizeColumnToContents(0)

    # receives signal on treeview clicked
    def tree_clicked(self, kind, signal):
        path = self.model.filePath(signal)
        if kind == 'double':
            if path[-3:] == 'c3d':
                self.mainwindow.studio_loader.c3d_loader(path)
                return

            elif path[-3:] == 'vsk':
                self.mainwindow.studio_loader.vsk_loader(path)
                return

        elif kind == 'single':
            if path in patient_dirs:
                self.update_sessions(path)
            elif path in session_dirs:
                self.update_trials(path)

    def table_clicked(self, kind, signal):
        target_row = signal.row()
        path_item = self.files_table.item(target_row, 4)
        if path_item:
            path = path_item.text()
            if kind == 'double':
                ext = path[-3:]
                if ext == 'c3d':
                    self.mainwindow.studio_loader.c3d_loader(path)
                elif ext == 'vsk':
                    self.mainwindow.studio_loader.vsk_loader(path)

            elif kind == 'single':
                if path in session_dirs:
                    self.update_trials(path)
