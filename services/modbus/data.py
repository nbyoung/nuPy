from configuration import ArrayStore, Status
from . import _data

class Model(_data.Model):

    def __init__(self, iterable):
        super().__init__(holdingCount=len(iterable))
        self._status = Status(ArrayStore('H', iterable))

    @property
    def status(self): return self._status

    @property
    def status(self):
        return self._status

    def holdingRead(self, getter, address):
        return getter.get(address)

    def holdingWrite(self, setter, address, value):
        setter.set(address, value)
        return setter.get(address)
    
