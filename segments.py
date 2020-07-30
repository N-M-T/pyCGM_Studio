import vtk


class Segments:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.segment_dict = dict()
        self.segment_keys = []
        self.segments = ['HED', 'LCL', 'LFE', 'LFO', 'LHN', 'LHU', 'LRA', 'LTI', 'LTO', 'PEL', 'RCL',
                         'RFE', 'RFO', 'RHN', 'RHU', 'RRA', 'RTI', 'RTO', 'TRX']

        named_colours = vtk.vtkNamedColors()
        self.colors = vtk.vtkUnsignedCharArray()
        self.colors.SetNumberOfComponents(3)
        colours = ['Blue', 'Red', 'Green']
        for colour in colours:
            self.colors.InsertNextTypedTuple(named_colours.GetColor3ub(colour))

        self.axes = ('O', 'P', 'A', 'L')

    def set_segment_keys(self):
        self.segment_keys = [*self.mainwindow.pycgm_data.Data['Bones']]

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
            self.remove_actors()
            self.segment_keys = []
            self.segment_dict = dict()

    def remove_actors(self):
        for key, segment in self.segment_dict.items():
            self.mainwindow.vtk3d_widget.ren.RemoveActor(segment['actor'])

    def segment_request(self, frame):
        if len(self.segment_keys) > 0:
            for key, segment in self.segment_dict.items():
                coords = [self.mainwindow.pycgm_data.Data['Bones'][key + axis][:3, frame] for axis in self.axes]
                coords[2] = (coords[0] + coords[2]) / 2
                coords[3] = (coords[0] + coords[3]) / 2
                segment['points'].Reset()
                for coord in coords:
                    segment['points'].InsertNextPoint(coord)



