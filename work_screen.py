from textual.app import App, ComposeResult
from textual import on
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Button, Static, ProgressBar, MaskedInput
from textual.widget import Widget
from textual.screen import Screen
from textual.reactive import reactive
from art import text2art
import os.path
import pandas as pd
import json
import openai
from requests.exceptions import RequestException
import time
import asyncio
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.manifold import MDS, TSNE
from umap import UMAP
from sklearn.cluster import KMeans
import ast
import plotly.express as px


class LogDisplay(Widget):

    log_elapsed = reactive('')

    def render(self):
        log = self.log_elapsed

        return log


class WorkScreen(Screen):

    CSS_PATH = 'work_screen.tcss'

    def __init__(self, mode, input_dataframe, input_column, input_api_key, input_algoritm, optionlist_embedding, maskedinput_cluster):
        super().__init__()
        self.mode = mode
        self.input_dataframe = input_dataframe
        self.input_column = input_column
        self.input_api_key = input_api_key
        self.input_algoritm = input_algoritm
        self.optionlist_embedding = optionlist_embedding
        self.client_log = [f'Обработка DataFrame {self.input_dataframe}\n| - ID - | - Text - |\n']
        self.count_clusters = maskedinput_cluster


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
                    Container(
                        VerticalScroll(
                            LogDisplay('logdisplay'),
                            id='scrollable_container_instruction',
                        ),
                        id='container_logs'
                    )
                ),
                Container(
                        Button('Запуск следующего этапа', id='butt'),
                        id='container_b',
                    ),
                id='container_body',
            ),
            id='container_main',
        )


    async def get_embedding(self, text, model):
        """API для получения эмбеддингов текста с помощью ChatGPT с обработкой ошибок"""

        text = text.replace("\n", " ")

        if model == 1:
            model = 'text-embedding-3-small'
        elif model == 2:
            model = 'text-embedding-3-large'
        elif model == 3:
            model = 'text-embedding-ada-002'


        info = self.query_one('#static_info', Static)
        api_key = self.input_api_key

        try:
            client = openai.OpenAI(
                api_key=str(api_key),
                base_url="https://api.proxyapi.ru/openai/v1"
            )

            # Запрос эмбеддингов
            response = await asyncio.to_thread(
                client.embeddings.create, input=[text], model=model
            )

            embedding = response.data[0].embedding
            return embedding

        except RequestException as e:
            info.update("Ошибка сети: проверьте подключение к интернету.")
        except Exception as e:
            info.update(f"Произошла неизвестная ошибка: {e}")
            with open('log.txt', 'w', encoding='utf-8') as file:
                file.write(str(e))

        return None
    

    async def background_task(self, df, model):
        for index, row in df.iterrows():
            await self.logging(row['id'], row['text'])

            embedding = await self.get_embedding(row['text'], model)

            df.at[index, 'ada_embedding'] = embedding

        new_file_name = self.input_dataframe.split('.')[0] + '_embedding.csv'
        df.to_csv(new_file_name, index=False)


    async def logging(self, id_log, log):
        
        progressbar = self.query_one('#progress_bar', ProgressBar)
        progressbar.update(progress=id_log)

        if len(self.client_log) > 11:
            self.client_log = [f'Обработка DataFrame {self.input_dataframe}\n| - ID - | - Text - |\n']

        id_log_str = f'{id_log: <8}'
        log_entry = f'\n{id_log_str}{log[:30]}...'
        self.client_log.append(log_entry)

        logs = ''.join(self.client_log)
        self.query_one(LogDisplay).log_elapsed = logs


    def state_embedding(self):
        mode = self.mode
        df_path = self.input_dataframe
        model = self.optionlist_embedding
        progressbar = self.query_one('#progress_bar', ProgressBar)

        if mode == (2 or 3):
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

        df['ada_embedding'] = None

        self.run_worker(self.background_task(df, model))


    async def update_progress(self, progressbar, value):
        """Обновляет прогресс бар."""
        progressbar.progress = min(value, 100)
        await asyncio.sleep(0.1)


    async def clustering(self, df, progressbar, input_algoritm):
        count_clusters = int(self.count_clusters)

        
        await self.update_progress(progressbar, 0)

        # Преобразование данных
        df['ada_embedding'] = df['ada_embedding'].apply(ast.literal_eval)
        await self.update_progress(progressbar, 10)

        embeddings = pd.DataFrame(df['ada_embedding'].tolist())
        await self.update_progress(progressbar, 20)
        kmeans = KMeans(n_clusters=int(count_clusters))
        df['cluster'] = kmeans.fit_predict(embeddings)
        await self.update_progress(progressbar, 30)


        if input_algoritm == 1:
            alg = FastICA(n_components=2)
            name = 'ICA'
        elif input_algoritm == 2:
            alg = MDS(n_components=2)
            name = 'MDS'
        elif input_algoritm == 3:
            alg = PCA(n_components=2)
            name = 'PCA'
        elif input_algoritm == 4:
            alg = TSNE(n_components=2)
            name = 'T-SNE'
        elif input_algoritm == 5:
            alg = UMAP(n_components=2, random_state=10)
            name = 'UMAP'
        
        await self.update_progress(progressbar, 40)
        alg = alg.fit_transform(embeddings)
        await self.update_progress(progressbar, 60)
        alg = pd.DataFrame(data=alg, columns=['x', 'y'])
        await self.update_progress(progressbar, 80)

        alg['telegram_id'] = df['telegram_id']
        alg['text'] = df['text']
        alg['cluster'] = df['cluster']
        await self.update_progress(progressbar, 100)

        fig = px.scatter(
            alg,
            x='x',
            y='y',
            color='cluster',
            hover_name='text',
            hover_data={'telegram_id': True},
            title=name,
        )

        fig.show()

    def state_clustering(self, input_algoritm):
        mode = self.mode
        df_path = self.input_dataframe
        progressbar = self.query_one('#progress_bar', ProgressBar)

        if mode == 'checkbox_cluster':
            return None

        df = pd.read_csv(df_path.split('.')[0] + '_embedding.csv', quotechar='"', escapechar='\\')

        # Запуск фоновой задачи кластеризации
        self.run_worker(self.clustering(df, progressbar, input_algoritm))

    @on(Button.Pressed, '#butt')
    def on_pressed_butt(self):
        static_state = self.query_one('#static_state', Static)
        progressbar = self.query_one('#progress_bar', ProgressBar)

        if str(static_state.renderable) == 'Ожидание процесса':
            static_state.update('Запрос embedding')
            self.state_embedding()
        elif str(static_state.renderable) == 'Запрос embedding':
            static_state.update('Кластеризация')
            self.state_clustering(self.input_algoritm)
