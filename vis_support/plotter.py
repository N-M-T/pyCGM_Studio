import numpy as np
import pyqtgraph as pg


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


class GraphicsLayout(pg.GraphicsLayout):
    """I overode this method as indexerrors kept raising when clearing plots"""
    def removeItem(self, item):
        try:
            """Remove *item* from the layout."""
            ind = self.itemIndex(item)
            self.layout.removeAt(ind)
            self.scene().removeItem(item)

            for r, c in self.items[item]:
                del self.rows[r][c]
            del self.items[item]

            item.geometryChanged.disconnect(self._updateItemBorder)
            del self.itemBorders[item]

            self.update()
        except:
            pass


class GraphicsLayoutWidget(pg.GraphicsView):
    def __init__(self, parent=None, show=False, size=None, title=None, **kargs):
        pg.mkQApp()
        pg.GraphicsView.__init__(self, parent)
        self.ci = GraphicsLayout(**kargs)
        for n in ['nextRow', 'nextCol', 'nextColumn', 'addPlot', 'addViewBox', 'addItem', 'getItem', 'addLayout',
                  'addLabel', 'removeItem', 'itemIndex', 'clear']:
            setattr(self, n, getattr(self.ci, n))
        self.setCentralItem(self.ci)

        if size is not None:
            self.resize(*size)

        if title is not None:
            self.setWindowTitle(title)

        if show is True:
            self.show()


class Plotter:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.downsample = None
        self.selected = dict()
        self.current_frame = None
        self.force_targets = ['Force.Fx', 'Force.Fy', 'Force.Fz']
        self.moment_targets = ['Moment.Mx', 'Moment.My', 'Moment.Mz']
        self.cop_targets = ['Cx', 'Cy', 'Cz']
        self.count = 0  # keep track of channels selected/deselected
        self.progress_lines = []
        self.mainwindow.pyqtgraph2d_widget.ci.layout.setSpacing(0.)
        self.mainwindow.pyqtgraph2d_widget.ci.layout.setContentsMargins(10., 10., 0., 10.)

    def update_channels(self):
        self.progress_lines = []

        # store information
        self.selected = dict()

        # update analog channels
        if len([*self.mainwindow.pycgm_data.Data['Analogs']]) > 0:
            for key in [*self.mainwindow.pycgm_data.Data['Analogs']]:
                self.selected[key] = dict()
                self.selected[key]['selected'] = False
                self.selected[key]['Group'] = 'Analogs'

                # attempt to add type and units
                if ('F' or 'f') in key:
                    self.selected[key]['Kind'] = 'Force'
                    self.selected[key]['Unit'] = 'N'
                elif ('M' or 'm') in key:
                    self.selected[key]['Kind'] = 'Moment'
                    self.selected[key]['Unit'] = 'N.mm'
                else:
                    self.selected[key]['Kind'] = 'Unknown'
                    self.selected[key]['Unit'] = 'Unknown'

                # attempt to add axis
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

        # update pycgm angles
        if len([*self.mainwindow.pycgm_data.Data['PyCGM Model Outputs']]) > 0:
            for key in [*self.mainwindow.pycgm_data.Data['PyCGM Model Outputs']]:
                self.selected[key] = dict()
                self.selected[key]['selected'] = False
                self.selected[key]['Kind'] = 'Model'
                self.selected[key]['Axis'] = 'Unknown'
                self.selected[key]['Group'] = 'PyCGM Model Outputs'
                self.selected[key]['Unit'] = 'deg'

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
        # handles a list of data series to plot
        self.remove_plots()
        self.progress_lines = []

        to_plot = [self.get_selected('Force'),
                   self.get_selected('Moment'),
                   self.get_selected('Unknown'),
                   self.get_selected('Model')]

        # add appropriate number of plots and progress lines
        plot_list = []
        chs = 0
        for group in to_plot:
            for ch in group:
                if len(ch) > 0:
                    plot = self.mainwindow.pyqtgraph2d_widget.addPlot(row=chs, col=0)
                    start = self.mainwindow.pycgm_data.Gen['Vid_FirstFrame']
                    end = self.mainwindow.pycgm_data.Gen['Vid_LastFrame']
                    line = plot.addLine(x=start,
                                        bounds=[start, end],
                                        movable=True,
                                        pen=pg.mkPen('b', width=6))

                    # connect movement of line so emit is called with frame number
                    line.sigDragged.connect(self.update_current_line)
                    self.progress_lines.append(line)

                    plot.showGrid(x=True, y=True)
                    plot_list.append(plot)
                    # channel[0] = data; channel[1] = yaxis name
                    plot.setLabel('left', ch[0][1])
                    chs += 1
        if chs < 1:
            return

        # sychronize axis scaling between subplots
        no_plots = len(plot_list)
        if no_plots > 1:
            for i in range(1, no_plots):
                plt1 = plot_list[0]
                nextplt = plot_list[i]
                nextplt.setXLink(plt1)

        # add data to plots
        chs2 = 0
        for group in to_plot:
            for ch in group:
                if len(ch) > 0:
                    plot = plot_list[chs2]

                    if chs2 < no_plots - 1:  # keep ticks on bottom plot only
                        plot.getAxis('bottom').setStyle(showValues=False)
                    else:
                        plot.setLabel('bottom', 'Frames')

                    for channel in ch:
                        y = channel[0]
                        x = np.arange(1, len(y) + 1, 1)
                        plot.plot(x, y, pen='w')

                    self.update_current_line('current')
                    chs2 += 1

    def update_current_line(self, frame):
        if len(self.progress_lines) > 0:
            if frame == 'current':
                frame = self.current_frame

            elif isinstance(frame, int):  # this is from emitter
                self.current_frame = frame

            else:  # this is vline from graphitem
                frame = int(frame.value())
                self.current_frame = frame

            for line in self.progress_lines:
                line.setValue(frame)

            self.mainwindow.emitter.emit(frame, from_bar=True)

    def remove_plots(self):
        self.mainwindow.pyqtgraph2d_widget.clear()

