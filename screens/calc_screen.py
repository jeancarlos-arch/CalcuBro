from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class CalcScreen(Screen):
    """Calculadora académica basada en el prototipo StudyMate."""

    scale_max = NumericProperty(10.0)
    scale_min = NumericProperty(7.0)
    scale_goal = NumericProperty(8.5)

    evaluated_text = StringProperty("70%")
    pending_text = StringProperty("30%")
    current_avg_text = StringProperty("8.14")
    accum_pts_text = StringProperty("5.70 de 10.0")
    max_possible_text = StringProperty("8.70")
    goal_status_text = StringProperty("")
    min_status_text = StringProperty("")
    sim_grade_text = StringProperty("")
    sim_result_text = StringProperty("")
    warning_text = StringProperty("")
    progress_percent = NumericProperty(70)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # La lista pertenece a esta pantalla, no a toda la clase.
        self.grades_list = []
        self.reset_example(rebuild=False)

    def on_pre_enter(self, *args):
        self.rebuild_grades_ui()
        self.calculate_results(silent=True)

    def set_scale_value(self, field, text):
        """Lee los campos de escala sin provocar errores al borrar o editar."""
        try:
            value = float(text)
        except (TypeError, ValueError):
            return

        if field == "max":
            if value > 0:
                self.scale_max = value
        elif field == "min":
            self.scale_min = value
        elif field == "goal":
            self.scale_goal = value

        self.calculate_results(silent=True)

    def reset_example(self, rebuild=True):
        """Restaura los mismos datos iniciales del prototipo HTML."""
        self.scale_max = 10.0
        self.scale_min = 7.0
        self.scale_goal = 8.5
        self.sim_grade_text = ""
        self.grades_list = [
            {"n": "Nota 1", "g": 8.0, "w": 25.0},
            {"n": "Nota 2", "g": 7.5, "w": 25.0},
            {"n": "Nota 3", "g": 9.0, "w": 20.0},
        ]

        if rebuild:
            self.rebuild_grades_ui()

        # Actualiza los campos visibles al restablecer, si la vista ya está cargada.
        for field, value in (
            ("scale_max_input", "10"),
            ("scale_min_input", "7"),
            ("scale_goal_input", "8.5"),
        ):
            widget = self.ids.get(field)
            if widget is not None:
                widget.text = value

        self.calculate_results(silent=True)

    def update_grade_val(self, index, field, text):
        if not 0 <= index < len(self.grades_list):
            return

        try:
            value = float(text) if text.strip() else 0.0
        except (TypeError, ValueError):
            return

        if value < 0:
            value = 0.0

        self.grades_list[index][field] = value
        self.calculate_results(silent=True)

    def add_grade(self):
        """Agrega una evaluación nueva y actualiza la lista y los resultados."""
        number = len(self.grades_list) + 1
        self.grades_list.append({"n": f"Nota {number}", "g": 0.0, "w": 0.0})
        self.rebuild_grades_ui()
        self.calculate_results(silent=True)

    def remove_grade(self, index):
        """Elimina la evaluación seleccionada."""
        if 0 <= index < len(self.grades_list):
            self.grades_list.pop(index)
            self.rebuild_grades_ui()
            self.calculate_results(silent=True)

    def rebuild_grades_ui(self):
        container = self.ids.get("grades_container")
        if container is None:
            return

        container.clear_widgets()

        for index, item in enumerate(self.grades_list):
            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height="94dp",
                padding=[12, 8],
                spacing=6,
            )

            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                background = RoundedRectangle(
                    pos=card.pos, size=card.size, radius=[12]
                )
                card.bind(
                    pos=lambda obj, value, shape=background: setattr(shape, "pos", value),
                    size=lambda obj, value, shape=background: setattr(shape, "size", value),
                )

            title_row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height="28dp",
                spacing="8dp",
            )
            title = Label(
                text=item["n"],
                color=(0.957, 0.965, 0.980, 1),
                bold=True,
                font_size="14sp",
                halign="left",
                valign="middle",
                text_size=(None, None),
            )
            delete_button = Button(
                text="Eliminar",
                size_hint=(None, 1),
                width="82dp",
                background_normal="",
                background_color=(0.173, 0.227, 0.322, 1),
                color=(0.949, 0.651, 0.353, 1),
                font_size="12sp",
            )
            delete_button.bind(
                on_release=lambda _button, i=index: self.remove_grade(i)
            )
            title_row.add_widget(title)
            title_row.add_widget(delete_button)

            fields = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height="42dp",
                spacing="10dp",
            )

            grade_box = BoxLayout(orientation="horizontal", spacing="5dp")
            grade_box.add_widget(Label(
                text="Nota",
                color=(0.627, 0.682, 0.753, 1),
                font_size="12sp",
                size_hint_x=None,
                width="38dp",
            ))
            grade_input = TextInput(
                text=str(item["g"]),
                multiline=False,
                input_filter="float",
                font_size="14sp",
                size_hint_y=None,
                height="38dp",
                background_normal="",
                background_active="",
                background_color=(0.063, 0.094, 0.153, 1),
                foreground_color=(0.957, 0.965, 0.980, 1),
                cursor_color=(0.545, 0.718, 1.0, 1),
                padding=[8, 8],
            )
            grade_input.bind(
                text=lambda instance, value, i=index:
                    self.update_grade_val(i, "g", value)
            )
            grade_box.add_widget(grade_input)

            weight_box = BoxLayout(orientation="horizontal", spacing="5dp")
            weight_box.add_widget(Label(
                text="Peso %",
                color=(0.627, 0.682, 0.753, 1),
                font_size="12sp",
                size_hint_x=None,
                width="48dp",
            ))
            weight_input = TextInput(
                text=str(item["w"]),
                multiline=False,
                input_filter="float",
                font_size="14sp",
                size_hint_y=None,
                height="38dp",
                background_normal="",
                background_active="",
                background_color=(0.063, 0.094, 0.153, 1),
                foreground_color=(0.957, 0.965, 0.980, 1),
                cursor_color=(0.545, 0.718, 1.0, 1),
                padding=[8, 8],
            )
            weight_input.bind(
                text=lambda instance, value, i=index:
                    self.update_grade_val(i, "w", value)
            )
            weight_box.add_widget(weight_input)

            fields.add_widget(grade_box)
            fields.add_widget(weight_box)
            card.add_widget(title_row)
            card.add_widget(fields)
            container.add_widget(card)

    @staticmethod
    def _need(goal, points, pending, maximum):
        if pending <= 0:
            if points >= goal:
                return "Meta alcanzada con tu nota final"
            return "No quedan evaluaciones y la meta no se alcanzó"

        needed = (goal - points) / (pending / 100.0)
        if needed > maximum:
            return (
                f"Meta no alcanzable: necesitarías {needed:.2f} "
                f"y el máximo es {maximum:g}"
            )
        if needed <= 0:
            return "¡Meta asegurada! Ya la alcanzaste"
        return f"Necesitas {needed:.2f} en el {pending:.0f}% pendiente"

    def calculate_results(self, silent=False):
        maximum = self.scale_max if self.scale_max > 0 else 10.0
        evaluated = sum(item["w"] for item in self.grades_list)
        points = sum(
            item["g"] * item["w"] / 100.0 for item in self.grades_list
        )
        pending = max(0.0, 100.0 - evaluated)

        self.progress_percent = min(100.0, max(0.0, evaluated))

        if evaluated > 100.0:
            self.warning_text = (
                f"Los pesos suman {evaluated:.1f}%. "
                "Ajusta para que no superen 100%."
            )
            self.evaluated_text = f"{evaluated:.1f}%"
            self.pending_text = "0%"
            self.current_avg_text = "—"
            self.accum_pts_text = f"{points:.2f} de {maximum:g}"
            self.max_possible_text = "—"
            self.goal_status_text = ""
            self.min_status_text = ""
            self.sim_result_text = ""
            return

        self.warning_text = ""
        average = points / evaluated * 100.0 if evaluated > 0 else 0.0
        final_max = points + maximum * pending / 100.0

        self.evaluated_text = f"{evaluated:.0f}%"
        self.pending_text = f"{pending:.0f}%"
        self.current_avg_text = f"{average:.2f}"
        self.accum_pts_text = f"{points:.2f} de {maximum:g}"
        self.max_possible_text = f"{final_max:.2f}"

        self.goal_status_text = (
            f"Objetivo {self.scale_goal:g}: "
            f"{self._need(self.scale_goal, points, pending, maximum)}"
        )
        self.min_status_text = (
            f"Para aprobar ({self.scale_min:g}): "
            f"{self._need(self.scale_min, points, pending, maximum)}"
        )

        simulation = self.sim_grade_text.strip()
        if simulation and pending > 0:
            try:
                simulated_grade = float(simulation)
                simulated_final = points + simulated_grade * pending / 100.0
                status = (
                    "aprobado"
                    if simulated_final >= self.scale_min
                    else "por debajo del mínimo"
                )
                self.sim_result_text = (
                    f"Con {simulated_grade:g} en lo pendiente, "
                    f"tu nota final sería {simulated_final:.2f} ({status})."
                )
            except ValueError:
                self.sim_result_text = ""
        else:
            self.sim_result_text = ""

        if not silent:
            app = App.get_running_app()
            if app and hasattr(app, "show_toast"):
                app.show_toast("Resultados calculados")

