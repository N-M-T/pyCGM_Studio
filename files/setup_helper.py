import numpy as np
from vis_support.markers import Markers
from core.truncated import is_truncated


def setup_data_source(mainwindow, filename):
    # get length of data and whether it has previously been truncated
    num_points, offset = is_truncated(mainwindow.pycgm_data)

    # marker source
    # ensure we have useable point data
    if len([*mainwindow.pycgm_data.Data['Markers']]) > 0:
        markers = Markers(mainwindow, num_points)
        markers.update_data(complete=True)
        markers.set_actor()
        mainwindow.set_markers(markers)

        # trajectory source
        mainwindow.trajectories.set_marker_keys()

        # emitter source
        mainwindow.emitter.set_offset(offset)

        # highlighting selected markers and trajectories
        mainwindow.highlighter.update_marker_names()

        # gap filling source
        mainwindow.gaps.init()
        mainwindow.gaps.find_gaps()
        mainwindow.gaps.populate_gap_table()

        # pass pycgm and gap dict to Receiver for undo/redo vis_support
        mainwindow.gap_receiver.update_marker_data_source = markers.update_data

    # check for bones
    mainwindow.segments.clear()
    if len([*mainwindow.pycgm_data.Data['Bones']]) > 0:  # manufacturer bones
        mainwindow.segments.set_segment_data()
    elif len([*mainwindow.pycgm_data.Data['pyCGM Bones']]) > 0:  # pycgm bones
        mainwindow.segments.set_segment_data(pycgm=True)
    mainwindow.segments.update_segments()

    # forceplatforms
    mainwindow.force_platforms.setup_fps()

    # plotter
    mainwindow.plotter.update_channels()

    # explorer widget
    mainwindow.explorer_widget.populate_tree()

    # operations source
    mainwindow.pipelines.clear_pipelines()
    mainwindow.pipelines.cgm_model.set_current_angles(None)

    # If we already have model outputs, set them
    arrs = []
    if len([*mainwindow.pycgm_data.Data['PyCGM Model Outputs']]) > 0:
        for key, arr in mainwindow.pycgm_data.Data['PyCGM Model Outputs'].items():
            arrs.append(arr.T)
        mainwindow.pipelines.cgm_model.set_current_angles(np.concatenate(arrs, axis=1))

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

    # change window titles
    mainwindow.setWindowTitle('PyCGM_Studio v1.0 - ' + mainwindow.pycgm_data.Gen['FileName'][:-4])
    mainwindow.vtk_title.set_text(mainwindow.pycgm_data.Gen['FileName'][:-4])
