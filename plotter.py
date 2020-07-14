import vtk
import numpy as np


def gen_array_table():
    arrx = vtk.vtkFloatArray()
    arrx.SetName('')
    arrd = vtk.vtkFloatArray()
    arrd.SetName('x')
    table = vtk.vtkTable()
    table.AddColumn(arrd)
    table.AddColumn(arrx)

    return table


def channel_finder(selected):
    """find forceplatform analog channel"""
    texts = []
    item_copy = selected

    while item_copy is not None:
        texts.append(item_copy.text(0))
        item_copy = item_copy.parent()

    path = "".join(texts)
    ind = path.find('#')

    if ind > 0:
        ch_key = selected.text(0)
        fp_no = str(path[ind + 1])

        return ch_key, fp_no


class Plotter:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.downsample = None
        self.selected = dict()
        self.current_frame = None
        self.force_targets = ['Force.Fx', 'Force.Fy', 'Force.Fz']
        self.moment_targets = ['Moment.Mx', 'Moment.My', 'Moment.Mz']
        self.cop_targets = ['Cx', 'Cy', 'Cz']
        self.line_tables = []
        self.prev_lines = []
        # keep track of channels selected/deselected
        self.count = 0

    def update_channels(self):
        # store information
        self.selected = dict()

        # update analog
        if len([*self.mainwindow.pycgm_data.Data['Analogs']]) > 0:
            for key in [*self.mainwindow.pycgm_data.Data['Analogs']]:
                self.selected[key] = dict()
                self.selected[key]['selected'] = False
                self.selected[key]['Group'] = 'Analogs'

                # add type and units if possible
                if ('F' or 'f') in key:
                    self.selected[key]['Kind'] = 'Force'
                    self.selected[key]['Unit'] = 'N'
                elif ('M' or 'm') in key:
                    self.selected[key]['Kind'] = 'Moment'
                    self.selected[key]['Unit'] = 'N.mm'
                else:
                    self.selected[key]['Kind'] = 'Unknown'
                    self.selected[key]['Unit'] = 'Unknown'

                # add axis if possible
                try:
                    self.selected[key]['Axis'] = [c in key for c in ('x', 'y', 'z')].index(True)
                except ValueError:
                    self.selected[key]['Axis'] = 'Unknown'

        # update angles
        models = ['Angles', 'Bones', 'Powers', 'Forces', 'Moments']
        units = ['deg', 'mm', 'W/kg', 'N/kg', 'N.mm/kg']
        for model, unit in zip(models, units):
            if len([*self.mainwindow.pycgm_data.Data[model]]) > 0:
                for key in [*self.mainwindow.pycgm_data.Data[model]]:
                    self.selected[key] = dict()
                    self.selected[key]['selected'] = False
                    self.selected[key]['Kind'] = 'Model'
                    self.selected[key]['Axis'] = 'Unknown'
                    self.selected[key]['Group'] = model
                    self.selected[key]['Unit'] = unit

        pointsamp = self.mainwindow.pycgm_data.Gen['Vid_SampRate']
        analogsamp = self.mainwindow.pycgm_data.Gen['Analog_SampRate']
        self.downsample = int(analogsamp / pointsamp)
        self.current_frame = self.mainwindow.pycgm_data.Gen['Vid_FirstFrame']

    def select(self, channel):
        if not self.selected[channel]['selected']:
            self.selected[channel]['selected'] = True

    def deselect(self, channel):
        if self.selected[channel]['selected']:
            self.selected[channel]['selected'] = False

    def plotter_picked_handler(self, item, selected=None, deselected=None, count=None):
        # don't plot until all selections/deselections have been made
        if self.count != count:
            self.count += 1

        # retreive channel name from item
        try:
            ch_key, fp_no = channel_finder(item)
            key = ch_key + fp_no
        except TypeError:
            key = item.text(0)

        # select/deselect channels
        for channel in [*self.selected]:

            if key == channel[-3:] or key == channel:
                if selected:
                    self.select(channel)
                elif deselected:
                    self.deselect(channel)

        # when we are ready call plotter
        if self.count == count or self.count > count:
            self.plot_sorter()
            self.count = 0

    def get_selected(self, ch_type):
        chans = [[], [], []]
        for ch_name, info in self.selected.items():
            if info['selected']:  # we have a selected channel
                kind = info['Kind']
                axis = info['Axis']
                group = info['Group']
                unit = info['Unit']
                unit_str = '(' + unit + ')'

                if kind == ch_type:  # we have a match
                    # retreive data
                    data = self.mainwindow.pycgm_data.Data[group][ch_name]
                    # determine how to allocate data and yaxis title for plot
                    if kind == 'Model':  # three axis: append to appropriate tuple index (0, 1, 2) = (x, y, z)
                        for i, ax in enumerate(('X', 'Y', 'Z')):
                            chans[i].append((data[i, :], ax + unit_str))

                    elif axis != 'Unknown':  # axis from analog data has been identified
                        # downsample all analog data but not model outputs
                        chans[axis].append((data[0::self.downsample], ch_name + unit_str))

                    elif axis == 'Unknown':
                        chans.append([(data[0::self.downsample], ch_name)])

        return chans

    def plot_sorter(self):
        self.remove_plots()
        to_plot = [self.get_selected('Force'),
                   self.get_selected('Moment'),
                   self.get_selected('Unknown'),
                   self.get_selected('Model')]

        # how many charts do we need for chart matrix
        chs = 0
        for group in to_plot:
            for ch in group:
                if len(ch) > 0:
                    chs += 1
        if chs < 1:
            return
        else:  # set chart matrix sizing
            self.mainwindow.vtk2d_widget.chart_matrix.SetSize(vtk.vtkVector2i(1, chs))
            self.mainwindow.vtk2d_widget.chart_matrix.SetGutter(vtk.vtkVector2f(15.0, 15.0))

            # populate chart matrix
            chs2 = 0
            for group in to_plot:
                for ch in group:
                    if len(ch) > 0:
                        chart = self.mainwindow.vtk2d_widget.chart_matrix.GetChart(vtk.vtkVector2i(0, chs2))
                        chart.ClearPlots()

                        if chs2 > 0:
                            chart.GetAxis(vtk.vtkAxis.BOTTOM).SetLabelsVisible(False)
                            chart.GetAxis(vtk.vtkAxis.BOTTOM).SetTicksVisible(False)

                        chart.GetAxis(vtk.vtkAxis.BOTTOM).SetTitle('')
                        # channel[0] = data; channel[1] = yaxis name
                        for channel in ch:
                            table = gen_array_table()
                            chart.GetAxis(vtk.vtkAxis.LEFT).SetTitle(channel[1])
                            data_to_plot = channel[0]
                            num_points = len(data_to_plot)
                            table.SetNumberOfRows(num_points)
                            indices = np.arange(1, num_points + 1, 1).astype(float)

                            for i in range(num_points):
                                table.SetValue(i, 0, indices[i])
                                table.SetValue(i, 1, data_to_plot[i])

                            line = chart.AddPlot(vtk.vtkChart.LINE)
                            line.SetInputData(table, 0, 1)
                            line.SetColor(0, 102, 178, 255)
                            line.SetWidth(0.1)

                        # this for progress line
                        line_table = gen_array_table()
                        line_table.SetNumberOfRows(2)
                        self.line_tables.append(line_table)

                        chs2 += 1

            self.mainwindow.vtk2d_widget.chart_matrix.Update()
            self.mainwindow.vtk2d_widget.iren.GetRenderWindow().Render()
            self.update_current_line('current')

    def update_current_line(self, frame):
        """this needs to be sped up significantly"""

        if frame == 'current':
            frame = self.current_frame
        else:
            self.current_frame = frame

        try:
            for i in range(len(self.line_tables)):
                chart = self.mainwindow.vtk2d_widget.chart_matrix.GetChart(vtk.vtkVector2i(0, i))

                if chart:
                    # remove old progress lines
                    [chart.RemovePlotInstance(lne) for lne in self.prev_lines]

                    minval = chart.GetAxis(vtk.vtkAxis.LEFT).GetMinimum()
                    maxval = chart.GetAxis(vtk.vtkAxis.LEFT).GetMaximum()

                    # 0, frame, minval
                    # 1, frame, maxval

                    self.line_tables[i].SetValue(0, 0, frame)
                    self.line_tables[i].SetValue(0, 1, minval)
                    self.line_tables[i].SetValue(1, 0, frame)
                    self.line_tables[i].SetValue(1, 1, maxval)

                    current_line = chart.AddPlot(vtk.vtkChart.LINE)
                    current_line.SetInputData(self.line_tables[i], 0, 1)
                    current_line.SetColor(0, 173, 216, 230)
                    current_line.SetWidth(2)

                    self.prev_lines.append(current_line)

                    self.mainwindow.vtk2d_widget.iren.GetRenderWindow().Render()

        except TypeError:
            pass

    def remove_plots(self):
        self.mainwindow.vtk2d_widget.chart_matrix.SetSize(vtk.vtkVector2i(0, 0))
        self.mainwindow.vtk2d_widget.chart_matrix.Update()
        self.mainwindow.vtk2d_widget.iren.GetRenderWindow().Render()
