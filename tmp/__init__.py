import os

class Path:

    def __init__(self, name):
        self._name = name

    def __enter__(self):
        try:
            tempdir = os.getcwd() + os.sep
        except AttributeError:
            tempdir = (os.getenv('PWD') or '/flash') + '/'  # ports/unix
            try:
                os.mkdir(tempdir)
            except OSError:
                pass
        self._path = tempdir + self._name
        return self._path

    def __exit__(self, *args):
        try:
            os.remove(self._path)
        except OSError:
            pass

    @property
    def name(self): return self._name
