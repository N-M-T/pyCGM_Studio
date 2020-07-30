import vtk


class VtkTitle:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        colors = vtk.vtkNamedColors()
        self.txt = vtk.vtkTextActor()
        txtprop = self.txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.BoldOn()
        txtprop.SetFontSize(26)
        txtprop.SetColor(colors.GetColor3d("White"))
        self.mainwindow.vtk3d_widget.ren.AddActor(self.txt)

    def set_text(self, instring):
        self.txt.SetInput(instring)

    def set_actor(self):
        self.mainwindow.vtk3d_widget.ren.AddActor(self.txt)

    def remove_actor(self):
        self.mainwindow.vtk3d_widget.ren.RemoveActor(self.txt)
