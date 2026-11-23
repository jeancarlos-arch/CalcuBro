import datetime
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class HomeScreen(Screen):
    greeting_text = StringProperty("Buenos días")
    student_subtitle = StringProperty("")
    choclito_bubble_text = StringProperty("¡Hola! Revisa tu día y sigue sumando avances.")

    # Horario dinámico de hoy
    active_class_name = StringProperty("Sin clases programadas")
    active_class_room = StringProperty("Toca para abrir tu horario")
    active_class_time = StringProperty("Día libre")
    next_class_info = StringProperty("Registra tus clases en la pestaña Horario")

    # Progreso de materias dinámico
    subjects_count_text = StringProperty("0 materias registradas")
    progress_percent = NumericProperty(0)
    progress_avg_text = StringProperty("0.00")
    motivational_text = StringProperty("¡Vas muy bien, cada paso cuenta!")

    # Pendientes de hoy
    reminders_count_text = StringProperty("0 actividades")
    reminders_summary_text = StringProperty("No tienes pendientes programados")

    def on_pre_enter(self, *args):
        self.refresh_dashboard()

    def refresh_dashboard(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store

        # 1. Datos del estudiante
        raw_name = store.student_name.strip() if store.student_name else ""
        first_name = raw_name.split()[0] if raw_name else ""
        if first_name:
            self.greeting_text = f"Buenos días, {first_name}"
        else:
            self.greeting_text = "Buenos días"

        career = store.student_career.strip() if store.student_career else ""
        semester = store.student_semester.strip() if store.student_semester else ""
        if career and semester:
            self.student_subtitle = f"{career} · {semester}"
        elif career or semester:
            self.student_subtitle = f"{career}{semester}"
        else:
            self.student_subtitle = ""

        # 2. Horario del día actual
        weekday = datetime.date.today().weekday()
        day_idx = min(weekday, 4)  # 0 a 4 (Lunes a Viernes)
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        today_name = day_names[day_idx] if weekday < 5 else "Fin de semana"

        if weekday < 5 and day_idx < len(store.schedule) and store.schedule[day_idx]:
            classes = store.schedule[day_idx]
            first_c = classes[0]
            self.active_class_name = first_c.get('n', 'Clase')
            self.active_class_room = f"Aula: {first_c.get('a', 'Por definir')}"
            self.active_class_time = f"{today_name} · {first_c.get('h', '')}"

            if len(classes) > 1:
                next_c = classes[1]
                self.next_class_info = f"Siguiente: {next_c.get('n', '')} · {next_c.get('h', '')}"
            else:
                self.next_class_info = "Única clase del día"
        else:
            self.active_class_name = "Sin clases programadas para hoy"
            self.active_class_room = "Toca para ver o agregar clases en tu horario"
            self.active_class_time = f"{today_name} · Sin horario activo"
            self.next_class_info = "Organiza tu semana en la pestaña Horario"

        # 3. Pendientes de hoy (Recordatorios)
        active_rems = [r for r in store.reminders if r.get('on', 0)] or store.reminders
        cnt = len(active_rems)
        if active_rems:
            self.reminders_count_text = f"{cnt} {'actividad' if cnt == 1 else 'actividades'}"
            top2 = active_rems[:2]
            self.reminders_summary_text = "\n".join([f"• {r.get('t', '')} · {r.get('d', '')}" for r in top2])
        else:
            self.reminders_count_text = "0 actividades"
            self.reminders_summary_text = "No tienes pendientes para hoy. ¡Todo al día!"

        # 4. Materias y progreso general del semestre
        subjects = store.subjects
        count = len(subjects)
        self.subjects_count_text = f"{count} {'materia' if count == 1 else 'materias'} en curso"

        if subjects:
            avg = store.get_general_avg()
            adv = store.get_general_adv()
            self.progress_percent = int(round(adv))
            self.progress_avg_text = f"{avg:.2f}"
            self.motivational_text = f"Promedio general {avg:.2f}. ¡Vas muy bien, cada paso cuenta!"
        else:
            avg = None
            self.progress_percent = 0
            self.progress_avg_text = "0.00"
            self.motivational_text = "Registra tus materias para monitorear tu progreso académico."

        # 5. Mensaje dinámico de Choclito adaptado al usuario
        name_suffix = f", {first_name}" if first_name else ""
        pending_phrase = (
            "no tienes pendientes activos"
            if cnt == 0
            else f"tienes {cnt} {'pendiente' if cnt == 1 else 'pendientes'}"
        )
        if avg is not None:
            self.choclito_bubble_text = (
                f"Hoy {pending_phrase} y vas con {avg:.2f} de promedio. ¡Tú puedes{name_suffix}!"
            )
        else:
            self.choclito_bubble_text = (
                f"Hoy {pending_phrase}. Registra tus materias para ver tu promedio{name_suffix}."
            )

    def navigate(self, screen_name):
        app = App.get_running_app()
        app.go_screen(screen_name)