from pyCGM_Single import pycgmStatic, pycgmIO, pycgmCalc
from PyQt5 import QtWidgets, QtGui, QtCore


class CgmModel:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.calibrated_measurements = None
        self.static_angles = None
        self.dynamic_angles = None

    def scgm_run_model(self, model_kind):
        if model_kind == 'Static cgm pipeline':
            self.run_static()
        elif model_kind == 'Dynamic cgm pipeline':
            self.run_dynamic()

    def run_static(self):
        flat_foot = False
        static_array = pycgmIO.dataAsArray(self.mainwindow.pycgm_data.Data['Markers'])

        if not self.mainwindow.vsk:
            print("Please load vsk in Files")
            return

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            self.calibrated_measurements = pycgmStatic.getStatic(static_array,
                                                                 self.mainwindow.vsk,
                                                                 flat_foot)
            self.static_angles = pycgmCalc.calcAngles(static_array,
                                                      start=None,
                                                      end=None,
                                                      vsk=self.calibrated_measurements,
                                                      splitAnglesAxis=False,
                                                      formatData=False)
            print(self.static_angles)
            QtWidgets.QApplication.restoreOverrideCursor()
        except Exception as err:
            print("Could not run static pipeline: ", err)

    def run_dynamic(self):
        if not self.calibrated_measurements:
            print("Please run static pipeline first")
            return

        dynamic_array = pycgmIO.dataAsArray(self.mainwindow.pycgm_data.Data['Markers'])
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            self.dynamic_angles = pycgmCalc.calcAngles(dynamic_array,
                                                       start=None,
                                                       end=None,
                                                       vsk=self.calibrated_measurements,
                                                       splitAnglesAxis=False,
                                                       formatData=False)
            print(self.dynamic_angles)
            QtWidgets.QApplication.restoreOverrideCursor()

        except Exception as err:
            print("Could not run dynamic pipeline: ", err)
