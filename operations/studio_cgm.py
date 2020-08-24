from pyCGM_Single import pycgmStatic, pycgmIO, pycgmCalc, pyCGM
import numpy as np
import copy
from core.threads import Worker
from pyCGM_Single.pycgmIO import markerKeys
from files.studio_io import model_bones_gen_pycgm


class CgmModel:
    def __init__(self, mainwindow):
        # todo: implement way to deal with gaps in data during modelling
        self.mainwindow = mainwindow
        self.calibrated_measurements = None
        self.current_array = None  # array (static or dynamic) to process
        self.current_model_kind = None
        self.target_markers = markerKeys()
        self.current_angles = None
        self.current_axes = None
        # gets garbage collected with PyInstaller but not when run with standard python
        # interpreter, so keep a reference here
        self.model_worker = None

    def set_current_array(self):
        marker_keys = self.mainwindow.pycgm_data.Data['Markers']

        # ensure all necessary markers are present and labelled correctly
        if not all(item in marker_keys for item in self.target_markers):
            if self.current_array:
                # ensure we remove old array so non associated vis_support cannot be performed
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

        # Overridden in pycgm module
        def calc(a, b, c, d):
            return angles, joints

        pycgmCalc.Calc = calc

        angles, axes = pycgmCalc.calcAngles(inarray,
                                            vsk=calibrated_measurements,
                                            splitAnglesAxis=True,
                                            formatData=True,
                                            axis=True)

        self.set_current_angles(angles)
        self.set_current_axes(axes)

    def run_static(self):
        self.current_model_kind = 'Static cgm pipeline'  # used to update status of run
        if not self.mainwindow.vsk:
            self.mainwindow.ui.messageBrowser.setText('Load VSK in files')
            return 0

        if not self.set_current_array():
            self.mainwindow.ui.messageBrowser.setText('Ensure PiG marker setup is used and all markers are labelled '
                                                      'correctly')
            return 0

        try:
            # get static offsets to be used for calculating angles in static and dynamic trials
            self.calibrated_measurements = pycgmStatic.getStatic(self.current_array,
                                                                 self.mainwindow.vsk,
                                                                 flat_foot=False)
        except Exception as err:
            self.mainwindow.ui.messageBrowser.setText('Could not calculate static offsets. Error : ' + str(err))
            return 0

        else:
            return self.gen_model_worker()  # we will start thread

    def run_dynamic(self):
        self.current_model_kind = 'Dynamic cgm pipeline'
        if not self.calibrated_measurements:
            self.mainwindow.ui.messageBrowser.setText("Run static pipeline first")
            return 0

        if not self.set_current_array():
            self.mainwindow.ui.messageBrowser.setText('Ensure PiG marker setup is used and all markers are labelled '
                                                      'correctly')
            return 0

        return self.gen_model_worker()  # we will start thread

    def gen_model_worker(self):
        # calcFrames() is time consuming so run in separate thread and update progress bar
        try:
            self.model_worker = Worker(self.calc_frames,
                                       inarray=self.current_array,
                                       calibrated_measurements=self.calibrated_measurements)
            self.model_worker.signals.finished.connect(self.thread_complete)
            self.model_worker.signals.progress.connect(self.mainwindow.pipelines.update_progress_bar)
            self.model_worker.signals.error.connect(self.thread_failed)
            self.model_worker.start()
        except Exception as err:
            print('threading: ', err)
            print('enter to exit')
            input()
        return 1  # thread is running

    def thread_complete(self):
        self.mainwindow.studio_io_ops.saved = False  # keep track of whether save is needed on exit
        self.mainwindow.pipelines.update_status(self.current_model_kind, status='success')
        self.mainwindow.pipelines.remove_operation(self.current_model_kind)
        # clear old segments and plots
        self.mainwindow.segments.clear()
        self.mainwindow.plotter.remove_plots()
        self.update_pycgm_angles(self.current_angles)
        self.update_pycgm_bones(self.current_axes)
        # run next operation
        self.mainwindow.pipelines.run_pipelines(from_operation=True)

    def thread_failed(self, intuple):
        # called by worker thread if something goes wrong
        self.mainwindow.pipelines.update_status(self.current_model_kind, status='failed')
        self.set_current_angles(None)
        self.set_current_axes(None)
        self.model_worker = None

    def update_pycgm_bones(self, axes):
        axes_list = model_bones_gen_pycgm()
        try:
            shape = np.shape(axes)
            count = 0
            for i in range(shape[1]):
                for j in range(shape[2]):
                    self.mainwindow.pycgm_data.Data['pyCGM Bones'][axes_list[count]] = axes[:, i, j].T
                    count += 1
            self.mainwindow.segments.set_segment_data(pycgm=True)
            self.mainwindow.segments.update_segments()
            self.mainwindow.emitter.emit('current')  # will need to render to show segments
        except Exception as err:
            print(err)

    def update_pycgm_angles(self, angles):
        angles_tup = ('PelvisAngles,RHipAngles,LHipAngles,RKneeAngles,LKneeAngles,RAnkleAngles,LAnkleAngles,'
                      'RFootProgressAngles,LFootProgressAngles,HeadAngles,ThoraxAngles,NeckAngles,SpineAngles,'
                      'RShoulderAngles,LShoulderAngles,RElbowAngles,LElbowAngles,RWristAngles,LWristAngles')
        angles_list = angles_tup.split(',')
        try:
            for i in range(np.shape(angles)[1]):
                self.mainwindow.pycgm_data.Data['PyCGM Model Outputs'][angles_list[i]] = angles[:, i].T
        except Exception as err:
            print(err)

        self.mainwindow.plotter.update_channels()
        self.mainwindow.explorer_widget.update_cgm_model_outputs()

    def set_current_angles(self, angles):
        self.current_angles = angles

    def set_current_axes(self, axes):
        self.current_axes = axes
