def name_helper(selected_id, marker_names):
    marker_id_str = str(marker_names.index(selected_id))
    selected_id = int(marker_id_str)

    return marker_id_str, selected_id


class Highlighter:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.marker_names = None
        self.highlighted = {}

    def update_marker_names(self):
        self.marker_names = [*self.mainwindow.markers.points]
        for mrk in self.marker_names:
            self.highlighted[str(self.marker_names.index(mrk))] = {'highlighted': False}

    def highlight_helper(self, marker_id_str):
        self.highlight_marker(highlight=marker_id_str)  # pass as str
        self.highlighted[marker_id_str]['highlighted'] = True

    def dehighlight_helper(self, marker_id_str):
        self.highlight_marker(dehighlight=marker_id_str)
        self.highlighted[marker_id_str]['highlighted'] = False

    def highlighter_picked_handler(self,
                                   selected_id,
                                   from_picker=None,
                                   from_explorer=None,
                                   from_gaps=None,
                                   selected=None,
                                   deselected=None):
        """This handles all highlighting calls from picker, explorer widget and gap table. Whilst
        gap table should update explorer widget and highlight markers, picker and explorer widget should not
        update gap table. As such, gap table is cleared whenever incoming from picker or explorer widget.
         Also, when a new gap table row is selected, all other explorer/picker selections are cleared."""

        if from_picker:
            marker_id_str = str(selected_id)
            if not self.highlighted[marker_id_str]['highlighted']:
                self.highlight_helper(marker_id_str)
                self.mainwindow.explorer_widget.highlight_marker_tree(self.marker_names[selected_id], highlight=True)

            elif self.highlighted[marker_id_str]['highlighted']:
                self.dehighlight_helper(marker_id_str)
                self.mainwindow.explorer_widget.highlight_marker_tree(self.marker_names[selected_id], dehighlight=True)

            self.mainwindow.gaps.clear_gap_table()

        elif from_explorer:
            # explorer sends str of marker name
            marker_id_str, _ = name_helper(selected_id, self.marker_names)

            # and has selection model that sends both selected and deselected items
            if selected:
                if not self.highlighted[marker_id_str]['highlighted']:  # this statement prevents recursion
                    self.highlight_helper(marker_id_str)
                    self.mainwindow.gaps.clear_gap_table()

            if deselected:
                if self.highlighted[marker_id_str]['highlighted']:
                    self.dehighlight_helper(marker_id_str)
                    self.mainwindow.gaps.clear_gap_table()

        elif from_gaps:
            # if new or nothing is selected (e.g. last gap traj deselected) clear highlighted dict
            self.clear_highlighted()

            if selected_id:
                marker_id_str, selected_id = name_helper(selected_id, self.marker_names)

                if selected:
                    self.highlight_helper(marker_id_str)
                    self.mainwindow.explorer_widget.highlight_marker_tree(self.marker_names[selected_id],
                                                                          highlight=True)

                elif deselected:
                    self.dehighlight_helper(marker_id_str)
                    self.mainwindow.explorer_widget.highlight_marker_tree(self.marker_names[selected_id],
                                                                          dehighlight=True)

    def highlight_marker(self, highlight=None, dehighlight=None):
        if highlight:
            highlight = int(highlight)  # convert back to int for marker list index
            self.mainwindow.markers.set_marker_colour(highlight, (102, 178, 255))
            self.mainwindow.markers.set_marker_size(highlight, (2, 2, 2))
            self.mainwindow.trajectories.update_trajectories(highlight, add=True)

        if dehighlight:
            dehighlight = int(dehighlight)
            self.mainwindow.markers.set_marker_colour(dehighlight, (192, 192, 192))
            self.mainwindow.markers.set_marker_size(dehighlight, (1, 1, 1))
            self.mainwindow.trajectories.update_trajectories(dehighlight, remove=True)

        self.mainwindow.emitter.emit('current')

    def clear_highlighted(self):
        for mrk, val in self.highlighted.items():
            if val['highlighted']:
                # modify this before updating explorer to prevent recursion
                val['highlighted'] = False
                self.highlight_marker(dehighlight=mrk)
                self.mainwindow.explorer_widget.highlight_marker_tree(self.marker_names[int(mrk)], dehighlight=True)




