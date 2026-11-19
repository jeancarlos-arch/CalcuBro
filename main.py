import os
import sys
from kivy.config import Config

# Configuración de ventana para apariencia móvil en desarrollo de escritorio
Config.set('graphics', 'width', '390')
Config.set('graphics', 'height', '780')
Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ColorProperty, BooleanProperty
from kivy.clock import Clock

# Paletas de colores: Modo Oscuro (prototipo actual) y Modo Claro (limpio y accesible)
DARK_THEME = {
    'bg_color': (0.063, 0.094, 0.153, 1),          # #101827
    'card_color': (0.106, 0.149, 0.220, 1),        # #1B2638
    'card_border': (0.173, 0.227, 0.322, 1),       # #2C3A52
    'primary_color': (0.337, 0.537, 0.910, 1),     # #5689E8
    'primary_text': (0.063, 0.094, 0.153, 1),      # Texto oscuro sobre botón primario
    'accent_blue': (0.545, 0.718, 1.0, 1),        # #8BB7FF
    'text_primary': (0.957, 0.965, 0.980, 1),      # #F4F6FA
    'text_secondary': (0.627, 0.682, 0.753, 1),    # #A0AEC0
    'nav_bg_color': (0.106, 0.149, 0.220, 1),      # #1B2638
    'nav_border': (0.173, 0.227, 0.322, 1),        # #2C3A52
    'input_bg': (0.063, 0.094, 0.153, 1),          # #101827
    'chip_inactive_bg': (0.106, 0.149, 0.220, 1),
    'chip_inactive_text': (0.627, 0.682, 0.753, 1),
    'btn_pressed': (0.137, 0.192, 0.280, 1),
    'green_color': (0.224, 0.788, 0.541, 1),       # #39C98A
    'orange_color': (0.949, 0.651, 0.353, 1),      # #F2A65A
    'bg_color_hex': '101827',
    'card_color_hex': '1b2638',
    'text_primary_hex': 'f4f6fa',
    'text_secondary_hex': 'a0aec0',
    'accent_blue_hex': '8bb7ff',
    'primary_color_hex': '5689e8',
    'green_color_hex': '39c98a',
    'orange_color_hex': 'f2a65a',
}

LIGHT_THEME = {
    'bg_color': (0.949, 0.957, 0.973, 1),          # #F2F4F8 (Fondo claro limpio)
    'card_color': (1.0, 1.0, 1.0, 1),              # #FFFFFF (Tarjeta blanca pura)
    'card_border': (0.860, 0.890, 0.930, 1),       # #DCE3ED (Borde sutil)
    'primary_color': (0.220, 0.450, 0.880, 1),     # #3873E0 (Azul primario accesible)
    'primary_text': (1.0, 1.0, 1.0, 1),             # Texto blanco sobre botón primario
    'accent_blue': (0.180, 0.420, 0.820, 1),       # #2E6BD1 (Azul para íconos/enlaces)
    'text_primary': (0.070, 0.100, 0.160, 1),      # #121A29 (Texto muy oscuro legible)
    'text_secondary': (0.420, 0.480, 0.560, 1),    # #6B7B8F (Gris medio accesible)
    'nav_bg_color': (1.0, 1.0, 1.0, 1),            # #FFFFFF (Barra inferior blanca)
    'nav_border': (0.860, 0.890, 0.930, 1),        # #DCE3ED
    'input_bg': (0.965, 0.975, 0.985, 1),          # #F6F8FB
    'chip_inactive_bg': (0.900, 0.925, 0.955, 1),
    'chip_inactive_text': (0.350, 0.410, 0.500, 1),
    'btn_pressed': (0.910, 0.930, 0.960, 1),
    'green_color': (0.130, 0.650, 0.400, 1),       # #21A666
    'orange_color': (0.880, 0.500, 0.120, 1),      # #E0801E
    'bg_color_hex': 'f2f4f8',
    'card_color_hex': 'ffffff',
    'text_primary_hex': '121a29',
    'text_secondary_hex': '6b7b8f',
    'accent_blue_hex': '2e6bd1',
    'primary_color_hex': '3873e0',
    'green_color_hex': '21a666',
    'orange_color_hex': 'e0801e',
}

# Registrar fuente de íconos MaterialIcons con ruta relativa
base_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_dir, 'assets', 'fonts', 'MaterialIcons-Regular.ttf')
if os.path.exists(font_path):
    LabelBase.register(name='MaterialIcons', fn_regular=font_path)

# Importar las clases de pantallas
from screens.welcome_screen import WelcomeScreen
from screens.home_screen import HomeScreen
from screens.subjects_screen import SubjectsScreen
from screens.detail_screen import DetailScreen
from screens.schedule_screen import ScheduleScreen
from screens.import_screen import ImportScreen
from screens.calc_screen import CalcScreen
from screens.progress_screen import ProgressScreen
from screens.diary_screen import DiaryScreen
from screens.remind_screen import RemindScreen
from screens.profile_screen import ProfileScreen
from screens.login_screen import LoginScreen


# Componentes y estilos globales en KV vinculados a la app de forma reactiva
GLOBAL_KV = """
#:import dp kivy.metrics.dp

<DarkCard@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(14)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: app.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: app.card_border
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(14)]
            width: dp(1)

<PrimaryButton@Button>:
    size_hint_y: None
    height: dp(46)
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    color: app.primary_text
    bold: True
    font_size: '15sp'
    canvas.before:
        Color:
            rgba: app.primary_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]

<GhostButton@Button>:
    size_hint_y: None
    height: dp(44)
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    color: app.accent_blue
    bold: True
    font_size: '14sp'
    canvas.before:
        Color:
            rgba: app.btn_pressed if self.state == 'down' else app.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: app.card_border
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(14)]
            width: dp(1)

<DangerButton@Button>:
    size_hint_y: None
    height: dp(42)
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    color: app.orange_color
    font_size: '13sp'
    canvas.before:
        Color:
            rgba: app.btn_pressed if self.state == 'down' else app.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
        Color:
            rgba: app.orange_color
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
            width: dp(1)

<ChipButton@Button>:
    is_active: False
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    font_size: '12sp'
    bold: True
    color: app.bg_color if self.is_active else app.text_secondary
    canvas.before:
        Color:
            rgba: app.primary_color if self.is_active else app.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
        Color:
            rgba: app.card_border
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
            width: dp(1)

<StyledTextInput@TextInput>:
    size_hint_y: None
    height: dp(40)
    multiline: False
    background_normal: ''
    background_active: ''
    background_color: (0, 0, 0, 0)
    foreground_color: app.text_primary
    cursor_color: app.accent_blue
    hint_text_color: app.text_secondary
    padding: [dp(12), dp(8)]
    canvas.before:
        Color:
            rgba: app.input_bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
        Color:
            rgba: app.primary_color if self.focus else app.card_border
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
            width: dp(1)

<RoundedSwitch@BoxLayout>:
    active: False
    on_active: pass
    size_hint: (None, None)
    size: (dp(52), dp(28))
    padding: dp(2)
    canvas.before:
        Color:
            rgba: app.green_color if self.active else app.card_border
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
    Widget:
        size_hint: (None, None)
        size: (dp(22), dp(22))
        pos: (root.x + root.width - dp(24) if root.active else root.x + dp(2), root.y + dp(3))
        canvas:
            Color:
                rgba: (1, 1, 1, 1) if root.active else app.text_secondary
            Ellipse:
                pos: self.pos
                size: self.size
    Button:
        background_color: (0, 0, 0, 0)
        size_hint: (1, 1)
        on_release:
            root.active = not root.active
            root.dispatch('on_active', root.active)

<CustomProgressBar@Widget>:
    value: 0
    bar_color: (0.224, 0.788, 0.541, 1)
    size_hint_y: None
    height: dp(7)
    canvas:
        Color:
            rgba: app.input_bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(4)]
        Color:
            rgba: self.bar_color if self.value > 0 else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: (max(dp(8), self.width * min(1.0, max(0.0, self.value / 100.0))), self.height) if self.value > 0 else (0, 0)
            radius: [dp(4)]

<TileButton@Button>:
    icon_text: ""
    title_text: ""
    markup: True
    text: f"[size=24sp][font=MaterialIcons]{self.icon_text}[/font][/size]\\n[size=12sp]{self.title_text}[/size]"
    halign: 'center'
    valign: 'middle'
    background_normal: ''
    background_down: ''
    background_color: (0, 0, 0, 0)
    color: app.accent_blue
    bold: True
    canvas.before:
        Color:
            rgba: app.btn_pressed if self.state == 'down' else app.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: app.card_border
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(14)]
            width: dp(1)

<ProfileLinkCard@ButtonBehavior+BoxLayout>:
    icon_text: ""
    link_title: ""
    size_hint_y: None
    height: dp(50)
    padding: [dp(14), 0]
    spacing: dp(12)
    canvas.before:
        Color:
            rgba: app.btn_pressed if self.state == 'down' else app.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: app.card_border
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(14)]
            width: dp(1)
    Label:
        text: root.icon_text
        font_name: 'MaterialIcons'
        font_size: '22sp'
        color: app.accent_blue
        size_hint_x: None
        width: dp(26)
        halign: 'center'
        valign: 'middle'
    Label:
        text: root.link_title
        font_size: '14sp'
        color: app.text_primary
        halign: 'left'
        valign: 'middle'
        text_size: self.size
    Label:
        text: ""
        font_name: 'MaterialIcons'
        font_size: '18sp'
        color: app.text_secondary
        size_hint_x: None
        width: dp(20)
        halign: 'right'
        valign: 'middle'

<NavBar@BoxLayout>:
    size_hint_y: None
    height: dp(62)
    padding: [dp(6), dp(4)]
    spacing: dp(4)
    canvas.before:
        Color:
            rgba: app.nav_bg_color
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: app.nav_border
        Line:
            points: [self.x, self.top, self.right, self.top]
            width: dp(1)

    Button:
        markup: True
        text: f"[size=20sp][font=MaterialIcons][/font][/size]\\n[size=10sp]Inicio[/size]"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: app.accent_blue if app.active_tab == 'home' else app.text_secondary
        bold: app.active_tab == 'home'
        on_release: app.go_screen('home', clear_history=True)

    Button:
        markup: True
        text: f"[size=20sp][font=MaterialIcons][/font][/size]\\n[size=10sp]Materias[/size]"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: app.accent_blue if app.active_tab == 'subjects' else app.text_secondary
        bold: app.active_tab == 'subjects'
        on_release: app.go_screen('subjects', clear_history=True)

    Button:
        markup: True
        text: f"[size=20sp][font=MaterialIcons][/font][/size]\\n[size=10sp]Horario[/size]"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: app.accent_blue if app.active_tab == 'schedule' else app.text_secondary
        bold: app.active_tab == 'schedule'
        on_release: app.go_screen('schedule', clear_history=True)

    Button:
        markup: True
        text: f"[size=20sp][font=MaterialIcons][/font][/size]\\n[size=10sp]Perfil[/size]"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: app.accent_blue if app.active_tab == 'profile' else app.text_secondary
        bold: app.active_tab == 'profile'
        on_release: app.go_screen('profile', clear_history=True)
"""


class DataStore:
    """Almacén central del estado académico de StudyMate con persistencia JSON"""
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'studymate_data.json')
    LEGACY_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calcubro_data.json')

    def __init__(self):
        # Datos del perfil del estudiante
        self.student_name = ""
        self.student_career = ""
        self.student_semester = ""
        self.is_logged_in = False

        # Preferencia de tema ('dark' u 'light')
        self.theme = "dark"

        # Materias del semestre
        self.subjects = []

        # Horario semanal (0: Lunes a 4: Viernes)
        self.schedule = [[], [], [], [], []]

        # Materia activa seleccionada para detalle
        self.active_subject = ""

        # Notificaciones y configuraciones
        self.global_notifications = True
        self.reminders = []
        self.diary_entries = []
        self.diary_questions = [
            "¿Cómo te fue hoy?",
            "¿Qué aprendiste?",
            "¿Qué te costó?",
            "¿Qué quieres mejorar?",
            "¿Cuál fue tu pequeño logro?"
        ]

        # Cargar datos persistidos si existen
        self.load_data()

    def save_data(self):
        """Guarda todo el estado en un archivo JSON local con persistencia completa."""
        import json
        payload = {
            'student_name': self.student_name,
            'student_career': self.student_career,
            'student_semester': self.student_semester,
            'is_logged_in': self.is_logged_in,
            'theme': self.theme,
            'subjects': self.subjects,
            'schedule': self.schedule,
            'global_notifications': self.global_notifications,
            'reminders': self.reminders,
            'diary_entries': self.diary_entries
        }
        try:
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[DataStore] Error al guardar datos: {e}")

    def load_data(self):
        """Carga el estado previo desde el archivo JSON si existe."""
        import json
        target_path = self.DATA_FILE if os.path.exists(self.DATA_FILE) else (self.LEGACY_DATA_FILE if os.path.exists(self.LEGACY_DATA_FILE) else None)
        if not target_path:
            return
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.student_name = data.get('student_name', '')
            self.student_career = data.get('student_career', '')
            self.student_semester = data.get('student_semester', '')
            self.is_logged_in = data.get('is_logged_in', bool(self.student_name))
            self.theme = data.get('theme', 'dark')
            self.subjects = data.get('subjects', [])
            self.schedule = data.get('schedule', [[], [], [], [], []])
            self.global_notifications = data.get('global_notifications', True)
            self.reminders = data.get('reminders', [])
            self.diary_entries = data.get('diary_entries', [])
        except Exception as e:
            print(f"[DataStore] Error al cargar datos: {e}")

    def get_active_subject_obj(self):
        for s in self.subjects:
            if s.get('n') == self.active_subject:
                return s
        return None

    def calc_categories_for(self, cat_list):
        pts = 0.0
        ev = 0.0
        tot = 0.0
        for c in cat_list:
            w = float(c.get('w', 0))
            tot += w
            graded = [it for it in c.get('it', []) if it.get('g') is not None]
            if graded:
                avg = sum(float(it['g']) for it in graded) / len(graded)
                pts += avg * w / 100.0
                ev += w
        ev_clamped = min(100.0, max(0.0, ev))
        tot_clamped = min(100.0, max(0.0, tot))
        pend_clamped = max(0.0, 100.0 - ev_clamped)
        return {'pts': pts, 'ev': ev_clamped, 'tot': tot_clamped, 'pend': pend_clamped}

    def get_subject_avg(self, subj):
        cats = subj.get('categories', [])
        if cats:
            k = self.calc_categories_for(cats)
            return (k['pts'] / k['ev'] * 100.0) if k['ev'] > 0 else 0.0
        return float(subj.get('a', 0.0))

    def get_subject_progress(self, subj):
        cats = subj.get('categories', [])
        if cats:
            return min(100.0, max(0.0, self.calc_categories_for(cats)['ev']))
        return min(100.0, max(0.0, float(subj.get('p', 0.0))))

    def get_general_avg(self):
        if not self.subjects:
            return 0.0
        return sum(self.get_subject_avg(s) for s in self.subjects) / len(self.subjects)

    def get_general_adv(self):
        if not self.subjects:
            return 0.0
        adv = sum(self.get_subject_progress(s) for s in self.subjects) / len(self.subjects)
        return min(100.0, max(0.0, adv))

    def calc_need(self, goal, pts, pend, max_score=10.0):
        if pend <= 0:
            if pts >= goal:
                return ('ok', 'Meta alcanzada con tu nota final')
            return ('wa', 'No quedan evaluaciones y la meta no se alcanzó')

        n = (goal - pts) / (pend / 100.0)
        if n > max_score:
            return ('wa', f'Meta no alcanzable: necesitarías {n:.2f} y el máximo es {max_score:.1f}')
        if n <= 0:
            return ('ok', '¡Meta asegurada! Ya la alcanzaste')
        return ('ok', f'Necesitas {n:.2f} en el {pend:.0f}% pendiente')


TAB_MAP = {
    'home': 'home',
    'calc': 'home',
    'diary': 'home',
    'progress': 'home',
    'remind': 'home',
    'subjects': 'subjects',
    'detail': 'subjects',
    'schedule': 'schedule',
    'import_schedule': 'schedule',
    'profile': 'profile',
    'login': 'profile'
}


class StudyMateApp(App):
    active_tab = StringProperty('home')
    current_theme = StringProperty('dark')
    is_dark = BooleanProperty(True)

    # Propiedades reactivas de colores para bind en .kv
    bg_color = ColorProperty(DARK_THEME['bg_color'])
    card_color = ColorProperty(DARK_THEME['card_color'])
    card_border = ColorProperty(DARK_THEME['card_border'])
    primary_color = ColorProperty(DARK_THEME['primary_color'])
    primary_text = ColorProperty(DARK_THEME['primary_text'])
    accent_blue = ColorProperty(DARK_THEME['accent_blue'])
    text_primary = ColorProperty(DARK_THEME['text_primary'])
    text_secondary = ColorProperty(DARK_THEME['text_secondary'])
    nav_bg_color = ColorProperty(DARK_THEME['nav_bg_color'])
    nav_border = ColorProperty(DARK_THEME['nav_border'])
    input_bg = ColorProperty(DARK_THEME['input_bg'])
    btn_pressed = ColorProperty(DARK_THEME['btn_pressed'])
    green_color = ColorProperty(DARK_THEME['green_color'])
    orange_color = ColorProperty(DARK_THEME['orange_color'])

    # Versiones hexadecimales para markup en textos f"[color={app.text_primary_hex}]..."
    bg_color_hex = StringProperty(DARK_THEME['bg_color_hex'])
    card_color_hex = StringProperty(DARK_THEME['card_color_hex'])
    text_primary_hex = StringProperty(DARK_THEME['text_primary_hex'])
    text_secondary_hex = StringProperty(DARK_THEME['text_secondary_hex'])
    accent_blue_hex = StringProperty(DARK_THEME['accent_blue_hex'])
    primary_color_hex = StringProperty(DARK_THEME['primary_color_hex'])
    green_color_hex = StringProperty(DARK_THEME['green_color_hex'])
    orange_color_hex = StringProperty(DARK_THEME['orange_color_hex'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_store = DataStore()
        self.history_stack = []

    def build(self):
        self.title = "StudyMate"

        # Cargar estilos globales
        Builder.load_string(GLOBAL_KV)

        # Cargar los 12 archivos .kv modulares
        kv_dir = os.path.join(base_dir, 'kv')
        kv_files = [
            'welcome.kv',
            'login.kv',
            'home.kv',
            'subjects.kv',
            'detail.kv',
            'schedule.kv',
            'import_schedule.kv',
            'calc.kv',
            'progress.kv',
            'diary.kv',
            'remind.kv',
            'profile.kv'
        ]

        for kv in kv_files:
            file_path = os.path.join(kv_dir, kv)
            if os.path.exists(file_path):
                Builder.load_file(file_path)

        # Contenedor raíz con ScreenManager y Toast flotante
        self.root_layout = FloatLayout()

        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(WelcomeScreen(name='welcome'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(SubjectsScreen(name='subjects'))
        self.sm.add_widget(DetailScreen(name='detail'))
        self.sm.add_widget(ScheduleScreen(name='schedule'))
        self.sm.add_widget(ImportScreen(name='import_schedule'))
        self.sm.add_widget(CalcScreen(name='calc'))
        self.sm.add_widget(ProgressScreen(name='progress'))
        self.sm.add_widget(DiaryScreen(name='diary'))
        self.sm.add_widget(RemindScreen(name='remind'))
        self.sm.add_widget(ProfileScreen(name='profile'))

        self.root_layout.add_widget(self.sm)

        # Widget Toast para mensajes emergentes
        self.toast_label = Label(
            text="",
            size_hint=(0.85, None),
            height='44dp',
            pos_hint={'center_x': 0.5, 'y': 0.11},
            color=(0.063, 0.094, 0.153, 1),
            font_size='13sp',
            bold=True,
            opacity=0
        )
        with self.toast_label.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            self.toast_color = Color(0.224, 0.788, 0.541, 0)
            self.toast_rect = RoundedRectangle(pos=self.toast_label.pos, size=self.toast_label.size, radius=[12])
            self.toast_label.bind(
                pos=lambda obj, val: setattr(self.toast_rect, 'pos', val),
                size=lambda obj, val: setattr(self.toast_rect, 'size', val)
            )

        self.root_layout.add_widget(self.toast_label)

        # Aplicar el tema guardado en el DataStore
        saved_theme = getattr(self.data_store, 'theme', 'dark')
        self.apply_theme(saved_theme)

        return self.root_layout

    def apply_theme(self, theme_name):
        """Aplica la paleta de colores reactiva de forma inmediata y actualiza Window.clearcolor."""
        palette = LIGHT_THEME if theme_name == 'light' else DARK_THEME
        self.current_theme = theme_name
        self.is_dark = (theme_name == 'dark')

        self.bg_color = palette['bg_color']
        self.card_color = palette['card_color']
        self.card_border = palette['card_border']
        self.primary_color = palette['primary_color']
        self.primary_text = palette['primary_text']
        self.accent_blue = palette['accent_blue']
        self.text_primary = palette['text_primary']
        self.text_secondary = palette['text_secondary']
        self.nav_bg_color = palette['nav_bg_color']
        self.nav_border = palette['nav_border']
        self.input_bg = palette['input_bg']
        self.btn_pressed = palette['btn_pressed']
        self.green_color = palette['green_color']
        self.orange_color = palette['orange_color']

        self.bg_color_hex = palette['bg_color_hex']
        self.card_color_hex = palette['card_color_hex']
        self.text_primary_hex = palette['text_primary_hex']
        self.text_secondary_hex = palette['text_secondary_hex']
        self.accent_blue_hex = palette['accent_blue_hex']
        self.primary_color_hex = palette['primary_color_hex']
        self.green_color_hex = palette['green_color_hex']
        self.orange_color_hex = palette['orange_color_hex']

        Window.clearcolor = palette['bg_color']

        if hasattr(self, 'data_store') and self.data_store:
            self.data_store.theme = theme_name
            self.data_store.save_data()

        # Refrescar pantallas activas con contenido dinámico
        if hasattr(self, 'sm') and self.sm:
            for screen in self.sm.screens:
                for meth in ('refresh_dashboard', 'refresh_subjects', 'refresh_classes', 'refresh_reminders', 'refresh_diary', 'refresh_progress', 'rebuild_grades_ui', 'refresh_view'):
                    if hasattr(screen, meth):
                        try:
                            getattr(screen, meth)()
                        except Exception:
                            pass

    def toggle_theme(self):
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme(new_theme)
        return new_theme

    def go_screen(self, screen_name, clear_history=False, direction='left'):
        if clear_history:
            self.history_stack.clear()
        elif self.sm.current != screen_name and self.sm.current != 'welcome':
            self.history_stack.append(self.sm.current)

        self.active_tab = TAB_MAP.get(screen_name, 'home')
        self.sm.transition.direction = direction
        self.sm.current = screen_name

    def go_back(self, direction='right'):
        if self.history_stack:
            prev = self.history_stack.pop()
            self.active_tab = TAB_MAP.get(prev, 'home')
            self.sm.transition.direction = direction
            self.sm.current = prev
        else:
            self.go_screen('home', clear_history=True, direction=direction)

    def show_toast(self, message):
        self.toast_label.text = message
        self.toast_label.opacity = 1
        self.toast_color.a = 1
        Clock.unschedule(self._hide_toast)
        Clock.schedule_once(self._hide_toast, 1.8)

    def _hide_toast(self, dt):
        self.toast_label.opacity = 0
        self.toast_color.a = 0


# Compatibilidad retroactiva con imports de CalcuBroApp
CalcuBroApp = StudyMateApp

if __name__ == '__main__':
    StudyMateApp().run()
