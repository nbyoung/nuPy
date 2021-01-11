import sys

if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
    import ujson as json
else:
    import asyncio
    import json

class StoreNotLoaded(Exception): pass
class StoreNotSaved(Exception): pass

class Store:

    def __init__(self, data={}):
        self._data = data

    def _dump(self): raise NotImplementedError


class JSONStore(Store):

    def __init__(self, path=None, jsonString='', doReset=False):
        self._path = path
        self._json = jsonString
        if doReset:
            self.__dump(json.loads(self._json))
        super().__init__(
            json.loads(self._json) if path is None else self._load()
        )

    def _load(self):
        tryAgain = True
        while True:
            try:
                with open(self._path) as f:
                    return json.load(f)
            except OSError:
                if tryAgain:
                    self.__dump(json.loads(self._json))
                    tryAgain = False
                else:
                    raise StoreNotLoaded(self._path)

    def __dump(self, data):
        if not self._path is None:
            try:
                with open(self._path, 'w') as f:
                    json.dump(data, f)
            except OSError:
                raise StoreNotSaved(self._path)

    def _dump(self):
        self.__dump(self._data)

_DOT = '.'

class StatusNotLockedError(Exception): pass

class Status:

    class _Getter:

        def __init__(self, status):
            self._status = status

        async def __aenter__(self):
            await self._status._lock.acquire()
            return self

        async def __aexit__(self, *args):
            self._status._lock.release()

        def get(self, path):
            def get(dictionary, path):
                if -1 < path.find(_DOT):
                    head, tail = path.split(_DOT, 1)
                    return get(dictionary[head], tail)
                else:
                    return dictionary[path]
            value = get(self._status._store._data, path)
            return value

    class _Setter(_Getter):

        def __init__(self, status):
            super().__init__(status)
            self._dirty = False

        async def __aenter__(self):
            await super().__aenter__()
            self._status._event.clear()
            return self

        async def __aexit__(self, *args):
            if self._dirty:
                self._status._store._dump()
                self._dirty = False
                self._status._event.set()
            await super().__aexit__(*args)

        def set(self, path, value):
            def set(dictionary, path, value):
                if -1 < path.find(_DOT):
                    head, tail = path.split(_DOT, 1)
                    set(dictionary[head], tail, value)
                else:
                    dictionary[path] = value
            if self._status._event.is_set():
                raise StatusNotLockedError
            else:
                set(self._status._store._data, path, value)
                self._dirty = True

    class _Watcher(_Setter):

        async def __aenter__(self):
            await self._status._event.wait()
            await super().__aenter__()
            return self

    def __init__(self, store):
        self._event = asyncio.Event()
        self._lock = asyncio.Lock()
        self._store = store
        self._getter = Status._Getter(self)
        self._setter = Status._Setter(self)
        self._watcher = Status._Watcher(self)

    @property
    def getter(self): return self._getter

    @property
    def setter(self): return self._setter

    @property
    def watcher(self): return self._watcher
