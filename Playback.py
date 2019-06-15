import json
import threading
import time
import sublime


class Playback(object):

    def __init__(self, owner, view, filename):
        self.owner = owner
        self.view = view
        self.filename = filename
        self.data = None
        self.which_event = 0
        self.total_events = 0
        self.total_time = 0
        self.play_start = 0.0
        self.prev_time = 0.0
        self.timer = None
        # disable any auto stuff?
        self.open()

    def run(self):
        pass

    def open(self):
        self.data = None
        with open(self.filename, 'r') as f:
            self.data = json.load(f)
        self.owner.view.window().run_command(
            "replace_jensaarai_main",
            {"text": self.data["initial_text"], "region": None})
        self.owner.view.sel().clear()
        self.owner.view.sel().add(sublime.Region(0, 0))
        self.total_time = (self.data["local_end_time"] -
                           self.data["local_start_time"])
        self.total_events = len(self.data['action'])
        self.owner.view.window().focus_view(self.owner.view)

    def do_event(self, ignore):
        event = self.data['action'][self.which_event]

        if 'u' in event['type']:
            self.owner.view.window().run_command(
                "move_cursor_jensaarai_main",
                {"start": event['change']['start'],
                    "end": event['change']['end']})
        elif 'c' in event['type']:
            if 'insert' in event['action']:
                self.owner.view.window().run_command(
                    "insert_jensaarai_main",
                    {"text": event["text"],
                     "point": event['change']['start']})
            elif 'remove' in event['action']:
                self.owner.view.window().run_command(
                    "remove_jensaarai_main",
                    {"start": event['change']['start'],
                        "end": event['change']['end']})
        elif 'e' in event['type']:
            cursor = sublime.Region(event['change']['start'],
                                    event['change']['end'])
            self.owner.manage_messages('e', cursor=cursor, who=event['lang'])
            self.owner.start_exec_highlight([cursor])
        elif 'o' in event['type']:
            pass

        self.which_event += 1
        if not ignore:
            self.handle_event()

    def handle_event(self):
        event = self.data['action'][self.which_event]

        # behind on events
        while (self.which_event + 1 < self.total_events and
                self.play_start - time.time() + event['time'] < 0.0):
            self.do_event(True)
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
        if self.timer is not None and self.timer.isAlive():
            self.timer.cancel()

    def rewind(self):
        self.stop()
        self.which_event = 0
        self.play_start = 0.0
        self.prev_time = 0.0
        self.owner.view.window().run_command(
            "replace_jensaarai_main",
            {"text": self.data["initial_text"], "region": None})

    def destroy(self):
        self.stop()
