import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.app import App


def make_rounded_btn(text, bg_color, text_color=None, height='44dp', bold=True):
    """Crea un botón con esquinas redondeadas usando canvas."""
    from kivy.metrics import dp
    app = App.get_running_app()
    if text_color is None:
        text_color = app.primary_text if app else (0.063, 0.094, 0.153, 1)
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


class ClassModal(ModalView):
    def __init__(self, day_index, class_index, on_save_cb, on_delete_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.75)
        self.day_index = day_index
        self.class_index = class_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        app = App.get_running_app()
        store = app.data_store if app else None
        class_data = {}
        if store and 0 <= day_index < len(store.schedule):
            day_classes = store.schedule[day_index]
            if 0 <= class_index < len(day_classes):
                class_data = day_classes[class_index]

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

        title = "Editar clase" if class_index >= 0 else "Agregar clase"
        root.add_widget(Label(text=f"[b]{title}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp', color=text_p))

        # Materia: con opción de seleccionar de materias registradas o escribir
        subject_names = [s.get('n', '') for s in store.subjects if s.get('n')] if store else []
        if subject_names:
            root.add_widget(Label(text="Seleccionar de tus materias:", size_hint_y=None, height='18dp', halign='left', color=text_s))
            default_sp = class_data.get('n', '') if class_data.get('n') in subject_names else subject_names[0]
            self.sp_subject = Spinner(text=default_sp, values=subject_names, size_hint_y=None, height='38dp', background_color=card_bg, color=text_p)
            self.sp_subject.bind(text=lambda inst, val: setattr(self.txt_name, 'text', val))
            root.add_widget(self.sp_subject)

        root.add_widget(Label(text="Nombre de la materia *", size_hint_y=None, height='18dp', halign='left', color=text_s))
        init_name = str(class_data.get('n', '')) or (subject_names[0] if subject_names else '')
        self.txt_name = TextInput(
            text=init_name,
            hint_text="Ej: Programación II",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_name)

        root.add_widget(Label(text="Horario (ej: 08:00 – 10:00) *", size_hint_y=None, height='18dp', halign='left', color=text_s))
        self.txt_time = TextInput(
            text=str(class_data.get('h', '08:00 – 10:00')),
            hint_text="08:00 – 10:00",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_time)

        root.add_widget(Label(text="Aula o enlace virtual", size_hint_y=None, height='18dp', halign='left', color=text_s))
        self.txt_room = TextInput(
            text=str(class_data.get('a', 'Aula 101')),
            hint_text="Ej: Lab 3, Aula B-204, Zoom",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_room)

        btn_save = make_rounded_btn("Guardar clase", primary_c, primary_txt, height='44dp')
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        if class_index >= 0:
            btn_del = make_rounded_btn("Eliminar clase", card_bg, orange_c, height='40dp', bold=False)
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = make_rounded_btn("Cancelar", card_bg, accent_b, height='40dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def save(self, *args):
        name = self.txt_name.text.strip()
        time_str = self.txt_time.text.strip()
        room = self.txt_room.text.strip()
        if not name or not time_str:
            App.get_running_app().show_toast("Materia y horario son obligatorios")
            return
        if self.on_save_cb:
            self.on_save_cb(self.day_index, self.class_index, name, time_str, room)
        self.dismiss()

    def delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.day_index, self.class_index)
        self.dismiss()


class ScheduleScreen(Screen):
    week_range_text = StringProperty("")
    current_day_idx = NumericProperty(0)  # 0: Lun, 1: Mar, 2: Mie, 3: Jue, 4: Vie
    class_reminder_active = BooleanProperty(True)

    d0_text = StringProperty("Lun\n--")
    d1_text = StringProperty("Mar\n--")
    d2_text = StringProperty("Mié\n--")
    d3_text = StringProperty("Jue\n--")
    d4_text = StringProperty("Vie\n--")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.week_offset = 0
        self.day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

    def on_pre_enter(self, *args):
        today_wd = datetime.date.today().weekday()
        if self.week_offset == 0:
            self.current_day_idx = min(today_wd, 4)
        self.update_week_text()
        self.refresh_classes()

    def get_monday_of_current_view(self):
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        monday += datetime.timedelta(weeks=self.week_offset)
        return monday

    def update_week_text(self):
        months_es = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        mon = self.get_monday_of_current_view()
        fri = mon + datetime.timedelta(days=4)

        m_str1 = months_es[mon.month - 1]
        m_str2 = months_es[fri.month - 1]

        if mon.month == fri.month:
            self.week_range_text = f"{mon.day} – {fri.day} {m_str1} {mon.year}"
        else:
            self.week_range_text = f"{mon.day} {m_str1} – {fri.day} {m_str2} {mon.year}"

        d_names = ["Lun", "Mar", "Mié", "Jue", "Vie"]
        chips_texts = []
        for i in range(5):
            d_date = mon + datetime.timedelta(days=i)
            chips_texts.append(f"{d_names[i]}\n{d_date.day}")

        self.d0_text = chips_texts[0]
        self.d1_text = chips_texts[1]
        self.d2_text = chips_texts[2]
        self.d3_text = chips_texts[3]
        self.d4_text = chips_texts[4]

    def prev_week(self):
        self.week_offset -= 1
        self.update_week_text()
        self.refresh_classes()

    def next_week(self):
        self.week_offset += 1
        self.update_week_text()
        self.refresh_classes()

    def select_day(self, day_index):
        self.current_day_idx = day_index
        self.refresh_classes()

    def refresh_classes(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        container = self.ids.get('classes_container')
        if not container:
            return
        container.clear_widgets()

        if 0 <= self.current_day_idx < len(store.schedule):
            classes = store.schedule[self.current_day_idx]
        else:
            classes = []

        card_bg = app.card_color
        card_border = app.card_border
        text_p = app.text_primary
        text_s = app.text_secondary
        accent_b = app.accent_blue
        green_hex = app.green_color_hex
        blue_hex = app.accent_blue_hex

        if not classes:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[16, 16], spacing=6)
            with empty_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_c = RoundedRectangle(pos=empty_box.pos, size=empty_box.size, radius=[12])
                Color(*card_border)
                l_c = Line(rounded_rectangle=[empty_box.x, empty_box.y, empty_box.width, empty_box.height, 12], width=1)
                empty_box.bind(pos=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                               size=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))

            day_name = self.day_names[self.current_day_idx]
            lbl1 = Label(text=f"[b]Sin clases programadas para el {day_name}[/b]", markup=True,
                         color=text_p, font_size='14sp', size_hint_y=None, height='24dp')
            lbl1.bind(size=lbl1.setter('text_size'))
            lbl2 = Label(text="Toca '+ Agregar clase' para registrar tu horario de este día.",
                         color=text_s, font_size='12sp', size_hint_y=None, height='36dp')
            lbl2.bind(size=lbl2.setter('text_size'))
            empty_box.add_widget(lbl1)
            empty_box.add_widget(lbl2)
            container.add_widget(empty_box)
            return

        is_today = (self.week_offset == 0 and self.current_day_idx == datetime.date.today().weekday())

        for idx, c in enumerate(classes):
            tag_text = ""
            if is_today:
                if idx == 0:
                    tag_text = f" [color={green_hex}]· En curso[/color]"
                elif idx == 1:
                    tag_text = f" [color={blue_hex}]· Próxima[/color]"

            card = BoxLayout(orientation='vertical', size_hint_y=None, height='86dp', padding=[14, 10], spacing=4)
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                Color(*card_border)
                l_bg = Line(rounded_rectangle=[card.x, card.y, card.width, card.height, 12], width=1)
                def _update_c(obj, val, r=r_bg, l=l_bg):
                    r.pos = obj.pos
                    r.size = obj.size
                    l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, 12]
                card.bind(pos=_update_c, size=_update_c)

            top_row = BoxLayout(size_hint_y=None, height='20dp')
            lbl_time = Label(text=f"[font=MaterialIcons][/font]  {c.get('h', '')}{tag_text}", markup=True,
                             color=accent_b, font_size='12sp',
                             halign='left', valign='middle')
            lbl_time.bind(size=lbl_time.setter('text_size'))
            top_row.add_widget(lbl_time)

            lbl_name = Label(text=f"[b]{c.get('n', '')}[/b]", markup=True, color=text_p,
                             font_size='15sp', halign='left', valign='middle', size_hint_y=None, height='24dp')
            lbl_name.bind(size=lbl_name.setter('text_size'))

            room_str = f"[font=MaterialIcons][/font]  Aula: {c.get('a', '')}" if c.get('a') else "[font=MaterialIcons][/font]  Aula no especificada"
            lbl_room = Label(text=room_str, markup=True, color=text_s,
                             font_size='12sp', halign='left', valign='middle', size_hint_y=None, height='18dp')
            lbl_room.bind(size=lbl_room.setter('text_size'))

            card.add_widget(top_row)
            card.add_widget(lbl_name)
            card.add_widget(lbl_room)

            from kivy.uix.relativelayout import RelativeLayout
            rl = RelativeLayout(size_hint_y=None, height='86dp')
            btn_click = Button(background_color=(0, 0, 0, 0), size_hint=(1, 1))
            btn_click.bind(on_release=lambda x, i=idx: self.open_class_modal(i))
            rl.add_widget(card)
            rl.add_widget(btn_click)
            container.add_widget(rl)

    def open_class_modal(self, class_index=-1):
        modal = ClassModal(
            day_index=self.current_day_idx,
            class_index=class_index,
            on_save_cb=self.save_class,
            on_delete_cb=self.delete_class
        )
        modal.open()

    def save_class(self, day_idx, class_idx, name, time_str, room):
        store = App.get_running_app().data_store
        while len(store.schedule) <= day_idx:
            store.schedule.append([])

        day_classes = store.schedule[day_idx]
        if 0 <= class_idx < len(day_classes):
            day_classes[class_idx] = {'n': name, 'h': time_str, 'a': room}
            App.get_running_app().show_toast(f"Clase '{name}' actualizada")
        else:
            day_classes.append({'n': name, 'h': time_str, 'a': room})
            App.get_running_app().show_toast(f"Clase '{name}' agregada")

        store.save_data()
        self.refresh_classes()

    def delete_class(self, day_idx, class_idx):
        store = App.get_running_app().data_store
        if 0 <= day_idx < len(store.schedule):
            day_classes = store.schedule[day_idx]
            if 0 <= class_idx < len(day_classes):
                removed = day_classes.pop(class_idx)
                store.save_data()
                App.get_running_app().show_toast(f"Clase '{removed.get('n', '')}' eliminada")
                self.refresh_classes()

    def toggle_reminder(self):
        self.class_reminder_active = not self.class_reminder_active
        msg = "Recordatorios de clase activados (30 min antes)" if self.class_reminder_active else "Recordatorios de clase desactivados"
        App.get_running_app().show_toast(msg)

    def go_import(self):
        App.get_running_app().go_screen('import_schedule')
