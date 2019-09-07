import sublime
import sublime_plugin
from .jensaarai import Jensaarai

jensaarai = None


# Overall start/stop
class StartJensaaraiCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        jensaarai = Jensaarai.Jensaarai(self.view)


class StopJensaaraiCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            if jensaarai.recording is not None:
                jensaarai.recording.save()
            jensaarai.close()


# Websocket start/stop
class StartJensaaraiWebsocketCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.start_ws()


class StopJensaaraiWebsocketCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.stop_ws()


# OSC server start/stop
class StartJensaaraiOscServerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.start_osc_server()


class StopJensaaraiOscServerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.stop_osc_server()


# OSC client start/stop
class StartJensaaraiOscClientCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.start_osc_client()


class StopJensaaraiOscClientCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.stop_osc_client()


# Tidal Terminus start/stop
class StartJensaaraiTidalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.start_tidal()


class StopJensaaraiTidalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.stop_tidal()


# Recording start/stop/save/open
class StartJensaaraiRecordingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.start_recording()


class StopJensaaraiRecordingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.stop_recording()


class SaveJensaaraiRecordingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            if jensaarai.recording is not None:
                jensaarai.recording.save()


class CreateJensaaraiPlaybackCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.create_playback(self.view.file_name())
        # else kick open jensaarai? and do this?


class PlayJensaaraiPlaybackCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None and jensaarai.playback is not None:
            jensaarai.playback.play()


class StopJensaaraiPlaybackCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None and jensaarai.playback is not None:
            jensaarai.playback.stop()


class RewindJensaaraiPlaybackCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None and jensaarai.playback is not None:
            jensaarai.playback.rewind()


class JumpToJensaaraiPlaybackCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if jensaarai is not None and jensaarai.playback is not None:
            self.view.window().show_input_panel(
                'Jump to min sec of recording',
                '0 0',
                self.on_done,
                None,
                None,
            )

    def on_done(self, input):
        jensaarai.playback.jump_to(input)


# Handle shift/cmd+enter commands
class ExecuteJensaaraiCommand(sublime_plugin.TextCommand):
    def run(self, edit, scope="lines"):
        global jensaarai
        if jensaarai is not None:
            jensaarai.make_execute_msg(scope)


# Ask and send language to remote
class SendJensaaraiLanguageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.view.window().show_input_panel(
                'Send Language Syntax',
                'python',
                self.on_done,
                None,
                None,
            )

    def on_done(self, input):
        jensaarai.make_language_msg(input)


# Insert/Remove/Replace into jensaarai main view
class InsertJensaaraiMainCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, point):
        global jensaarai
        if jensaarai is not None:
            jensaarai.view.insert(edit, point, text)


class RemoveJensaaraiMainCommand(sublime_plugin.TextCommand):
    def run(self, edit, start, end):
        global jensaarai
        if jensaarai is not None:
            jensaarai.view.erase(
                edit,
                sublime.Region(start, start + end))


class ReplaceJensaaraiMainCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, region):
        global jensaarai
        if jensaarai is not None:
            jensaarai.view.replace(
                edit,
                sublime.Region(0, jensaarai.view.size()),
                text)


class MoveCursorJensaaraiMainCommand(sublime_plugin.TextCommand):
    def run(self, edit, start, end):
        global jensaarai
        if jensaarai is not None:
            jensaarai.view.sel().clear()
            jensaarai.view.sel().add(sublime.Region(start, end))


# Dump OSC server messages to console
class InsertJensaaraiConsoleCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        global jensaarai
        if jensaarai is not None and jensaarai.osc_server is not None:
            console = jensaarai.osc_server.console
            console.insert(edit, console.size(), text)
            console.sel().clear()
            console.sel().add(
                sublime.Region(console.size(), console.size()))
            console.show(console.sel())
            jensaarai.set_error_highlights(text)


# Dump recording into a file
class InsertJensaaraiRecordingCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        global jensaarai
        if jensaarai is not None:
            if jensaarai.recording is not None:
                jensaarai.recording.file.insert(edit, 0, text)


# Handlers for edits, cursor, and window close
class EditListener(sublime_plugin.EventListener):
    def on_modified_async(self, view):
        global jensaarai
        if jensaarai is not None:
            if jensaarai.view == view and jensaarai.playback is None:
                jensaarai.make_edits_msg()

    def on_selection_modified_async(self, view):
        global jensaarai
        if jensaarai is not None and jensaarai.playback is None:
            if jensaarai.view == view:
                jensaarai.make_cursors_msg()

    def on_close(self, view):
        global jensaarai
        if jensaarai is not None:
            if jensaarai.view == view:
                jensaarai.close()
                jensaarai = None

