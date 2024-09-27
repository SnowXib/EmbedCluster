from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Button, Static, Input, Markdown
from textual.screen import Screen
from main_screen import MainScreen
from art import text2art


class InfoScreen(Screen):

    CSS_PATH = 'info_screen.tcss'
    AUTO_FOCUS = '#button_start'
    
    


    def compose(self) -> ComposeResult:
        label = text2art(">>EmbedCluster>>", font='cyberlarge')

        instruction1 = '''
        Добро пожаловать в приложение для кластеризации данных!

        Это приложение позволяет вам:

        1. Загрузить ваш набор данных: '''     
        instruction2 = '''
        Добавьте название вашего .csv или .xslx файла, который требует анализа '''

        instruction3 = '''
        2. Выберите столбец для анализа и получите embeddings: '''

        instruction4 = '''
        Наше приложение использует API ChatGPT для генерации эмбеддингов для каждой записи,
        что позволяет преобразовать текстовые данные в числовые векторы.'''

        instruction5 = '''
        3. Выбрать алгоритм кластеризации: '''

        instruction6 = '''
        Вы можете выбрать один из нескольких алгоритмов кластеризации, включая:
            - T-SNE
            - PCA
            - ICA
            - MDS
            - TruncatedSVD
            - UMAP2D
            - UMAP3D'''

        instruction7 = '''
        4. Просмотреть результаты: '''

        instruction8 = '''
        После кластеризации вы сможете визуализировать результаты и анализировать, 
        как ваши данные сгруппированы.'''

        instruction9 = '''
        5. Интерактивная визуализация: '''

        instruction10 = '''
        Нажмите на точки в графике, чтобы увидеть подробную информацию о каждой записи.
        '''

        yield Container(
            Container(
                Static(renderable=label, id='static_label'),
                id='container_head',
            ),
            VerticalScroll(
                Container(
                    Static(instruction1, id='markdown_instruction_heading1'),
                    Static(instruction2, id='markdown_instruction_information1'),
                    Static(instruction3, id='markdown_instruction_heading2'),
                    Static(instruction4, id='markdown_instruction_information2'),
                    Static(instruction5, id='markdown_instruction_heading3'),
                    Static(instruction6, id='markdown_instruction_information3'),
                    Static(instruction7, id='markdown_instruction_heading4'),
                    Static(instruction8, id='markdown_instruction_information4'),
                    Static(instruction9, id='markdown_instruction_heading5'),
                    Static(instruction10, id='markdown_instruction_information5'),
                    id='container_instruction',
                ),
                id='scrollable_container_instruction',
            ),
            Container(
                Button('Начать работу', id='button_start'),
                Button('Demo', id='demo_button'),
                id='container_buttons'
            ),
            id='container_main',
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'button_start':
            self.app.push_screen(MainScreen())
        elif event.button.id == 'demo_button':
            pass