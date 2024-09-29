from textual.app import App, ComposeResult
from textual import on
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Button, Static, ProgressBar
from textual.screen import Screen
from textual.reactive import reactive
from art import text2art
import os.path
import pandas as pd
import json
import openai


class WorkScreen(Screen):

    CSS_PATH = 'work_screen.tcss'

    def __init__(self, mode, input_dataframe, input_column, input_api_key, input_algoritm, optionlist_embedding):
        super().__init__()
        self.mode = mode
        self.input_dataframe = input_dataframe
        self.input_column = input_column
        self.input_api_key = input_api_key
        self.input_algoritm = input_algoritm
        self.optionlist_embedding = optionlist_embedding
        self.client_log = [f'Обработка DataFrame {self.input_dataframe}\n| - ID - | - Text - |\n']


    def compose(self):

        label = ''

        yield Container(
            Container(
                    Static(renderable=label, id='static_label'),
                    id='container_head',
                ),

            Container(
                Container(
                    Container(
                        Static(renderable='Ожидание процесса', id='static_state'),
                        ProgressBar(total=100, id='progress_bar'),
                        Static(renderable='INFO', id='static_info'),
                        id='container_info'
                    ),
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


    def get_embedding(self, text, model):
        """API для получения эмбеддингов текста с помощью ChatGPT с обработкой ошибок"""

        text = text.replace("\n", " ")

        info = self.query_one('#static_info', Static)
        api_key = self.input_api_key

        try:
            client = openai(
                api_key=str(api_key),
                base_url="https://api.proxyapi.ru/openai/v1"
            )

            response = client.embeddings.create(input=[text], model=model)

            embedding = response.data[0].embedding
            return embedding

        except error.AuthenticationError as e:
            info.update('Ошибка аутентификации')
            print(f"Ошибка аутентификации: {e}")
            return None

        except error.RateLimitError as e:
            info.update('Превышен лимит запросов')
            print(f"Превышен лимит запросов: {e}")
            return None

        except error.OpenAIError as e:
            info.update('Ошибка API OpenAI')
            print(f"Ошибка API OpenAI: {e}")
            return None

        except Exception as e:
            info.update('Произошла непредвиденная ошибка')
            print(f"Произошла непредвиденная ошибка: {e}")
            return None


    def logging(self, id_log, log):

        static_log = self.query_one('#static_log', Static)
        progressbar = self.query_one('#progress_bar', ProgressBar)

        progressbar.update(progress=id_log)

        if len(self.client_log) > 30:
            self.client_log = [f'Обработка DataFrame {self.input_dataframe}\n| - ID - | - Text - |\n']

        id_log = ' ' + str(id_log)
        while len(id_log) < 8:
            id_log += ' '
        log = '\n' + id_log + log[:30] + '...'
        self.client_log.extend([log])

        static_log.renderable = str(self.client_log)




    def state_embedding(self):
        mode = self.mode
        df_path = self.input_dataframe
        model = self.optionlist_embedding
        progressbar = self.query_one('#progress_bar', ProgressBar)

        if mode == ('checkbox_cluster' or 'checkbox_embed'):
            return None
        
        if '&' in df_path:
            df_path.split('&')
            df = df_path[0] 
            sep = df_path[1]
        else:
            df = df_path
            sep = ';'
        
        if df_path.endswith('.xlsx'):
            df = pd.read_excel(df_path, sheet_name=0, nrows=10)
        elif df_path.endswith('.csv'):
            df = pd.read_csv(df_path, sep=sep, nrows=10)

        progressbar.total = len(df)

        new_file_name = df_path.split('.')[0] + '_embedding' +'.csv'

        df['ada_embedding'] = df.apply(lambda row: self.logging(row['id'], row['text']) or self.get_embedding(row['text'], model), axis=1)
        df.to_csv(f'{new_file_name}', index=False)


    @on(Button.Pressed, '#butt')
    def on_pressed_butt(self):
        static_state = self.query_one('#static_state', Static)
        info = self.query_one('#static_info', Static)
        butt = self.query_one('#butt', Button)

        if str(static_state.renderable) == 'Ожидание процесса':
            self.state_embedding()



