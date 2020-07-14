import vtk


class Picker:
    def __init__(self, mainwindow, change_styles):
        self.mainwindow = mainwindow
        self.change_styles = change_styles
        self.current_style = None
        self.change = None

    def pick_event(self, cone_release=None):
        # get position of cursor on mouse press and poked renderer
        click_pos = self.mainwindow.vtk3d_widget.iren.GetEventPosition()
        ren = self.mainwindow.vtk3d_widget.iren.FindPokedRenderer(click_pos[0], click_pos[1])

        # this for picking glyphs
        cell_picker = vtk.vtkCellPicker()
        cell_picker.Pick(click_pos[0], click_pos[1], 0, ren)

        # only continue if we have a file loaded
        if self.mainwindow.markers:
            input_ids = self.mainwindow.markers.glyph.GetOutput().GetPointData().GetArray("InputPointIds")

            if input_ids:
                cell = self.mainwindow.markers.glyph.GetOutput().GetCell(cell_picker.GetCellId())
                if cell and cell.GetNumberOfPoints() > 0:
                    input_id = cell.GetPointId(0)
                    selected_id = int(input_ids.GetTuple1(input_id))

                    if selected_id > 0:
                        self.mainwindow.highlighter.highlighter_picked_handler(selected_id, from_picker=True)

        # selecting draggable cone actor
        prop_picker = vtk.vtkPropPicker()
        prop_picker.Pick(click_pos[0], click_pos[1], 0, ren)
        picked_actor_id = prop_picker.GetActor()

        if self.mainwindow.gaps.gap_cone_actor_start == picked_actor_id:
            self.change_styles.change_style('actor', cone_dir='start')
            self.current_style = 'actor'

        elif self.mainwindow.gaps.gap_cone_actor_end == picked_actor_id:
            self.change_styles.change_style('actor', cone_dir='end')
            self.current_style = 'actor'

        # a cone actor has been dragged or selected and we are releasing
        if cone_release:
            if self.current_style == 'actor':
                self.current_style = 'camera'
                self.change_styles.change_style('camera')





