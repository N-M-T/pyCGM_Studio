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


'''def main():
    #  Decide what approach to use.
    use_function_callback = True

    colors = vtk.vtkNamedColors()

    # Create the Renderer, RenderWindow and RenderWindowInteractor.
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Use a cone as a source.
    source = vtk.vtkConeSource()
    source.SetCenter(0, 0, 0)
    source.SetRadius(1)
    # Use the golden ratio for the height. Because we can!
    source.SetHeight(1.6180339887498948482)
    source.SetResolution(128)
    source.Update()

    # Pipeline
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d("peacock"))
    # Lighting
    actor.GetProperty().SetAmbient(0.3)
    actor.GetProperty().SetDiffuse(0.0)
    actor.GetProperty().SetSpecular(1.0)
    actor.GetProperty().SetSpecularPower(20.0)

    # Get an outline of the data set for context.
    outline = vtk.vtkOutlineFilter()
    outline.SetInputData(source.GetOutput())
    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(outline.GetOutputPort())
    outlineActor = vtk.vtkActor()
    outlineActor.GetProperty().SetColor(colors.GetColor3d("Black"))
    outlineActor.SetMapper(outlineMapper)

    # Add the actors to the renderer, set the background and size.
    ren.AddActor(actor)
    ren.AddActor(outlineActor)
    ren.SetBackground(colors.GetColor3d("AliceBlue"))
    renWin.SetSize(512, 512)

    # Set up a nice camera position.
    camera = vtk.vtkCamera()
    camera.SetPosition(4.6, -2.0, 3.8)
    camera.SetFocalPoint(0.0, 0.0, 0.0)
    camera.SetClippingRange(3.2, 10.2)
    camera.SetViewUp(0.3, 1.0, 0.13)
    ren.SetActiveCamera(camera)

    renWin.Render()
    renWin.SetWindowName("CallBack")

    axes1 = MakeAxesActor()
    om1 = vtk.vtkOrientationMarkerWidget()
    om1.SetOrientationMarker(axes1)
    # Position lower left in the viewport.
    om1.SetViewport(0, 0, 0.2, 0.2)
    om1.SetInteractor(iren)
    om1.EnabledOn()
    om1.InteractiveOn()

    # Set up the callback.
    if use_function_callback:
        # We are going to output the camera position when the event is triggered
        #  so we add the active camera as an attribute.
        GetOrientation.cam = ren.GetActiveCamera()
        # Register the callback with the object that is observing.
        iren.AddObserver('EndInteractionEvent', GetOrientation)
        iren.AddObserver('TimerEvent', GetOrientation)
    else:
        iren.AddObserver('EndInteractionEvent', OrientationObserver(ren.GetActiveCamera()))
        # Or:
        # observer = OrientationObserver(ren.GetActiveCamera())
        # iren.AddObserver('EndInteractionEvent', observer)

    iren.Initialize()
    iren.Start()


def GetOrientation(caller, ev):
    """
    Print out the orientation.

    We must do this before we register the callback in the calling function.
        GetOrientation.cam = ren.GetActiveCamera()

    :param caller:
    :param ev: The event.
    :return:
    """
    # Just do this to demonstrate who called callback and the event that triggered it.
    print(caller.GetClassName(), "Event Id:", ev)
    # Now print the camera orientation.
    CameraOrientation(GetOrientation.cam)


class OrientationObserver(object):
    def __init__(self, cam):
        self.cam = cam

    def __call__(self, caller, ev):
        # Just do this to demonstrate who called callback and the event that triggered it.
        print(caller.GetClassName(), "Event Id:", ev)
        # Now print the camera orientation.
        CameraOrientation(self.cam)


def CameraOrientation(cam):
    fmt1 = "{:>15s}"
    fmt2 = "{:9.6g}"
    print(fmt1.format("Position:"), ', '.join(map(fmt2.format, cam.GetPosition())))
    print(fmt1.format("Focal point:"), ', '.join(map(fmt2.format, cam.GetFocalPoint())))
    print(fmt1.format("Clipping range:"), ', '.join(map(fmt2.format, cam.GetClippingRange())))
    print(fmt1.format("View up:"), ', '.join(map(fmt2.format, cam.GetViewUp())))
    print(fmt1.format("Distance:"), fmt2.format(cam.GetDistance()))


def MakeAxesActor():
    axes = vtk.vtkAxesActor()
    axes.SetShaftTypeToCylinder()
    axes.SetXAxisLabelText('X')
    axes.SetYAxisLabelText('Y')
    axes.SetZAxisLabelText('Z')
    axes.SetTotalLength(1.0, 1.0, 1.0)
    axes.SetCylinderRadius(0.5 * axes.GetCylinderRadius())
    axes.SetConeRadius(1.025 * axes.GetConeRadius())
    axes.SetSphereRadius(1.5 * axes.GetSphereRadius())
    return axes


if __name__ == '__main__':
    main()'''


class vtkHoverCallback:
    def __init__(self):
        """callback"""

    def execute(self, event, calldata):
        print(event, calldata)
        '''if event:
            if event == 'TimerEvent':
                print('hovering')
            if event == 'EndInteractionEvent':
                print('moving')'''


def main():
    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(640, 480)
    renderWindow.AddRenderer(renderer)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renderWindow)

    source = vtk.vtkSphereSource()
    source.SetRadius(5)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    renderer.AddActor(actor)
    
    hover_widget = vtk.vtkHoverWidget()
    hover_widget.SetInteractor(iren)
    hover_widget.SetTimerDuration(1000)

    hover_callback = vtkHoverCallback()
    hover_widget.AddObserver('TimerEvent', hover_callback.execute)
    # hover_callback.AddObserver('MouseMoveEvent', hover_callback.execute)

    # Render and interact
    renderWindow.Render()

    hover_widget.On()

    # Start
    iren.Initialize()
    iren.Start()


if __name__ == "__main__":
    main()