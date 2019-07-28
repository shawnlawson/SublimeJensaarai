import threading
import json
from .deps.pythonosc import dispatcher, osc_server
from .deps.pythonosc import osc_message_builder, udp_client


class OSCServer(threading.Thread):
    def __init__(self, owner, ip="127.0.0.1", inPort=8888):
        super(OSCServer, self).__init__()
        self.owner = owner
        self.port = inPort
        self.ip = ip
        self.server = None
        self.console = self.owner.view.window().new_file()
        self.console.window().run_command(
            "carry_file_to_pane", {"direction": "down"})
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/python_feedback", self.python_callback)
        self.dispatcher.map("/glsl_feedback", self.glsl_callback)
        self.dispatcher.map("/tidal_rewrite", self.tidal_rewrite_callback)

    def run(self):
        self.server = osc_server.ThreadingOSCUDPServer(
            (self.ip, self.port),
            self.dispatcher
        )
        self.owner.view.window().run_command(
            "travel_to_pane", {"direction": "up"})
        self.owner.view.window().focus_view(self.owner.view)
        print("Started OSCServer {}".format(self.server.server_address))
        self.server.serve_forever()

    def close(self):
        if self.console is not None:
            self.console.window().focus_view(self.console)
            self.console.window().run_command('close_file')
            self.owner.view.window().focus_view(self.owner.view)
            self.owner.view.window().run_command(
                "destroy_pane", {"direction": "down"})
        if self.server is not None:
            self.server.shutdown()
            self.server = None
            print("closed osc server")

    def python_callback(self, unused_addr, args):
        self.owner.view.window().run_command(
            "insert_jensaarai_console",
            {"text": '\n' + args}
        )

    def glsl_callback(self, unused_addr, args):
        self.owner.view.window().run_command(
            "insert_jensaarai_console",
            {"text": '\n' + args}
        )

    def tidal_rewrite_callback(self, unused_addr, args):
        event = json.loads(args)

        if 'u' in event['type']:
            self.owner.recv_local_cursor(event)
        elif 'c' in event['type']:
            self.owner.recv_changes(event)
        elif 'e' in event['type']:
            self.owner.recv_executes(event)
        elif 'o' in event['type']:
            self.owner.recv_remote_cursor(event)


class OSCClient(threading.Thread):
    def __init__(self, owner, ip="127.0.0.1", outPort=7777):
        super(OSCClient, self).__init__()
        self.owner = owner
        self.ip = ip
        self.port = outPort
        self.client = None

    def run(self):
        self.client = udp_client.UDPClient(self.ip, self.port)
        print("Started OSCClient " + self.ip + " " + str(self.port))

    def close(self):
        if self.client is not None:
            self.client._sock.close()
            self.client = None
            print("closed osc client")

    def send(self, addr, message):
        msg = osc_message_builder.OscMessageBuilder(address=addr)
        msg.add_arg(message, arg_type="s")
        msg = msg.build()
        self.client.send(msg)
