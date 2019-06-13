import threading
import sublime


class Tidal(object):
    def __init__(self, owner):
        self.owner = owner
        sublime.active_window().run_command(
            "terminus_open", {
                "cmd": [
                    "zsh",
                    "-i",
                    "-l",
                    "/Users/lawsos2/.ghcup/bin/ghci",
                    "-XOverloadedStrings",
                    "-ghci-script",
                    "$packages/Jensaarai/BootTidal.hs"
                ],
                "cwd": "$file",
                "title": "jensaarai tidal",
                "tag": "tidal_session",
                "post_window_hooks": [
                    ["carry_file_to_pane", {"direction": "down"}],
                    ["travel_to_pane", {"direction": "up"}]
                ],
                "auto_close": False
            }
        )

    def send(self, text):
        self.owner.view.window().run_command(
            "terminus_send_string",
            {
                "string": self.sanitize(text) + '\n',
                "tag": "tidal_session"
            }
        )

    def sanitize(self, text):
        return text.replace("\n", " ").replace("\t", " ")

    def close(self):
        self.owner.view.window().run_command("terminus_close_all")
        self.owner.view.window().run_command(
            "destroy_pane", {"direction": "down"})
        self.owner.view.window().focus_view(self.owner.view)
