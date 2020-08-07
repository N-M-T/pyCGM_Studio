import vtk
from QVTKRenderWindowInteractorMod import QVTKRenderWindowInteractorMod
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from pycgm_interactor_styles import PycgmTrackballStyle, PycgmDragActorStyle
from PyQt5 import QtWidgets
from floorplane import build_plane


class VTK2d(QtWidgets.QFrame):
    def __init__(self, parent):
        super(VTK2d, self).__init__(parent)
        self.iren = QVTKRenderWindowInteractor()
        self.vl = QtWidgets.QHBoxLayout()
        self.vl.addWidget(self.iren)
        self.setLayout(self.vl)
        self.iren.Initialize()
        self.view = vtk.vtkContextView()
        self.chart_matrix = vtk.vtkChartMatrix()
        self.view.GetScene().AddItem(self.chart_matrix)
        self.ren = self.view.GetRenderer()
        self.iren.GetRenderWindow().AddRenderer(self.ren)


class VTK3d(QtWidgets.QWidget):
    def __init__(self, parent):
        super(VTK3d, self).__init__(parent)
        # create custom renderwindowinteractor
        self.iren = QVTKRenderWindowInteractorMod()
        self.pycgm_trackball_style = PycgmTrackballStyle(self.iren)
        self.iren.SetInteractorStyle(self.pycgm_trackball_style)

        # renderer
        self.ren = vtk.vtkRenderer()

        # add renderer to custom renderwindowinteractor
        self.render_window = self.iren.GetRenderWindow()
        self.render_window.AddRenderer(self.ren)
        self.pycgm_drag_actor_style = PycgmDragActorStyle(self.iren, self.ren)

        self.vl = QtWidgets.QHBoxLayout()
        self.vl.addWidget(self.iren)
        self.setLayout(self.vl)

        # camera
        self.camera = self.ren.GetActiveCamera()

        # set floor plane
        self.ren.AddActor(build_plane(position=.2, params=(0, 5600, 800), colour=(1, 1, 1)))
        self.ren.AddActor(build_plane(position=0, params=(0, 5000, 200), colour=(.4, .4, .4)))
        self.ren.AddActor(build_plane(position=.2, params=(0, 5600, 800), colour=(1, 1, 1)))

        # set camera properties
        self.camera.Pitch(70.0)
        self.camera.Roll(0.0)
        self.camera.Yaw(0.0)

        # add axes
        axes_actor = vtk.vtkAxesActor()

        # orientation widget
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(axes_actor)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()
        self.ren.ResetCamera()

        self.iren.Initialize()
