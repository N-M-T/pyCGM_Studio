from PyQt5 import QtWidgets
import time


class VtkTimerCallback:
    """
    Timer callback for playing animation

    The repeatingtimer fires every 10ms. To get appropriate scaling factor:
    1 / 0.01 = 100
    sampfreq (e.g. 120) / 100 = scale (e.g. 1.2)
    """
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.sfreq = None
        self.actual_start = 0
        self.timer_count = 0
        self.timer_end = 0
        self.frame_number = 0
        self.timer_ID = None
        self.scale_time = None

    def execute(self, obj, event):
        # how long for emit of one full frame
        t2 = time.time()
        dur = t2 - self.scale_time
        # lag = dur - 0.016
        # print("frame dur: ", dur, "latency: ", lag)
        scale = int(self.sfreq * dur)
        self.scale_time = t2
        self.timer_count += scale
        iren = obj

        if self.timer_count < self.timer_end:
            self.mainwindow.ui.vtkScrollSlider.setValue(self.timer_count)
        else:
            self.timer_count = self.actual_start
            self.mainwindow.ui.vtkScrollSlider.setValue(self.timer_count)
            iren.ResetTimer(self.timer_ID)


class Player:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.playing = False
        self.mainwindow.pycgm_data = None
        self.call_back = None
        self.timer_ID = None

    def update_callback(self):
        self.call_back.sfreq = self.mainwindow.pycgm_data.Gen['Vid_SampRate']
        self.call_back.actual_start = self.mainwindow.pycgm_data.Gen['Vid_FirstFrame']
        self.call_back.timer_end = self.mainwindow.pycgm_data.Gen['Vid_LastFrame']

    def play(self):
        if self.mainwindow.pycgm_data:
            if self.call_back:
                self.update_callback()
            else:
                self.call_back = VtkTimerCallback(self.mainwindow)
                self.update_callback()
                self.call_back.PlayStateChanged = self.play_state_changed
                self.mainwindow.vtk3d_widget.iren.AddObserver('TimerEvent', self.call_back.execute, 1000)
                self.timer_ID = self.mainwindow.vtk3d_widget.iren.CreateRepeatingTimer(10)
                self.call_back.timer_ID = self.timer_ID

            if not self.playing:
                self.mainwindow.vtk3d_widget.iren.ResetTimer(self.timer_ID)
                self.call_back.scale_time = time.time()
                self.call_back.timer_count = self.mainwindow.ui.vtkScrollSlider.value()
                self.play_state_changed(state='playing')

            elif self.playing:
                self.play_state_changed(state='paused')

    def play_state_changed(self, state):
        if state == 'playing':
            self.playing = True
            self.mainwindow.ui.playButton.setIcon(self.mainwindow.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        else:
            self.mainwindow.vtk3d_widget.iren.DestroyTimer('evt', self.timer_ID)
            self.playing = False
            self.mainwindow.ui.playButton.setIcon(self.mainwindow.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

    def isplaying(self):
        return self.playing
