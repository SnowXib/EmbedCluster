from textual.app import App, ComposeResult
from textual import on
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widgets import Button, Static, Input, Select, RadioButton, RadioSet
from textual.widgets import MaskedInput
from textual.screen import Screen
from art import text2art
import os.path
import pandas as pd
import json
from work_screen import WorkScreen


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
                            Input(placeholder='Название датафрейма с расширением', id='input_dataframe'),
                            Input(placeholder='Столбец для кластера', id='input_column'),
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
                                RadioButton(label = 'Запустить отображение сразу', id='checkbox_cluster'),
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
        
        elif event.pressed.id == 'checkbox_def':
            input_algoritm.disabled = False
            input_api_key.disabled = False
            optionlist_embedding.disabled = False
            maskedinput_cluster.disabled = False
            


    def insert_password_json(self, password):
        pas = {'api_key': password}
        with open('config.json', 'w') as file:
            json.dump(pas, file, indent=4)

    
    def parse_df(self, input_df):
        self.remove_class("error")
        error_widget = self.query_one('#static_error', Static)

        if '&' in input_df:
            input_df.split('&')
            df = input_df[0] 
            sep = input_df[1]
        else:
            df = input_df
            sep = ';'
        # TODO Сделать в два потока
        if input_df.endswith('.xlsx'):
            cl = pd.read_excel(input_df, sheet_name=0, nrows=10)
        elif input_df.endswith('.csv'):
            cl = pd.read_csv(input_df, sep=sep, nrows=10)
        error_widget.update("Неподдерживаемый формат файла.")
        self.add_class("error")
        
        return df, cl
            

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
        input_df = self.query_one('#input_dataframe', Input).value
    
        input_column = self.query_one('#input_column', Input).value
        input_api_key = self.query_one('#input_api_key', Input).value
        input_algoritm = self.query_one('#input_algoritm', Select).value
        optionlist_embedding = self.query_one('#optionlist_embedding', Select).value
        error_widget = self.query_one('#static_error', Static)
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

            df, cl = self.parse_df(input_df)

            column_name = self.query_one('#input_column', Input).value
            if column_name not in cl.columns:
                error_widget.update("Столбец не найден в DataFrame.")
                self.add_class("error")
            else:
                self.remove_class("error")

                if self.query_one('#checkbox_def', RadioButton).value:
                    
                    if input_api_key and isinstance(input_algoritm, int) and isinstance(optionlist_embedding, int) and isinstance(maskedinput_cluster, str):
                            self.insert_password_json(input_api_key)
                            self.app.push_screen(WorkScreen(mode, input_df, input_column, input_api_key, input_algoritm, optionlist_embedding, maskedinput_cluster))
                    else:
                        error_widget.update("Форма не заполнена")
                        self.add_class("error")

                elif self.query_one('#checkbox_embed', RadioButton).value:

                    if isinstance(input_algoritm, int) and isinstance(maskedinput_cluster, str):
                        self.app.push_screen(WorkScreen(mode, input_df, input_column, input_api_key, input_algoritm, optionlist_embedding, maskedinput_cluster))
                    else:
                        error_widget.update("Форма не заполнена")
                        self.add_class("error")

                elif self.query_one('#checkbox_cluster', RadioButton).value:

                    self.app.push_screen(WorkScreen(mode=mode, input_dataframe=input_df, input_column=input_column, input_api_key=input_api_key, input_algoritm=input_algoritm, optionlist_embedding=optionlist_embedding))

        else:
            error_widget.update("Форма не заполнена")
            self.add_class("error")

    
    @on(Input.Changed, '#input_column')
    def on_input_changed(self):
        dataframe = self.query_one('#input_dataframe', Input).value
        if dataframe and not os.path.exists(dataframe):
            self.add_class("error")
        else: 
            self.remove_class("error")


    def on_select_changed(self, event: Select.Changed):
        if event.select.id == 'input_algoritm':
            error_widget = self.query_one('#static_error', Static)
            
            dataframe = self.query_one('#input_dataframe', Input).value
            if os.path.exists(dataframe):
                self.read_df(dataframe)
            else:
                error_widget.update("Столбец не найден в DataFrame.")
                self.add_class("error")


                    
    def read_df(self, dataframe):

        df, cl = self.parse_df(dataframe)
        error_widget = self.query_one('#static_error', Static)
            
        column_name = self.query_one('#input_column', Input).value
        if column_name not in cl.columns:
            error_widget.update("Столбец не найден в DataFrame.")
            self.add_class("error")
        else:
            self.remove_class("error")