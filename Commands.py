import sublime
import sublime_plugin
from . import Jensaarai

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


class OpenJensaaraiRecordingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global jensaarai
        if jensaarai is not None:
            jensaarai.view.window().run_command("prompt_open")


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


# Dump OSC server messages to console
class InsertJensaaraiConsoleCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
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
            if jensaarai.view == view:
                jensaarai.make_edits_msg()

    def on_selection_modified_async(self, view):
        global jensaarai
        if jensaarai is not None:
            if jensaarai.view == view:
                jensaarai.make_cursors_msg()

    def on_close(self, view):
        global jensaarai
        if jensaarai is not None:
            if jensaarai.view == view:
                jensaarai.close()
                jensaarai = None
