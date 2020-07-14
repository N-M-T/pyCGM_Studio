from PyQt5 import QtWidgets, QtCore, QtGui
from spinner import Spinner
from pyCGM_Single.pycgmIO import loadVSK
from pyCGM_Single.c3dez import C3DData
from setup_helpers import setup_data_source


def model_bones_gen():
    return ['HEDO', 'HEDA', 'HEDL', 'HEDP', 'LCLO', 'LCLA', 'LCLL', 'LCLP', 'LFEO', 'LFEA', 'LFEL', 'LFEP',
            'LFOO', 'LFOA', 'LFOL', 'LFOP', 'LHNO', 'LHNA', 'LHNL', 'LHNP', 'LHUO', 'LHUA', 'LHUL', 'LHUP',
            'LRAO', 'LRAA', 'LRAL', 'LRAP', 'LTIO', 'LTIA', 'LTIL', 'LTIP', 'LTOO', 'LTOA', 'LTOL', 'LTOP',
            'PELO', 'PELA', 'PELL', 'PELP', 'RCLO', 'RCLA', 'RCLL', 'RCLP', 'RFEO', 'RFEA', 'RFEL', 'RFEP',
            'RFOO', 'RFOA', 'RFOL', 'RFOP', 'RHNO', 'RHNA', 'RHNL', 'RHNP', 'RHUO', 'RHUA', 'RHUL', 'RHUP',
            'RRAO', 'RRAA', 'RRAL', 'RRAP', 'RTIO', 'RTIA', 'RTIL', 'RTIP', 'RTOO', 'RTOA', 'RTOL', 'RTOP',
            'TRXO', 'TRXA', 'TRXL', 'TRXP']


def load_c3d(filepath):
    """
    data.Data['Angles'] : joint angle model outputs
    data.Data['Powers'] : joint power model outputs
    data.Data['Forces'] : joint forces model outputs
    data.Data['Moments'] : joint moments model outputs
    data.Data['Analogs'] : analog channels
    data.Data['AllPoints'] : all point data (markers, bones, centreofmass etc.)
    data.Data['Markers'] : this contains markers as well as bones
    """

    data = C3DData(None, filepath)
    bone_keys = model_bones_gen()
    data.Data['Bones'] = dict()
    if 'LLCAL' not in [*data.Data['Markers']]:
        # quick fix for plugingait bones data
        for key in [*data.Data['Markers']]:
            if key in bone_keys:
                data.Data['Bones'][key] = data.Data['Markers'][key]
                del data.Data['Markers'][key]
    return data


class StudioLoader:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow

    def c3d_loader(self, filepath):
        # clear any previous loads
        if self.mainwindow.pycgm_data:
            self.mainwindow.pycgm_data = None
            self.mainwindow.ui.explorerTree.clear()
            self.mainwindow.ui.gapTable.clearContents()

            # if opening file with analog data but no markers, we need to clear
            # old marker data as new will not be instantiated
            if self.mainwindow.markers:
                self.mainwindow.markers.reset_helper()
                self.mainwindow.markers.remove_actors()
                self.mainwindow.handler.clear_history()
                self.mainwindow.plotter.remove_plots()
                self.mainwindow.emitter.markers = None
                self.mainwindow.picker.markers = None
                self.mainwindow.highlighter.markers = None

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        #try:
        with Spinner(string='Loading', ui=self.mainwindow.ui):
            if self.mainwindow.playing:
                self.mainwindow.play_state_changed(state='Paused')
            self.mainwindow.set_data(load_c3d(filepath))
            setup_data_source(self.mainwindow, filepath)

        QtWidgets.QApplication.restoreOverrideCursor()

        #except Exception as err:
            #print('Problem loading: ', err)
            #QtWidgets.QApplication.restoreOverrideCursor()

    def vsk_loader(self, filepath):
        try:
            vsk = loadVSK(filepath, dict=False)  # this needs changing as dict false returns a dict
            self.mainwindow.explorer_widget.populate_vsk_form(filepath, vsk)
            self.mainwindow.set_vsk(vsk)

        except Exception as err:
            print('Problem loading vsk: ', err)



