class UpdateIndices(object):
    def __init__(self):
        self._start = None
        self._end = None
        self._observers = []

    @property
    def dragged_start(self):
        return self._start

    @property
    def dragged_end(self):
        return self._end

    @dragged_start.setter
    def dragged_start(self, value):
        self._start = value
        for callback in self._observers:
            callback(self._start, self._end)

    @dragged_end.setter
    def dragged_end(self, value):
        self._end = value
        for callback in self._observers:
            callback(self._start, self._end)

    def bind_to(self, callback):
        self._observers.append(callback)
