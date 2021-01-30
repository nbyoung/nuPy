try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
import tmp
from _thread       import allocate_lock

from services import network
from services.microwebsrv2 import Service as MicroWebSrv2Service
from MicroWebSrv2 import MicroWebSrv2, WebRoute, GET, POST

import web

class WebServer(web.Server):

    #
    # Load the PyHTML module and define the static pages
    #

    pyhtmlMod = MicroWebSrv2.LoadModule('PyhtmlTemplate')
    pyhtmlMod.ShowDebug = True
    pyhtmlMod.SetGlobalVar('TestVar', 12345)

    @WebRoute(GET, '/test-redir')
    def RequestTestRedirect(microWebSrv2, request) :
        request.Response.ReturnRedirect('/test.pdf')

    @WebRoute(GET, '/test-post', name='TestPost1/2')
    def RequestTestPost(microWebSrv2, request) :
        content = """\
        <!DOCTYPE html>
        <html>
            <head>
                <title>POST 1/2</title>
            </head>
            <body>
                <h2>MicroWebSrv2 - POST 1/2</h2>
                User address: %s<br />
                <form action="/test-post" method="post">
                    First name: <input type="text" name="firstname"><br />
                    Last name:  <input type="text" name="lastname"><br />
                    <input type="submit" value="OK">
                </form>
            </body>
        </html>
        """ % request.UserAddress[0]
        request.Response.ReturnOk(content)

    @WebRoute(POST, '/test-post', name='TestPost2/2')
    def RequestTestPost(microWebSrv2, request) :
        data = request.GetPostedURLEncodedForm()
        try :
            firstname = data['firstname']
            lastname  = data['lastname']
        except :
            request.Response.ReturnBadRequest()
            return
        content   = """\
        <!DOCTYPE html>
        <html>
            <head>
                <title>POST 2/2</title>
            </head>
            <body>
                <h2>MicroWebSrv2 - POST 2/2</h2>
                Hello %s %s :)<br />
            </body>
        </html>
        """ % ( MicroWebSrv2.HTMLEscape(firstname),
                MicroWebSrv2.HTMLEscape(lastname) )
        request.Response.ReturnOk(content)

    #
    # Define the WebSockets server and handlers
    #

    def OnWebSocketAccepted(microWebSrv2, webSocket) :
        print('Example WebSocket accepted:')
        print('   - User   : %s:%s' % webSocket.Request.UserAddress)
        print('   - Path   : %s'    % webSocket.Request.Path)
        print('   - Origin : %s'    % webSocket.Request.Origin)
        if webSocket.Request.Path.lower() == '/wschat' :
            WebServer.WSJoinChat(webSocket)
        else :
            webSocket.OnTextMessage   = WebServer.OnWebSocketTextMsg
            webSocket.OnBinaryMessage = WebServer.OnWebSocketBinaryMsg
            webSocket.OnClosed        = WebServer.OnWebSocketClosed

    def OnWebSocketTextMsg(webSocket, msg) :
        print('WebSocket text message: %s' % msg)
        webSocket.SendTextMessage('Received "%s"' % msg)

    def OnWebSocketBinaryMsg(webSocket, msg) :
        print('WebSocket binary message: %s' % msg)

    def OnWebSocketClosed(webSocket) :
        print('WebSocket %s:%s closed' % webSocket.Request.UserAddress)

    _chatWebSockets = [ ]
    _chatLock = allocate_lock()

    def WSJoinChat(webSocket) :
        webSocket.OnTextMessage = WebServer.OnWSChatTextMsg
        webSocket.OnClosed      = WebServer.OnWSChatClosed
        addr = webSocket.Request.UserAddress
        with WebServer._chatLock :
            for ws in WebServer._chatWebSockets :
                ws.SendTextMessage('<%s:%s HAS JOINED THE CHAT>' % addr)
            WebServer._chatWebSockets.append(webSocket)
            webSocket.SendTextMessage('<WELCOME %s:%s>' % addr)

    def OnWSChatTextMsg(webSocket, msg) :
        addr = webSocket.Request.UserAddress
        with WebServer._chatLock :
            for ws in WebServer._chatWebSockets :
                ws.SendTextMessage('<%s:%s> %s' % (addr[0], addr[1], msg))

    def OnWSChatClosed(webSocket) :
        addr = webSocket.Request.UserAddress
        with WebServer._chatLock :
            if webSocket in WebServer._chatWebSockets :
                WebServer._chatWebSockets.remove(webSocket)
                for ws in WebServer._chatWebSockets :
                    ws.SendTextMessage('<%s:%s HAS LEFT THE CHAT>' % addr)

    #
    # Load the WebSockets module and assign the server
    #

    wsMod = MicroWebSrv2.LoadModule('WebSockets')
    wsMod.OnWebSocketAccepted = OnWebSocketAccepted

async def _amain(port):
    with tmp.Path('network.json') as networkPath:
        networkStatus = network.Status(networkPath)
        stopService, results = await service.Runner(
        ).add(
            network.Service(networkStatus)
        ).add(
            MicroWebSrv2Service(port=WebServer.port, root=WebServer.root)
        ).run()
        log.info('%s %s', stopService.__class__.__name__, results or '')

def main(port=80, level=logger.INFO):
    global log
    logger.set(level=level)
    log = logger.get('modbus')
    try:
        asyncio.run(_amain(port))
    except KeyboardInterrupt:
        pass

def debug():
    main(8000, level=logger.DEBUG)
    
#main()
debug()
