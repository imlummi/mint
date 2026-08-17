from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Label, Input, Header
import socket
import threading
import getpass

winuser = getpass.getuser()
computer_name = socket.gethostname()

class ChatInput(Input):
    def on_mount(self) -> None:
        self.cursor_blink = True

class thething(App):
    CSS_PATH = 'useless.tcss'
    def __init__(self):
        super().__init__()
        self.setup_step = "ip"
        self.host = ''

    def compose(self):
        with Vertical():                            
            with Horizontal(classes='topbar'):
                yield Label('Mint', classes='topbar-left')
                yield Label(f"{winuser}@{computer_name}", classes='topbar-right')

            with Horizontal():
                with Vertical(classes='left'):
                    screen = Label("""                                                                                                       
[#1f5b40]             ::.             [/]
[#236245]           :##*+:            [/]
[#27694b]          .****+=            [/]
[#2b7051]   ....   =*##++=            [/]
[#2f7756] .==+++=-=:*-=**-..-+*+:     [/]
[#337e5c]  =+++++=##-.=++====+**=     [/]
[#378562]    :-=#%%=+%++=++-:-:=+*+*+.   [/]
[#3c8c68]  .+**++*%@@@@#*+++-=#++++++**. [/]
[#40936e]  +#*++-*##%*+%@@@%%****+====-: [/]
[#449b74]  -*++:-+##=-#@@@@%%%%%#.       [/]
[#48a27a]       :+#==. +*#%%#####+.      [/]
[#4da980]       .+++.     .+**###*:      [/]
[#51b186]        ..          ..---.      [/]
""", id='screen', classes='panel')
                    screen.border_title = "branding?"
                    yield screen

                    output = Label(f"""
connected to:{self.host}
""", id='output', classes='panel')
                    output.border_title = "status"
                    yield output
                    

                right = Vertical(classes='right panel')
                right.border_title = "chat"

                with right:
                    with Horizontal(classes='message-bar'):
                        yield ChatInput(placeholder='ip address', id='chatinput')

                    with VerticalScroll(id='ring'):
                        yield Label("")


    def on_input_submitted(self, event: Input.Submitted):
        value = event.input.value

        if self.setup_step == "ip":
            self.host = value
            self.setup_step = "username"

            event.input.value = ""
            event.input.placeholder = "username"

        elif self.setup_step == "username":
            self.username = value
            self.setup_step = "chat"

            event.input.value = ""
            event.input.placeholder = "type bro"

            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect((self.host, 55555))

            threading.Thread(
                target=self.receive_messages,
                daemon=True
            ).start()

            output = self.query_one('#output', Label)
            output.update(
            f'username: {self.username}\n\n\n\n\n'
            f'connected to: {self.host}'
            )

        elif self.setup_step == "chat":
            msg = value

            full_msg = f"<{self.username}> {msg}"

            ring = self.query_one("#ring", VerticalScroll)
            ring.mount(Label(full_msg))

            self.client.send(full_msg.encode("utf-8"))

            event.input.value = ""

    def receive_messages(self):
        while True:
            data = self.client.recv(1024)

            if not data:
                break

            message = data.decode("utf-8")
            self.call_from_thread(self.add_messages, message)

    def add_messages(self, message):
        ring = self.query_one("#ring", VerticalScroll)
        ring.mount(Label(message))

thething().run()