from textual.app import ComposeResult
from textual import on
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widgets import Button, Static, Input, Select, RadioButton, RadioSet
from textual.widgets import MaskedInput
from textual.screen import Screen
from art import text2art
import os.path
import pandas as pd
import json
from work_screen import WorkScreen
from pathlib import Path
from cluster_working import ClusterWorking

class MainScreen(Screen):

    CSS_PATH = 'main_screen.tcss'
    AUTO_FOCUS = '#input_dataframe'


    def compose(self) -> ComposeResult:
        """Создание виджетов экрана авторизации."""

        info = '''
        Загрузите данные в формате CSV или xlsx. Если вы используете xlsx, то 
        используйте в нем только первый лист. Если CSV имеет не стандартный sep, то 
        пропишите в конце "&[разделительный символ]" по умолчанию ;
        Для начала работы вам необходимо заполнить форму с указанием необходимых параметров
        
        Памятка для алгоритмов:
        '''

        with open("info.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        info += data['info_main_screen']

        label = text2art(">>EmbedCluster>>", font='small')

        current_directory = Path('.')

        self.files = [f for f in current_directory.iterdir() 
             if f.is_file() and f.suffix in ['.csv', '.xlsx']]

        options_list = []
        i = 0

        for file in self.files:
            i += 1
            options_list.append((f'{file}', i))
        
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
                        Static(renderable='Файла не существует', id='static_error'),
                        Container(
                            Container(
                                Select(prompt='Датафрейм', id='input_dataframe',
                                       options=options_list),
                                Input(placeholder='sep для csv', id='input_sep', disabled=True),
                                       id='container_df'
                            ),
                            Select(prompt='Столбец для кластера', id='input_column', options=[]),
                            Input(placeholder='Ваш API ключ', id='input_api_key'),
                            Select(prompt='Embedding-model', tooltip='Информация о моделях находится выше', 
                                   options=[('text-embedding-3-small', 1), ('text-embedding-3-large', 2),
                                            ('text-embedding-ada-002', 3)], 
                                            id='optionlist_embedding'),
                            Container(
                                Select(prompt='Метод', tooltip='Информацию об алгоритмах можно получить выше', 
                                       options=[('ICA', 1), ('MDS', 2), ('PCA', 3), ('T-SNE', 4),
                                                ('UMAP2D', 5), ('TruncatedSVD', 6)], 
                                       id='input_algoritm'),
                                MaskedInput(template="999;0", id='maskedinput_cluster'),
                                id='container_alg'
                            ),
                            id='vertical_input',
                        ),
                        Container(
                            RadioSet(
                                RadioButton(label = 'Стандартный режим', id='checkbox_def', value=True),
                                RadioButton(label = 'Не делать embedding', id='checkbox_embed'),
                                RadioButton(label = 'Работа с кластерами', id='checkbox_cluster'),
                                id='radio_group',
                            ),
                             Button('Вставить api_key из памяти', id='button_insert_api_key'),
                            id='vertical_checkbox',
                        ),
                        id="container_inputs"
                    ),
                    Container(
                        Button('Запуск', id='b'),
                        id='container_b'
                    ),
                    id='container_body'
                ),
                id='container_main',
            )
        
        
    @on(RadioSet.Changed, "#radio_group")
    def on_radio_group_changed(self, event: RadioSet.Changed) -> None:
        input_api_key = self.query_one('#input_api_key')
        optionlist_embedding = self.query_one('#optionlist_embedding')
        input_algoritm = self.query_one('#input_algoritm')
        input_column = self.query_one('#input_column')
        maskedinput_cluster = self.query_one('#maskedinput_cluster')


        if event.pressed.id == 'checkbox_embed':
            input_algoritm.disabled = False
            maskedinput_cluster.disabled = False
            input_api_key.disabled = True
            optionlist_embedding.disabled = True
        
        elif event.pressed.id == 'checkbox_cluster':
            input_algoritm.disabled = True
            input_api_key.disabled = True
            optionlist_embedding.disabled = True
            maskedinput_cluster.disabled = True
            input_column.disabled = True
        
        elif event.pressed.id == 'checkbox_def':
            input_algoritm.disabled = False
            input_api_key.disabled = False
            optionlist_embedding.disabled = False
            maskedinput_cluster.disabled = False
            

    def insert_password_json(self, password):
        pas = {'api_key': password}
        with open('config.json', 'w') as file:
            json.dump(pas, file, indent=4)

    
    def parse_df(self, input_df, sep):
        self.remove_class("error")
        error_widget = self.query_one('#static_error', Static)
        
        # TODO Сделать в два потока

        if len(sep) > 0:
            if input_df.endswith('.xlsx'):
                try:
                    cl = pd.read_excel(input_df, sheet_name=0, nrows=10)
                except:
                    error_widget.update("Ошибка чтения")
                    self.add_class("error")
                    return None
            elif input_df.endswith('.csv'):
                try:
                    cl = pd.read_csv(input_df, sep=sep, nrows=10)
                except:
                    error_widget.update("Ошибка чтения")
                    self.add_class("error")
                    return None
            else:
                error_widget.update("Неподдерживаемый формат файла.")
                self.add_class("error")
        else:
            error_widget.update("Неподдерживаемый формат sep.")
            self.add_class("error")
            return None
        
        return cl
    

    @on(Select.Changed, '#input_dataframe')
    def input_dataframe(self):
        index = self.query_one('#input_dataframe', Select).value
        i = 0
        for str_df in self.files:
            i += 1
            str_df = str(str_df)
            if str_df.endswith('.csv') and i == index:
                self.query_one('#input_sep').disabled = False    
                self.df = str_df    
        
    @on(Input.Changed, '#input_sep')
    def on_input_sep_changed(self):
        sep = self.query_one('#input_sep', Input).value
        self.read_df(self.df, sep)


    @on(Button.Pressed, '#button_insert_api_key')
    def on_pressed_button_api(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            if data.get('api_key', False):
                input = self.query_one('#input_api_key', Input)
                input.value = str(data['api_key'])
            

    @on(Button.Pressed, '#b')
    def on_pressed_button_start(self):
        error_widget = self.query_one('#static_error', Static)
        try:
            input_df = self.df
        except:
            error_widget.update("Форма не заполнена")
            self.add_class("error")
            return None
    
        input_column = self.query_one('#input_column', Select).value

        if input_column is None:
            error_widget.update("Форма не заполнена")
            self.add_class("error")
            return None

        sep = self.query_one('#input_sep', Input).value

        if sep == '':
            error_widget.update("Форма не заполнена")
            self.add_class("error")
            return None

        input_api_key = self.query_one('#input_api_key', Input).value
        input_algoritm = self.query_one('#input_algoritm', Select).value
        optionlist_embedding = self.query_one('#optionlist_embedding', Select).value
        checkbox_def = self.query_one('#checkbox_def', RadioButton)
        checkbox_embed = self.query_one('#checkbox_embed', RadioButton)
        checkbox_cluster = self.query_one('#checkbox_cluster', RadioButton)
        maskedinput_cluster = self.query_one('#maskedinput_cluster', MaskedInput).value

        mode = ''

        if checkbox_def.value:
            mode = 'checkbox_def'
        elif checkbox_embed.value:
            mode = 'checkbox_embed'
        elif checkbox_cluster.value:
            mode = 'checkbox_cluster'

        if input_df and os.path.exists(input_df):

            if mode == 'checkbox_cluster':
                self.app.push_screen(ClusterWorking())

            if self.query_one('#checkbox_def', RadioButton).value:
                
                if input_api_key and isinstance(input_algoritm, int) and isinstance(optionlist_embedding, int) and isinstance(maskedinput_cluster, str):
                        self.insert_password_json(input_api_key)
                        self.app.push_screen(WorkScreen(mode=mode, input_dataframe=input_df, input_column=input_column, input_api_key=input_api_key, input_algoritm=input_algoritm, optionlist_embedding=optionlist_embedding, sep=sep, maskedinput_cluster=maskedinput_cluster))
                else:
                    error_widget.update("Форма не заполнена")
                    self.add_class("error")

            elif self.query_one('#checkbox_embed', RadioButton).value:

                if isinstance(input_algoritm, int) and isinstance(maskedinput_cluster, str):
                    self.app.push_screen(WorkScreen(mode=mode, input_dataframe=input_df, input_column=input_column, input_api_key=input_api_key, input_algoritm=input_algoritm, optionlist_embedding=optionlist_embedding, sep=sep, maskedinput_cluster=maskedinput_cluster))
                else:
                    error_widget.update("Форма не заполнена")
                    self.add_class("error")

        else:
            error_widget.update("Форма не заполнена")
            self.add_class("error")

                    
    def read_df(self, dataframe, sep):
        cl = self.parse_df(str(dataframe), sep)
        error_widget = self.query_one('#static_error', Static)
        input_column = self.query_one('#input_column', Select)
        options_list = []

        if cl is None:
            return

        for i, column in enumerate(cl.columns, start=1):
            options_list.append((f'{column}', i))

        input_column.set_options(options_list)
        input_column.refresh()

        
        
        # if column_name not in cl.columns:
        #     error_widget.update("Столбец не найден в DataFrame.")
        #     self.add_class("error")
        # else:
        #     self.remove_class("error")