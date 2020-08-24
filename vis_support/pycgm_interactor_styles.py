import vtk
from PyQt5.QtCore import Qt
from core import utilities as ut
import numpy as np


class PycgmTrackballStyle(vtk.vtkInteractorStyleTrackballActor):
    def __init__(self, iren, parent=None):
        # set global up for camera
        self.mp_global_up = [0.0, 0.0, 1.0]

        self.AddObserver("LeftButtonPressEvent", self.mouse_press)
        self.AddObserver("LeftButtonReleaseEvent", self.mouse_release)
        self.AddObserver("MiddleButtonPressEvent", self.mouse_press)
        self.AddObserver("MiddleButtonReleaseEvent", self.mouse_release)
        self.AddObserver("RightButtonPressEvent", self.mouse_press)
        self.AddObserver("RightButtonReleaseEvent", self.mouse_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)

        self.iren = iren
        self.ren_win = self.iren.GetRenderWindow()
        self.left = False
        self.right = False
        self.rotating = False
        self.panning = False
        self.zooming = False
        self.picker = None

    def set_picker(self, picker):
        self.picker = picker

    def after_style_switch(self):
        self.left = False
        self.rotating = False
        self.zooming = False

    def mouse_press(self, obj, event):
        # _ActiveButton is private attribute of interactor
        if self.iren._ActiveButton == Qt.MiddleButton:
            self.panning = True
        elif self.iren._ActiveButton == Qt.LeftButton:
            if self.right and not self.left:
                self.left = True
                self.panning = True
                self.rotating = False
            elif not self.left:
                self.left = True
                self.rotating = True
                self.picker.pick_event()
        if self.iren._ActiveButton == Qt.RightButton:
            if self.left and not self.right:
                self.right = True
                self.panning = True
                self.rotating = False
            elif not self.right:
                self.right = True
                self.zooming = True

    def mouse_release(self, obj, event):
        if self.iren._ActiveButton == Qt.MiddleButton:
            self.panning = False
        elif self.iren._ActiveButton == Qt.LeftButton:
            if self.right and self.left:
                self.left = False
                self.panning = False
                self.zooming = True
            elif self.left:
                self.left = False
                self.rotating = False
                self.zooming = False
        if self.iren._ActiveButton == Qt.RightButton:
            if self.left and self.right:
                self.right = False
                self.panning = False
                self.rotating = True
            elif self.right:
                self.right = False
                self.zooming = False

    def mouse_move(self, obj, event):
        last_xy_pos = self.iren.GetLastEventPosition()
        last_x = last_xy_pos[0]
        last_y = last_xy_pos[1]

        xypos = self.iren.GetEventPosition()
        x = xypos[0]
        y = xypos[1]
        center = self.iren.GetRenderWindow().GetSize()
        center_x = center[0] / 2.0
        center_y = center[1] / 2.0

        ren = self.iren.FindPokedRenderer(x, y)

        if self.rotating:
            self.rotate(ren.GetActiveCamera(), x, y, last_x, last_y,
                        center_x, center_y)

        elif self.panning:
            self.pan(ren, ren.GetActiveCamera(), x, y, last_x, last_y,
                     center_x, center_y)

        elif self.zooming:
            self.dolly(ren, ren.GetActiveCamera(), y, last_y)

    def rotate(self, camera, x, y, last_x, last_y, center_x, center_y):

        """
        This one is associated with the left mouse button. It translates x
        and y relative motions into camera azimuth and elevation commands.
        """

        rx = -360.0 * (x - last_x) / center_x
        ry = 90.0 * (y - last_y) / center_y

        camera_up = camera.GetViewUp()
        camera_proj = camera.GetDirectionOfProjection()
        global_up = self.mp_global_up

        axis_right = ut.normalize(np.cross(camera_proj, global_up))
        angle_up = np.arccos(np.dot(camera_up, global_up)) * 180.0 / np.pi

        if angle_up + ry >= 90.0:
            ry = 89.0 - angle_up

        fp = camera.GetFocalPoint()
        transform = vtk.vtkTransform()
        transform.Identity()
        transform.Translate(fp[0], fp[1], fp[2])
        transform.RotateWXYZ(rx, global_up)
        transform.RotateWXYZ(ry, axis_right)
        transform.Translate(-fp[0], -fp[1], -fp[2])
        camera.ApplyTransform(transform)

        camera.OrthogonalizeViewUp()

        self.ren_win.Render()

    def pan(self, renderer, camera, x, y, last_x, last_y, center_x, center_y):

        """
        Pan translates x-y motion into translation of the focal point and
        position.
        """

        f_point = camera.GetFocalPoint()
        f_point_0 = f_point[0]
        f_point_1 = f_point[1]
        f_point_2 = f_point[2]

        p_point = camera.GetPosition()
        p_point_0 = p_point[0]
        p_point_1 = p_point[1]
        p_point_2 = p_point[2]

        renderer.SetWorldPoint(f_point_0, f_point_1, f_point_2, 1.0)
        renderer.WorldToDisplay()
        d_point = renderer.GetDisplayPoint()
        focal_depth = d_point[2]

        a_point_0 = center_x + (x - last_x)
        a_point_1 = center_y + (y - last_y)

        renderer.SetDisplayPoint(a_point_0, a_point_1, focal_depth)
        renderer.DisplayToWorld()
        r_point = renderer.GetWorldPoint()
        r_point_0 = r_point[0]
        r_point_1 = r_point[1]
        r_point_2 = r_point[2]
        r_point_3 = r_point[3]

        if r_point_3 != 0.0:
            r_point_0 = r_point_0 / r_point_3
            r_point_1 = r_point_1 / r_point_3
            r_point_2 = r_point_2 / r_point_3

        camera.SetFocalPoint((f_point_0 - r_point_0) / 2.0 + f_point_0,
                             (f_point_1 - r_point_1) / 2.0 + f_point_1,
                             (f_point_2 - r_point_2) / 2.0 + f_point_2)
        camera.SetPosition((f_point_0 - r_point_0) / 2.0 + p_point_0,
                           (f_point_1 - r_point_1) / 2.0 + p_point_1,
                           (f_point_2 - r_point_2) / 2.0 + p_point_2)
        self.ren_win.Render()

    def dolly(self, renderer, camera, y, last_y):

        """
        Dolly converts y-motion into a camera dolly commands.
        """

        dolly_factor = pow(1.02, (0.5 * (y - last_y)))
        if camera.GetParallelProjection():
            parallel_scale = camera.Getparallel_scale() * dolly_factor
            camera.Setparallel_scale(parallel_scale)
        else:
            camera.Dolly(dolly_factor)
            renderer.ResetCameraClippingRange()

        self.ren_win.Render()


class PycgmDragActorStyle(vtk.vtkInteractorStyleTrackballActor):
    def __init__(self, iren, ren, parent=None):
        self.AddObserver('LeftButtonReleaseEvent', self.left_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)
        self.RemoveObservers("MiddleButtonPressEvent")
        self.RemoveObservers("RightButtonPressEvent")
        self.RemoveObservers("CharEvent")
        self.left_pressed = False
        self.cone_dir = None
        self.iren = iren
        self.ren = ren
        self.ren_win = iren.GetRenderWindow()
        self.start_base_x = 0.
        self.end_base_x = 0.
        self.picker = None
        self.gaps = None

    def set_picker(self, picker):
        self.picker = picker

    def set_gaps(self, gaps):
        self.gaps = gaps

    def left_release(self, obj, event):
        self.left_pressed = False
        self.cone_dir = None
        self.picker.pick_event(cone_release=True)

    def left_press(self, cone_dir):
        self.cone_dir = cone_dir
        self.left_pressed = True

    def display_to_world(self, display_coords):
        self.ren.SetDisplayPoint(display_coords)
        self.ren.DisplayToView()
        self.ren.GetViewPoint()
        self.ren.ViewToWorld()
        world_coords = self.ren.GetWorldPoint()
        return np.asarray(world_coords)[:-1]

    def mouse_move(self, obj, event):
        """This method is a quick hack to get the cones draggable.
        Needs cleaning up and modifying so the cursor is bound to cone
        boundary"""
        last_pos = self.iren.GetLastEventPosition()
        next_pos = self.iren.GetEventPosition()
        last_disp_coords = np.asarray([last_pos[0], last_pos[1], 0])
        next_disp_coords = np.asarray([next_pos[0], next_pos[1], 0])
        last_world_coords = self.display_to_world(last_disp_coords)
        next_world_coords = self.display_to_world(next_disp_coords)
        world_direction = (last_world_coords - next_world_coords)[0]

        if world_direction > 0:
            direction = 'forwards'
        elif world_direction < 0:
            direction = 'backwards'
        else:
            direction = 'none'

        if self.cone_dir == 'start':
            if direction == 'backwards':
                self.start_base_x += .5
                if self.start_base_x.is_integer():
                    ind = str(int(self.start_base_x))
                    isvalid = self.gaps.set_dragged_start(ind)
                    if isvalid:
                        self.ren_win.Render()
                    else:
                        self.start_base_x -= .5
                        return

            elif direction == 'forwards':
                if self.start_base_x > 0:
                    self.start_base_x -= .5
                    if self.start_base_x.is_integer():
                        ind = str(int(self.start_base_x))
                        self.gaps.set_dragged_start(ind)
                        self.ren_win.Render()

        if self.cone_dir == 'end':
            if direction == 'backwards':
                if self.end_base_x > 0:
                    self.end_base_x -= .5
                    if self.end_base_x.is_integer():
                        ind = str(int(self.end_base_x))
                        self.gaps.set_dragged_end(ind)
                        self.ren_win.Render()

            elif direction == 'forwards':
                self.end_base_x += .5
                if self.end_base_x.is_integer():
                    ind = str(int(self.end_base_x))
                    isvalid = self.gaps.set_dragged_end(ind)
                    if isvalid:
                        self.ren_win.Render()
                    else:
                        self.end_base_x -= .5
                        return

    def reset_base_x(self):
        self.start_base_x = 0.
        self.end_base_x = 0.


class ChangeStyles:
    def __init__(self, vtk3d_widget):
        self.vtk3d_widget = vtk3d_widget

    def change_style(self, style, cone_dir=None):
        if style == 'actor':
            self.vtk3d_widget.iren.SetInteractorStyle(self.vtk3d_widget.pycgm_drag_actor_style)
            self.vtk3d_widget.pycgm_drag_actor_style.left_press(cone_dir)

        elif style == 'camera':
            self.vtk3d_widget.iren.SetInteractorStyle(self.vtk3d_widget.pycgm_trackball_style)
            self.vtk3d_widget.pycgm_trackball_style.after_style_switch()
