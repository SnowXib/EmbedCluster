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
    from art import text2art
    #print(text2art(">>EmbedCluster>>", font='bulbhead'))
    #print(text2art(">>EmbedCluster>>", font='block'))
    #print(text2art(">>EmbedCluster>>", font='banner'))
    #print(text2art(">>EmbedCluster>>", font='bubble'))
    #print(text2art(">>EmbedCluster>>", font='doh'))
    #print(text2art(">>EmbedCluster>>", font='digital'))
    #print(text2art(">>EmbedCluster>>", font='dot'))
    #print(text2art(">>EmbedCluster>>", font='script'))
    print(text2art(">>EmbedCluster>>", font='slant'))
    print(text2art(">>EmbedCluster>>", font='small'))
    print(text2art(">>EmbedCluster>>", font='standard'))
    print(text2art(">>EmbedCluster>>", font='bulbhead'))
    print(text2art(">>EmbedCluster>>", font='letters'))
    print(text2art(">>EmbedCluster>>", font='cyberlarge'))
    print(text2art(">>EmbedCluster>>", font='ghost'))
    print(text2art(">>EmbedCluster>>", font='hscript'))
    print(text2art(">>EmbedCluster>>", font='slant'))
    print(text2art(">>EmbedCluster>>", font='ascii'))
    print(text2art(">>EmbedCluster>>", font='char1'))
    print(text2art(">>EmbedCluster>>", font='3d'))
    print(text2art(">>EmbedCluster>>", font='starwars'))
    #print(text2art(">>EmbedCluster>>", font='rectangles'))

    app = MyApp()
    app.run()