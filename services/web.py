from collections import namedtuple
import _thread

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from configuration import Status
import service

from MicroWebSrv2 import MicroWebSrv2, RegisterRoute

class HTTP:
    GET     = 'GET'
    HEAD    = 'HEAD'
    POST    = 'POST'
    PUT     = 'PUT'
    DELETE  = 'DELETE'
    OPTIONS = 'OPTIONS'
    PATCH   = 'PATCH'

Route = namedtuple('Route', ('name', 'method', 'path', 'callback', 'data'))

class API:

    class _Endpoint:

        def __init__(self, name, path, status, isWritable):
            self._name = name
            self._status = status
            method = HTTP.GET
            RegisterRoute(self._get, method, path, name + method)
            if isWritable:
                method = HTTP.POST
                RegisterRoute(self._post, method, path, name + method)

        def _get(self, mws2, request):
            async def sendJSON():
                async with self._status.getter as getter:
                    request.Response.ContentType = 'application/json'
                    request.Response.ReturnOk(getter.getJSON())
            asyncio.run(sendJSON())

        def _post(self, mws2, request):
            async def receiveJSON():
                async with self._status.setter as setter:
                    respond = request.Response.ReturnBadRequest
                    if request.ContentType.lower() == 'application/json' :
                        try:
                            jsonString = bytes(request.Content).decode('UTF-8')
                            setter.updateJSON(jsonString)
                            respond = request.Response.ReturnOk
                        except Exception as exception:
                            pass
                    respond()
            asyncio.run(receiveJSON())

    _webSocketModule = MicroWebSrv2.LoadModule('WebSockets')

    def __init__(self, basePath):
        self._basePath = basePath
        self._webSocketClients = []
        self._webSocketClientsLock = _thread.allocate_lock()
        def onWebSocketTextMessage(webSocket, textMessage):
            pass
        def onWebSocketBinaryMessage(webSocket, binaryMessage):
            pass
        def onWebSocketClosed(webSocket):
            with self._webSocketClientsLock:
                if webSocket in self._webSocketClients:
                    self._webSocketClients.remove(webSocket)
        def onWebSocketAccepted(mws2, webSocket):
            with self._webSocketClientsLock:
                self._webSocketClients.append(webSocket)
            webSocket.OnTextMessage = onWebSocketTextMessage
            webSocket.OnBinaryMessage = onWebSocketBinaryMessage
            webSocket.OnClosed = onWebSocketClosed
        API._webSocketModule.OnWebSocketAccepted = onWebSocketAccepted

    def _notifyClients(self, name):
        with self._webSocketClientsLock:
            for client in self._webSocketClients:
                client.SendTextMessage(name)

    def _close(self):
        with self._webSocketClientsLock:
            for client in self._webSocketClients:
                client.Close()

    def add(self, name, jsonStore, isWritable=True):
        path = '%s/%s' % (self._basePath, name)
        status = Status(jsonStore, onSet=Status.OnSet(self._notifyClients, name))
        endpoint = API._Endpoint(name, path, status, isWritable)
        return status

_service = None

class ServiceError(OSError): pass

class Service(service.Service):

    # TODO serverStatus: client address, bytes received

    def __init__(self, root='/flash/www', routeList=(), api=API('/api'), port=80):
        self._api = api
        for r in routeList:
            RegisterRoute(
                lambda mws2, request: r.callback(request, r.data),
                r.method, r.path, r.name,
            )
        self._mws2 = MicroWebSrv2()
        self._mws2.BindAddress = ('0.0.0.0', port)
        self._mws2.SetEmbeddedConfig()
        self._mws2.RootPath = root
        HOME = '/'
        if not self._mws2.ResolvePhysicalPath(HOME):
            raise MicroWebSrv2Exception(
                "RootPath '%s' does not resolve with URL '%s'"
                % (self._mws2.RootPath, HOME)
            )
        self._mws2.NotFoundURL = HOME
        self._mws2.StartManaged()

    @property
    def microwebsrv2(self): return self._mws2
    
    async def loop(self, stopCallback):
        if not self._mws2.IsRunning: stopCallback()
        await asyncio.sleep(1)

    async def onStop(self):
        self._api._close()
        self._mws2.Stop()
