import vtk
import vtk.util.numpy_support as vtk_np
import numpy as np
np.set_printoptions(suppress=True)


def traj_gen(colour=None, properties=None):
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    polydata = vtk.vtkPolyData()
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()
    polydata.SetPoints(points)
    polydata.SetLines(lines)
    mapper.SetInputData(polydata)
    actor.SetMapper(mapper)

    if colour:
        actor.GetProperty().SetColor(colour)
    if properties:
        actor.SetProperty(properties)

    return points, lines, polydata, actor


class Trajectories:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.marker_keys = []
        self.highlighted = {}
        self.emitted = False

    def set_marker_keys(self):
        self.marker_keys = [*self.mainwindow.pycgm_data.Data['Markers']]

    def update_trajectories(self, selected_id, add=None, remove=None):
        if add:
            pnts, lnes, plydat, act = traj_gen(colour=(0.0, .3, 1.0))
            self.highlighted[selected_id] = {'points': pnts,
                                             'lines': lnes,
                                             'polydata': plydat,
                                             'actor': act}
            self.mainwindow.vtk3d_widget.ren.AddActor(act)

        if remove:
            self.mainwindow.vtk3d_widget.ren.RemoveActor(self.highlighted[selected_id]['actor'])
            del self.highlighted[selected_id]

    def trajectory_request(self, frame):
        half = 50
        lower = frame - half
        upper = frame + half

        if lower < 0:
            lower = 0
        if upper > self.mainwindow.pycgm_data.Gen['Vid_LastFrame']:
            upper = self.mainwindow.pycgm_data.Gen['Vid_LastFrame']

        ncoords = upper - lower

        for key, objs in self.highlighted.items():
            if self.emitted:
                objs['polydata'].Reset()

            point_coords = self.mainwindow.pycgm_data.Data['Markers'][self.marker_keys[int(key)]][:3, lower:upper].T
            objs['points'].SetData(vtk_np.numpy_to_vtk(point_coords))

            # cannot get this method to work
            # cells_npy = np.arange(ncoords, dtype=np.int64)
            # objs['lines'].SetCells(ncoords, vtk_np.numpy_to_vtkIdTypeArray(cells_npy))

            # old method
            objs['lines'].InsertNextCell(ncoords)
            for k in range(ncoords):
                objs['lines'].InsertCellPoint(k)

            objs['points'].Modified()
            objs['lines'].Modified()
            objs['polydata'].Modified()

        self.emitted = True





