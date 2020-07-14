import vtk
import numpy as np
import vtk.util.numpy_support as vtk_np


class Markers:
    def __init__(self, mainwindow, num_points):
        self.emitted = False
        self.points = mainwindow.pycgm_data.Data['Markers']
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
        self.sphere = vtk.vtkSphereSource()
        self.sphere.SetRadius(12)
        self.sphere.SetThetaResolution(8)
        self.sphere.SetPhiResolution(8)
        self.sphere.Update()
        self.cloud_points = vtk.vtkPoints()
        self.cloud_points.SetNumberOfPoints(self.num_points)
        self.poly_data = vtk.vtkPolyData()
        self.poly_data.SetPoints(self.cloud_points)
        self.poly_data.GetPointData().SetScalars(self.size)
        self.poly_data.GetPointData().AddArray(self.colours)
        self.glyph = vtk.vtkGlyph3D()
        self.glyph.SetGeneratePointIds(True)
        self.glyph.SetInputData(self.poly_data)
        self.glyph.SetSourceConnection(self.sphere.GetOutputPort())
        self.glyph.SetScaleModeToScaleByScalar()
        self.glyph.Update()
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.glyph.GetOutputPort())
        self.mapper.SetScalarModeToUsePointFieldData()
        self.mapper.SelectColorArray(1)
        self.mapper.SetScalarRange(0, self.num_points)
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

        self.vtk_markers_source = []

    def update_data(self, complete=None, individual=None):
        # create a list of numpy arrays containing each frame of marker data.
        # vtk numpy support then allocates array to point cloud at marker frame
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
        except Exception as err:
            print(err)
            # this needs resolving

    def reset_helper(self):
        self.cloud_points.Reset()
        self.poly_data.Reset()

    def remove_actors(self):
        self.mainwindow.vtk3d_widget.ren.RemoveActor(self.actor)



