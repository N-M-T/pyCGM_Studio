import vtk
import numpy as np
from core_operations import utilities as ut


def request_pycgm_segment(key, segment, coords):
    # todo: calculate length of limbs using jc and extend segments accordingly
    offsets = np.asarray([120, 80])
    # extend legs and arms (arbitrary length for now)
    if key[-2:] in ['TI', 'FE', 'HU', 'RA']:
        offsets = offsets + np.asarray([120, 0])
    o = coords[0]
    x = coords[1]
    y = coords[2]
    z = coords[3]
    x_unit_vector = np.array(ut.unit(o - x))
    x_newpos = o - (x_unit_vector * offsets[0])
    y_unit_vector = np.array(ut.unit(o - y))
    y_newpos = o - (y_unit_vector * offsets[1])
    z_unit_vector = np.array(ut.unit(o - z))
    z_newpos = o - (z_unit_vector * offsets[1])
    coords[1] = x_newpos
    coords[2] = y_newpos
    coords[3] = z_newpos
    segment['points'].Reset()
    for coord in coords:
        segment['points'].InsertNextPoint(coord)


def request_manufacturer_segment(segment, coords):
    coords[2] = (coords[0] + coords[2]) / 2
    coords[3] = (coords[0] + coords[3]) / 2
    segment['points'].Reset()
    for coord in coords:
        segment['points'].InsertNextPoint(coord)


class Segments:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.segment_dict = dict()
        self.segment_keys = []
        self.segment_data = None
        self.segments = ['HED', 'LCL', 'LFE', 'LFO', 'LHN', 'LHU', 'LRA', 'LTI', 'PEL', 'RCL',
                         'RFE', 'RFO', 'RHN', 'RHU', 'RRA', 'RTI', 'TRX']

        named_colours = vtk.vtkNamedColors()
        self.colors = vtk.vtkUnsignedCharArray()
        self.colors.SetNumberOfComponents(3)
        colours = ['Blue', 'Red', 'Green']
        for colour in colours:
            self.colors.InsertNextTypedTuple(named_colours.GetColor3ub(colour))
        self.axes = ('O', 'P', 'A', 'L')
        self.using_pycgm_segments = False

    def set_segment_data(self, pycgm=None):
        if pycgm:
            self.using_pycgm_segments = True
            self.segment_keys = [*self.mainwindow.pycgm_data.Data['pyCGM Bones']]
            self.segment_data = self.mainwindow.pycgm_data.Data['pyCGM Bones']
        else:
            self.using_pycgm_segments = False
            self.segment_keys = [*self.mainwindow.pycgm_data.Data['Bones']]
            self.segment_data = self.mainwindow.pycgm_data.Data['Bones']

    def update_segments(self):
        if len(self.segment_keys) > 0:
            for segment in self.segments:
                line_list = []
                for i in range(1, 4):
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, 0)
                    line.GetPointIds().SetId(1, i)
                    line_list.append(line)

                points = vtk.vtkPoints()
                lines = vtk.vtkCellArray()
                polydata = vtk.vtkPolyData()
                mapper = vtk.vtkPolyDataMapper()
                actor = vtk.vtkActor()

                for line in line_list:
                    lines.InsertNextCell(line)

                polydata.SetPoints(points)
                polydata.SetLines(lines)
                polydata.GetCellData().SetScalars(self.colors)
                mapper.SetInputData(polydata)
                actor.SetMapper(mapper)
                actor.GetProperty().SetLineWidth(3)
                self.segment_dict[segment] = {'points': points,
                                              'polydata': polydata,
                                              'actor': actor}
            self.set_actors()

    def set_actors(self):
        for key, segment in self.segment_dict.items():
            self.mainwindow.vtk3d_widget.ren.AddActor(segment['actor'])

    def clear(self):
        if len(self.segment_keys) > 0:
            for key, segment in self.segment_dict.items():
                self.mainwindow.vtk3d_widget.ren.RemoveActor(segment['actor'])
            self.segment_keys = []
            self.segment_dict = dict()

    def segment_request(self, frame):
        if len(self.segment_keys) > 0:
            for key, segment in self.segment_dict.items():
                coords = [self.segment_data[key + axis][:3, frame] for axis in self.axes]
                if self.using_pycgm_segments:
                    request_pycgm_segment(key, segment, coords)
                else:
                    request_manufacturer_segment(segment, coords)




