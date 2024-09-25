from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Static, Input
from textual.screen import Screen
from art import text2art
from info_screen import InfoScreen


class FirstScreen(Screen):

    CSS_PATH = "first_screen.tcss"

    def compose(self) -> ComposeResult:
        logo = text2art(">>EmbedCluster>>", font='slant')
        yield Container(
            Static(renderable = logo, id='static_logo'),
            Container(
                Static(renderable = 'Простое в использовании приложение для создания эмбеддингов и кластеризации данных. Помогает анализировать и находить связи в ваших данных с помощью AI.', id='static_info'),
                Button("Перейти к обучению", id='button_start_work'),
                id='container_start',
            ),
            id='container_first',
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Обработчик нажатия на кнопку."""
        if event.button.id == "button_start_work":
            self.app.push_screen(InfoScreen())
            



