import os
import tempfile

class Path:

    def __init__(self, name):
        self._name = name

    def __enter__(self):
        self._path = tempfile.gettempdir() + os.sep + self._name
        return self._path

    def __exit__(self, *args):
        try:
            os.remove(self._path)
        except OSError:
            pass

    @property
    def name(self): return self._name
