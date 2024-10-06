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
from sklearn.decomposition import PCA, FastICA
from sklearn.manifold import MDS, TSNE
from umap import UMAP
from sklearn.cluster import KMeans
import ast
import plotly.express as px
import plotext as plt
from art import text2art
from cluster_working import ClusterWorking


class LogDisplay(Widget):

    logo = text2art("  >>EmbedCluster>>", font='bulbhead')

    logo = '\n\n\n\n\n' + logo

    log_elapsed = reactive(f'{logo}')

    def render(self):
        log = self.log_elapsed

        return log


class WorkScreen(Screen):

    CSS_PATH = 'work_screen.tcss'

    def __init__(self, mode, input_dataframe, input_column, input_api_key, input_algoritm, optionlist_embedding, maskedinput_cluster, sep):
        super().__init__()
        self.mode = mode
        self.input_dataframe = input_dataframe

        if self.input_dataframe.endswith('.xlsx'):
            cl = pd.read_excel(self.input_dataframe, sheet_name=0, nrows=10)
        elif self.input_dataframe.endswith('.csv'):
            cl = pd.read_csv(self.input_dataframe, sep=sep, nrows=10)

        for i, column in enumerate(cl.columns, start=1):
            if i == input_column:
                self.input_column = column

        self.input_api_key = input_api_key
        self.input_algoritm = input_algoritm
        self.optionlist_embedding = optionlist_embedding
        self.sep = sep

        max_width_id = 13 + 4
        max_width_text = 28 + 4
        max_width_embedding = 28 + 4

        input_column_text = self.input_column
        extra_dashes_text = max_width_text - len(input_column_text)
        left_dashes_text = extra_dashes_text // 2
        right_dashes_text = extra_dashes_text - left_dashes_text
        input_column_formatted = f'{"-" * left_dashes_text} {input_column_text} {"-" * right_dashes_text}'

        id_column_text = "ID"
        extra_dashes_id = max_width_id - len(id_column_text)
        left_dashes_id = extra_dashes_id // 2
        right_dashes_id = extra_dashes_id - left_dashes_id
        id_column_formatted = f'{"-" * left_dashes_id} {id_column_text} {"-" * right_dashes_id}'

        embedding_column_text = "Embedding"
        extra_dashes_embedding = max_width_embedding - len(embedding_column_text)
        left_dashes_embedding = extra_dashes_embedding // 2
        right_dashes_embedding = extra_dashes_embedding - left_dashes_embedding
        embedding_column_formatted = f'{"-" * left_dashes_embedding} {embedding_column_text} {"-" * right_dashes_embedding}'

        self.client_log = [f'Обработка DataFrame {self.input_dataframe}\n| {id_column_formatted} | {input_column_formatted} | {embedding_column_formatted} |\n']
        self.count_clusters = maskedinput_cluster


    def compose(self):

        render = ''

        label = text2art(">>EmbedCluster>>", font='bubble')

        if self.mode == 'checkbox_def':
            render = 'Ожидание процесса'
        elif self.mode == 'checkbox_embed':
            render = 'Запрос embedding'
        elif self.mode == 'checkbox_cluster':
            render = 'Кластеризация'
        else:
            render = self.mode

        yield Container(
            Container(
                    Static(renderable=label, id='static_label'),
                    id='container_head',
                ),
            Container(
                Container(
                    Container(
                        Static(renderable=render, id='static_state'),
                        ProgressBar(total=100, id='progress_bar'),
                        Static(renderable = 'Ожидание', id='static_info'),
                        id='container_info'
                    ),
                    Container(
                            LogDisplay(id='logdisplay'),
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


    async def get_embedding(self, inf, model):
        """API для получения эмбеддингов текста с помощью ChatGPT с обработкой ошибок"""

        if isinstance(inf, str):
            inf = inf.replace("\n", " ")

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
                client.embeddings.create, input=[inf], model=model
            )

            embedding = response.data[0].embedding
            return embedding

        except RequestException as e:
            info.update("Ошибка сети: проверьте подключение к интернету.")
            self.add_class('error_info')
        except Exception as e:
            info.update(f"Произошла неизвестная ошибка: {e}")
            self.add_class('error_info')
            with open('log.txt', 'w', encoding='utf-8') as file:
                file.write(str(e))

        return None
    

    async def background_task_embedding(self, df, model):
        for index, row in df.iterrows():
            embedding = await self.get_embedding(row[self.input_column], model)

            await self.logging(row['id'], row[self.input_column], embedding)

            df.at[index, 'ada_embedding'] = embedding

        self.query_one('#butt').disabled = False
        self.remove_class('success_info')

        new_file_name = 'embedding.csv'
        df.to_csv(new_file_name, index=False)


    async def logging(self, id_log, log, embedding):
        log = str(log)
        max_width_id = 15 + 4
        max_width_text = 30 + 4
        max_width_embedding = 30 + 4
    
        progressbar = self.query_one('#progress_bar', ProgressBar)
        progressbar.update(progress=id_log)
    
        if len(self.client_log) > 13:
            id_column_text = "ID"
            id_column_length = max_width_id - 2
            extra_dashes_id = id_column_length - len(id_column_text)
            left_dashes_id = extra_dashes_id // 2
            right_dashes_id = extra_dashes_id - left_dashes_id
            id_column_formatted = f'{"-" * left_dashes_id} {id_column_text} {"-" * right_dashes_id}'
    
            input_column_text = self.input_column
            input_column_length = max_width_text - 2
            extra_dashes_text = input_column_length - len(input_column_text)
            left_dashes_text = extra_dashes_text // 2
            right_dashes_text = extra_dashes_text - left_dashes_text
            input_column_formatted = f'{"-" * left_dashes_text} {input_column_text} {"-" * right_dashes_text}'
    
            embedding_column_text = "Embedding"
            embedding_column_length = max_width_embedding - 2
            extra_dashes_embedding = embedding_column_length - len(embedding_column_text)
            left_dashes_embedding = extra_dashes_embedding // 2
            right_dashes_embedding = extra_dashes_embedding - left_dashes_embedding
            embedding_column_formatted = f'{"-" * left_dashes_embedding} {embedding_column_text} {"-" * right_dashes_embedding}'
    
            self.client_log = [f'Обработка DataFrame {self.input_dataframe}\n| {id_column_formatted} | {input_column_formatted} | {embedding_column_formatted} |\n']
    
        id_log_str = f'{str(id_log):^{max_width_id}}'
    
        def format_text(text, max_width):
            if len(text) > max_width:
                return f'{text[:max_width - 3]}...'
            return f'{text:^{max_width}}'
    
        formatted_text = format_text(log, max_width_text)
        formatted_embedding = format_text(str(embedding), max_width_embedding)
    
        log_entry = f'| {id_log_str} | {formatted_text} | {formatted_embedding} |\n'
    
        self.client_log.append(log_entry)
    
        logs = ''.join(self.client_log)
    
        self.query_one(LogDisplay).log_elapsed = logs

    # TODO: объединить функции logging и logging_name
    async def logging_name(self, cluster, number, cluster_name):

        max_width_cluster = 15 + 23
        max_width_name = 30 + 23

        if len(self.client_log) > 13 or len(self.client_log) == 0:
            cluster_column_text = "CLUSTER"
            cluster_column_length = max_width_cluster - 2
            extra_dashes_cluster = cluster_column_length - len(cluster_column_text)
            left_dashes_cluster = extra_dashes_cluster // 2
            right_dashes_cluster = extra_dashes_cluster - left_dashes_cluster
            cluster_column_formatted = f'{"-" * left_dashes_cluster} {cluster_column_text} {"-" * right_dashes_cluster}'

            name_column_text = "NAME"
            name_column_length = max_width_name - 2
            extra_dashes_name = name_column_length - len(name_column_text)
            left_dashes_name = extra_dashes_name // 2
            right_dashes_name = extra_dashes_name - left_dashes_name
            name_column_formatted = f'{"-" * left_dashes_name} {name_column_text} {"-" * right_dashes_name}'

            self.client_log = [f'Обработка DataFrame {self.input_dataframe}\n| {cluster_column_formatted} | {name_column_formatted} |\n']

        progressbar = self.query_one('#progress_bar', ProgressBar)
        progressbar.update(progress=number)

        cluster_str = f'{str(cluster):^{max_width_cluster}}'

        def format_text(text, max_width):
            if len(text) > max_width:
                return f'{text[:max_width - 3]}...'
            return f'{text:^{max_width}}'

        formatted_name = format_text(cluster_name, max_width_name)

        log_entry = f'| {cluster_str} | {formatted_name} |\n'

        self.client_log.append(log_entry)

        logs = ''.join(self.client_log)

        self.query_one(LogDisplay).log_elapsed = logs


    def state_embedding(self):
        mode = self.mode
        df_path = self.input_dataframe
        model = self.optionlist_embedding
        butt = self.query_one('#butt')
        progressbar = self.query_one('#progress_bar', ProgressBar)
        
        if df_path.endswith('.xlsx'):
            df = pd.read_excel(df_path, sheet_name=0, nrows=50)
        elif df_path.endswith('.csv'):
            df = pd.read_csv(df_path, sep=self.sep, nrows=50)

        progressbar.total = len(df)

        df['ada_embedding'] = None

        self.run_worker(self.background_task_embedding(df, model))

    
    async def use_gpt(self, system: str, user: str, v=4, mode="text"):
        """Асинхронная API для взаимодействия с GPT."""

        with open('config.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        client = openai.OpenAI(
            api_key=str(data['api_key']),
            base_url="https://api.proxyapi.ru/openai/v1"
        )

        model = "gpt-4o-mini" if v == 4 else "gpt-3.5-turbo-1106"

        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        if mode == "json":
            params["response_format"] = {"type": "json_object"}
            params["messages"][0]["content"] = (
                "You are a helpful assistant designed to output JSON. " + system
            )

        chat_completion = await asyncio.to_thread(client.chat.completions.create, **params)

        response_content = chat_completion.choices[0].message.content

        if mode == "json":
            return json.loads(response_content)  # Исправлено здесь

        return response_content


    async def background_task_name(self, df):
        unique_clusters = df['cluster'].unique() 
        result_data = []

        with open('prompt.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        prompt = data[0]['prompt']

        self.client_log = ''
        number = 0

        for cluster in unique_clusters:
            number += 1
            cluster_values = df[df['cluster'] == cluster][self.input_column].head(5).tolist()

            cluster_name = await self.use_gpt(system=f'Я провожу кластеризацию с помощью алгоритма {self.input_algoritm} + {prompt}', user=str(cluster_values), v=4, mode="json")

            if cluster_name:
                await self.logging_name(cluster, number, cluster_name['name'])

                result_data.append({'cluster': cluster, 'cluster_name': cluster_name['name']})

        result_df = pd.DataFrame(result_data)

        new_file_name = 'name_cluster.csv'
        result_df.to_csv(new_file_name, index=False)

        # Восстанавливаем интерфейс, если это нужно
        self.query_one('#butt').disabled = False
        self.remove_class('success_info')


    async def update_progress(self, progressbar, value):
        """Обновляет прогресс бар."""
        progressbar.progress = min(value, 100)
        await asyncio.sleep(0.1)


    async def clustering(self, df, progressbar, input_algoritm):
        count_clusters = int(self.count_clusters)
        await self.update_progress(progressbar, 0)

        df['ada_embedding'] = df['ada_embedding'].apply(ast.literal_eval)
        await self.update_progress(progressbar, 10)

        embeddings = pd.DataFrame(df['ada_embedding'].tolist())
        await self.update_progress(progressbar, 20)
        
        kmeans = KMeans(n_clusters=count_clusters)
        df['cluster'] = kmeans.fit_predict(embeddings)
        await self.update_progress(progressbar, 30)

        # Выбор алгоритма
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
        alg[self.input_column] = df[self.input_column]
        alg['cluster'] = df['cluster']
        await self.update_progress(progressbar, 100)

        fig = px.scatter(
            alg,
            x='x',
            y='y',
            color='cluster',
            hover_name=self.input_column,
            title=name,
        )

        fig.write_html("interactive_plot.html")

        new_file_name = 'clusters.csv'
        alg.to_csv(new_file_name, index=False)


    def state_clustering(self, input_algoritm):
        mode = self.mode
        df_path = self.input_dataframe
        progressbar = self.query_one('#progress_bar', ProgressBar)

        if mode == 'checkbox_cluster':
            return None

        df = pd.read_csv('embedding.csv', quotechar='"', escapechar='\\')

        self.run_worker(self.clustering(df, progressbar, input_algoritm))

        butt = self.query_one('#butt', Button)
        butt.disabled = False
        self.remove_class('succes_info')

    
    def state_name_cluster(self):
        df_path = self.input_dataframe

        df_path = 'clusters.csv'

        dataframe = pd.read_csv(df_path, sep=',')

        progressbar = self.query_one('#progress_bar', ProgressBar)
        progressbar.total = int(self.count_clusters)

        self.run_worker(self.background_task_name(dataframe))


    @on(Button.Pressed, '#butt')
    def on_pressed_butt(self):
        static_state = self.query_one('#static_state', Static)
        static_info = self.query_one('#static_info', Static)
        butt = self.query_one('#butt', Button)
        butt.disabled = True

        if str(static_state.renderable) == 'Ожидание процесса':
            static_info.update('Ошибок не найдено')
            self.add_class('success_info')
            static_state.update('Запрос embedding')
            self.state_embedding()
        elif str(static_state.renderable) == 'Запрос embedding':
            static_info.update('Ошибок не найдено')
            static_state.update('Кластеризация')
            self.state_clustering(self.input_algoritm)
        elif str(static_state.renderable) == 'Кластеризация':
            self.remove_class('visible')
            self.add_class('unvisible')
            static_state.update('Работа с DataFrame')
            self.state_name_cluster()
        elif str(static_state.renderable) == 'Работа с DataFrame':
            self.app.push_screen(ClusterWorking())
