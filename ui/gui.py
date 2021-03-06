# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\M.Hollands\PycharmProjects\pyCGM_Studio\ui\gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1176, 809)
        mainWindow.setStyleSheet("")
        self.centralWidget = QtWidgets.QWidget(mainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout_2.setContentsMargins(0, 1, 2, 1)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.centralLayout = QtWidgets.QVBoxLayout()
        self.centralLayout.setSpacing(0)
        self.centralLayout.setObjectName("centralLayout")
        self.gridLayout_2.addLayout(self.centralLayout, 0, 0, 1, 1)
        self.horizontalLayout1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout1.setSpacing(8)
        self.horizontalLayout1.setObjectName("horizontalLayout1")
        self.playButton = QtWidgets.QPushButton(self.centralWidget)
        self.playButton.setText("")
        self.playButton.setAutoDefault(False)
        self.playButton.setDefault(False)
        self.playButton.setFlat(True)
        self.playButton.setObjectName("playButton")
        self.horizontalLayout1.addWidget(self.playButton)
        self.vtkScrollSlider = QtWidgets.QSlider(self.centralWidget)
        self.vtkScrollSlider.setStyleSheet("")
        self.vtkScrollSlider.setOrientation(QtCore.Qt.Horizontal)
        self.vtkScrollSlider.setObjectName("vtkScrollSlider")
        self.horizontalLayout1.addWidget(self.vtkScrollSlider)
        self.currentFrame = QtWidgets.QLabel(self.centralWidget)
        self.currentFrame.setMinimumSize(QtCore.QSize(30, 0))
        self.currentFrame.setObjectName("currentFrame")
        self.horizontalLayout1.addWidget(self.currentFrame)
        self.gridLayout_2.addLayout(self.horizontalLayout1, 1, 0, 1, 1)
        mainWindow.setCentralWidget(self.centralWidget)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.toolDock = QtWidgets.QDockWidget(mainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolDock.sizePolicy().hasHeightForWidth())
        self.toolDock.setSizePolicy(sizePolicy)
        self.toolDock.setMaximumSize(QtCore.QSize(524287, 524287))
        self.toolDock.setBaseSize(QtCore.QSize(0, 0))
        self.toolDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.toolDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.toolDock.setObjectName("toolDock")
        self.verticalLayout_3 = QtWidgets.QWidget()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayout_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gapFillToolButton = QtWidgets.QPushButton(self.verticalLayout_3)
        self.gapFillToolButton.setMinimumSize(QtCore.QSize(150, 0))
        self.gapFillToolButton.setStyleSheet("QPushButton\n"
"{\n"
"  text-align: left;\n"
"}\n"
"\n"
"QPushButton::pressed\n"
"{\n"
"  border: none;\n"
"  margin: 0px;\n"
"  padding: 0px;\n"
"}\n"
"\n"
"QPushButton::flat\n"
"{\n"
"  border: none;\n"
"  margin: 0px;\n"
"  padding: 0px;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Resources/Images/uparrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.gapFillToolButton.setIcon(icon)
        self.gapFillToolButton.setIconSize(QtCore.QSize(11, 12))
        self.gapFillToolButton.setFlat(True)
        self.gapFillToolButton.setObjectName("gapFillToolButton")
        self.verticalLayout_2.addWidget(self.gapFillToolButton)
        self.frame_2 = QtWidgets.QFrame(self.verticalLayout_3)
        self.frame_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_2.addWidget(self.frame_2)
        self.gapFillWidget = QtWidgets.QWidget(self.verticalLayout_3)
        self.gapFillWidget.setObjectName("gapFillWidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.gapFillWidget)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.gapTable = QtWidgets.QTableWidget(self.gapFillWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gapTable.sizePolicy().hasHeightForWidth())
        self.gapTable.setSizePolicy(sizePolicy)
        self.gapTable.setStyleSheet("")
        self.gapTable.setFrameShape(QtWidgets.QFrame.Panel)
        self.gapTable.setObjectName("gapTable")
        self.gapTable.setColumnCount(0)
        self.gapTable.setRowCount(0)
        self.verticalLayout_5.addWidget(self.gapTable)
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        self.prevGap = QtWidgets.QLabel(self.gapFillWidget)
        self.prevGap.setObjectName("prevGap")
        self.horizontalLayout2.addWidget(self.prevGap)
        self.gapLength = QtWidgets.QLabel(self.gapFillWidget)
        self.gapLength.setAlignment(QtCore.Qt.AlignCenter)
        self.gapLength.setObjectName("gapLength")
        self.horizontalLayout2.addWidget(self.gapLength)
        self.nextGap = QtWidgets.QLabel(self.gapFillWidget)
        self.nextGap.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nextGap.setObjectName("nextGap")
        self.horizontalLayout2.addWidget(self.nextGap)
        self.verticalLayout_5.addLayout(self.horizontalLayout2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gapLeftButton = QtWidgets.QPushButton(self.gapFillWidget)
        self.gapLeftButton.setText("")
        self.gapLeftButton.setFlat(True)
        self.gapLeftButton.setObjectName("gapLeftButton")
        self.horizontalLayout.addWidget(self.gapLeftButton)
        self.currentGapLength = QtWidgets.QTextBrowser(self.gapFillWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentGapLength.sizePolicy().hasHeightForWidth())
        self.currentGapLength.setSizePolicy(sizePolicy)
        self.currentGapLength.setObjectName("currentGapLength")
        self.horizontalLayout.addWidget(self.currentGapLength)
        self.gapRightButton = QtWidgets.QPushButton(self.gapFillWidget)
        self.gapRightButton.setText("")
        self.gapRightButton.setFlat(True)
        self.gapRightButton.setObjectName("gapRightButton")
        self.horizontalLayout.addWidget(self.gapRightButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.splineLabel = QtWidgets.QLabel(self.gapFillWidget)
        self.splineLabel.setObjectName("splineLabel")
        self.verticalLayout_5.addWidget(self.splineLabel)
        self.frame = QtWidgets.QFrame(self.gapFillWidget)
        self.frame.setMaximumSize(QtCore.QSize(16777215, 90))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.maxGapLengthLabel = QtWidgets.QLabel(self.frame)
        self.maxGapLengthLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.maxGapLengthLabel.setObjectName("maxGapLengthLabel")
        self.verticalLayout.addWidget(self.maxGapLengthLabel)
        self.maxGapLength = QtWidgets.QLineEdit(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.maxGapLength.setFont(font)
        self.maxGapLength.setObjectName("maxGapLength")
        self.verticalLayout.addWidget(self.maxGapLength)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.undo = QtWidgets.QPushButton(self.frame)
        self.undo.setObjectName("undo")
        self.horizontalLayout_2.addWidget(self.undo)
        self.splineButton = QtWidgets.QPushButton(self.frame)
        self.splineButton.setObjectName("splineButton")
        self.horizontalLayout_2.addWidget(self.splineButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5.addWidget(self.frame)
        self.verticalLayout_2.addWidget(self.gapFillWidget)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.toolDock.setWidget(self.verticalLayout_3)
        mainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.toolDock)
        self.filesDock = QtWidgets.QDockWidget(mainWindow)
        self.filesDock.setStyleSheet("border-bottom-color: rgb(4, 4, 4);")
        self.filesDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.filesDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.filesDock.setObjectName("filesDock")
        self.filesTree = QtWidgets.QWidget()
        self.filesTree.setObjectName("filesTree")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.filesTree)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.filesLayout = QtWidgets.QVBoxLayout()
        self.filesLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.filesLayout.setSpacing(0)
        self.filesLayout.setObjectName("filesLayout")
        self.verticalLayout_7.addLayout(self.filesLayout)
        self.filesDock.setWidget(self.filesTree)
        mainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.filesDock)
        self.cgmPipelinesDock = QtWidgets.QDockWidget(mainWindow)
        self.cgmPipelinesDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.cgmPipelinesDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.cgmPipelinesDock.setObjectName("cgmPipelinesDock")
        self.dockWidgetContents_4 = QtWidgets.QWidget()
        self.dockWidgetContents_4.setObjectName("dockWidgetContents_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.dockWidgetContents_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.pipelineOperationsWidget = QtWidgets.QTreeWidget(self.dockWidgetContents_4)
        self.pipelineOperationsWidget.setObjectName("pipelineOperationsWidget")
        self.verticalLayout_6.addWidget(self.pipelineOperationsWidget)
        self.label = QtWidgets.QLabel(self.dockWidgetContents_4)
        self.label.setObjectName("label")
        self.verticalLayout_6.addWidget(self.label)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.playOperations = QtWidgets.QPushButton(self.dockWidgetContents_4)
        self.playOperations.setText("")
        self.playOperations.setFlat(True)
        self.playOperations.setObjectName("playOperations")
        self.horizontalLayout_4.addWidget(self.playOperations)
        self.pipelineBar = QtWidgets.QProgressBar(self.dockWidgetContents_4)
        self.pipelineBar.setProperty("value", 0)
        self.pipelineBar.setObjectName("pipelineBar")
        self.horizontalLayout_4.addWidget(self.pipelineBar)
        self.verticalLayout_6.addLayout(self.horizontalLayout_4)
        self.pipelineSelectedWidget = QtWidgets.QTreeWidget(self.dockWidgetContents_4)
        self.pipelineSelectedWidget.setObjectName("pipelineSelectedWidget")
        self.verticalLayout_6.addWidget(self.pipelineSelectedWidget)
        self.gridLayout_3.addLayout(self.verticalLayout_6, 0, 0, 1, 1)
        self.cgmPipelinesDock.setWidget(self.dockWidgetContents_4)
        mainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.cgmPipelinesDock)
        self.explorerWidget = QtWidgets.QDockWidget(mainWindow)
        self.explorerWidget.setStyleSheet("border-right-color: rgb(24, 24, 24);")
        self.explorerWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.explorerWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.explorerWidget.setObjectName("explorerWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setMaximumSize(QtCore.QSize(304, 16777215))
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.explorerTree = QtWidgets.QTreeWidget(self.dockWidgetContents)
        self.explorerTree.setFrameShape(QtWidgets.QFrame.Panel)
        self.explorerTree.setColumnCount(1)
        self.explorerTree.setObjectName("explorerTree")
        self.explorerTree.header().setVisible(True)
        self.explorerTree.header().setCascadingSectionResizes(False)
        self.verticalLayout_4.addWidget(self.explorerTree)
        self.vskScrollArea = QtWidgets.QScrollArea(self.dockWidgetContents)
        self.vskScrollArea.setMaximumSize(QtCore.QSize(286, 16777215))
        self.vskScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.vskScrollArea.setWidgetResizable(True)
        self.vskScrollArea.setObjectName("vskScrollArea")
        self.vskWidget = QtWidgets.QWidget()
        self.vskWidget.setGeometry(QtCore.QRect(0, 0, 260, 1085))
        self.vskWidget.setObjectName("vskWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.vskWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_8 = QtWidgets.QFrame(self.vskWidget)
        self.frame_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_8.setObjectName("frame_8")
        self.gridLayout.addWidget(self.frame_8, 37, 0, 1, 2)
        self.nameLabel = QtWidgets.QLabel(self.vskWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.gridLayout.addWidget(self.nameLabel, 6, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.vskWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.Height = QtWidgets.QLineEdit(self.vskWidget)
        self.Height.setObjectName("Height")
        self.gridLayout.addWidget(self.Height, 9, 1, 1, 1)
        self.massKgLabel = QtWidgets.QLabel(self.vskWidget)
        self.massKgLabel.setObjectName("massKgLabel")
        self.gridLayout.addWidget(self.massKgLabel, 8, 0, 1, 1)
        self.nameLineEdit = QtWidgets.QLineEdit(self.vskWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.gridLayout.addWidget(self.nameLineEdit, 6, 1, 1, 1)
        self.LeftLegLength = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftLegLength.setObjectName("LeftLegLength")
        self.gridLayout.addWidget(self.LeftLegLength, 16, 1, 1, 1)
        self.aSISToTrochanterLabel = QtWidgets.QLabel(self.vskWidget)
        self.aSISToTrochanterLabel.setObjectName("aSISToTrochanterLabel")
        self.gridLayout.addWidget(self.aSISToTrochanterLabel, 17, 0, 1, 1)
        self.InterAsisDistance = QtWidgets.QLineEdit(self.vskWidget)
        self.InterAsisDistance.setObjectName("InterAsisDistance")
        self.gridLayout.addWidget(self.InterAsisDistance, 10, 1, 1, 1)
        self.PelvisLength = QtWidgets.QLineEdit(self.vskWidget)
        self.PelvisLength.setObjectName("PelvisLength")
        self.gridLayout.addWidget(self.PelvisLength, 11, 1, 1, 1)
        self.headOffsetDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.headOffsetDegLabel.setObjectName("headOffsetDegLabel")
        self.gridLayout.addWidget(self.headOffsetDegLabel, 12, 0, 1, 1)
        self.HeadOffset = QtWidgets.QLineEdit(self.vskWidget)
        self.HeadOffset.setObjectName("HeadOffset")
        self.gridLayout.addWidget(self.HeadOffset, 12, 1, 1, 1)
        self.Bodymass = QtWidgets.QLineEdit(self.vskWidget)
        self.Bodymass.setObjectName("Bodymass")
        self.gridLayout.addWidget(self.Bodymass, 8, 1, 1, 1)
        self.pelvisLengthMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.pelvisLengthMmLabel.setObjectName("pelvisLengthMmLabel")
        self.gridLayout.addWidget(self.pelvisLengthMmLabel, 11, 0, 1, 1)
        self.heightMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.heightMmLabel.setObjectName("heightMmLabel")
        self.gridLayout.addWidget(self.heightMmLabel, 9, 0, 1, 1)
        self.interASISDistanceMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.interASISDistanceMmLabel.setObjectName("interASISDistanceMmLabel")
        self.gridLayout.addWidget(self.interASISDistanceMmLabel, 10, 0, 1, 1)
        self.legLengthLabel = QtWidgets.QLabel(self.vskWidget)
        self.legLengthLabel.setObjectName("legLengthLabel")
        self.gridLayout.addWidget(self.legLengthLabel, 16, 0, 1, 1)
        self.LeftSoleDelta = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftSoleDelta.setObjectName("LeftSoleDelta")
        self.gridLayout.addWidget(self.LeftSoleDelta, 21, 1, 1, 1)
        self.soleDeltaMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.soleDeltaMmLabel.setObjectName("soleDeltaMmLabel")
        self.gridLayout.addWidget(self.soleDeltaMmLabel, 21, 0, 1, 1)
        self.LeftKneeWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftKneeWidth.setObjectName("LeftKneeWidth")
        self.gridLayout.addWidget(self.LeftKneeWidth, 18, 1, 1, 1)
        self.LeftTibialTorsion = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftTibialTorsion.setObjectName("LeftTibialTorsion")
        self.gridLayout.addWidget(self.LeftTibialTorsion, 20, 1, 1, 1)
        self.shankRotationDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.shankRotationDegLabel.setObjectName("shankRotationDegLabel")
        self.gridLayout.addWidget(self.shankRotationDegLabel, 23, 0, 1, 1)
        self.LeftThighRotation = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftThighRotation.setObjectName("LeftThighRotation")
        self.gridLayout.addWidget(self.LeftThighRotation, 22, 1, 1, 1)
        self.kneeWidthLabel = QtWidgets.QLabel(self.vskWidget)
        self.kneeWidthLabel.setObjectName("kneeWidthLabel")
        self.gridLayout.addWidget(self.kneeWidthLabel, 18, 0, 1, 1)
        self.ankleWidthMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.ankleWidthMmLabel.setObjectName("ankleWidthMmLabel")
        self.gridLayout.addWidget(self.ankleWidthMmLabel, 19, 0, 1, 1)
        self.LeftAnkleWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftAnkleWidth.setObjectName("LeftAnkleWidth")
        self.gridLayout.addWidget(self.LeftAnkleWidth, 19, 1, 1, 1)
        self.tibialTorsionLabel = QtWidgets.QLabel(self.vskWidget)
        self.tibialTorsionLabel.setObjectName("tibialTorsionLabel")
        self.gridLayout.addWidget(self.tibialTorsionLabel, 20, 0, 1, 1)
        self.thighRotationDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.thighRotationDegLabel.setObjectName("thighRotationDegLabel")
        self.gridLayout.addWidget(self.thighRotationDegLabel, 22, 0, 1, 1)
        self.LeftAsisTrocanterDistance = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftAsisTrocanterDistance.setObjectName("LeftAsisTrocanterDistance")
        self.gridLayout.addWidget(self.LeftAsisTrocanterDistance, 17, 1, 1, 1)
        self.LeftShankRotation = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftShankRotation.setObjectName("LeftShankRotation")
        self.gridLayout.addWidget(self.LeftShankRotation, 23, 1, 1, 1)
        self.kneeWidthMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.kneeWidthMmLabel.setObjectName("kneeWidthMmLabel")
        self.gridLayout.addWidget(self.kneeWidthMmLabel, 46, 0, 1, 1)
        self.RightKneeWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.RightKneeWidth.setObjectName("RightKneeWidth")
        self.gridLayout.addWidget(self.RightKneeWidth, 46, 1, 1, 1)
        self.ankleWidthMmLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.ankleWidthMmLabel_2.setObjectName("ankleWidthMmLabel_2")
        self.gridLayout.addWidget(self.ankleWidthMmLabel_2, 47, 0, 1, 1)
        self.RightAnkleWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.RightAnkleWidth.setObjectName("RightAnkleWidth")
        self.gridLayout.addWidget(self.RightAnkleWidth, 47, 1, 1, 1)
        self.staticRotOffDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.staticRotOffDegLabel.setObjectName("staticRotOffDegLabel")
        self.gridLayout.addWidget(self.staticRotOffDegLabel, 27, 0, 1, 1)
        self.tibialTorsionDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.tibialTorsionDegLabel.setObjectName("tibialTorsionDegLabel")
        self.gridLayout.addWidget(self.tibialTorsionDegLabel, 48, 0, 1, 1)
        self.RightLegLength = QtWidgets.QLineEdit(self.vskWidget)
        self.RightLegLength.setObjectName("RightLegLength")
        self.gridLayout.addWidget(self.RightLegLength, 44, 1, 1, 1)
        self.LeftStaticPlantFlex = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftStaticPlantFlex.setObjectName("LeftStaticPlantFlex")
        self.gridLayout.addWidget(self.LeftStaticPlantFlex, 26, 1, 1, 1)
        self.aSISToTrochanterMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.aSISToTrochanterMmLabel.setObjectName("aSISToTrochanterMmLabel")
        self.gridLayout.addWidget(self.aSISToTrochanterMmLabel, 45, 0, 1, 1)
        self.staticPlantarFlexDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.staticPlantarFlexDegLabel.setObjectName("staticPlantarFlexDegLabel")
        self.gridLayout.addWidget(self.staticPlantarFlexDegLabel, 26, 0, 1, 1)
        self.legLengthMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.legLengthMmLabel.setObjectName("legLengthMmLabel")
        self.gridLayout.addWidget(self.legLengthMmLabel, 44, 0, 1, 1)
        self.RightAsisTrocanterDistance = QtWidgets.QLineEdit(self.vskWidget)
        self.RightAsisTrocanterDistance.setObjectName("RightAsisTrocanterDistance")
        self.gridLayout.addWidget(self.RightAsisTrocanterDistance, 45, 1, 1, 1)
        self.RightTibialTorsion = QtWidgets.QLineEdit(self.vskWidget)
        self.RightTibialTorsion.setObjectName("RightTibialTorsion")
        self.gridLayout.addWidget(self.RightTibialTorsion, 48, 1, 1, 1)
        self.RightWristWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.RightWristWidth.setObjectName("RightWristWidth")
        self.gridLayout.addWidget(self.RightWristWidth, 57, 1, 1, 1)
        self.handThicknessMmLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.handThicknessMmLabel_2.setObjectName("handThicknessMmLabel_2")
        self.gridLayout.addWidget(self.handThicknessMmLabel_2, 58, 0, 1, 1)
        self.RightHandThickness = QtWidgets.QLineEdit(self.vskWidget)
        self.RightHandThickness.setObjectName("RightHandThickness")
        self.gridLayout.addWidget(self.RightHandThickness, 58, 1, 1, 1)
        self.RightThighRotation = QtWidgets.QLineEdit(self.vskWidget)
        self.RightThighRotation.setObjectName("RightThighRotation")
        self.gridLayout.addWidget(self.RightThighRotation, 50, 1, 1, 1)
        self.ankleAbAddDegLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.ankleAbAddDegLabel_2.setObjectName("ankleAbAddDegLabel_2")
        self.gridLayout.addWidget(self.ankleAbAddDegLabel_2, 54, 0, 1, 1)
        self.RightShankRotation = QtWidgets.QLineEdit(self.vskWidget)
        self.RightShankRotation.setObjectName("RightShankRotation")
        self.gridLayout.addWidget(self.RightShankRotation, 51, 1, 1, 1)
        self.shoulderOffsetLabel = QtWidgets.QLabel(self.vskWidget)
        self.shoulderOffsetLabel.setObjectName("shoulderOffsetLabel")
        self.gridLayout.addWidget(self.shoulderOffsetLabel, 55, 0, 1, 1)
        self.RightStaticPlantFlex = QtWidgets.QLineEdit(self.vskWidget)
        self.RightStaticPlantFlex.setObjectName("RightStaticPlantFlex")
        self.gridLayout.addWidget(self.RightStaticPlantFlex, 52, 1, 1, 1)
        self.soleDeltaMmLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.soleDeltaMmLabel_2.setObjectName("soleDeltaMmLabel_2")
        self.gridLayout.addWidget(self.soleDeltaMmLabel_2, 49, 0, 1, 1)
        self.RightShoulderOffset = QtWidgets.QLineEdit(self.vskWidget)
        self.RightShoulderOffset.setObjectName("RightShoulderOffset")
        self.gridLayout.addWidget(self.RightShoulderOffset, 55, 1, 1, 1)
        self.wristWidthLabel = QtWidgets.QLabel(self.vskWidget)
        self.wristWidthLabel.setObjectName("wristWidthLabel")
        self.gridLayout.addWidget(self.wristWidthLabel, 57, 0, 1, 1)
        self.staticPlantFlexDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.staticPlantFlexDegLabel.setObjectName("staticPlantFlexDegLabel")
        self.gridLayout.addWidget(self.staticPlantFlexDegLabel, 52, 0, 1, 1)
        self.RightSoleDelta = QtWidgets.QLineEdit(self.vskWidget)
        self.RightSoleDelta.setObjectName("RightSoleDelta")
        self.gridLayout.addWidget(self.RightSoleDelta, 49, 1, 1, 1)
        self.ankleAbAddDegLabel = QtWidgets.QLabel(self.vskWidget)
        self.ankleAbAddDegLabel.setObjectName("ankleAbAddDegLabel")
        self.gridLayout.addWidget(self.ankleAbAddDegLabel, 28, 0, 1, 1)
        self.thighRotationDegLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.thighRotationDegLabel_2.setObjectName("thighRotationDegLabel_2")
        self.gridLayout.addWidget(self.thighRotationDegLabel_2, 50, 0, 1, 1)
        self.RightAnkleAbAdd = QtWidgets.QLineEdit(self.vskWidget)
        self.RightAnkleAbAdd.setObjectName("RightAnkleAbAdd")
        self.gridLayout.addWidget(self.RightAnkleAbAdd, 54, 1, 1, 1)
        self.shoulderOffsetMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.shoulderOffsetMmLabel.setObjectName("shoulderOffsetMmLabel")
        self.gridLayout.addWidget(self.shoulderOffsetMmLabel, 31, 0, 1, 1)
        self.elbowWidthMmLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.elbowWidthMmLabel_2.setObjectName("elbowWidthMmLabel_2")
        self.gridLayout.addWidget(self.elbowWidthMmLabel_2, 56, 0, 1, 1)
        self.shankRotationDegLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.shankRotationDegLabel_2.setObjectName("shankRotationDegLabel_2")
        self.gridLayout.addWidget(self.shankRotationDegLabel_2, 51, 0, 1, 1)
        self.staticRotOffDegLabel_2 = QtWidgets.QLabel(self.vskWidget)
        self.staticRotOffDegLabel_2.setObjectName("staticRotOffDegLabel_2")
        self.gridLayout.addWidget(self.staticRotOffDegLabel_2, 53, 0, 1, 1)
        self.RightElbowWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.RightElbowWidth.setObjectName("RightElbowWidth")
        self.gridLayout.addWidget(self.RightElbowWidth, 56, 1, 1, 1)
        self.LeftStaticRotOff = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftStaticRotOff.setObjectName("LeftStaticRotOff")
        self.gridLayout.addWidget(self.LeftStaticRotOff, 27, 1, 1, 1)
        self.RightStaticRotOff = QtWidgets.QLineEdit(self.vskWidget)
        self.RightStaticRotOff.setObjectName("RightStaticRotOff")
        self.gridLayout.addWidget(self.RightStaticRotOff, 53, 1, 1, 1)
        self.LeftElbowWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftElbowWidth.setObjectName("LeftElbowWidth")
        self.gridLayout.addWidget(self.LeftElbowWidth, 32, 1, 1, 1)
        self.LeftHandThickness = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftHandThickness.setObjectName("LeftHandThickness")
        self.gridLayout.addWidget(self.LeftHandThickness, 34, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.vskWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 36, 0, 1, 1)
        self.wristWidthMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.wristWidthMmLabel.setObjectName("wristWidthMmLabel")
        self.gridLayout.addWidget(self.wristWidthMmLabel, 33, 0, 1, 1)
        self.handThicknessMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.handThicknessMmLabel.setObjectName("handThicknessMmLabel")
        self.gridLayout.addWidget(self.handThicknessMmLabel, 34, 0, 1, 1)
        self.LeftWristWidth = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftWristWidth.setObjectName("LeftWristWidth")
        self.gridLayout.addWidget(self.LeftWristWidth, 33, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.vskWidget)
        self.label_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 14, 0, 1, 1)
        self.LeftAnkleAbAdd = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftAnkleAbAdd.setObjectName("LeftAnkleAbAdd")
        self.gridLayout.addWidget(self.LeftAnkleAbAdd, 28, 1, 1, 1)
        self.LeftShoulderOffset = QtWidgets.QLineEdit(self.vskWidget)
        self.LeftShoulderOffset.setObjectName("LeftShoulderOffset")
        self.gridLayout.addWidget(self.LeftShoulderOffset, 31, 1, 1, 1)
        self.elbowWidthMmLabel = QtWidgets.QLabel(self.vskWidget)
        self.elbowWidthMmLabel.setObjectName("elbowWidthMmLabel")
        self.gridLayout.addWidget(self.elbowWidthMmLabel, 32, 0, 1, 1)
        self.frame_5 = QtWidgets.QFrame(self.vskWidget)
        self.frame_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_5.setObjectName("frame_5")
        self.gridLayout.addWidget(self.frame_5, 3, 0, 1, 2)
        self.frame_6 = QtWidgets.QFrame(self.vskWidget)
        self.frame_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setObjectName("frame_6")
        self.gridLayout.addWidget(self.frame_6, 15, 0, 1, 2)
        self.frame_3 = QtWidgets.QFrame(self.vskWidget)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout.addWidget(self.frame_3, 13, 0, 1, 1)
        self.frame_7 = QtWidgets.QFrame(self.vskWidget)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.gridLayout.addWidget(self.frame_7, 35, 0, 1, 1)
        self.vskScrollArea.setWidget(self.vskWidget)
        self.verticalLayout_4.addWidget(self.vskScrollArea)
        self.splitterLayout = QtWidgets.QVBoxLayout()
        self.splitterLayout.setObjectName("splitterLayout")
        self.verticalLayout_4.addLayout(self.splitterLayout)
        self.frame_4 = QtWidgets.QFrame(self.dockWidgetContents)
        self.frame_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_4.addWidget(self.frame_4)
        self.explorerWidget.setWidget(self.dockWidgetContents)
        mainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.explorerWidget)
        self.messageWidget = QtWidgets.QDockWidget(mainWindow)
        self.messageWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.messageWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.messageWidget.setObjectName("messageWidget")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.messageBrowser = QtWidgets.QTextBrowser(self.dockWidgetContents_2)
        self.messageBrowser.setMinimumSize(QtCore.QSize(0, 0))
        self.messageBrowser.setObjectName("messageBrowser")
        self.gridLayout_4.addWidget(self.messageBrowser, 0, 0, 1, 1)
        self.messageWidget.setWidget(self.dockWidgetContents_2)
        mainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.messageWidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1176, 21))
        self.menubar.setObjectName("menubar")
        mainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(mainWindow)
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        mainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpen = QtWidgets.QAction(mainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionRunModel = QtWidgets.QAction(mainWindow)
        self.actionRunModel.setObjectName("actionRunModel")

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "PyCGM Studio"))
        self.currentFrame.setText(_translate("mainWindow", "0"))
        self.toolDock.setWindowTitle(_translate("mainWindow", "Tools"))
        self.gapFillToolButton.setText(_translate("mainWindow", "Gap Filling"))
        self.prevGap.setText(_translate("mainWindow", "Prev Gap"))
        self.gapLength.setText(_translate("mainWindow", "Gap Length"))
        self.nextGap.setText(_translate("mainWindow", "Next Gap"))
        self.splineLabel.setText(_translate("mainWindow", "Spline Fill"))
        self.maxGapLengthLabel.setText(_translate("mainWindow", "Max Gap Length:"))
        self.maxGapLength.setText(_translate("mainWindow", "50"))
        self.undo.setText(_translate("mainWindow", "Undo"))
        self.splineButton.setText(_translate("mainWindow", "Fill"))
        self.filesDock.setWindowTitle(_translate("mainWindow", "Files"))
        self.cgmPipelinesDock.setWindowTitle(_translate("mainWindow", "Pipelines"))
        self.pipelineOperationsWidget.headerItem().setText(0, _translate("mainWindow", "Pipeline operations"))
        self.label.setText(_translate("mainWindow", "Run"))
        self.pipelineSelectedWidget.headerItem().setText(0, _translate("mainWindow", "Selected Operations"))
        self.explorerWidget.setWindowTitle(_translate("mainWindow", "Explorer"))
        self.explorerTree.headerItem().setText(0, _translate("mainWindow", "Acquisition"))
        self.nameLabel.setText(_translate("mainWindow", "Name"))
        self.label_2.setText(_translate("mainWindow", "VSK properties"))
        self.massKgLabel.setText(_translate("mainWindow", "Mass (kg)"))
        self.aSISToTrochanterLabel.setText(_translate("mainWindow", "ASIS to trochanter (mm)"))
        self.headOffsetDegLabel.setText(_translate("mainWindow", "Head offset (deg)"))
        self.pelvisLengthMmLabel.setText(_translate("mainWindow", "Pelvis length (mm)"))
        self.heightMmLabel.setText(_translate("mainWindow", "Height (mm)"))
        self.interASISDistanceMmLabel.setText(_translate("mainWindow", "Inter ASIS distance (mm)"))
        self.legLengthLabel.setText(_translate("mainWindow", "Leg length (mm)"))
        self.soleDeltaMmLabel.setText(_translate("mainWindow", "Sole delta (mm)"))
        self.shankRotationDegLabel.setText(_translate("mainWindow", "Shank rotation (deg)"))
        self.kneeWidthLabel.setText(_translate("mainWindow", "Knee width (mm)"))
        self.ankleWidthMmLabel.setText(_translate("mainWindow", "Ankle width (mm)"))
        self.tibialTorsionLabel.setText(_translate("mainWindow", "Tibial torsion (deg)"))
        self.thighRotationDegLabel.setText(_translate("mainWindow", "Thigh rotation (deg)"))
        self.kneeWidthMmLabel.setText(_translate("mainWindow", "Knee width (mm)"))
        self.ankleWidthMmLabel_2.setText(_translate("mainWindow", "Ankle width (mm)"))
        self.staticRotOffDegLabel.setText(_translate("mainWindow", "Static rot off (deg)"))
        self.tibialTorsionDegLabel.setText(_translate("mainWindow", "Tibial torsion (deg)"))
        self.aSISToTrochanterMmLabel.setText(_translate("mainWindow", "ASIS to trochanter (mm)"))
        self.staticPlantarFlexDegLabel.setText(_translate("mainWindow", "Static plant flex (deg)"))
        self.legLengthMmLabel.setText(_translate("mainWindow", "Leg length (mm)"))
        self.handThicknessMmLabel_2.setText(_translate("mainWindow", "Hand thickness (mm)"))
        self.ankleAbAddDegLabel_2.setText(_translate("mainWindow", "Ankle ab add (deg)"))
        self.shoulderOffsetLabel.setText(_translate("mainWindow", "Shoulder offset"))
        self.soleDeltaMmLabel_2.setText(_translate("mainWindow", "Sole delta (mm)"))
        self.wristWidthLabel.setText(_translate("mainWindow", "Wrist width"))
        self.staticPlantFlexDegLabel.setText(_translate("mainWindow", "Static plant flex (deg)"))
        self.ankleAbAddDegLabel.setText(_translate("mainWindow", "Ankle ab add (deg)"))
        self.thighRotationDegLabel_2.setText(_translate("mainWindow", "Thigh rotation (deg)"))
        self.shoulderOffsetMmLabel.setText(_translate("mainWindow", "Shoulder offset (mm)"))
        self.elbowWidthMmLabel_2.setText(_translate("mainWindow", "Elbow width (mm)"))
        self.shankRotationDegLabel_2.setText(_translate("mainWindow", "Shank rotation (deg)"))
        self.staticRotOffDegLabel_2.setText(_translate("mainWindow", "Static rot off (deg)"))
        self.label_4.setText(_translate("mainWindow", " Right"))
        self.wristWidthMmLabel.setText(_translate("mainWindow", "Wrist width (mm)"))
        self.handThicknessMmLabel.setText(_translate("mainWindow", "Hand thickness (mm)"))
        self.label_3.setText(_translate("mainWindow", "Left"))
        self.elbowWidthMmLabel.setText(_translate("mainWindow", "Elbow width (mm)"))
        self.messageWidget.setWindowTitle(_translate("mainWindow", "Messages"))
        self.toolBar.setWindowTitle(_translate("mainWindow", "toolBar"))
        self.actionOpen.setText(_translate("mainWindow", "Load motion capture"))
        self.actionRunModel.setText(_translate("mainWindow", "Run model"))

import resources_rc
