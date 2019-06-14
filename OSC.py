import threading
from pythonosc import dispatcher, osc_server, osc_message_builder, udp_client


class OSCServer(threading.Thread):
    def __init__(self, owner, ip="127.0.0.1", outPort=8888):
        super(OSCServer, self).__init__()
        self.owner = owner
        self.port = outPort
        self.ip = ip
        self.server = None
        self.console = self.owner.view.window().new_file()
        self.console.window().run_command(
            "carry_file_to_pane", {"direction": "down"})
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/python_feedback", self.pythonCallback)
        self.dispatcher.map("/glsl_feedback", self.glslCallback)

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

    def pythonCallback(self, unused_addr, args):
        self.owner.view.window().run_command(
            "insert_jensaarai_console",
            {"text": '\n' + args}
        )

    def glslCallback(self, unused_addr, args):
        self.owner.view.window().run_command(
            "insert_jensaarai_console",
            {"text": '\n' + args}
        )


class OSCClient(threading.Thread):
    def __init__(self, owner, ip="127.0.0.1", inPort=7777):
        super(OSCClient, self).__init__()
        self.owner = owner
        self.ip = ip
        self.port = inPort
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
