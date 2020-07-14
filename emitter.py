class Emitter:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.current_frame = None
        self.update_current_line = None
        self.offset = None

    def set_offset(self, offset):
        self.offset = offset

    def emit(self, frame):
        if frame == 'current':
            frame = self.current_frame
        else:
            self.current_frame = frame

        self.mainwindow.ui.currentFrame.setText(str(frame))

        # if data has been truncated, remove offset
        if self.offset:
            frame = frame - self.offset

        if self.mainwindow.markers:
            self.mainwindow.markers.marker_request(frame)
            self.mainwindow.trajectories.trajectory_request(frame)
            self.mainwindow.gaps.ingap_request(frame)
            self.mainwindow.explorer_widget.highlight_marker_label(frame)

        self.mainwindow.vtk3d_widget.iren.Render()
        self.mainwindow.plotter.update_current_line(frame)
