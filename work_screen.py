from textual.app import App, ComposeResult
from textual import on
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Button, Static, Input, OptionList, Select, Checkbox, RadioButton, RadioSet
from textual.screen import Screen
from textual.reactive import reactive
from art import text2art
import os.path
import pandas as pd
import json


class WorkScreen(Screen):

    def __init__(self, mode, input_dataframe, input_column, input_api_key, input_algoritm, optionlist_embedding):
        self.mode = mode
        self.input_dataframe = input_dataframe
        self.input_column = input_column
        self.input_api_key = input_api_key
        self.input_algoritm = input_algoritm
        self.optionlist_embedding = optionlist_embedding

    CSS_PATH = 'work_screen.tcss'

    def compose(self):

        label = ''

        yield Container(
            Container(
                    Static(renderable=label, id='static_label'),
                    id='container_head',
                ),

            Container(
                Container(
                    Static(renderable='INFO', id='static_info'),
                    Static(renderable='Ожидание процесса', id='static_state'),
                    Static(renderable='Process', id='static_process'),
                    Static(renderable='Log', id='static_log'),
                    id='container_process',
                ),
                Container(
                        Button('Запуск следующего этапа', id='butt'),
                        id='container_b',
                    ),
                id='container_body',
            ),
            id='container_main',
        )



    def state_embedding(self, static_process, static_log):
        optionlist_embedding = self.query_one('#optionlist_embedding', RadioButton)
        info = self.query_one('#info', Static)
        info.update(f'{optionlist_embedding.value}')


        

    @on(Button.Pressed, '#butt')
    def on_pressed_butt(self):
        static_state = self.query_one('#static_state', Static)
        static_process = self.query_one('#static_process', Static)
        static_log = self.query_one('#static_log', Static)
        info = self.query_one('#static_info', Static)
        
        info.update(f'{self.input_dataframe}')
        butt = self.query_one('#butt', Button)

        if static_state.renderable == 'Ожидание процесса':
            info.update(f'')
            self.state_embedding(static_process, static_log)