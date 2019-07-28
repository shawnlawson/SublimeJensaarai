import json
import time


class Recording(object):

    def __init__(self, owner, start_text):
        self.recording = []
        self.owner = owner
        self.start_text = start_text
        self.file = None

    def add(self, message):
        self.recording.append(message)

    def erase(self):
        self.recording = []

    def save(self):
        window = self.owner.view.window()
        self.file = window.new_file()
        window.set_view_index(self.file, 0, 0)
        window.focus_view(self.file)
        self.file.run_command(
            "insert_jensaarai_recording",
            {"text": json.dumps({
                "version": 5,
                "playback": 1,
                "editor_type": "sublime",
                "initial_text": self.start_text,
                "action": self.recording,
                "local_end_time": time.time(),
                "local_start_time": self.owner.start_time,
                "final_text": self.owner.get_buffer()
            },
                indent=True
            )
            }
        )
        window.run_command('prompt_save_as')
