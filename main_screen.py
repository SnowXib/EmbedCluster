from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Button, Static, Input, OptionList, Select, Checkbox
from textual.screen import Screen
from art import text2art
import os.path
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial


class MainScreen(Screen):

    CSS_PATH = 'main_screen.tcss'

    def compose(self) -> ComposeResult:
        """Создание виджетов экрана авторизации."""

        info = '''
        Загрузите данные в формате CSV или xlsx. Если вы используете xlsx, то 
        используйте в нем только первый лист
        Нажмите "Сгенерировать эмбеддинги" для обработки данных.
        Выберите алгоритм кластеризации и нажмите "Запустить кластеризацию".
        Изучите результаты на графике.'''

        label = text2art(">>EmbedCluster>>", font='small')
        
        yield Container(
                Container(
                    Static(renderable=label, id='static_label'),
                    id='container_head',
                ),
                Container(
                    VerticalScroll(
                        Container(
                            Static(renderable='''
        Инструкция по использованию:''', id='markdown_instruction_heading1'),
                            Static(renderable=info, id='markdown_instruction_information1'),
                            id='container_instruction',
                        ),
                        id='scrollable_container_instruction',
                    ),
                    Container(
                        Container(
                            Static(renderable='Файла не существует', id='static_error'),
                            Input(placeholder='Название датафрейма с расширением', id='input_dataframe'),
                            Input(placeholder='Стоблец по которому будет проведена кластеризация', id='input_column'),
                            Input(placeholder='Ваш API ключ', id='input_api_key'),
                            Select(prompt='Алгоритм кластеризации', tooltip='Информацию об алгоритмах можно получить выше', 
                                   options=[('ICA', 1), ('MDS', 2), ('PCA', 3), ('T-SNE', 4),
                                            ('UMAP2D', 5), ('UMAP3D', 6), ('TruncatedSVD', 7)], 
                                   id='input_algoritm'),
                            Select(prompt='Embedding-model', tooltip='Информация о моделях находится выше', 
                                   options=[('text-embedding-3-small', 1), ('text-embedding-3-large', 2),
                                            ('text-embedding-ada-002', 3)], 
                                    id='optionlist_embedding'),
                            id='vertical_input',
                        ),
                        Container(
                            Checkbox(label = 'Не делать embedding', id='checkbox_embed'),
                            Checkbox(label = 'Запустить кластеризацию сразу', id='checkbox_cluster'),
                            id='vertical_checkbox',
                        ),
                        id="container_inputs"
                    ),
                    Container(
                        Button('Запуск', id='button_start', disabled=True),
                        id='container_buttons'
                    ),
                    id='container_body'
                ),
                id='container_main',
            )
        
    async def on_input_changed(self, event: Input.Changed):
        if event.input.id == 'input_column':
            dataframe = self.query_one('#input_dataframe', Input).value
            if dataframe and not os.path.exists(dataframe):
                self.add_class("error")
            else:
                self.remove_class("error")

    async def on_select_changed(self, event: Select.Changed):
        if event.select.id == 'input_algoritm':
            dataframe = self.query_one('#input_dataframe', Input).value
            if os.path.exists(dataframe):
                file_size = os.path.getsize(dataframe)
                file_size_mb = file_size / (1024 * 1024)
                if file_size_mb < 100:
                    await self.async_apply_read_and_check_df(dataframe)


    async def async_apply_read_and_check_df(self, df_path):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.read_df(df_path))

                    
    async def read_df(self, dataframe):
        self.remove_class("error")
        error_widget = self.query_one('#static_error', Static)

        if dataframe.endswith('.xlsx'):
            df = pd.read_excel(dataframe, sheet_name=0)
        elif dataframe.endswith('.csv'):
            df = pd.read_csv(dataframe, sep=';')
        else:
            error_widget.update("Неподдерживаемый формат файла.")
            self.add_class("error")
            return

        column_name = self.query_one('#input_column', Input).value
        if column_name not in df.columns:
            error_widget.update("Столбец не найден в DataFrame.")
            self.add_class("error")
        else:
            self.remove_class("error")



    # if mode == 'csv':
        # df = pd.read_csv(f'{dataframe_path}', sep=';')
    # elif mode == 'xlsx':
        # df = pd.read_excel(dataframe_path, sheet_name=0)

    








