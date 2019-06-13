import json
# from tkinter import *
import time
import threading


class Playback(threading.Thread):

    def __init__(self, owner):
        super(Playback, self).__init__()
        self.events = []
        self.owner = owner
        self.which_event = 0
        self.file = None

        # set recordings to none
        # disable any auto stuff?
        # self.open()

    def run(self):
        pass

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

    def open(self):
        #some sublime UI to choose file
        #parse file into self.events
        #set initial text

      #   it.lw_version = json_file['version']
      # it.lw_playback = (json_file['playback'] ? json_file['playback'] : 1)
      # it.lw_type = json_file['editor_type']
      # it.lw_finaltext = (json_file['finaltext'] ? json_file['finaltext'] : '')
      # it.lw_initialText = (json_file['initialtext'] ? json_file['initialtext'] : '')
      # it.setValue(it.lw_initialText)
      # it.lw_data_index = 0
      # it.lw_data = json_file['action']
      # it.lw_endTime = it.lw_data[it.lw_data.length - 1].t
      #build tk UI
      # w2 = Scale(master, from_=0, to=200,tickinterval=10, orient=HORIZONTAL)
      #   w2.set(23)
      # Button(master, text='Show', command=show_values).pack()

        pass

    def handleEvent(self):
        #see scheduleNextEventFunc and triggerPlayAceFunc
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def rewind(self):
        pass
