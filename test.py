import numpy as np
from utilities import linear_spline, nan_helper
from scipy.interpolate import interp1d
from abc import ABCMeta, abstractmethod
import time
np.set_printoptions(suppress=True, precision=2)


'''class Command(metaclass=ABCMeta):
    """The command interface, which all commands will implement"""

    @abstractmethod
    def execute(*args):
        """The required execute method which all command objects will use"""


class UndoRedo(metaclass=ABCMeta):
    """The Undo Redo interface"""
    @abstractmethod
    def history(self):
        """the history of the states"""

    @abstractmethod
    def undo(self):
        """for undoing the history of the states"""

    @abstractmethod
    def redo(self):
        """for redoing the history of the states"""


class Handler(UndoRedo):
    """The Invoker Class"""

    def __init__(self):
        self._commands = {}
        self._history = [()]  # A default start
        self._history_position = 0  # The position that is used for UNDO/REDO

    @property
    def history(self):
        """Return all records in the History list"""
        return self._history

    def register(self, command_name, command):
        """All commands are registered in the Invoker Class"""
        self._commands[command_name] = command

    def execute(self, command_name, *args):
        """Execute a pre defined command and log in history"""
        if command_name in self._commands.keys():
            self._history_position += 1
            self._commands[command_name].execute(args)
            if len(self._history) == self._history_position:
                # This is a new event in history
                self._history.append((time.time(), command_name, args))
            else:
                # This occurs if there was one of more UNDOs and then a new
                # execute command happened. In case of UNDO, the history_position
                # changes, and executing new commands purges any history after
                # the current position"""
                self._history = self._history[:self._history_position+1]

                self._history[self._history_position] = (time.time(), command_name, args)

                # self._history[self._history_position] = {
                #    time.time(): [command_name, args]
                # }
        else:
            print(f"Command [{command_name}] not recognised")

    def undo(self):
        """Undo a command if there is a command that can be undone.
        Update the history position so that further UNDOs or REDOs"""

        if self._history_position > 1:

            self._history_position -= 1
            self._commands[
                self._history[self._history_position][1]
            ].execute(self._history[self._history_position][2])
        else:
            print("nothing to undo")

    def redo(self):
        """Perform a REDO if the history_position is less than the end of the history list"""
        if self._history_position + 1 < len(self._history):
            self._history_position += 1
            self._commands[
                self._history[self._history_position][1]
            ].execute(self._history[self._history_position][2])
        else:
            print("nothing to REDO")


class SaveSplineCommand(Command):
    """A Command object, which implements the ICommand interface"""

    def __init__(self, handler):
        self._handler = handler

    def execute(self, *args):
        self._handler.save_spline(args)



class Receiver:
    def __init__(self, inarray):
        self.inarray = inarray
        self.pycgm_data = None
        self.saved = False
        self.current_spline = None

    def set_spline(self, do=None):
        if do:
            # scipy spline method
            y = inarray[:, 1].copy()
            nans, x = nan_helper(inarray[:, 1])
            y[nans] = np.interp(x(nans), x(~nans), y[~nans])
            x2 = x(~nans)
            y2 = y[~nans]
            f2 = interp1d(x2, y2, kind='cubic')
            xnew = np.arange(0, len(inarray), 1)
            splined = f2(xnew)
            self.current_spline = splined

        else:
            self.current_spline = inarray[:, 1]

        return self.current_spline

    def save_spline(self, *args):
        print(*args[0][0])


inarray = np.asarray([[1, 1, 1],
                     [2, 2, 2],
                     [np.nan, np.nan, np.nan],
                     [np.nan, np.nan, np.nan],
                     [5, 5, 5],
                     [6, 6, 6],
                     [7, 7, 7]])
receiver = Receiver(inarray)

# Create Commands
save_spline = SaveSplineCommand(receiver)
# off = OffCommand(receiver)

# Register the commands with the invoker (Switch)
handler = Handler()
handler.register("save_spline", save_spline)
# handler.register("off", off)

# mimic user interactions
spline = receiver.set_spline()
handler.execute("save_spline", spline) # gap
spline = receiver.set_spline(do='do')
handler.execute("save_spline", spline) # spline
handler.undo()  # gap

spline = receiver.set_spline()
handler.execute("save_spline", spline) # gap
spline = receiver.set_spline(do='do')
handler.execute("save_spline", spline) # spline

handler.undo()
handler.redo()
handler.redo()
handler.redo()
handler.undo()
handler.undo()
handler.undo()
handler.undo()
handler.undo()
handler.undo()

spline = receiver.set_spline()
handler.execute("save_spline", spline) # gap
spline = receiver.set_spline(do='do')
handler.execute("save_spline", spline) # spline'''


'''
# new_start = 2
# start = 6

# numpy spline method
# indices = np.transpose(np.arange(new_start, start, 1) + np.zeros((3, 1)))
# np.interp(x(nans), x(~nans), y[~nans])
# f2 = interp1d(x(~nans), y[~nans], kind='cubic')'''
import sys
from PyQt5 import QtGui, QtCore
import jtextfsm as textfsm


class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("PyQT tuts!")
        self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))
        self.home()

        sys.stdout = Stream(newText=self.onUpdateText)

    def onUpdateText(self, text):
        cursor = self.process.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def home(self):

        w = QtGui.QWidget()
        self.setCentralWidget(w)
        lay = QtGui.QVBoxLayout(w)
        btn = QtGui.QPushButton("Generate")
        btn.clicked.connect(self.TextFSM)

        self.process  = QtGui.QTextEdit()
        self.process.moveCursor(QtGui.QTextCursor.Start)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(500)
        self.process.setLineWrapMode(QtGui.QTextEdit.FixedPixelWidth)

        lay.addWidget(btn)
        lay.addWidget(self.process)

        self.show()

    def TextFSM(self):

        nameFile = 'Switch'

        try:
            input_file = open(nameFile + '.txt', encoding='utf-8')  # show version
            raw_text_data = input_file.read()
            input_file.close()

            input_file2 = open(nameFile + '.txt', encoding='utf-8')  # show env
            raw_text_data2 = input_file2.read()
            input_file2.close()

            input_file3 = open(nameFile + '.txt', encoding='utf-8')  # show flash
            raw_text_data3 = input_file3.read()
            input_file3.close()

            input_file4 = open(nameFile + '.txt', encoding='utf-8')  # show memory statistic
            raw_text_data4 = input_file4.read()
            input_file4.close()

            input_file5 = open(nameFile + '.txt', encoding='utf-8')  # show process cpu
            raw_text_data5 = input_file5.read()
            input_file5.close()

            template = open("show-version.textfsm")  # show version
            re_table = textfsm.TextFSM(template)
            fsm_results = re_table.ParseText(raw_text_data)

            template2 = open("show-env.textfsm")  # show env
            re_table2 = textfsm.TextFSM(template2)
            fsm_results2 = re_table2.ParseText(raw_text_data2)

            template3 = open("show-flash.textfsm")  # show flash
            re_table3 = textfsm.TextFSM(template3)
            fsm_results3 = re_table3.ParseText(raw_text_data3)

            template4 = open("show-memory-statistic.textfsm")  # show memory statistic
            re_table4 = textfsm.TextFSM(template4)
            fsm_results4 = re_table4.ParseText(raw_text_data4)

            template5 = open("show-process-cpu.textfsm")  # show process cpu
            re_table5 = textfsm.TextFSM(template5)
            fsm_results5 = re_table5.ParseText(raw_text_data5)

            outfile_name = open(nameFile + "-show-version.csv", "w+")  # show version
            outfile = outfile_name

            outfile_name2 = open(nameFile + "-show-env.csv", "w+")  # show env
            outfile2 = outfile_name2

            outfile_name3 = open(nameFile + "-show-flash.csv", "w+")  # show flash
            outfile3 = outfile_name3

            outfile_name4 = open(nameFile + "-show-memory-statistic.csv", "w+")  # show memory statistic
            outfile4 = outfile_name4

            outfile_name5 = open(nameFile + "-show-process-cpu.csv", "w+")  # show process cpu
            outfile5 = outfile_name5

            print(re_table.header)  # show version
            for s in re_table.header:
                outfile.write("%s;" % s)
            outfile.write("\n")

            counter = 0
            for row in fsm_results:  # show version
                print(row)
                for s in row:
                    outfile.write("%s;" % s)
                outfile.write("\n")
                counter += 1
            print("Write %d records" % counter)

            print(re_table2.header)  # show env
            for s in re_table2.header:
                outfile2.write("%s;" % s)
            outfile2.write("\n")

            counter = 0
            for row in fsm_results2:  # show env
                print(row)
                for s in row:
                    outfile2.write("%s;" % s)
                outfile2.write("\n")
                counter += 1
            print("Write %d records" % counter)

            print(re_table3.header)  # show flash
            for s in re_table3.header:
                outfile3.write("%s;" % s)
            outfile3.write("\n")

            counter = 0
            for row in fsm_results3:  # show flash
                print(row)
                for s in row:
                    outfile3.write("%s;" % s)
                outfile3.write("\n")
                counter += 1
            print("Write %d records" % counter)

            print(re_table4.header)  # show memory statistics
            for s in re_table4.header:
                outfile4.write("%s;" % s)
            outfile4.write("\n")

            counter = 0
            for row in fsm_results4:  # show memory statistics
                print(row)
                for s in row:
                    outfile4.write("%s;" % s)
                outfile4.write("\n")
                counter += 1
            print("Write %d records" % counter)

            print(re_table5.header)  # show process cpu
            for s in re_table5.header:
                outfile5.write("%s;" % s)
            outfile5.write("\n")

            counter = 0
            for row in fsm_results5:  # show process cpu
                print(row)
                for s in row:
                    outfile5.write("%s;" % s)
                outfile5.write("\n")
                counter += 1
            print("Write %d records" % counter)
        except IOError:
            print("Error: There Have File does not appear to exist.")
            QtGui.QMessageBox.question(self, 'Warning', "ERROR:Please check you're '.txt' file and TextFSM File.")


def run():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())


run()