from markers import Markers
from trajectories import Trajectories
from truncated import is_truncated


def setup_data_source(mainwindow, filename):
    # get length of data and whether it has previously been truncated
    num_points, offset = is_truncated(mainwindow.pycgm_data)

    # marker source
    # ensure we have useable point data
    if len([*mainwindow.pycgm_data.Data['Markers']]) > 0:
        markers = Markers(mainwindow, num_points)
        markers.update_data(complete=True)
        mainwindow.vtk3d_widget.ren.AddActor(markers.actor)
        mainwindow.set_markers(markers)

        # trajectory source
        trajectories = Trajectories(mainwindow)
        mainwindow.set_trajectories(trajectories)

        # emitter source
        mainwindow.emitter.set_offset(offset)

        # highlighting selected markers and trajectories
        mainwindow.highlighter.update_marker_names()

        # gap filling source
        mainwindow.gaps.init()
        mainwindow.gaps.find_gaps()
        mainwindow.gaps.populate_gap_table()

        # pass pycgm and gap dict to Receiver for undo/redo operations
        mainwindow.gap_receiver.update_marker_data_source = markers.update_data

    # plotter
    mainwindow.plotter.update_channels()

    # explorer widget
    mainwindow.explorer_widget.populate_tree()

    # pipelines source
    mainwindow.pipelines.set_loaded_filepath(filename)

    # set slider values
    mainwindow.ui.vtkScrollSlider.setMinimum(mainwindow.pycgm_data.Gen['Vid_FirstFrame'])
    mainwindow.ui.vtkScrollSlider.setMaximum(mainwindow.pycgm_data.Gen['Vid_LastFrame'])
    mainwindow.ui.vtkScrollSlider.setSingleStep(1)
    mainwindow.ui.vtkScrollSlider.setTickInterval((num_points - mainwindow.pycgm_data.Gen['Vid_FirstFrame']) / 120)
    mainwindow.ui.vtkScrollSlider.setValue(mainwindow.pycgm_data.Gen['Vid_FirstFrame'])

    # make stuff visible
    mainwindow.ui.playButton.setEnabled(True)
    mainwindow.ui.vtkScrollSlider.setEnabled(True)
    mainwindow.ui.currentFrame.setVisible(True)
    mainwindow.ui.toolDock.setVisible(True)
    mainwindow.ui.cgmPipelinesDock.setVisible(True)

    # emit a frame of mocap
    mainwindow.emitter.emit(mainwindow.pycgm_data.Gen['Vid_FirstFrame'])

    # change window title
    mainwindow.setWindowTitle('PyCGM_Studio v1.0 - ' + mainwindow.pycgm_data.Gen['FileName'][:-4])
