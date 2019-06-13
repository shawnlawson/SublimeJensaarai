import threading
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
try:
    from tornado import speedups
except ImportError:
    speedups = None

# file:///Users/lawsos2/LiveCoding/Liveware/TD/codeOverlay/index.html


class WSHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def initialize(self, owner):
        self.owner = owner

    def check_origin(self, origin):
        return True

    def open(self):
        self.set_nodelay(True)
        self.connections.add(self)
        print ('new connection')

    def on_message(self, message):
        self.owner.make_init_msg()
        # print ('message received %s' % message)

    @classmethod
    def send_messages(cls, message):
        remove = set()
        for ws in cls.connections:
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                remove.add(ws)
            else:
                ws.write_message(message)
        for ws in remove:
            cls.connections.remove(ws)

    def on_close(self):
        print ('connection closed')


class WSServer(threading.Thread):
    def __init__(self, owner, ip="127.0.0.1", ioPort=5678):
        super(WSServer, self).__init__()
        self.owner = owner
        self.ip = ip
        self.port = ioPort
        self.server = None

    def run(self):
        app = tornado.web.Application(
            [(r'/', WSHandler, {'owner': self.owner})]
        )
        self.server = tornado.httpserver.HTTPServer(app)
        self.server.listen(self.port)
        print("started websocket server on " + self.ip + " " + str(self.port))
        # self.loop = tornado.ioloop.PeriodicCallback(
            # self.check_ten_seconds,
            # 1000, io_loop=tornado.ioloop.IOLoop.instance())
        tornado.ioloop.IOLoop.instance().start()

    def close(self):
        if self.server is not None:
            tornado.ioloop.IOLoop.instance().stop()
            self.server.stop()
            # self.server.close()
            # self.server = None
            print("tried to close wss server")

