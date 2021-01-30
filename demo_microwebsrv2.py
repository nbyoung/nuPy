try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
import tmp

from services import network
from services.microwebsrv2 import Service as MicroWebSrv2Service
from MicroWebSrv2 import MicroWebSrv2, WebRoute, GET, POST

import web

class WebServer(web.Server):

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

class OperatingService(service.Service):

    def __init__(self, networkStatus, period=10.0):
        self._networkStatus = networkStatus
        self._period = period

    async def loop(self, stopCallback):
        async with self._networkStatus.setter as setter:
            isDHCP = setter.get('is_dhcp')
            isDHCP = not isDHCP
            setter.set('is_dhcp', isDHCP)
            log.info('DHCP' if isDHCP else 'Static')
        await asyncio.sleep(self._period)

async def _amain(port):
    with tmp.Path('network.json') as networkPath:
        networkStatus = network.Status(networkPath)
        stopService, results = await service.Runner(
        ).add(
            network.Service(networkStatus)
        ).add(
            MicroWebSrv2Service(port=WebServer.port, root=WebServer.root)
        ).add(
            OperatingService(networkStatus)
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
