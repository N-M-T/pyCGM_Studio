from PyQt5 import QtCore, QtWidgets, QtGui


def gen_sub(widget, kind):
    sub_window = SubWindow(kind)
    sub_window.layout.addWidget(widget)
    return sub_window


class SubWindow(QtWidgets.QWidget):
    def __init__(self, kind, parent=None, flags=QtCore.Qt.Widget, toolbar=None):
        super(SubWindow, self).__init__(parent, flags)
        self.layout = QtWidgets.QVBoxLayout()
        self.CustomBar = CustomBar(self, kind, toolbar)
        self.layout.addWidget(self.CustomBar)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setMinimumWidth(20)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def set_combo_box(self, insert_at_0, insert_at_1):
        self.CustomBar.view.clear()
        self.CustomBar.view.addItem(insert_at_0)
        self.CustomBar.view.addItem(insert_at_1)


class CustomBar(QtWidgets.QWidget):
    def __init__(self, parent, kind, toolbar=None):
        super(CustomBar, self).__init__()
        self.handle_split = None
        self.parent = parent
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.title = QtWidgets.QLabel("View")
        self.kind = kind
        self.toolbar = toolbar
        btn_size = 20
        self.view = QtWidgets.QComboBox()
        self.view.activated.connect(self.selection_change)
        self.view.setStyleSheet("""
                                QWidget{
                                    border-radius: 0px;
                                    font-size: 10pt;
                                    text-align:left;
                                    background: #d7d6d5;
                                }
                                QComboBox::drop-down{
                                    border: 0px;
                                    subcontrol-position: left;
                                }
                                QComboBox::down-arrow{
                                    image: url(./Resources/Images/downarrow.png);
                                    width: 12px;
                                    height: 12px;
                                }""")

        self.view.setFixedSize(150, btn_size)

        style_sheet = """
                    QWidget{
                        border-radius: 1px;
                        background: #d7d6d5;
                        font-size: 12pt;
                        text-align:left;
                    }"""

        self.split_horizontal = QtWidgets.QPushButton()
        self.split_horizontal.setIcon(QtGui.QIcon('./Resources/images/divisionhorizontal.png'))
        self.split_horizontal.setIconSize(QtCore.QSize(btn_size - 2.5, btn_size - 2))
        self.split_horizontal.clicked.connect(self.split_horizontally)
        self.split_horizontal.setFixedSize(btn_size, btn_size)
        self.split_horizontal.setStyleSheet(style_sheet)

        self.close = QtWidgets.QPushButton()
        self.close.setIcon(QtGui.QIcon('./Resources/images/close.png'))
        self.close.setIconSize(QtCore.QSize(btn_size - 7, btn_size - 7))
        self.close.clicked.connect(self.close_window)
        self.close.setFixedSize(btn_size, btn_size)
        self.close.setStyleSheet(style_sheet)

        spacer = QtWidgets.QSpacerItem(8, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.layout.addSpacerItem(spacer)
        self.layout.insertWidget(1, self.view)

        if self.toolbar:
            self.layout.insertWidget(1, self.toolbar)

        self.layout.insertWidget(2, self.title)
        self.layout.insertWidget(3, self.split_horizontal)
        self.layout.addSpacerItem(spacer)
        self.layout.insertWidget(5, self.close)

        self.title.setStyleSheet("""
            background: #d7d6d5;
            color: #d7d6d5;
        """)

        self.setLayout(self.layout)

        self.start = QtCore.QPoint(0, 0)

    def resizeEvent(self, QResizeEvent):
        super(CustomBar, self).resizeEvent(QResizeEvent)
        self.title.setFixedWidth(self.parent.width())

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())

    def selection_change(self):
        self.handle_split(new_view=self.view.currentText())

    def split_vertically(self):
        pass

    def split_horizontally(self):
        self.handle_split(direction='horizontal')

    def close_window(self):
        self.handle_split(action='close', kind=self.kind)




