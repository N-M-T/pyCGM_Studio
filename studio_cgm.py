from pyCGM_Single import pycgmStatic, pycgmIO, pycgmCalc, pyCGM
import numpy as np
import copy
from threads import Worker
from pyCGM_Single.pycgmIO import markerKeys


# todo: print error messages to textbrowser
def handle_error(message, err=None):
    print(message + ': ', err)


class CgmModel:
    def __init__(self, mainwindow):
        # todo: implement way to deal with gaps in data during modelling
        self.mainwindow = mainwindow
        self.calibrated_measurements = None
        self.current_array = None  # array (static or dynamic) to process
        self.current_model_kind = None
        self.target_markers = markerKeys()
        self.current_angles = None

    def set_current_array(self):
        marker_keys = self.mainwindow.pycgm_data.Data['Markers']

        # ensure all necessary markers are present and labelled correctly
        if not all(item in marker_keys for item in self.target_markers):
            if self.current_array:
                # ensure we remove old array so non associated operations cannot be performed
                self.current_array = None
            return 0

        array_copy = copy.deepcopy(self.mainwindow.pycgm_data.Data['Markers'])
        self.current_array = pycgmIO.dataAsArray(array_copy)
        return 1

    def scgm_run_model(self, model_kind):
        if model_kind == 'Static cgm pipeline':
            return self.run_static()

        elif model_kind == 'Dynamic cgm pipeline':
            return self.run_dynamic()

    def calc_frames(self, progress_callback, inarray=None, calibrated_measurements=None):
        length = len(inarray)
        angles = []
        joints = []
        for ind, frame in enumerate(inarray):
            angle, jcs = pyCGM.JointAngleCalc(frame, calibrated_measurements)
            angles.append(angle)
            joints.append(jcs)
            progress_callback.emit((ind + 1) * 100 / length)

        # in pycgm module
        def calc(a, b, c, d):
            return angles, joints

        pycgmCalc.Calc = calc

        angles = pycgmCalc.calcAngles(inarray,
                                      vsk=calibrated_measurements,
                                      splitAnglesAxis=False,
                                      formatData=False)

        self.update_pycgm_data(angles)
        self.set_current_angles(angles)

    def run_static(self):
        self.current_model_kind = 'Static cgm pipeline'  # used to update status of run
        if not self.mainwindow.vsk:
            handle_error(message="Please load vsk in Files")
            return 0

        if not self.set_current_array():
            handle_error(message='Please ensure PiG marker setup is used and all markers are labelled correctly')
            return 0

        try:
            # get static offsets to be used for calculating angles in static and dynamic trials
            self.calibrated_measurements = pycgmStatic.getStatic(self.current_array,
                                                                 self.mainwindow.vsk,
                                                                 flat_foot=False)
        except Exception as err:
            handle_error(message='Could not calculate static offsets: ', err=err)
            return 0

        else:
            return self.gen_model_worker()  # we will start thread

    def run_dynamic(self):
        self.current_model_kind = 'Dynamic cgm pipeline'
        if not self.calibrated_measurements:
            handle_error(message="Please run static pipeline first")
            return 0

        if not self.set_current_array():
            handle_error(message='Please ensure PiG marker setup is used and all markers are labelled correctly')
            return 0

        return self.gen_model_worker()  # we will start thread

    def gen_model_worker(self):
        # calcFrames() is time consuming so run in separate thread and update progress bar
        model_worker = Worker(self.calc_frames,
                              inarray=self.current_array,
                              calibrated_measurements=self.calibrated_measurements)
        model_worker.signals.finished.connect(self.thread_complete)
        model_worker.signals.progress.connect(self.mainwindow.pipelines.update_progress_bar)
        model_worker.signals.error.connect(self.thread_failed)
        model_worker.start()
        return 1  # thread is running

    def thread_complete(self):
        self.mainwindow.pipelines.update_status(self.current_model_kind, status='success')
        self.mainwindow.pipelines.remove_operation(self.current_model_kind)
        self.mainwindow.pipelines.run_pipelines(from_operation=True)

    def thread_failed(self, intuple):
        # called by worker thread if something goes wrong
        handle_error(message=intuple[0], err=intuple[1])
        self.mainwindow.pipelines.update_status(self.current_model_kind, status='failed')
        self.set_current_angles(None)

    def update_pycgm_data(self, angles):
        angles_tup = ('Pelvis,RHip,LHip,RKnee,LKnee,RAnkle,LAnkle,'
                      'RFootProgress,LFootProgress,Head,Thorax,Neck,Spine,'
                      'RShoulder,LShoulder,RElbow,LElbow,RWrist,LWrist')
        angles_list = angles_tup.split(',')
        angles = np.transpose(angles)

        # 19 angles, 57 columns (x, y, z)
        for i in range(0, 20):
            threes = i * 3
            z = threes - 1
            x = z - 2
            y = z - 1
            self.mainwindow.pycgm_data.Data['PyCGM Model Outputs'][angles_list[i - 1]] = \
                np.asarray([angles[x],
                            angles[y],
                            angles[z]])

        self.mainwindow.plotter.update_channels()
        self.mainwindow.explorer_widget.update_cgm_model_outputs()

    def set_current_angles(self, angles):
        self.current_angles = angles
