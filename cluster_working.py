from textual.app import App, ComposeResult
from textual import on
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Button, Static, ProgressBar, DataTable, Input
from textual.widget import Widget
from textual.screen import Screen
from textual.reactive import reactive
from art import text2art
import os.path
import pandas as pd
from art import text2art

class ClusterWorking(Screen):

    CSS_PATH = 'cluster_working.tcss'

    def compose(self):

        label = ''

        yield Container(
            Container(
                    Static(renderable=label, id='static_label'),
                    id='container_head',
                ),
            Container(
                Container(
                    DataTable(
                        id='datatable_df'
                    ),
                    id='container_table'
                ),
                Container(
                    id='container_work_input'
                ),
                Static(renderable='Файла не существует', id='static_error'),
                Container(
                        Input(placeholder = 'Введите команду', id='input_cmd'),
                        Button("Запуск", id='button_enter'),
                        id='container_cmd',
                    ),
                id='container_body',
            ),
            id='container_main',
        )


    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        df = pd.read_csv('name_cluster.csv', sep=',')
        
        table.add_columns(*df.columns)

        for _, row in df.iterrows():
            table.add_row(*[str(value) for value in row])

    
    @on(Button.Pressed, '#button_enter')
    def on_input_cmd_changed(self):
        client_cmd = self.query_one('#input_cmd', Input)
        static_error = self.query_one('#static_error', Static)
        df = pd.read_csv('name_cluster.csv', sep=',')

        self.remove_class('error')

        cmd = client_cmd.value.split(' ')

        # MERGE 1 <- 2
        if cmd[0] == 'MERGE':
            if cmd[2] == '<-':
                if cmd[1] not in df['cluster'].tolist():
                    self.add_class('error')
                    static_error.update(f'Кластер {cmd[1]} отсутствует')
                cluster_1 = cmd[1]
                cluster_2 = cmd[3]
            elif cmd[2] == '->':
                cluster_1 = cmd[3]
                cluster_2 = cmd[1]
            else:
                self.add_class('error')
                static_error.update('Ошибка определения слияния')

        elif cmd[0] == 'PLUS':
            ...
            





        

