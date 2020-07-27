import vtk


def bone_segment_generator(mainwindow):
    axes = ('O', 'P', 'A', 'L')
    segments = ['HED', 'LCL', 'LFE', 'LFO', 'LHN', 'LHU', 'LRA', 'LTI', 'LTO', 'PEL', 'RCL',
                'RFE', 'RFO', 'RHN', 'RHU', 'RRA', 'RTI', 'RTO', 'TRX']

    for segment in segments:
        coords = []
        for axis in axes:
            bone_key = segment + axis
            coords.append(mainwindow.pycgm_data.Data['Bones'][bone_key][:3, 0])

        coords[2] = (coords[0] + coords[2]) / 2
        coords[3] = (coords[0] + coords[3]) / 2

        lines_poly_data = vtk.vtkPolyData()

        # Create a vtkPoints container and store the points in it
        pts = vtk.vtkPoints()
        for coord in coords:
            pts.InsertNextPoint(coord)

        # Add the points to the polydata container
        lines_poly_data.SetPoints(pts)

        line_list = []
        for i in range(1, 4):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, 0)
            line.GetPointIds().SetId(1, i)
            line_list.append(line)

        # Create a vtkCellArray container and store the lines in it
        lines = vtk.vtkCellArray()
        for line in line_list:
            lines.InsertNextCell(line)

        # Add the lines to the polydata container
        lines_poly_data.SetLines(lines)

        namedColors = vtk.vtkNamedColors()

        # Create a vtkUnsignedCharArray container and store the colors in it
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colours = ['Blue', 'Red', 'Green']
        for colour in colours:
            colors.InsertNextTypedTuple(namedColors.GetColor3ub(colour))
        lines_poly_data.GetCellData().SetScalars(colors)

        # Setup the visualization pipeline
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(lines_poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(3)
        mainwindow.vtk3d_widget.ren.AddActor(actor)


class Segments:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.segments = dict()
        self.segment_keys = []

    def set_segment_keys(self):
        self.segment_keys = [*self.mainwindow.pycgm_data.Data['Bones']]

    def update_segments(self):
        if len(self.segment_keys) > 0:
            bone_segment_generator(self.mainwindow)

    def segment_request(self):
        pass








