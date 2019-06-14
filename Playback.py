import json
import threading
import time
import sublime


class Playback(threading.Thread):

    def __init__(self, owner, view):
        super(Playback, self).__init__()
        self.owner = owner
        self.view = view
        self.data = None
        self.which_event = 0
        self.total_events = 0
        self.total_time = 0
        self.play_start = 0.0
        self.timer = None
        # disable any auto stuff?
        self.open()

    def run(self):
        pass

    def open(self):
        # strData = self.view.substr(sublime.Region(0, self.view.size()))
        self.data = json.loads(
            self.view.substr(sublime.Region(0, self.view.size())))
        self.owner.view.window().run_command(
            "replace_jensaarai_main",
            {"text": self.data["initialtext"], "region": None})
        self.total_time = (self.data["local_end_time"] -
                           self.data["local_start_time"])
        self.total_events = len(self.data['action'])

    def do_event(self, ignore):
        event = self.data['action'][self.which_event]

        if event['type'] is 'u':
            # multiple cursors?
            pass
        elif event['type'] is 'c' and event['action'] is 'insert':
            self.owner.view.window().run_command(
                "insert_jensaarai_main",
                {
                    "text": event["text"],
                    "region": sublime.Region(
                        event['change']['start'],
                        event['change']['end'])
                })
        elif event['type'] is 'c' and event['action'] is 'remove':
            self.owner.view.window().run_command(
                "replace_jensaarai_main",
                {"region": sublime.Region(
                    event['change']['start'],
                    event['change']['end'])})
        elif event['type'] is 'e':
            pass
        elif event['type'] is 'o':
            pass

        if not ignore:
            self.handle_event()

    def handle_event(self):
        event = self.data['action'][self.which_event]

        # behind on events
        while (self.which_event + 1 < self.total_events and
                self.play_start - time.time() + event['time'] < 0):
            self.do_event(True)
            self.which_event += 1
            event = self.data['action'][self.which_event]

        # out of events
        if self.which_event + 1 >= self.total_events:
            self.stop()
        # or some remaining
        else:
            when = self.play_start - time.time() + event['time']
            self.timer = threading.Timer(when, self.do_event, [False])
            self.timer.start()

    def play(self):
        self.play_start = time.time()
        self.handle_event()

    def stop(self):
        if self.timer.isActive():
            self.timer.cancel()

    def rewind(self):
        self.stop()
        self.which_event = 0
        self.play_start = 0.0
        self.owner.view.window().run_command(
            "replace_jensaarai_main",
            {"text": self.data["initialtext"], "region": None})
