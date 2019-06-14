import sublime
import threading
import difflib
import copy
import json
import time
from . import Recording
from . import OSC
from . import WS
from . import Tidal


class Jensaarai(threading.Thread):

    def __init__(self, view):
        super(Jensaarai, self).__init__()
        self.view = view
        self.shadow = self.get_buffer()
        self.start_time = time.time()
        self.settings = sublime.load_settings("Jensaarai.sublime-settings")
        self.glslTimer = threading.Timer(.250, self.auto_glsl)
        self.glslTag = None
        self.ws_server = None
        self.osc_server = None
        self.osc_client = None
        self.tidal = None
        self.recording = None
        if self.settings.get("enable_recording"):
            self.start_recording()
        if self.settings.get("osc_touch_designer_enable"):
            self.start_osc_client()
        if self.settings.get("osc_server_enable"):
            self.start_osc_server()
        if self.settings.get("websocket"):
            self.start_ws()
        if self.settings.get("terminus_tidal"):
            self.start_tidal()
        self.start()

    def run(self):
        pass

    def make_init_msg(self):
        # special case
        if self.ws_server is not None:
            WS.WSHandler.send_messages(
                json.dumps({'type': 'i', 'raw': self.get_buffer()}))

    def make_edits_msg(self):
        new_buffer = self.get_buffer()

        if self.glslTimer.isAlive():
            self.glslTimer.cancel()

        diffs = difflib.SequenceMatcher(None, self.shadow, new_buffer)
        for tag, i1, i2, j1, j2 in diffs.get_opcodes():
            if tag is "delete":
                self.manage_messages(
                    'c',
                    sublime.Region(j1, i2 - i1),
                    action='remove',
                    text=self.shadow[i1:i2])

            elif tag is "insert":
                self.manage_messages(
                    'c',
                    sublime.Region(j1, j2),
                    action='insert',
                    text=new_buffer[j1:j2])

        self.shadow = new_buffer
        if self.osc_client is not None:
            self.glslTimer = threading.Timer(.250, self.auto_glsl)
            self.glslTimer.start()

    def make_cursors_msg(self):
        for cursor in self.view.sel():
            self.manage_messages('u', cursor)

    def make_execute_msg(self, scope):
        cursors = []
        text = ""

        # copy cursors so that we can replace later
        for c in self.view.sel():
            cursors.append(copy.deepcopy(c))

        # This chuck creates single unified cursor selection
        if scope == "lines":
            text = self.get_selected_lines()
        elif scope == "block":
            text = self.get_selected_blocks()
        elif scope == "all":
            pass

        cursor = self.view.sel()[0]
        loc = self.view.rowcol(cursor.begin())
        start = loc[0]
        lines = self.get_buffer().splitlines(True)
        length = len(lines)
        if start == length:
            start -= 1
        who, where = self.get_language(lines, start)

        self.start_exec_highlight(self.view.sel())

        self.manage_messages('e', cursor, text=text, who=who)

        # replace current cursors
        self.view.sel().clear()
        for cursor in cursors:
            self.view.sel().add(cursor)

    def make_language_msg(self, lang):
        self.manage_messages('l', self.view.sel()[0], who=lang)

    def manage_messages(self, type, cursor, text='', action='', who=''):
        msg = {
            'type': type,
            'time': time.time() - self.start_time,
            'action': action,
            'change': {
                'start': cursor.a,
                'end': cursor.b
            },
            'reverse': 'false' if cursor.a <= cursor.b else 'true',
            'lang': who
        }
        if self.recording is not None:
            self.recording.add(msg)
        if self.ws_server is not None:
            WS.WSHandler.send_messages(json.dumps(msg))
        if self.osc_client is not None:
            if who is 'python' or who is 'glsl':
                self.osc_client.send("/" + who, text)
        if self.tidal is not None and who is 'tidal':
            self.tidal.send(text)
        # if firebase

    def auto_glsl(self):
        lines = self.get_buffer().splitlines(True)
        for cursor in self.view.sel():
            loc = self.view.rowcol(cursor.begin())
            start = end = loc[0]
            length = len(lines)
            if start == length:
                start -= 1
                end -= 1
            who, self.glslTag = self.get_language(lines, start)

        if who == 'glsl':
            while end + 1 <= length:
                if ('//glsl' in lines[end] or
                        '//python' in lines[end] or
                        '//tidal' in lines[end]):
                    break
                else:
                    end += 1

            self.manage_messages(
                '',
                self.view.sel()[0],
                who=who,
                text=''.join(lines[self.glslTag + 1: end]))

    def set_error_highlights(self, errors):
        self.view.erase_regions("glslError")
        errorLines = errors.splitlines()
        for err in errorLines:
            parts = err.split(':')
            pLen = len(parts)
            if pLen is 4 or pLen is 6:
                p = self.view.text_point(int(parts[2]) + self.glslTag - 50, 0)
                self.view.add_regions(
                    'glslError',
                    [self.view.full_line(p)],
                    'selection',
                    '',
                    sublime.DRAW_STIPPLED_UNDERLINE |
                    sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL
                )

    def patch_view(self, edit, patch):
        pass

    def start_exec_highlight(self, where):
        self.view.add_regions(
            'jensaarai',             # region name
            where,                   # region
            'selection',             # color scope name
            '',                      # gutton icon
            sublime.DRAW_NO_OUTLINE  # outline
        )
        sublime.set_timeout(lambda: self.view.erase_regions("jensaarai"), 300)

    def get_selected_blocks(self):
        parts = []
        self.view.run_command("expand_selection_to_paragraph")
        for sel in self.view.sel():
            for line in self.view.lines(sel):
                parts.append(self.view.substr(line))
        return "\n".join(parts)

    def get_selected_lines(self):
        parts = []
        for sel in self.view.sel():
            self.view.sel().add(self.view.full_line(sel))
        for sel in self.view.sel():
            for line in self.view.lines(sel):
                parts.append(self.view.substr(line))
        return "\n".join(parts)

    def get_language(self, lines, start):
        while start >= 0:
            if '//glsl' in lines[start]:
                return 'glsl', start
            elif '//python' in lines[start]:
                return 'python', start
            elif '//tidal' in lines[start]:
                return 'tidal', start
            else:
                start -= 1
        return None, start

    def get_buffer(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def start_ws(self):
        if self.ws_server is None:
            self.ws_server = WS.WSServer(self)
            self.ws_server.start()

    def stop_ws(self):
        if self.ws_server is not None:
            self.ws_server.close()
            self.ws_server = None

    def start_osc_server(self):
        if self.osc_server is None:
            self.osc_server = OSC.OSCServer(self)
            self.osc_server.start()

    def stop_osc_server(self):
        if self.osc_server is not None:
            self.osc_server.close()
            self.osc_server = None

    def start_osc_client(self):
        if self.osc_client is None:
            self.osc_client = OSC.OSCClient(self)
            self.osc_client.start()
            self.glslTimer.start()

    def stop_osc_client(self):
        if self.osc_client is not None:
            self.osc_client.close()
            self.osc_client = None

    def start_tidal(self):
        if self.tidal is None:
            self.tidal = Tidal.Tidal(self)

    def stop_tidal(self):
        if self.tidal is not None:
            self.tidal.close()
            self.tidal = None

    def start_recording(self):
        if self.recording is None:
            self.recording = Recording.Recording(self, self.get_buffer())

    def stop_recording(self):
        if self.recording is not None:
            self.recording.erase()
            self.recording = None

    def close(self):
        self.stop_recording()
        self.stop_osc_client()
        self.stop_osc_server()
        self.stop_ws()
        self.stop_tidal()
