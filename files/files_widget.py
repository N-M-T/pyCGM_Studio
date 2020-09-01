from PyQt5 import QtWidgets, QtCore, QtGui
import os
from functools import partial
from xml.dom import minidom


class IconProvider(QtWidgets.QFileIconProvider):
    def icon(self, file_info):
        if file_info.isDir():
            path = file_info.absoluteFilePath()
            if path in self.patient_dirs:
                return QtGui.QIcon(":images/patientball.png")
            if path in self.session_dirs:
                return QtGui.QIcon(":images/sessionball.png")

        if file_info.isFile():
            file_dir = file_info.absolutePath()
            file_base = file_info.completeBaseName()
            file_ext = file_info.suffix()
            file_name = file_dir + "/" + file_base + '.' + file_ext
            if file_name in self.trials:
                return QtGui.QIcon(":images/trialball.png")
            elif file_name in self.vsks:
                return QtGui.QIcon(":images/vskball.png")

        return QtWidgets.QFileIconProvider.icon(self, file_info)


class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.decorationPosition = QtWidgets.QStyleOptionViewItem.Left


class Files:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
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
        self.path = ''
        # self.path = 'C:/Users/M.Hollands/Desktop/'
        # self.path = "C:/Users/M.Hollands/Desktop/pyCGM-master/SampleData/Sample_2"
        # self.path = QtCore.QDir.currentPath()
        # self.path = "C:/Users/M.Hollands/Desktop/Dunhill project/Decor/Decor_staircase_Vicon_Processed/"
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(self.path)
        self.current_dir = None
        icon_provider = IconProvider()
        icon_provider.mainwindow = self.mainwindow
        self.patient_dirs = list()
        self.session_dirs = list()
        self.trials = list()
        self.vsks = list()
        icon_provider.patient_dirs = self.patient_dirs
        icon_provider.session_dirs = self.session_dirs
        icon_provider.trials = self.trials
        icon_provider.vsks = self.vsks
        self.model.setIconProvider(icon_provider)
        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.path))
        self.tree.clicked.connect(partial(self.tree_clicked, 'single'))
        self.tree.doubleClicked.connect(partial(self.tree_clicked, 'double'))
        self.tree.expanded.connect(partial(self.tree_clicked, 'single'))
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
        self.mainwindow.ui.filesLayout.addWidget(splitter)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        self.exts = ['c3d', 'vsk']
        self.update_all(self.path)

    def set_current_path(self, path):
        self.current_dir = path

    def save_state(self):
        return self.current_dir

    def load_state(self, filepath):
        try:
            self.tree.setCurrentIndex(self.model.index(filepath))
        except:  # if file structure is altered revert to root
            pass

    def update_all(self, path):
        # this finds all Vicon files and assigns icons
        dir_no = 0  # only explore 50 directories deep
        for current_dir, dirnames, filenames in os.walk(path):
            if dir_no > 50:
                break
            current_dir = current_dir.replace(os.sep, '/')
            for filename in filenames:
                ext = filename[-3:]
                if filename[-11:-4] == 'Patient':
                    if current_dir not in self.patient_dirs:
                        self.patient_dirs.append(current_dir)

                elif filename[-11:-4] == 'Session':
                    if current_dir not in self.session_dirs:
                        self.session_dirs.append(current_dir)

                elif ext == 'c3d':
                    trial_name = current_dir + '/' + filename
                    if trial_name not in self.trials:
                        self.trials.append(trial_name)

                elif ext == 'vsk':
                    vsk_name = current_dir + '/' + filename
                    if vsk_name not in self.vsks:
                        self.vsks.append(vsk_name)
            dir_no += 1

    def tree_clicked(self, kind, signal):
        # receives signal on treeview clicked
        path = self.model.filePath(signal)
        self.set_current_path(path)
        self.update_all(path)

        if kind == 'double':  # load directly from file tree view
            ext = path[-3:]
            if ext in self.exts:
                # check we need to save prior to loading new file
                self.mainwindow.studio_io_ops.save_dialog()
                self.mainwindow.studio_io_ops.studio_loader(path)

        if kind == 'single':  # transfer dir table
            if path in self.patient_dirs:
                self.update_sessions(path)
            elif path in self.session_dirs:
                self.update_trials(path)

    def table_clicked(self, kind, signal):
        target_row = signal.row()
        path_item = self.files_table.item(target_row, 4)
        if path_item:
            path = path_item.text()
            self.set_current_path(path)
            if kind == 'double':  # load c3d
                self.mainwindow.studio_io_ops.save_dialog()
                self.mainwindow.studio_io_ops.studio_loader(path)

            elif kind == 'single':  # open session
                if path in self.session_dirs:
                    self.update_trials(path)

    def update_trials(self, path):
        # populates table with all trials in session directory once a tree item (session) is clicked
        self.files_table.setRowCount(0)
        for current_dir, dirnames, filenames in os.walk(path):
            current_dir = current_dir.replace(os.sep, '/')
            for filename in filenames:
                ext = filename[-3:]
                if ext in self.exts:
                    name = filename[:-4]
                    self.files_table.insertRow(self.files_table.rowCount())
                    item = QtWidgets.QTableWidgetItem(name)
                    if ext == 'c3d':
                        icon = QtGui.QIcon(":images/trialball.png")
                    else:
                        icon = QtGui.QIcon(":images/vskball.png")
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
                    icon = QtGui.QIcon(":images/sessionball.png")
                    item.setIcon(icon)
                    self.files_table.setItem(self.files_table.rowCount() - 1, 0, item)
                    self.files_table.setItem(self.files_table.rowCount() - 1, 4,
                                             QtWidgets.QTableWidgetItem(current_dir))

        self.files_table.resizeColumnToContents(0)
