from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


def make_rounded_btn(text, bg_color, text_color, height='44dp', bold=True):
    """Crea un botón con esquinas redondeadas usando canvas."""
    from kivy.metrics import dp
    btn = Button(
        text=text, size_hint_y=None, height=height,
        background_normal='', background_down='',
        background_color=(0, 0, 0, 0),
        color=text_color, bold=bold, font_size='14sp'
    )
    from kivy.graphics import Color, RoundedRectangle
    with btn.canvas.before:
        c = Color(*bg_color)
        r = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])
        btn.bind(pos=lambda obj, val, _r=r: setattr(_r, 'pos', val),
                 size=lambda obj, val, _r=r: setattr(_r, 'size', val))
    return btn


def compute_dynamic_achievements(store):
    """Calcula logros en tiempo real basados en los datos reales del estudiante."""
    achievements = []
    subjects = store.subjects

    # 1. Primera materia
    has_subjs = len(subjects) >= 1
    achievements.append(("Primera materia registrada", has_subjs))

    # 2. Extraer todas las calificaciones reales
    all_grades = []
    for s in subjects:
        for c in s.get('categories', []):
            for it in c.get('it', []):
                if it.get('g') is not None:
                    all_grades.append(float(it['g']))

    # 3. Primer 9.0 o superior
    has_nine = any(g >= 9.0 for g in all_grades)
    achievements.append(("Primer 9.0 o superior en una evaluación", has_nine))

    # 4. Meta alcanzada
    goal_subjs = [s.get('n', 'Materia') for s in subjects if store.get_subject_avg(s) >= float(s.get('pgoal', 8.5)) and store.get_subject_progress(s) > 0]
    if goal_subjs:
        achievements.append((f"Meta alcanzada en {goal_subjs[0]}", True))
    else:
        achievements.append(("Alcanzar meta en alguna materia", False))

    # 5. Diario
    has_diary = len(store.diary_entries) >= 1
    achievements.append(("Primera entrada en tu diario", has_diary))

    # 6. Constancia en el diario
    diary_streak = len(store.diary_entries) >= 3
    achievements.append(("Constancia en el diario (3+ entradas)", diary_streak))

    # 7. Horario
    has_schedule = any(len(day_classes) > 0 for day_classes in store.schedule)
    achievements.append(("Horario de clases configurado", has_schedule))

    # 8. Promedio sobresaliente
    avg = store.get_general_avg()
    achievements.append((f"Promedio general >= 9.0 (actual: {avg:.2f})", avg >= 9.0 and has_subjs))

    return achievements


class AchievementsModal(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.72)
        self.auto_dismiss = True

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        root.add_widget(Label(text="[b]Tus logros[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        store = App.get_running_app().data_store
        achievements = compute_dynamic_achievements(store)

        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(do_scroll_x=False)
        box_ach = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=[0, 4])
        box_ach.bind(minimum_height=box_ach.setter('height'))

        for text, completed in achievements:
            row = BoxLayout(size_hint_y=None, height='44dp', padding=[10, 8])
            with row.canvas.before:
                from kivy.graphics import Color as RColor, RoundedRectangle as RRect
                RColor(0.063, 0.094, 0.153, 1)
                r_r = RRect(pos=row.pos, size=row.size, radius=[8])
                row.bind(pos=lambda obj, val, r=r_r: setattr(r, 'pos', val),
                         size=lambda obj, val, r=r_r: setattr(r, 'size', val))

            star_color = "39c98a" if completed else "a0aec0"
            star_icon = "" if completed else ""
            lbl = Label(text=f"[color={star_color}][font=MaterialIcons]{star_icon}[/font][/color]  {text}", markup=True,
                        font_size='13sp', halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)
            box_ach.add_widget(row)

        scroll.add_widget(box_ach)
        root.add_widget(scroll)

        btn_close = make_rounded_btn("Cerrar", (0.106, 0.149, 0.220, 1), (0.545, 0.718, 1.0, 1), height='42dp', bold=False)
        btn_close.bind(on_release=self.dismiss)
        root.add_widget(btn_close)

        self.add_widget(root)


class ProgressScreen(Screen):
    general_avg_text = StringProperty("0.00")
    semester_adv_text = StringProperty("0%")
    goals_met_text = StringProperty("0 de 0")
    best_subject_name = StringProperty("Sin materias")
    best_subject_score = StringProperty("-")
    focus_subject_name = StringProperty("Sin materias")
    focus_subject_score = StringProperty("-")

    # Puntuaciones y alturas para el gráfico de barras dinámico
    p1_score_text = StringProperty("-")
    p2_score_text = StringProperty("-")
    p1_height = NumericProperty(0)
    p2_height = NumericProperty(0)
    current_height = NumericProperty(0)

    def on_pre_enter(self, *args):
        self.refresh_stats()

    def refresh_stats(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        subjects = store.subjects
        avg = store.get_general_avg()
        adv = store.get_general_adv()

        self.general_avg_text = f"{avg:.2f}"
        self.semester_adv_text = f"{adv:.0f}%"
        self.current_height = min(100, max(0, int(avg * 10)))

        # Metas cumplidas
        if subjects:
            met = sum(1 for s in subjects if store.get_subject_avg(s) >= float(s.get('pgoal', 8.5)) and store.get_subject_progress(s) > 0)
            self.goals_met_text = f"{met} de {len(subjects)}"
        else:
            self.goals_met_text = "0 de 0"

        # Materias mejor y a mejorar
        sorted_subjs = sorted(subjects, key=lambda s: store.get_subject_avg(s), reverse=True)
        if sorted_subjs:
            best = sorted_subjs[0]
            worst = sorted_subjs[-1]
            self.best_subject_name = best.get('n', '')
            self.best_subject_score = f"{store.get_subject_avg(best):.2f}"
            self.focus_subject_name = worst.get('n', '')
            self.focus_subject_score = f"{store.get_subject_avg(worst):.2f}"
        else:
            self.best_subject_name = "Sin materias"
            self.best_subject_score = "-"
            self.focus_subject_name = "Sin materias"
            self.focus_subject_score = "-"

        # Cálculo dinámico de Parciales según notas ingresadas
        all_grades = []
        for s in subjects:
            for c in s.get('categories', []):
                for it in c.get('it', []):
                    if it.get('g') is not None:
                        all_grades.append(float(it['g']))

        if len(all_grades) >= 2:
            mid = len(all_grades) // 2
            p1 = sum(all_grades[:mid]) / mid
            p2 = sum(all_grades[mid:]) / (len(all_grades) - mid)
            self.p1_score_text = f"{p1:.2f}"
            self.p1_height = min(100, max(0, int(p1 * 10)))
            self.p2_score_text = f"{p2:.2f}"
            self.p2_height = min(100, max(0, int(p2 * 10)))
        elif len(all_grades) == 1:
            p1 = all_grades[0]
            self.p1_score_text = f"{p1:.2f}"
            self.p1_height = min(100, max(0, int(p1 * 10)))
            self.p2_score_text = "-"
            self.p2_height = 0
        else:
            self.p1_score_text = "-"
            self.p1_height = 0
            self.p2_score_text = "-"
            self.p2_height = 0

    def show_achievements(self):
        modal = AchievementsModal()
        modal.open()
