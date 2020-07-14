from abc import ABCMeta, abstractmethod
import time


class Command(metaclass=ABCMeta):
    @abstractmethod
    def execute(*args):
        pass


class UndoRedo(metaclass=ABCMeta):
    @abstractmethod
    def history(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def redo(self):
        pass


class Handler(UndoRedo):
    def __init__(self):
        self._commands = {}
        self._history = [()]
        self._history_position = 0

    @property
    def history(self):
        return self._history

    def register(self, command_name, command):
        self._commands[command_name] = command

    def execute(self, command_name, *args):
        if command_name in self._commands.keys():
            self._history_position += 1
            self._commands[command_name].execute(args)
            if len(self._history) == self._history_position:
                self._history.append((time.time(), command_name, args))
            else:
                self._history = self._history[:self._history_position+1]
                self._history[self._history_position] = (time.time(), command_name, args)

    def undo(self):
        if self._history_position > 1:
            self._history_position -= 1

            if self._history[self._history_position][2][4] == 'spline':
                self._history_position -= 1

            self._commands[
                self._history[self._history_position][1]
            ].execute(self._history[self._history_position][2])

    def redo(self):
        if self._history_position + 1 < len(self._history):
            self._history_position += 1
            self._commands[
                self._history[self._history_position][1]
            ].execute(self._history[self._history_position][2])

    def clear_history(self):
        self._history = [()]
        self._history_position = 0


class GapReceiver:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow

    def save_spline(self, *args):
        start = args[0][0][0]
        end = args[0][0][1]
        spline = args[0][0][2]
        marker = args[0][0][3]
        # kind = args[0][0][4]
        gap_starts = args[0][0][5]
        gap_ends = args[0][0][6]
        gap_list = args[0][0][7]

        self.mainwindow.pycgm_data.Data['Markers'][marker][:3, start:end] = spline.T
        self.mainwindow.gaps.gap_dict[marker]['starts'] = gap_starts
        self.mainwindow.gaps.gap_dict[marker]['ends'] = gap_ends
        self.mainwindow.gaps.gap_dict[marker]['count'] = len(gap_starts)
        self.mainwindow.gaps.gap_dict[marker]['gap_list'] = gap_list

        self.update_marker_data_source(individual=marker)


class SaveSplineCommand(Command):
    def __init__(self, handler):
        self._handler = handler

    def execute(self, *args):
        self._handler.save_spline(args)
