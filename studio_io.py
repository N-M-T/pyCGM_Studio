from PyQt5 import QtWidgets, QtCore, QtGui
from pyCGM_Single.pycgmIO import loadVSK
from pyCGM_Single.c3dez import C3DData
from setup_helper import setup_data_source
from threads import Worker
import numpy as np


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

    # add dict for model outputs calculated by PyCGM
    data.Data['PyCGM Model Outputs'] = dict()
    return data


class StudioIo:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.current_filepath = None

    def set_current_filepath(self, path):
        self.current_filepath = path

    def studio_exporter(self, kind, result):
        if kind == 'Export spreadsheet (.csv)':
            return self.csv_exporter(result)

    def csv_exporter(self, result):
        try:
            filename, data, delimiter, header, fmt = writeResult(result,
                                                                 self.current_filepath[:-4])
        except Exception as err:
            print('Could not save file :', err)
            return 0

        else:
            return self.gen_worker(filename, data, delimiter, header, fmt)  # we will start thread

    def gen_worker(self, filename, data, delimiter, header, fmt):
        worker = Worker(savetxt,
                              filename,
                              data,
                              delimiter=delimiter,
                              header=header,
                              fmt=fmt)

        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.mainwindow.pipelines.update_progress_bar)
        worker.signals.error.connect(self.thread_failed)
        worker.start()
        return 1

    def thread_complete(self):
        self.mainwindow.pipelines.update_status('Export spreadsheet (.csv)', status='success')
        self.mainwindow.pipelines.remove_operation('Export spreadsheet (.csv)')
        self.mainwindow.pipelines.run_pipelines(from_operation=True)

    def thread_failed(self, intuple):
        print(intuple[0], err=intuple[1])
        self.mainwindow.pipelines.update_status('Export spreadsheet (.csv)', status='failed')

    def studio_loader(self, path):
        self.set_current_filepath(path)
        ext = self.current_filepath[-3:]
        if ext == 'c3d':
            self.c3d_loader()
        elif ext == 'vsk':
            self.vsk_loader()

    def c3d_loader(self):
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
        try:
            if self.mainwindow.playing:
                self.mainwindow.play_state_changed(state='Paused')
            self.mainwindow.set_data(load_c3d(self.current_filepath))
            setup_data_source(self.mainwindow, self.current_filepath)
            QtWidgets.QApplication.restoreOverrideCursor()

        except Exception as err:
            print('Problem loading: ', err)
            QtWidgets.QApplication.restoreOverrideCursor()

    def vsk_loader(self):
        try:
            vsk = loadVSK(self.current_filepath, dict=False)  # this needs changing as dict false returns a dict
            self.mainwindow.explorer_widget.populate_vsk_form(self.current_filepath, vsk)
            self.mainwindow.set_vsk(vsk)

        except Exception as err:
            print('Problem loading vsk: ', err)


def writeResult(data, filename, **kargs):
    """
    Writes the result of the calculation into a csv file
    @param data Motion Data as a matrix of frames as rows
    @param filename Name to save the csv
    @param kargs
            delimiter Delimiter for the csv. By default it's using ','
            angles True or false to save angles. Or a list of angles to save
            axis True of false to save axis. Or a list of axis to save
    Examples
    #save angles and axis
    writeResultNumPy(result,"outputfile0.csv")
    #save 'R Hip' angles 'L Foot' and all the axis
    writeResultNumPy(result,"outputfile1.csv",angles=['R Hip','L Foot'])
    #save only axis "R ANKZ","L ANKO","L ANKX"
    writeResultNumPy(result,"outputfile4.csv",angles=False,axis=["R ANKZ","L ANKO","L ANKX"])
    #save only angles
    writeResultNumPy(result,"outputfile6.csv",axis=False)
    """
    # Used to split the arrays with angles and axis
    # Start Joint Angles
    SJA = 0
    # End Joint Angles
    EJA = SJA + 19 * 3
    # Start Axis
    SA = EJA
    # End Axis
    EA = SA + 72 * 3

    pyver = 3

    labelsAngs = ['Pelvis', 'R Hip', 'L Hip', 'R Knee', 'L Knee', 'R Ankle',
                  'L Ankle', 'R Foot', 'L Foot',
                  'Head', 'Thorax', 'Neck', 'Spine', 'R Shoulder', 'L Shoulder',
                  'R Elbow', 'L Elbow', 'R Wrist', 'L Wrist']

    labelsAxis = ["PELO", "PELX", "PELY", "PELZ", "HIPO", "HIPX", "HIPY", "HIPZ", "R KNEO", "R KNEX", "R KNEY",
                  "R KNEZ", "L KNEO", "L KNEX", "L KNEY", "L KNEZ", "R ANKO", "R ANKX", "R ANKY", "R ANKZ",
                  "L ANKO", "L ANKX", "L ANKY", "L ANKZ", "R FOOO", "R FOOX", "R FOOY", "R FOOZ", "L FOOO",
                  "L FOOX", "L FOOY", "L FOOZ", "HEAO", "HEAX", "HEAY", "HEAZ", "THOO", "THOX", "THOY", "THOZ",
                  "R CLAO", "R CLAX", "R CLAY", "R CLAZ", "L CLAO", "L CLAX", "L CLAY", "L CLAZ", "R HUMO",
                  "R HUMX", "R HUMY", "R HUMZ", "L HUMO", "L HUMX", "L HUMY", "L HUMZ", "R RADO", "R RADX",
                  "R RADY", "R RADZ", "L RADO", "L RADX", "L RADY", "L RADZ", "R HANO", "R HANX", "R HANY",
                  "R HANZ", "L HANO", "L HANX", "L HANY", "L HANZ"]

    outputAngs = True
    outputAxis = True
    dataFilter = None
    delimiter = ","
    filterData = []
    if 'delimiter' in kargs:
        delimiter = kargs['delimiter']
    if 'angles' in kargs:
        if kargs['angles'] == True:
            outputAngs = True
        elif kargs['angles'] == False:
            outputAngs = False
            labelsAngs = []
        elif isinstance(kargs['angles'], (list, tuple)):
            filterData = [i * 3 for i in range(len(labelsAngs)) if labelsAngs[i] not in kargs['angles']]
            if len(filterData) == 0:
                outputAngs = False
            labelsAngs = [i for i in labelsAngs if i in kargs['angles']]

    if 'axis' in kargs:
        if kargs['axis'] == True:
            outputAxis = True
        elif kargs['axis'] == False:
            outputAxis = False
            labelsAxis = []
        elif isinstance(kargs['axis'], (list, tuple)):
            filteraxis = [i * 3 + SA for i in range(len(labelsAxis)) if labelsAxis[i] not in kargs['axis']]
            filterData = filterData + filteraxis
            if len(filteraxis) == 0:
                outputAxis = False
            labelsAxis = [i for i in labelsAxis if i in kargs['axis']]

    if len(filterData) > 0:
        filterData = np.repeat(filterData, 3)
        filterData[1::3] = filterData[1::3] + 1
        filterData[2::3] = filterData[2::3] + 2

    if outputAngs == outputAxis == False:
        return
    elif outputAngs == False:
        print(np.shape(data))
        dataFilter = np.transpose(data)
        dataFilter = dataFilter[SA:EA]
        dataFilter = np.transpose(dataFilter)
        print(np.shape(dataFilter))
        print(filterData)
        filterData = [i - SA for i in filterData]
        print(filterData)
    elif outputAxis == False:
        dataFilter = np.transpose(data)
        dataFilter = dataFilter[SJA:EJA]
        dataFilter = np.transpose(dataFilter)

    if len(filterData) > 0:
        if type(dataFilter) == type(None):
            dataFilter = np.delete(data, filterData, 1)
        else:
            dataFilter = np.delete(dataFilter, filterData, 1)
    if type(dataFilter) == type(None):
        dataFilter = data
    header = ","
    headerAngs = ["Joint Angle,,,", ",,,x = flexion/extension angle", ",,,y= abudction/adduction angle",
                  ",,,z = external/internal rotation angle", ",,,"]
    headerAxis = ["Joint Coordinate", ",,,###O = Origin", ",,,###X = X axis orientation",
                  ",,,###Y = Y axis orientation", ",,,###Z = Z axis orientation"]
    for angs, axis in zip(headerAngs, headerAxis):
        if outputAngs == True:
            header = header + angs + ",,," * (len(labelsAngs) - 1)
        if outputAxis == True:
            header = header + axis + ",,," * (len(labelsAxis) - 1)
        header = header + "\n"
    labels = ","
    if len(labelsAngs) > 0:
        labels = labels + ",,,".join(labelsAngs) + ",,,"
    if len(labelsAxis) > 0:
        labels = labels + ",,,".join(labelsAxis)
    labels = labels + "\n"
    if pyver == 2:
        xyz = "frame num," + "X,Y,Z," * (len(dataFilter[0]) / 3)
    else:
        xyz = "frame num," + "X,Y,Z," * (len(dataFilter[0]) // 3)
    header = header + labels + xyz
    # Creates the frame numbers
    frames = np.arange(len(dataFilter), dtype=dataFilter[0].dtype)
    # Put the frame numbers in the first dimension of the data
    dataFilter = np.column_stack((frames, dataFilter))
    start = 1500
    end = 3600
    # dataFilter = dataFilter[start:]

    return filename + '.csv', dataFilter, delimiter, header, "%.15f"


from numpy.compat import (
    asstr, asunicode, bytes, os_fspath, os_PathLike
)


def savetxt(fname, X, fmt='%.18e', delimiter=' ', newline='\n', header='',
            footer='', comments='# ', encoding=None, progress_callback=None):

    """numpy.savetxt modified to output progress """

    # Py3 conversions first
    if isinstance(fmt, bytes):
        fmt = asstr(fmt)
    delimiter = asstr(delimiter)

    class WriteWrap:
        """Convert to bytes on bytestream inputs.
        """
        def __init__(self, fh, encoding):
            self.fh = fh
            self.encoding = encoding
            self.do_write = self.first_write

        def close(self):
            self.fh.close()

        def write(self, v):
            self.do_write(v)

        def write_bytes(self, v):
            if isinstance(v, bytes):
                self.fh.write(v)
            else:
                self.fh.write(v.encode(self.encoding))

        def write_normal(self, v):
            self.fh.write(asunicode(v))

        def first_write(self, v):
            try:
                self.write_normal(v)
                self.write = self.write_normal
            except TypeError:
                # input is probably a bytestream
                self.write_bytes(v)
                self.write = self.write_bytes

    own_fh = False
    if isinstance(fname, os_PathLike):
        fname = os_fspath(fname)
    if isinstance(fname, str):
        # datasource doesn't support creating a new file ...
        open(fname, 'wt').close()
        fh = np.lib._datasource.open(fname, 'wt', encoding=encoding)
        own_fh = True
    elif hasattr(fname, 'write'):
        # wrap to handle byte output streams
        fh = WriteWrap(fname, encoding or 'latin1')
    else:
        raise ValueError('fname must be a string or file handle')

    try:
        X = np.asarray(X)

        # Handle 1-dimensional arrays
        if X.ndim == 0 or X.ndim > 2:
            raise ValueError(
                "Expected 1D or 2D array, got %dD array instead" % X.ndim)
        elif X.ndim == 1:
            # Common case -- 1d array of numbers
            if X.dtype.names is None:
                X = np.atleast_2d(X).T
                ncol = 1

            # Complex dtype -- each field indicates a separate column
            else:
                ncol = len(X.dtype.names)
        else:
            ncol = X.shape[1]

        iscomplex_X = np.iscomplexobj(X)
        # `fmt` can be a string with multiple insertion points or a
        # list of formats.  E.g. '%10.5f\t%10d' or ('%10.5f', '$10d')
        if type(fmt) in (list, tuple):
            if len(fmt) != ncol:
                raise AttributeError('fmt has wrong shape.  %s' % str(fmt))
            format = asstr(delimiter).join(map(asstr, fmt))
        elif isinstance(fmt, str):
            n_fmt_chars = fmt.count('%')
            error = ValueError('fmt has wrong number of %% formats:  %s' % fmt)
            if n_fmt_chars == 1:
                if iscomplex_X:
                    fmt = [' (%s+%sj)' % (fmt, fmt), ] * ncol
                else:
                    fmt = [fmt, ] * ncol
                format = delimiter.join(fmt)
            elif iscomplex_X and n_fmt_chars != (2 * ncol):
                raise error
            elif ((not iscomplex_X) and n_fmt_chars != ncol):
                raise error
            else:
                format = fmt
        else:
            raise ValueError('invalid fmt: %r' % (fmt,))

        if len(header) > 0:
            header = header.replace('\n', '\n' + comments)
            fh.write(comments + header + newline)
        if iscomplex_X:
            for row in X:
                row2 = []
                for number in row:
                    row2.append(number.real)
                    row2.append(number.imag)
                s = format % tuple(row2) + newline
                fh.write(s.replace('+-', '-'))
        else:
            length = len(X)
            for ind, row in enumerate(X):
                try:
                    v = format % tuple(row) + newline
                except TypeError:
                    raise TypeError("Mismatch between array dtype ('%s') and "
                                    "format specifier ('%s')"
                                    % (str(X.dtype), format))
                fh.write(v)

                progress_callback.emit((ind + 1) * 100 / length)

        if len(footer) > 0:
            footer = footer.replace('\n', '\n' + comments)
            fh.write(comments + footer + newline)
    finally:
        if own_fh:
            fh.close()
