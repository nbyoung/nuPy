try:
    import uarray as array
    import uasyncio as asyncio
    import ujson as json
except ImportError:
    import array
    import asyncio
    import json

class StoreNotLoaded(Exception): pass
class StoreNotSaved(Exception): pass

class Store:
    def save(self): raise NotImplementedError
    def get(self, key): raise NotImplementedError
    def set(self, key, value): raise NotImplementedError


_DOT = '.'


class JSONStore(Store):

    def __init__(self, path=None, jsonString='', doReset=False):
        self._path = path
        self._json = jsonString
        if doReset:
            self._dump(json.loads(self._json))
        self._data = json.loads(self._json) if path is None else self._load()

    def _load(self):
        tryAgain = True
        while True:
            try:
                with open(self._path) as f:
                    return json.load(f)
            except OSError:
                if tryAgain:
                    self._dump(json.loads(self._json))
                    tryAgain = False
                else:
                    raise StoreNotLoaded(self._path)

    def _dump(self, data):
        if not self._path is None:
            try:
                with open(self._path, 'w') as f:
                    json.dump(data, f)
            except OSError:
                raise StoreNotSaved(self._path)

    def save(self):
        self._dump(self._data)

    def get(self, path):
        def get(dictionary, path):
            if -1 < path.find(_DOT):
                head, tail = path.split(_DOT, 1)
                return get(dictionary[head], tail)
            else:
                return dictionary[path]
        return get(self._data, path)

    def set(self, path, value):
        def set(dictionary, path, value):
            if -1 < path.find(_DOT):
                head, tail = path.split(_DOT, 1)
                set(dictionary[head], tail, value)
            else:
                dictionary[path] = value
        set(self._data, path, value)

    @property
    def jsonInitial(self): return self._json

    @property
    def json(self): return json.dumps(self._data)
        
    def updateJSON(self, jsonString):
        dirty = False
        def _updateData(toData, fromData):
            nonlocal dirty
            # warning: No tuples and no lists of objects
            for key in toData.keys():
                if key in fromData and type(fromData[key]) == type(toData[key]):
                    if isinstance(toData[key], dict):
                        _updateData(toData[key], fromData[key])
                    elif type(toData[key]) in (list, int, float, str, bool):
                        toData[key] = fromData[key]
                        dirty = True
                    else:
                        raise ValueError('Illegal type at %s' % key)
        _updateData(self._data, json.loads(jsonString))
        return dirty


class ArrayStore(Store):

    def __init__(self, typecode, iterable=()):
        self._array = array.array(typecode, iterable)

    def save(self): pass
    
    def get(self, key): return self._array[key]

    def set(self, key, value): self._array[key] = value

    @property
    def json(self):
        return '[ ' + ', '.join([json.dumps(v) for v in self._data]) + ' ]'


class StatusNotLockedError(Exception): pass

class Status:

    class OnSet:

        def __init__(self, callback=lambda argument: None, argument=None):
            self._callback = callback
            self._argument = argument

        def call(self): self._callback(self._argument)

    class _Getter:

        def __init__(self, status):
            self._status = status

        async def __aenter__(self):
            await self._status._lock.acquire()
            return self

        async def __aexit__(self, *args):
            self._status._lock.release()

        def get(self, key):
            return self._status._store.get(key)

        def getInitialJSON(self): return self._status._store.jsonInitial

        def getJSON(self): return self._status._store.json

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
                self._status._store.save()
                self._dirty = False
                self._status._event.set()
                self._status._onSet.call()
            await super().__aexit__(*args)

        def set(self, key, value):
            if self._status._event.is_set():
                raise StatusNotLockedError
            else:
                self._status._store.set(key, value)
                self._dirty = True

        def updateJSON(self, jsonString):
            if self._status._event.is_set():
                raise StatusNotLockedError
            else:
                self._dirty = self._status._store.updateJSON(jsonString)

    class _Watcher(_Setter):

        async def __aenter__(self):
            await self._status._event.wait()
            await super().__aenter__()
            return self

    def __init__(self, store, onSet=OnSet()):
        self._store = store
        self._onSet = onSet
        self._event = asyncio.Event()
        self._lock = asyncio.Lock()
        self._getter = Status._Getter(self)
        self._setter = Status._Setter(self)
        self._watcher = Status._Watcher(self)

    @property
    def event(self): return self._event

    @property
    def store(self): return self._store

    @property
    def getter(self): return self._getter

    @property
    def setter(self): return self._setter

    @property
    def watcher(self): return self._watcher
