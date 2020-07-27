'''from PyQt5 import QtCore, QtWidgets

from pyCGM_Single import pycgmStatic, pycgmIO, pycgmCalc, pyCGM


def getfilenames():
    directory = 'C:/Users/M.Hollands/PycharmProjects/pyCGM_Studio/pyCGM-master/SampleData/ROM/'
    dynamic_trial = directory + 'Sample_Dynamic.c3d'
    static_trial = directory + 'Sample_Static.c3d'
    vsk_file = directory + 'Sample_SM.vsk'
    outputfile = directory + 'pycgm_results'

    return dynamic_trial, static_trial, vsk_file, outputfile


def loadData(dynamic_trial, static_trial, vsk_file):
    # load the data, usually there is some checks in here to make sure we loaded
    # correctly, but for now we assume its loaded
    motion_data = pycgmIO.loadData(dynamic_trial)
    vskdata = pycgmIO.loadVSK(vsk_file)
    static_data = pycgmIO.loadData(static_trial)
    # The vsk is loaded, but for some reasons the return is split, so we combine
    vsk = pycgmIO.createVskDataDict(vskdata[0], vskdata[1])
    # print("Motion Data Length:", len(motion_data))

    return motion_data, vsk, static_data


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(float)


class ModelWorker(QtCore.QThread):  # QtCore.QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(ModelWorker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    def run(self):
        result = self.function(*self.args, **self.kwargs)
        self.signals.result.emit(result)
        self.signals.finished.emit()


def update_progress_bar(percentage):
    print(percentage)


class Main(QtWidgets.QWidget):
    def __init__(self):
        super(Main, self).__init__()

        self.current_angles = None
        self.saved = False

        # Load the filenames
        dynamic_trial, self.static_trial, vsk_file, outputfile = getfilenames()

        # Load a dynamic trial, static trial, and vsk (subject measurements)
        motion_data, vsk_data, static_data = loadData(dynamic_trial, self.static_trial, vsk_file)

        # Calculate the static offsets
        flat_foot = False
        calibrated_measurements = pycgmStatic.getStatic(static_data, vsk_data, flat_foot)

        # Run calcFrames() in separate thread and update progress bar
        # passing the calibrated subject measurements
        model_worker = ModelWorker(self.calc_frames,
                                   inarray=static_data,
                                   calibrated_measurements=calibrated_measurements)

        model_worker.signals.finished.connect(self.thread_complete)
        model_worker.signals.progress.connect(update_progress_bar)
        model_worker.start()

    def thread_complete(self):
        if not self.saved:
            self.saved = True

            filename, data, delimiter, header, fmt = pycgmIO.writeResult(self.current_angles,
                                                                         self.static_trial[:-4])

            print(filename, data, delimiter, header, fmt)
            # start new thread (this will be in stack for main project)
            model_worker = ModelWorker(savetxt,
                                       filename,
                                       data,
                                       delimiter=delimiter,
                                       header=header,
                                       fmt=fmt)

            model_worker.signals.finished.connect(self.thread_complete)
            model_worker.signals.progress.connect(update_progress_bar)
            model_worker.start()
        else:
            print('file saved')

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

        self.current_angles = angles


def create_dict(angles):
    angles_tup = ('PelvisAngles,RHipAngles,LHipAngles,RKneeAngles,LKneeAngles,RAnkleAngles,LAnkleAngles,'
                  'RFootProgressAngles,LFootProgressAngles,HeadAngles,ThoraxAngles,NeckAngles,SpineAngles,'
                  'RShoulderAngles,LShoulderAngles,RElbowAngles,LElbowAngles,RWristAngles,LWristAngles')
    angles_list = angles_tup.split(',')
    angles = np.transpose(angles)
    angles_dict = dict()

    # 19 angles, 57 columns (x, y, z)
    for i in range(1, 20):
        threes = i * 3
        z = threes - 1
        x = z - 2
        y = z - 1
        angles_dict[angles_list[i - 1]] = np.asarray([angles[x],
                                                      angles[y],
                                                      angles[z]])

    return angles_dict'''


from numpy.compat import (
    asstr, asunicode, bytes, os_fspath, os_PathLike
)


def savetxt(fname, X, fmt='%.18e', delimiter=' ', newline='\n', header='',
            footer='', comments='# ', encoding=None, progress_callback=None):

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
    # if _is_string_like(fname):
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



import vtk


def main():
    # Create the polydata where we will store all the geometric data
    linesPolyData = vtk.vtkPolyData()

    # Create three points
    origin = [0.0, 0.0, 0.0]
    p0 = [1.0, 0.0, 0.0]
    p1 = [0.0, 1.0, 0.0]

    # Create a vtkPoints container and store the points in it
    pts = vtk.vtkPoints()
    pts.InsertNextPoint(origin)
    pts.InsertNextPoint(p0)
    pts.InsertNextPoint(p1)

    # Add the points to the polydata container
    linesPolyData.SetPoints(pts)

    # Create the first line (between Origin and P0)
    line0 = vtk.vtkLine()
    line0.GetPointIds().SetId(0, 0)  # the second 0 is the index of the Origin in linesPolyData's points
    line0.GetPointIds().SetId(1, 1)  # the second 1 is the index of P0 in linesPolyData's points

    # Create the second line (between Origin and P1)
    line1 = vtk.vtkLine()
    line1.GetPointIds().SetId(0, 0)  # the second 0 is the index of the Origin in linesPolyData's points
    line1.GetPointIds().SetId(1, 2)  # 2 is the index of P1 in linesPolyData's points

    # Create a vtkCellArray container and store the lines in it
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(line0)
    lines.InsertNextCell(line1)

    # Add the lines to the polydata container
    linesPolyData.SetLines(lines)

    namedColors = vtk.vtkNamedColors()

    # Create a vtkUnsignedCharArray container and store the colors in it
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    try:
        colors.InsertNextTupleValue(namedColors.GetColor3ub("Tomato"))
        colors.InsertNextTupleValue(namedColors.GetColor3ub("Mint"))
    except AttributeError:
        # For compatibility with new VTK generic data arrays.
        colors.InsertNextTypedTuple(namedColors.GetColor3ub("Tomato"))
        colors.InsertNextTypedTuple(namedColors.GetColor3ub("Mint"))

    # Color the lines.
    # SetScalars() automatically associates the values in the data array passed as parameter
    # to the elements in the same indices of the cell data array on which it is called.
    # This means the first component (red) of the colors array
    # is matched with the first component of the cell array (line 0)
    # and the second component (green) of the colors array
    # is matched with the second component of the cell array (line 1)
    linesPolyData.GetCellData().SetScalars(colors)

    # Setup the visualization pipeline
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(linesPolyData)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetLineWidth(4)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(namedColors.GetColor3d("SlateGray"))

    window = vtk.vtkRenderWindow()
    window.SetWindowName("Colored Lines")
    window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    # Visualize
    window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()
