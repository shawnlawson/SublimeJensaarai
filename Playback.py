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
        self.elapsed_time = 0.0
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
        # behind on events
        while self.which_event < self.total_events:
            event_time = self.data['action'][self.which_event]['time']
            if self.play_start - time.time() + event_time < 0.0:
                self.do_event(True)
            else:
                break

        # out of events, split to not trigger new more events
        if self.which_event >= self.total_events:
            # and out of time
            if self.elapsed_time >= self.total_time:
                self.stop()
        else:
            event_time = self.data['action'][self.which_event]['time']
            when = self.play_start - time.time() + event_time
            self.timer = threading.Timer(when, self.do_event, [False])
            self.timer.start()

    def play(self):
        self.play_start = time.time() - self.elapsed_time
        self.status_timer = threading.Timer(1.0, self.status_update)
        self.status_timer.start()
        self.handle_event()

    def stop(self):
        if self.timer is not None and self.timer.isAlive():
            self.timer.cancel()
        if self.status_timer is not None and self.status_timer.isAlive():
            self.status_timer.cancel()
        self.elapsed_time = time.time() - self.play_start

    def rewind(self):
        self.stop()
        self.which_event = 0
        self.play_start = 0.0
        self.elapsed_time = 0.0
        self.owner.view.window().run_command(
            "replace_jensaarai_main",
            {"text": self.data["initial_text"], "region": None})

    def jump_to(self, input):
        parts = input.split()
        if len(parts) > 2:
            print("Too many numbers. Use:# #")
            return

        time_jump = 0
        if len(parts) > 1:
            min = int(parts[0])
            sec = int(parts[1])
            time_jump = min * 60 + sec
        elif len(parts) == 1:
            time_jump = int(parts[0])
        else:
            print("Not time specified")
            return

        if time_jump < 0 or time_jump > self.total_time:
            print("Time not valid, either too big or too small")
            return

        self.elapsed_time = time_jump
        self.play_start = time.time() - self.elapsed_time

    def status_update(self):
        self.owner.view.erase_status('playback')
        self.elapsed_time = time.time() - self.play_start
        percent_done = self.elapsed_time / self.total_time
        status = '['
        status += ' ' * math.floor(percent_done * 50)
        status += '|'
        status += ' ' * math.floor((1.0 - percent_done) * 50)
        status += ']\t'
        status += (str(math.floor(self.elapsed_time / 60)) + ":" +
                   str(math.floor(self.elapsed_time % 60)) + "\t")
        status += (str(math.floor(self.total_time / 60)) + ":" +
                   str(math.floor(self.total_time % 60)) + "\t")
        self.owner.view.set_status('playback', status)
        self.status_timer = threading.Timer(0.25, self.status_update)
        self.status_timer.start()

    def destroy(self):
        self.owner.view.erase_status('playback')
        self.stop()
