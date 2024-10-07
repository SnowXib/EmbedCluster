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
import plotly.express as px

class ClusterWorking(Screen):

    CSS_PATH = 'cluster_working.tcss'

    def compose(self):

        label = text2art(">>EmbedCluster>>", font='script')
        info = '''
        MERGE cluster: 1[номер кластера] <- cluster: 2[номер кластера] -- слить cluster 2 к cluster 1

        ADD obj: 1[номер объекта] to cluster: 2[номер кластера] -- добавить объект 1 к cluster 2   
'''

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
                    Static(info, id='markdown_instruction_information1'),
                    id='container_instruction',
                ),
                Static(renderable='Ошибка', id='static_error_cmd'),
                Container(
                    Container(
                        Input(placeholder = 'Введите команду', id='input_cmd'),
                        Button("Запуск", id='button_enter'),
                        id='container_cmd',
                    ),
                    Container(
                        Input(placeholder='Введите column', id='input_enter_column'),
                        Input(placeholder='Введите title', id='input_title'),
                        Button("Сгенерировать график", id='button_graph'),
                        id='container_gen_graph'
                    ),
                id='container_body_input',
                ),
            ),
            id='container_main',
        )


    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        df = pd.read_csv('name_cluster.csv', sep=',')
        
        table.add_columns(*df.columns)

        for _, row in df.iterrows():
            table.add_row(*[str(value) for value in row])

    
    def check_exist(self, obj, df, column):
        if int(obj) not in df[f'{column}'].tolist():
            static_error = self.query_one('#static_error_cmd', Static)
            self.add_class('error_cmd')
            static_error.update(f'В column {column} отсутствует {obj}')
            return None
        return 1

    
    def update_table(self, df):
        table = self.query_one(DataTable)
        table.clear()
        for _, row in df.iterrows():
            table.add_row(*[str(value) for value in row])


    @on(Button.Pressed, '#button_enter')
    def on_input_cmd_changed(self):
        client_cmd = self.query_one('#input_cmd', Input)
        static_error = self.query_one('#static_error_cmd', Static)
        df_name = pd.read_csv('name_cluster.csv')
        df_clusters = pd.read_csv('clusters.csv')

        self.remove_class('error_cmd')
        self.remove_class('success_cmd')

        cmd = client_cmd.value.split(' ')

        # Проверка формата команды MERGE
        if cmd[0] == 'MERGE':

            if len(cmd) == 6:
                if not self.check_exist(cmd[2], df_name, 'cluster') or not self.check_exist(cmd[5], df_name, 'cluster'):
                    return None
            else:
                self.add_class('error_cmd')
                static_error.update('Ошибка формата команды MERGE')
                return None
            
            if cmd[3] == '<-':
                cluster_1 = int(cmd[2])
                cluster_2 = int(cmd[5])
            elif cmd[3] == '->':
                cluster_1 = int(cmd[5])
                cluster_2 = int(cmd[2])
            else:
                self.add_class('error_cmd')
                static_error.update('Ошибка определения направления слияния')
                return None

            df_name.loc[df_name['cluster'] == cluster_2, 'cluster'] = cluster_1

            df_clusters.loc[df_clusters['cluster'] == cluster_2, 'cluster'] = cluster_1

            # Сохраняем обновленные датафреймы
            df_name.to_csv('name_cluster.csv', index=False)
            df_clusters.to_csv('clusters.csv', index=False)

            self.add_class('success_cmd')
            static_error.update(f'Кластеры {cluster_2} и {cluster_1} успешно объединены')
            self.update_table(df=df_name)
        #  0   1   2 3     4     5
        # ADD obj: 1 to cluster: 3
        elif cmd[0] == 'ADD':

            if not self.check_exist(cmd[2], df_clusters, 'id') and self.check_exist(cmd[5], df_name, 'cluster'):
                return None

            if cmd[3] == 'to':  
                obj_1 = int(cmd[2])
                cluster_1 = int(cmd[5])
                
                df_clusters.loc[df_clusters['id'] == obj_1, 'cluster'] = cluster_1

                df_clusters.to_csv('clusters.csv', index=False)

                self.add_class('success_cmd')
                static_error.update(f'Объект {obj_1} успешно добавлен в кластер {cluster_1}')
            else:
                self.add_class('error')
                static_error.update('Ошибка определения добавления')
                return None
        else:
            self.add_class('error_cmd')
            static_error.update(f'Команды {cmd[0]} не существует')
            return None
            
    @on(Button.Pressed, '#button_graph')
    def button_graph_pressed(self):
        static_error = self.query_one('#static_error_cmd', Static)
        input_entrer_column = self.query_one('#input_enter_column', Input)
        input_title = self.query_one('#input_title', Input)

        df_clusters = pd.read_csv('clusters.csv')

        if not input_entrer_column.value and input_title.value:
            self.add_class('error_cmd')
            static_error.update('Ошибка формы')
            return None
        
        if not input_entrer_column.value in df_clusters.head():
            self.add_class('error_cmd')
            static_error.update(f'Ошибка column')
            return None

        fig = px.scatter(
            df_clusters,
            x='x',
            y='y',
            color='cluster',
            hover_name=input_entrer_column.value,
            title=input_title.value,
        )

        fig.write_html("interactive_plot.html")

        self.add_class('success_cmd')
        static_error.update('interactive_plot.html успешно создан')
    