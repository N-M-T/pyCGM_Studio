from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt


class QVTKRenderWindowInteractorMod(QVTKRenderWindowInteractor):
    """
    From what I could find, vtkInteractorStyleTrackballCamera didn't support left and right
    mouse click (17.04.20), which I wanted for panning. So I hacked my own method, but it needed a private
    attribute from the interactor: _ActiveButton to be modified on mouse release, which is a
    QtButtonEvent. So this class inherits the QVTKRenderWindowInteractor and overrides the
    mouseReleaseEvent
    """

    def mouseReleaseEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(ev.x(), ev.y(),
                                            ctrl, shift, chr(0), 0, None)

        self._ActiveButton = ev.button()  # private attribute

        if self._ActiveButton == Qt.LeftButton:
            self._Iren.LeftButtonReleaseEvent()
        elif self._ActiveButton == Qt.RightButton:
            self._Iren.RightButtonReleaseEvent()
        elif self._ActiveButton == Qt.MidButton:
            self._Iren.MiddleButtonReleaseEvent()
