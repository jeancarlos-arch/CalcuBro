from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty
from kivy.app import App


def make_rounded_btn(text, bg_rgba, text_rgba=None, height='44dp', radius=14, bold=True):
    app = App.get_running_app()
    if text_rgba is None:
        text_rgba = app.bg_color if app else (0.063, 0.094, 0.153, 1)
    btn = Button(
        text=text,
        size_hint_y=None,
        height=height,
        background_normal='',
        background_down='',
        background_color=(0, 0, 0, 0),
        color=text_rgba,
        bold=bold,
        font_size='14sp'
    )
    with btn.canvas.before:
        from kivy.graphics import Color, RoundedRectangle
        Color(*bg_rgba)
        r = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[radius])
        btn.bind(pos=lambda inst, val, rect=r: setattr(rect, 'pos', val),
                 size=lambda inst, val, rect=r: setattr(rect, 'size', val))
    return btn


class SubjectModal(ModalView):
    def __init__(self, subject_index=-1, on_save_cb=None, on_delete_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.75)
        self.subject_index = subject_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        app = App.get_running_app()
        store = app.data_store if app else None
        subj_data = {}
        if store and 0 <= subject_index < len(store.subjects):
            subj_data = store.subjects[subject_index]

        card_bg = app.card_color if app else (0.106, 0.149, 0.220, 1)
        card_border = app.card_border if app else (0.173, 0.227, 0.322, 1)
        input_bg = app.input_bg if app else (0.063, 0.094, 0.153, 1)
        text_p = app.text_primary if app else (0.957, 0.965, 0.980, 1)
        text_s = app.text_secondary if app else (0.627, 0.682, 0.753, 1)
        primary_c = app.primary_color if app else (0.337, 0.537, 0.910, 1)
        primary_txt = app.primary_text if app else (0.063, 0.094, 0.153, 1)
        orange_c = app.orange_color if app else (0.949, 0.651, 0.353, 1)
        accent_b = app.accent_blue if app else (0.545, 0.718, 1.0, 1)

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle, Line
            Color(*card_bg)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[14])
            Color(*card_border)
            line = Line(rounded_rectangle=[root.x, root.y, root.width, root.height, 14], width=1)
            def update_root(obj, val, r=rect, l=line):
                r.pos = obj.pos
                r.size = obj.size
                l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, 14]
            root.bind(pos=update_root, size=update_root)

        title = "Editar materia" if subject_index >= 0 else "Nueva materia"
        root.add_widget(Label(text=f"[b]{title}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp', color=text_p))

        # Nombre de la materia
        root.add_widget(Label(text="Nombre de la materia *", size_hint_y=None, height='18dp', halign='left', color=text_s))
        self.txt_name = TextInput(
            text=str(subj_data.get('n', '')),
            hint_text="Ej: Cálculo Diferencial",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_name)

        # Docente
        root.add_widget(Label(text="Docente (opcional)", size_hint_y=None, height='18dp', halign='left', color=text_s))
        self.txt_teacher = TextInput(
            text=str(subj_data.get('teacher', '')),
            hint_text="Ej: Ing. Morales",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_teacher)

        # Fila: Nota mínima y Meta
        grades_row = BoxLayout(size_hint_y=None, height='60dp', spacing=10)

        b_min = BoxLayout(orientation='vertical', spacing=2)
        b_min.add_widget(Label(text="Nota mínima", size_hint_y=None, height='18dp', color=text_s, font_size='11sp'))
        self.txt_min = TextInput(
            text=str(subj_data.get('pmin', 7.0)),
            multiline=False, input_filter='float', size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        b_min.add_widget(self.txt_min)

        b_goal = BoxLayout(orientation='vertical', spacing=2)
        b_goal.add_widget(Label(text="Meta deseada", size_hint_y=None, height='18dp', color=text_s, font_size='11sp'))
        self.txt_goal = TextInput(
            text=str(subj_data.get('pgoal', 8.5)),
            multiline=False, input_filter='float', size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        b_goal.add_widget(self.txt_goal)

        grades_row.add_widget(b_min)
        grades_row.add_widget(b_goal)
        root.add_widget(grades_row)

        # Botones de Acción
        btn_save = make_rounded_btn("Guardar materia", primary_c, primary_txt, height='44dp')
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        if subject_index >= 0:
            btn_del = make_rounded_btn("Eliminar materia", card_bg, orange_c, height='40dp', bold=False)
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = make_rounded_btn("Cancelar", card_bg, accent_b, height='40dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def save(self, *args):
        name = self.txt_name.text.strip()
        if not name:
            App.get_running_app().show_toast("El nombre de la materia es obligatorio")
            return
        teacher = self.txt_teacher.text.strip()
        try:
            pmin = float(self.txt_min.text)
        except ValueError:
            pmin = 7.0
        try:
            pgoal = float(self.txt_goal.text)
        except ValueError:
            pgoal = 8.5

        if self.on_save_cb:
            self.on_save_cb(self.subject_index, name, teacher, pmin, pgoal)
        self.dismiss()

    def delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.subject_index)
        self.dismiss()


class SubjectsScreen(Screen):
    subtitle_text = StringProperty("0 materias este semestre")

    def on_pre_enter(self, *args):
        self.refresh_subjects()

    def refresh_subjects(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        subjects = store.subjects
        count = len(subjects)
        self.subtitle_text = f"{count} {'materia' if count == 1 else 'materias'} registradas"

        container = self.ids.get('subjects_container')
        if not container:
            return

        container.clear_widgets()

        card_bg = app.card_color
        card_border = app.card_border
        text_p = app.text_primary
        text_s = app.text_secondary
        accent_b = app.accent_blue
        bar_bg = app.input_bg

        if not subjects:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', padding=[16, 20], spacing=8)
            with empty_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_c = RoundedRectangle(pos=empty_box.pos, size=empty_box.size, radius=[12])
                Color(*card_border)
                l_c = Line(rounded_rectangle=[empty_box.x, empty_box.y, empty_box.width, empty_box.height, 12], width=1)
                empty_box.bind(pos=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                               size=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))

            lbl1 = Label(text="[b]Aún no has registrado materias[/b]", markup=True,
                         color=text_p, font_size='14sp', size_hint_y=None, height='24dp')
            lbl1.bind(size=lbl1.setter('text_size'))
            lbl2 = Label(text="Toca '+ Agregar materia' para comenzar a organizar tus notas y horario.",
                         color=text_s, font_size='12sp', size_hint_y=None, height='36dp')
            lbl2.bind(size=lbl2.setter('text_size'))
            empty_box.add_widget(lbl1)
            empty_box.add_widget(lbl2)
            container.add_widget(empty_box)
            return

        for idx, subj in enumerate(subjects):
            name = subj.get('n', 'Materia')
            teacher = subj.get('teacher', '')
            pmin = float(subj.get('pmin', 7.0))
            avg = store.get_subject_avg(subj)
            evaluated = store.get_subject_progress(subj)

            card = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[14, 12], spacing=6)
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                Color(*card_border)
                l_rect = Line(rounded_rectangle=[card.x, card.y, card.width, card.height, 12], width=1)
                def _update_card(obj, val, r=rect, l=l_rect):
                    r.pos = obj.pos
                    r.size = obj.size
                    l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, 12]
                card.bind(pos=_update_card, size=_update_card)

            # Fila superior: Nombre, botón editar y Nota
            top_row = BoxLayout(size_hint_y=None, height='28dp', spacing=6)
            lbl_name = Label(text=f"[b]{name}[/b]", markup=True, halign='left', valign='middle',
                             color=text_p, font_size='15sp')
            lbl_name.bind(size=lbl_name.setter('text_size'))

            color_grade = app.green_color if avg >= pmin else app.orange_color
            lbl_grade = Label(text=f"[b]{avg:.2f}[/b]", markup=True, halign='right', valign='middle',
                              color=color_grade, font_size='18sp', size_hint_x=None, width='60dp')
            lbl_grade.bind(size=lbl_grade.setter('text_size'))

            btn_edit = Button(
                text="", font_name='MaterialIcons', size_hint=(None, None), size=('30dp', '28dp'),
                background_normal='', background_color=(0, 0, 0, 0), font_size='16sp',
                color=accent_b
            )
            btn_edit.bind(on_release=lambda x, i=idx: self.open_subject_modal(i))

            top_row.add_widget(lbl_name)
            top_row.add_widget(btn_edit)
            top_row.add_widget(lbl_grade)

            # Subtítulo: Docente o Evaluado %
            sub_info = f"{teacher} · {evaluated:.0f}% evaluado" if teacher else f"Promedio actual · {evaluated:.0f}% evaluado"
            lbl_sub = Label(text=sub_info, halign='left', valign='middle',
                            color=text_s, font_size='12sp', size_hint_y=None, height='18dp')
            lbl_sub.bind(size=lbl_sub.setter('text_size'))

            # Barra de progreso
            from kivy.uix.widget import Widget
            bar = Widget(size_hint_y=None, height='6dp')
            with bar.canvas:
                from kivy.graphics import Color as BColor, RoundedRectangle as BRect
                BColor(*bar_bg)
                r_bg = BRect(pos=bar.pos, size=bar.size, radius=[3])
                BColor(*color_grade)
                r_fill = BRect(pos=bar.pos, size=(bar.width * (min(100, evaluated) / 100.0), bar.height), radius=[3])

                def update_bar(w, val, r_b=r_bg, r_f=r_fill, ev=evaluated):
                    r_b.pos = w.pos
                    r_b.size = w.size
                    r_f.pos = w.pos
                    r_f.size = (w.width * (min(100, max(0, ev)) / 100.0), w.height)

                bar.bind(pos=update_bar, size=update_bar)

            card.add_widget(top_row)
            card.add_widget(lbl_sub)
            card.add_widget(bar)

            # Wrapper interactivo para abrir detalle
            from kivy.uix.relativelayout import RelativeLayout
            rl = RelativeLayout(size_hint_y=None, height='100dp')
            btn_wrapper = Button(background_color=(0, 0, 0, 0), size_hint=(1, 1))
            btn_wrapper.bind(on_release=lambda instance, s=subj: self.open_detail(s))
            rl.add_widget(card)
            rl.add_widget(btn_wrapper)

            # Volver a poner el botón de editar al frente para que reciba click
            btn_edit_overlay = Button(
                text="", size_hint=(None, None), size=('34dp', '34dp'),
                pos_hint={'right': 0.85, 'top': 0.95},
                background_color=(0, 0, 0, 0)
            )
            btn_edit_overlay.bind(on_release=lambda x, i=idx: self.open_subject_modal(i))
            rl.add_widget(btn_edit_overlay)

            container.add_widget(rl)

    def open_detail(self, subject):
        app = App.get_running_app()
        app.data_store.active_subject = subject.get('n', '')
        app.go_screen('detail')

    def open_subject_modal(self, subject_index=-1):
        modal = SubjectModal(
            subject_index=subject_index,
            on_save_cb=self.save_subject,
            on_delete_cb=self.delete_subject
        )
        modal.open()

    def save_subject(self, idx, name, teacher, pmin, pgoal):
        store = App.get_running_app().data_store
        if idx >= 0 and idx < len(store.subjects):
            store.subjects[idx]['n'] = name
            store.subjects[idx]['teacher'] = teacher
            store.subjects[idx]['pmin'] = pmin
            store.subjects[idx]['pgoal'] = pgoal
            App.get_running_app().show_toast(f"Materia '{name}' actualizada")
        else:
            new_subj = {
                'n': name,
                'teacher': teacher,
                'pmin': pmin,
                'pgoal': pgoal,
                'a': 0.0,
                'p': 0.0,
                'categories': [
                    {'n': 'Deberes', 'w': 20, 'm': 'a', 'it': []},
                    {'n': 'Lecciones', 'w': 15, 'm': 'a', 'it': []},
                    {'n': 'Proyecto', 'w': 20, 'm': 'a', 'it': []},
                    {'n': 'Examen final', 'w': 45, 'm': 'a', 'it': []}
                ]
            }
            store.subjects.append(new_subj)
            App.get_running_app().show_toast(f"Materia '{name}' registrada")

        store.save_data()
        self.refresh_subjects()

    def delete_subject(self, idx):
        store = App.get_running_app().data_store
        if 0 <= idx < len(store.subjects):
            removed = store.subjects.pop(idx)
            store.save_data()
            App.get_running_app().show_toast(f"Materia '{removed.get('n', '')}' eliminada")
            self.refresh_subjects()
