from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(float)
    error = QtCore.pyqtSignal(tuple)


class Worker(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
        except Exception as err:
            self.signals.error.emit(('Something went wrong', err))
            return
        else:
            self.signals.result.emit(result)

        self.signals.finished.emit()
