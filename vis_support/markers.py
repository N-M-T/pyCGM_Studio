import vtk
import numpy as np
import vtk.util.numpy_support as vtk_np


class Markers:
    def __init__(self, mainwindow, num_points):
        self.mainwindow = mainwindow
        self.emitted = False
        self.points = self.mainwindow.pycgm_data.Data['Markers']
        self.marker_names = [*self.points]
        self.num_points = num_points
        self.size = vtk.vtkUnsignedCharArray()
        self.size.SetNumberOfComponents(3)
        self.size.SetNumberOfTuples(self.num_points)
        self.colours = vtk.vtkUnsignedCharArray()
        self.colours.SetNumberOfComponents(3)
        self.colours.SetNumberOfTuples(self.num_points)

        for i in range(0, self.num_points):
            self.colours.SetTuple(i, (192, 192, 192))
            self.size.SetTuple(i, (1, 1, 1))

        # point cloud
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(12)
        sphere.SetThetaResolution(8)
        sphere.SetPhiResolution(8)
        sphere.Update()
        self.cloud_points = vtk.vtkPoints()
        self.cloud_points.SetNumberOfPoints(self.num_points)
        self.poly_data = vtk.vtkPolyData()
        self.poly_data.SetPoints(self.cloud_points)
        self.poly_data.GetPointData().SetScalars(self.size)
        self.poly_data.GetPointData().AddArray(self.colours)
        self.glyph = vtk.vtkGlyph3D()
        self.glyph.SetGeneratePointIds(True)
        self.glyph.SetInputData(self.poly_data)
        self.glyph.SetSourceConnection(sphere.GetOutputPort())
        self.glyph.SetScaleModeToScaleByScalar()
        self.glyph.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.glyph.GetOutputPort())
        mapper.SetScalarModeToUsePointFieldData()
        mapper.SelectColorArray(1)
        mapper.SetScalarRange(0, self.num_points)
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.vtk_markers_source = []

    def set_actor(self):
        self.mainwindow.vtk3d_widget.ren.AddActor(self.actor)

    def update_data(self, complete=None, individual=None):
        # create a list of numpy arrays containing each frame of marker data.
        # vis_toolkit numpy vis_support then allocates array to point cloud at marker frame
        # request.
        # update all marker trajectories
        if complete:
            self.vtk_markers_source = []
            for frame in range(self.num_points):
                data = np.empty([len([*self.points]), 3], dtype=float)
                for ind, (marker, val) in enumerate(self.points.items()):
                    data[ind, :] = val[:3, frame]
                self.vtk_markers_source.append(data)

        # update individual marker trajectory
        elif individual:
            index = self.marker_names.index(individual)
            for frame in range(self.num_points):
                data = self.points[individual][:3, frame]
                self.vtk_markers_source[frame][index] = data

    def set_marker_colour(self, marker_id, rgb_tuple):
        self.colours.SetTuple(marker_id, rgb_tuple)

    def set_marker_size(self, marker_id, size_tuple):
        self.size.SetTuple(marker_id, size_tuple)

    def marker_request(self, frame):
        try:
            self.cloud_points.SetData(vtk_np.numpy_to_vtk(self.vtk_markers_source[frame]))
            self.cloud_points.Modified()
            self.poly_data.Modified()
            self.glyph.Update()
            self.emitted = True
        except Exception:
            # this needs resolving
            pass

    def reset_helper(self):
        self.cloud_points.Reset()
        self.poly_data.Reset()

    def remove_actors(self):
        self.mainwindow.vtk3d_widget.ren.RemoveActor(self.actor)




