class Emitter:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.current_frame = None
        self.update_current_line = None
        self.offset = None

    def set_offset(self, offset):
        self.offset = offset

    def emit(self, frame, from_bar=None):
        if frame == 'current':
            frame = self.current_frame
        else:
            self.current_frame = frame

        self.mainwindow.ui.currentFrame.setText(str(frame))

        # if data has been truncated, remove offset
        if self.offset:
            frame = frame - self.offset

        # show markers if data is loaded
        if self.mainwindow.pycgm_data:
            self.mainwindow.markers.marker_request(frame)
            self.mainwindow.trajectories.trajectory_request(frame)
            self.mainwindow.gaps.ingap_request(frame)
            self.mainwindow.explorer_widget.highlight_marker_label(frame)

        self.mainwindow.vtk3d_widget.iren.Render()

        # set slider position
        if not self.mainwindow.ui.vtkScrollSlider.isSliderDown():
            self.mainwindow.ui.vtkScrollSlider.setValue(frame)

        # set plot progress bar if not from plot progress bar
        if not from_bar:
            self.mainwindow.plotter.update_current_line(frame)
