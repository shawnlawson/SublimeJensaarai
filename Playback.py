import json
import threading
import time
import math
import sublime


class Playback(object):

    def __init__(self, owner, view, filename):
        self.owner = owner
        self.view = view
        self.filename = filename
        self.data = None
        self.which_event = 0
        self.total_events = 0
        self.total_time = 0.0
        self.play_start = 0.0
        self.prev_time = 0.0
        self.timer = None
        self.status_timer = None
        self.open()

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
            self.owner.recv_local_cursor(event)
        elif 'c' in event['type']:
            self.owner.recv_changes(event)
        elif 'e' in event['type']:
            self.owner.recv_executes(event)
        elif 'o' in event['type']:
            self.owner.recv_remote_cursor(event)

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
        self.status_timer = threading.Timer(1.0, self.status_update)
        self.status_timer.start()
        self.handle_event()

    def stop(self):
        if self.timer is not None and self.timer.isAlive():
            self.timer.cancel()
        if self.status_timer is not None and self.status_timer.isAlive():
            self.status_timer.cancel()

    def rewind(self):
        self.stop()
        self.which_event = 0
        self.play_start = 0.0
        self.prev_time = 0.0
        self.owner.view.window().run_command(
            "replace_jensaarai_main",
            {"text": self.data["initial_text"], "region": None})

    def status_update(self):
        self.owner.view.erase_status('playback')
        play_head = time.time() - self.play_start
        status = (str(math.floor(play_head / 60)) + ":" +
                  str(math.floor(play_head % 60)) + "\t")
        status += (str(math.floor(self.total_time / 60)) + ":" +
                   str(math.floor(self.total_time % 60)) + "\t")
        self.owner.view.set_status('playback', status)
        self.status_timer = threading.Timer(1.0, self.status_update)
        self.status_timer.start()

    def destroy(self):
        self.owner.view.erase_status('playback')
        self.stop()
