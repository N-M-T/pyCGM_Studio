import vtk
import numpy as np


def fp_source(centre, sizes, label):
    colors = vtk.vtkNamedColors()

    text_source = vtk.vtkVectorText()
    text_source.SetText(label)
    text_source.Update()

    # Create a mapper and actor
    text_mapper = vtk.vtkPolyDataMapper()
    text_mapper.SetInputConnection(text_source.GetOutputPort())

    text_actor = vtk.vtkActor()
    text_actor.SetMapper(text_mapper)
    text_actor.GetProperty().SetColor(colors.GetColor3d('White'))
    scalex = (sizes[0]) / 2
    scaley = (sizes[1]) / 2
    text_centre = centre + (scalex/2, -scaley/3, 0)
    text_actor.SetPosition(text_centre)
    text_actor.SetOrientation(0, 0, 90)
    text_actor.SetScale(scalex)

    # Colored faces cube setup
    cube_source = vtk.vtkCubeSource()
    cube_source.SetXLength(sizes[0])
    cube_source.SetYLength(sizes[1])
    cube_source.SetZLength(sizes[2])
    cube_centre = centre - (0, 0, 1)
    cube_source.SetCenter(cube_centre)

    # cube_source.SetBounds(bounds)
    cube_source.Update()

    cube_mapper = vtk.vtkPolyDataMapper()
    cube_mapper.SetInputData(cube_source.GetOutput())
    cube_mapper.Update()
    cube_actor = vtk.vtkActor()
    cube_actor.SetMapper(cube_mapper)

    # cube colourage
    face_colors = vtk.vtkUnsignedCharArray()
    face_colors.SetNumberOfComponents(3)
    face_x_plus = colors.GetColor3ub('Grey')
    face_x_minus = colors.GetColor3ub('Grey')
    face_y_plus = colors.GetColor3ub('Grey')
    face_y_minus = colors.GetColor3ub('Grey')
    face_z_plus = colors.GetColor3ub('Grey')
    face_z_minus = colors.GetColor3ub('Red')

    face_colors.InsertNextTypedTuple(face_x_minus)
    face_colors.InsertNextTypedTuple(face_x_plus)
    face_colors.InsertNextTypedTuple(face_y_minus)
    face_colors.InsertNextTypedTuple(face_y_plus)
    face_colors.InsertNextTypedTuple(face_z_minus)
    face_colors.InsertNextTypedTuple(face_z_plus)
    cube_source.GetOutput().GetCellData().SetScalars(face_colors)

    return cube_actor, text_actor


def get_bounds(fp):
    centre = np.average(fp, axis=0)
    sizes = []
    for i in range(3):
        sizes.append(abs(max(fp[:, i]) - min(fp[:, i])) + 1)

    return centre, sizes


class ForcePlatforms:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.fps = []
        self.fps_showing = False

    def setup_fps(self):
        if len(self.fps) > 0:
            self.remove_fps()

        # no_forceplatforms = self.mainwindow.pycgm_data.c3d['parameters']['FORCE_PLATFORM']['USED']['value'][0]
        force_plts = self.mainwindow.pycgm_data.c3d['parameters']['FORCE_PLATFORM']['CORNERS']['value'].T

        for n, fp in enumerate(force_plts):
            centre, sizes = get_bounds(fp)
            fp_actors = fp_source(centre, sizes, str(n + 1))
            self.fps.append(fp_actors)

        self.show_fps()

    def show_fps(self):
        if not self.fps_showing:
            if len(self.fps) > 0:
                for actor in self.fps:
                    self.mainwindow.vtk3d_widget.ren.AddActor(actor[0])
                    self.mainwindow.vtk3d_widget.ren.AddActor(actor[1])
                self.fps_showing = True

    def remove_fps(self):
        for actor in self.fps:
            self.mainwindow.vtk3d_widget.ren.RemoveActor(actor[0])
            self.mainwindow.vtk3d_widget.ren.RemoveActor(actor[1])
        self.fps.clear()
        self.fps_showing = False





