import vtk
from core_operations import utilities as ut
import numpy as np
from vis_cgm.trajectories import traj_gen
from PyQt5 import QtWidgets, QtGui, QtCore
from core_operations.spline_updater import UpdateIndices
from functools import partial


def cone_gen():
    vtk_property = vtk.vtkProperty()
    vtk_property.SetColor(0.0, .3, 1.0)
    vtk_property.SetDiffuse(0.7)
    vtk_property.SetSpecular(0.4)
    vtk_property.SetSpecularPower(20)

    cone = vtk.vtkConeSource()
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()

    cone.SetResolution(60)
    cone.SetRadius(12.0)
    cone.SetHeight(36.0)

    mapper.SetInputConnection(cone.GetOutputPort())
    actor.SetMapper(mapper)
    actor.SetProperty(vtk_property)

    return cone, actor


def gap_finder(in_array):
    """
    helper function to find gaps in marker trajectories. 
    :param in_array: 1d array of marker trajectories
    :return: dict of gap info including count, and start and end
            indices
    """
    nan_ind = np.where(np.isfinite(in_array))[0]
    lower_bounds = (nan_ind + 1)[:-1]
    upper_bounds = (nan_ind - 1)[1:]
    mask = lower_bounds <= upper_bounds
    upper_bounds, lower_bounds = upper_bounds[mask], lower_bounds[mask]

    gaps = {'count': len(upper_bounds),
            'starts': list(lower_bounds),
            'ends': list(upper_bounds),
            'gap_list': []}

    for start, end in zip(lower_bounds, upper_bounds):
        gap = list(range(start, end + 1))
        gaps['gap_list'] = [*gaps['gap_list'], *gap, 'nan']

    return gaps


def set_cones(cone_source, cone_actor, direction, valids, start, array):

    if direction == 'forward':
        e = valids[0]
        s = valids[-1]
    elif direction == 'backward':
        e = valids[-1]
        s = valids[0]

    if len(valids) == 1:
        vector = array[s, :]
    else:
        vector = array[s, :] - array[e, :]

    unit_vector = np.array(ut.unit(vector))
    cone_pos = array[start] - (unit_vector * 18)  # 18 = half length of cone
    cone_actor.SetPosition(cone_pos)
    cone_source.SetDirection(vector)


def vtk_spline_gen(colour):
    pnts, lnes, plydat, act = traj_gen(colour=colour)
    return {'points': pnts,
            'lines': lnes,
            'polydata': plydat,
            'actor': act}


def set_spline(vtk_spline, spline):
    """update vis_toolkit stuff with spline"""
    sub_length = 0
    ind_list = []
    for ind, coord in enumerate(spline):
        vtk_spline['points'].InsertNextPoint(coord)

        if sub_length < 2:
            ind_list.append(ind)
            sub_length += 1
        else:
            vtk_spline['lines'].InsertNextCell(sub_length)
            for i in ind_list:
                vtk_spline['lines'].InsertCellPoint(i)

            sub_length = 0
            ind_list = []


class Gaps(object):
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.vtk_spline_linear = vtk_spline_gen(colour=(1.0, .1, 0.3))
        self.vtk_spline_cubic = vtk_spline_gen(colour=(0.0, .3, 1.0))
        self.gap_cone_forward, self.gap_cone_actor_start = cone_gen()
        self.gap_cone_backward, self.gap_cone_actor_end = cone_gen()

        self.mainwindow.ui.gapTable.setFocusPolicy(QtCore.Qt.NoFocus)
        self.mainwindow.ui.gapTable.itemClicked.connect(self.gap_table_selected)
        self.mainwindow.ui.gapTable.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        style = """QTableView::item:selected { 
                               color:white; 
                               background:blue;}
                           QTableCornerButton::section{
                               background-color:#232326;}
                           QHeaderView::section {
                               color:black; 
                               background-color:#f6f6f6;
                               padding:2px;}"""

        self.mainwindow.ui.gapTable.setStyleSheet(style)
        self.mainwindow.ui.gapTable.setColumnCount(2)
        self.mainwindow.ui.gapTable.setHorizontalHeaderLabels(['Trajectory', 'Gaps'])
        header = self.mainwindow.ui.gapTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.mainwindow.ui.gapTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.mainwindow.ui.gapFillToolButton.clicked.connect(self.show_gap_filling)  # show/hide widget

        self.mainwindow.ui.gapLeftButton.setIcon(self.mainwindow.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
        self.mainwindow.ui.gapRightButton.setIcon(self.mainwindow.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
        self.mainwindow.ui.gapRightButton.clicked.connect(partial(self.gap_shift, 'forward'))
        self.mainwindow.ui.gapLeftButton.clicked.connect(partial(self.gap_shift, 'backward'))
        self.mainwindow.ui.splineButton.clicked.connect(self.spline)
        self.mainwindow.ui.undo.clicked.connect(self.undo_operation)

    def init(self):
        # subscribe to spline updater. Dragged cones will update spline_indices
        self.updates = UpdateIndices()
        self.updates.bind_to(self.set_dragged_indices)

        self.gap_dict = {}
        self.gaps_shown = False
        self.current_gap_marker = None
        self.current_gap_count = None

        # used to keep track of current frame in gap status (ingap_request())
        self.in_gap = None
        self.current_gap_index = None

        self.current_array = None
        self.current_start = None
        self.current_new_start = None

        self.current_end = None
        self.current_new_end = None

        self.current_spline = None
        self.current_gap_length = None

    def set_data(self, data):
        self.mainwindow.pycgm_data = data

    def show_gap_filling(self):
        if not self.mainwindow.ui.gapFillWidget.isVisible():
            self.mainwindow.ui.gapFillWidget.setVisible(True)
            self.mainwindow.ui.gapFillToolButton.setIcon(QtGui.QIcon("./Resources/Images/uparrow.png"))
        else:
            self.mainwindow.ui.gapFillWidget.setVisible(False)
            self.mainwindow.ui.gapFillToolButton.setIcon(QtGui.QIcon("./Resources/Images/downarrow.png"))

    def find_gaps(self):
        for mrker, val in self.mainwindow.pycgm_data.Data['Markers'].items():
            if mrker[0] != '*':
                gaps = gap_finder(val[0, :])
                if gaps['count'] > 0:  # individual data points will not be shown
                    self.gap_dict[mrker] = gaps

    def populate_gap_table(self):
        # self.ui.gapTable.setRowCount(len(self.gap_dict.keys()))
        index = 0
        for mrker, values in self.gap_dict.items():
            if values['count'] > 0:
                index += 1
        self.mainwindow.ui.gapTable.setRowCount(index)

        index = 0
        for mrker, values in self.gap_dict.items():
            # don't show row when all gaps have been filled
            if values['count'] > 0:
                self.mainwindow.ui.gapTable.setItem(index, 0, QtWidgets.QTableWidgetItem(mrker))
                self.mainwindow.ui.gapTable.setItem(index, 1, QtWidgets.QTableWidgetItem(str(values['count'])))
                index += 1
        self.mainwindow.ui.gapTable.verticalHeader().setVisible(False)

    def gap_table_selected(self):
        # remove old gap actors and reset visuals
        self.reset_helper()
        items = self.mainwindow.ui.gapTable.selectedItems()
        if items:
            marker = str(items[0].text())
            self.mainwindow.highlighter.highlighter_picked_handler(marker, from_gaps=True, selected=True)
            # allocate current marker, array and gap counter (used to iterate through gaps)
            self.current_gap_marker = marker
            self.current_array = self.mainwindow.pycgm_data.Data['Markers'][self.current_gap_marker][:3, :].T
            self.current_gap_count = 0

        else:
            # if we are deselecting, set current gap marker to None and reset counter
            self.current_gap_marker = None
            self.current_gap_count = 0
            # no deselection signal for gap table. So send this to highlight
            # handler, which will clear highlighted
            marker = None
            self.mainwindow.highlighter.highlighter_picked_handler(marker, from_gaps=True)
            self.mainwindow.ui.currentGapLength.clear()

    def clear_gap_table(self):
        self.current_gap_marker = None
        self.current_gap_count = 0
        self.reset_helper()
        self.mainwindow.ui.gapTable.clearSelection()

    def gap_shift(self, direction=None, index=None, reset=None, from_spline=None):
        # if animation is playing, do not shift with buttons
        if direction and self.mainwindow.player.isplaying():
            return
        # if we are outside of a gap reset stuff
        if reset:
            self.reset_helper()
            return

        # check if gaps are already filled
        if self.current_gap_marker and self.gap_dict[self.current_gap_marker]['count'] < 1:
            # there are no gaps: they are probably filled!
            self.reset_helper()
            self.clear_gap_table()
            return

        # input from ingap request
        if index:
            # we don't need to update current frame here
            update_frame = False
            # if no gap has already been shown, set current gap to index
            if not self.current_gap_count:
                self.current_gap_count = index
            # or overwrite if previous gap exists and has already been shown
            elif self.current_gap_count != index:
                self.current_gap_count = index

        # input from forward and backward gap filling tool buttons
        elif direction:
            if not self.current_gap_marker:
                return

            update_frame = True
            if direction == 'forward' and not from_spline:
                # if from spline, no need to advance as gap info changes following each
                # successful spline
                self.current_gap_count += 1
            elif direction == 'backward' and not from_spline:
                self.current_gap_count -= 1

            # reset when iterating forwards past end (or backwards past beginning) of gap list
            if self.current_gap_count > self.gap_dict[self.current_gap_marker]['count']:
                self.current_gap_count = 1
            elif self.current_gap_count < 1:
                self.current_gap_count = self.gap_dict[self.current_gap_marker]['count']

        # set default indices and spline
        self.set_default_indices()
        self.set_default_spline(update_frame)

    def set_default_indices(self):
        # retrieve start and end of required gap using gap count as index
        # point_dict[marker]['gaps'] contains actual frames missing (start:end) so need to
        # remove or add 1 frame to gap count
        start = self.gap_dict[self.current_gap_marker]['starts'][self.current_gap_count - 1] - 1
        end = self.gap_dict[self.current_gap_marker]['ends'][self.current_gap_count - 1] + 1

        # set default attributes
        self.current_start = start
        self.current_end = end

        # when we shift gaps these also need updating
        self.updates.dragged_start = start
        self.updates.dragged_end = end

    def set_default_spline(self, update_frame):
        # show the default linear and cubic spline
        self.perform_spline()

        # reset the drag actor style base_x variable which defines the movement of the cone on mousemove
        self.mainwindow.vtk3d_widget.pycgm_drag_actor_style.reset_base_x()

        if update_frame:
            # jump current frame to start of gap. Advance 2 frames so that current frame falls within the gap
            # and marker is not visible
            self.mainwindow.emitter.emit(self.current_start + 2)
            self.mainwindow.ui.vtkScrollSlider.setValue(self.current_start + 2)

    def set_dragged_start(self, ind):
        start_fa = int(ind)
        # distance between dragged cone location and original gap start
        # self.current_start set initially as default by self.set_default_indices()
        start = self.current_start - start_fa
        # get start value of current spline (set as default by self.set_default_spline())
        stop_val = self.current_array[int(start) - 2, 0]
        # As cone is dragged backward through data, confirm the new values are valid. If
        # not disable dragging
        if np.isfinite(stop_val) and self.current_start - start <= 100:
            # update attribute which will call show_spline()
            self.updates.dragged_start = start
            return 1

    def set_dragged_end(self, ind):
        end_fa = int(ind)
        end = self.current_end + end_fa
        stop_val = self.current_array[int(end) + 2, 0]  # stop whilst we have 2 valid indices
        if np.isfinite(stop_val):
            self.updates.dragged_end = end
            return 1

    def set_dragged_indices(self, start, end):
        """when cones are dragged this is called as observer of self.updates"""
        # on first call one of these will be of type None so set to default value
        if not start:
            start = self.current_start
        if not end:
            end = self.current_end

        self.perform_spline(start=start, end=end, from_dragging=True)

    def start_valid_helper(self, start, to_remove=None):
        # find excess valid data before start and after end to use for splining
        if to_remove:
            val = to_remove
        else:
            val = 0

        valid_starts = []
        for i in range(start, start - val, -1):
            if np.isfinite(self.current_array[i, 0]):
                valid_starts.append(i)
            else:
                break
        valid_starts.reverse()

        return valid_starts

    def end_valid_helper(self, end, to_add=None):
        if to_add:
            val = to_add
        else:
            val = 0

        valid_ends = []
        for j in range(end, end + val):
            if j < len(self.current_array):  # don't overcount
                if np.isfinite(self.current_array[j, 0]):
                    valid_ends.append(j)
                else:
                    break

        return valid_ends

    def prepare_data_for_spline(self, valid_starts, valid_ends, from_dragging=None):
        # the start and end of spline will correspond to the start and end of excess data
        new_start = valid_starts[-1]
        spline_start = valid_starts[0]
        new_end = valid_ends[0]
        spline_end = valid_ends[-1]

        # copy array to prevent overwriting
        y3d = self.current_array.copy()

        # convert values between dragged cones and old start/stop to nans so
        # they are not included in spline
        if from_dragging:
            if new_start < self.current_start:
                self.current_new_start = new_start
                y3d[new_start:self.current_start + 1, :] = np.nan
            else:
                self.current_new_start = None

            if new_end > self.current_end:
                self.current_new_end = new_end
                y3d[self.current_end: new_end, :] = np.nan
            else:
                self.current_new_end = None

        y3d = y3d[spline_start:spline_end, :]

        return y3d

    def perform_spline(self, from_dragging=None, start=None, end=None):
        # set start and end values
        if not start:
            start = self.current_start
        if not end:
            end = self.current_end

        try:
            # retrieve excess data before start and after end to use for splining
            valid_starts = self.start_valid_helper(start, to_remove=5)
            valid_ends = self.end_valid_helper(end, to_add=5)

            # prepare data for splining
            y3d = self.prepare_data_for_spline(valid_starts, valid_ends, from_dragging)

            # perform splining operation
            np_linear_splined, np_cubic_splined = ut.spliner(y3d)

        except Exception:
            pass

            if self.gaps_shown:
                self.reset_helper()
            return

        # prepare vis_toolkit actors and visuals
        if not self.gaps_shown:
            self.add_gap_actors()
            self.gaps_shown = True
        else:
            self.reset_visuals()

        # remove redundant start and end portions of spline if necessary
        np_cubic_splined = np_cubic_splined[len(valid_starts)-1:-len(valid_ends)+1]

        # set current spline attribute
        self.current_spline = np_cubic_splined

        # update mainwindow.ui with current gap length
        self.mainwindow.ui.currentGapLength.setText(str(len(self.current_spline)))

        # set vis_toolkit stuff with spline
        set_spline(self.vtk_spline_linear, np_linear_splined)
        set_spline(self.vtk_spline_cubic, np_cubic_splined)

        # set new cones
        self.set_forward_cone(start=start)
        self.set_backward_cone(end=end)

        # modify vis_toolkit polydata
        self.vtk_spline_linear['polydata'].Modified()
        self.vtk_spline_cubic['polydata'].Modified()

    def set_forward_cone(self, start=None):
        # this won't be called before show_spline() so no need to alter current_marker etc.
        valid_starts = self.start_valid_helper(start, to_remove=10)

        if len(valid_starts) > 0:
            set_cones(self.gap_cone_forward, self.gap_cone_actor_start, 'forward', valid_starts,
                      start, self.current_array)

    def set_backward_cone(self, end=None):
        valid_ends = self.end_valid_helper(end, to_add=10)

        if len(valid_ends) > 0:
            set_cones(self.gap_cone_backward, self.gap_cone_actor_end, 'backward', valid_ends,
                      end, self.current_array)

    def undo_operation(self):
        self.mainwindow.handler.undo()
        self.populate_gap_table()

        # only try to update frame if gaps still available
        if self.current_gap_marker and self.gap_dict[self.current_gap_marker]['count'] > 0:
            self.gap_shift(direction='backward', from_spline=True)
            self.mainwindow.emitter.emit('current')

    def spline(self):
        # do we have a highlighted marker? take from gap table
        items = self.mainwindow.ui.gapTable.selectedItems()
        if items:
            # ensure it has gaps
            # if self.gap_dict[marker]['count'] > 0:
            # do we have a maximum gap length? If not set default of 10
            max_gap_length = self.mainwindow.ui.maxGapLength.text()
            if not max_gap_length:
                self.mainwindow.ui.maxGapLength.setText('10')
            elif max_gap_length and int(max_gap_length) < 1:
                self.mainwindow.ui.maxGapLength.setText('10')

            splined = self.save_spline()

            if splined:
                self.populate_gap_table()
                self.gap_shift(direction='forward', from_spline=True)
                self.mainwindow.emitter.emit('current')

    def save_spline(self):
        if self.current_new_start:
            start = self.current_new_start
        elif self.current_start:
            start = self.current_start

        if self.current_new_end:
            end = self.current_new_end
        elif self.current_end:
            end = self.current_end

        if type(self.current_spline) == np.ndarray:
            # check current gap is within maximum gap length
            gap_length = len(self.current_spline)
            if gap_length <= int(self.mainwindow.ui.maxGapLength.text()):

                # store gap info and spline in history
                old_traj = self.mainwindow.pycgm_data.Data['Markers'][self.current_gap_marker][:3, start:end].copy()
                old_gap_starts = self.gap_dict[self.current_gap_marker]['starts']
                old_gap_ends = self.gap_dict[self.current_gap_marker]['ends']
                old_gap_list = self.gap_dict[self.current_gap_marker]['gap_list']

                # save first call as original marker trajectory to revert to
                # on this call, transpose the old trajectory
                self.mainwindow.handler.execute("save_spline", start, end, old_traj.T, self.current_gap_marker, 'gap',
                                     old_gap_starts, old_gap_ends, old_gap_list)

                # copy old gap dict information and update to reflect that gap has been filled
                new_gap_starts = old_gap_starts.copy()
                new_gap_ends = old_gap_ends.copy()
                del new_gap_starts[self.current_gap_count - 1]
                del new_gap_ends[self.current_gap_count - 1]

                new_gap_list = old_gap_list.copy()
                gap_ind_count = 0
                gap_ind_list = []
                for cnt, ind in enumerate(new_gap_list):
                    gap_ind_list.append(cnt)
                    if ind == 'nan':
                        gap_ind_count += 1
                        if gap_ind_count - 1 != self.current_gap_count - 1:
                            gap_ind_list = []
                        elif gap_ind_count - 1 == self.current_gap_count - 1:
                            del new_gap_list[gap_ind_list[0]:gap_ind_list[-1] + 1]
                            break

                # on this call save spline and new gap dict info in history
                self.mainwindow.handler.execute("save_spline", start, end, self.current_spline, self.current_gap_marker, 'spline',
                                     new_gap_starts, new_gap_ends, new_gap_list)

                return 1

    def ingap_request(self, frame):
        # check if current gap is showing
        if self.current_gap_marker:
            if frame in self.gap_dict[self.current_gap_marker]['gap_list']:
                if not self.in_gap:
                    self.in_gap = True
                    count = 1
                    for i in self.gap_dict[self.current_gap_marker]['gap_list']:
                        if i == 'nan':
                            count += 1
                        elif i == frame:
                            self.current_gap_index = count
                            self.gap_shift(index=self.current_gap_index)
                            break

            elif self.in_gap:
                self.gap_shift(reset=True)
                self.current_gap_index = None
                self.in_gap = False

    def reset_helper(self):
        self.reset_visuals()
        self.remove_gap_actors()
        self.gaps_shown = False
        self.current_spline = None

    def remove_gap_actors(self):
        self.mainwindow.vtk3d_widget.ren.RemoveActor(self.vtk_spline_linear['actor'])
        self.mainwindow.vtk3d_widget.ren.RemoveActor(self.vtk_spline_cubic['actor'])
        self.mainwindow.vtk3d_widget.ren.RemoveActor(self.gap_cone_actor_start)
        self.mainwindow.vtk3d_widget.ren.RemoveActor(self.gap_cone_actor_end)
        self.mainwindow.vtk3d_widget.ren.GetRenderWindow().Render()

    def add_gap_actors(self):
        self.mainwindow.vtk3d_widget.ren.AddActor(self.vtk_spline_linear['actor'])
        self.mainwindow.vtk3d_widget.ren.AddActor(self.vtk_spline_cubic['actor'])
        self.mainwindow.vtk3d_widget.ren.AddActor(self.gap_cone_actor_start)
        self.mainwindow.vtk3d_widget.ren.AddActor(self.gap_cone_actor_end)

    def reset_visuals(self):
        self.vtk_spline_linear['points'].Reset()
        self.vtk_spline_cubic['points'].Reset()
        self.vtk_spline_linear['lines'].Reset()
        self.vtk_spline_cubic['lines'].Reset()
        self.vtk_spline_linear['polydata'].Reset()
        self.vtk_spline_cubic['polydata'].Reset()

