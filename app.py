from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Static, Input
from textual.screen import Screen
from first_screen import FirstScreen

class MyApp(App):

    def on_mount(self) -> None:
        """Когда приложение запустится, показать первый экран."""
        self.push_screen(FirstScreen())

if __name__ == "__main__":
    app = MyApp()
    app.run()