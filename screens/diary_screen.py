import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App

SPANISH_MONTHS = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

def make_rounded_btn(text, bg_rgba, text_rgba=(0.063, 0.094, 0.153, 1), height='44dp', radius=14, bold=True):
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


def make_rounded_input(text="", height='68dp', multiline=True, hint_text=""):
    """Crea un campo de texto moderno con bordes redondeados y tema oscuro."""
    from kivy.metrics import dp
    txt = TextInput(
        text=text,
        hint_text=hint_text,
        multiline=multiline,
        size_hint_y=None,
        height=height,
        background_normal='',
        background_active='',
        background_color=(0, 0, 0, 0),
        foreground_color=(0.957, 0.965, 0.980, 1),
        cursor_color=(0.545, 0.718, 1.0, 1),
        hint_text_color=(0.627, 0.682, 0.753, 0.5),
        padding=[dp(12), dp(10)],
        font_size='13sp'
    )
    with txt.canvas.before:
        from kivy.graphics import Color, RoundedRectangle, Line
        Color(0.106, 0.149, 0.220, 1)
        r = RoundedRectangle(pos=txt.pos, size=txt.size, radius=[dp(12)])
        Color(0.173, 0.227, 0.322, 0.9)
        l = Line(rounded_rectangle=[txt.x, txt.y, txt.width, txt.height, dp(12)], width=dp(1))

        def _update(obj, val, _r=r, _l=l):
            _r.pos = obj.pos
            _r.size = obj.size
            _l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, dp(12)]

        txt.bind(pos=_update, size=_update)
    return txt


class DiaryEntryModal(ModalView):
    def __init__(self, entry_index, on_save_cb, on_delete_cb, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.92, 0.85)
        self.auto_dismiss = True
        self.entry_index = entry_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        store = App.get_running_app().data_store
        entry = store.diary_entries[entry_index] if entry_index < len(store.diary_entries) else {'d': '', 'v': []}
        questions = store.diary_questions

        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation='vertical', padding=14, spacing=8, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            self.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        root.add_widget(Label(text=f"[b]{entry.get('d', '')}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        self.inputs = []
        for i, q in enumerate(questions):
            root.add_widget(Label(text=q, color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                                  size_hint_y=None, height='20dp', halign='left'))
            ans = entry.get('v', [])[i] if i < len(entry.get('v', [])) else ''
            txt = make_rounded_input(text=ans, height='64dp', multiline=True)
            self.inputs.append(txt)
            root.add_widget(txt)

        btn_save = make_rounded_btn("Guardar cambios", (0.337, 0.537, 0.910, 1), (0.063, 0.094, 0.153, 1), height='44dp')
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        btn_del = make_rounded_btn("Eliminar entrada", (0.106, 0.149, 0.220, 1), (0.949, 0.651, 0.353, 1), height='40dp', bold=False)
        btn_del.bind(on_release=self.delete)
        root.add_widget(btn_del)

        btn_cancel = make_rounded_btn("Cancelar", (0.106, 0.149, 0.220, 1), (0.545, 0.718, 1.0, 1), height='40dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def save(self, *args):
        new_values = [inp.text.strip() for inp in self.inputs]
        self.on_save_cb(self.entry_index, new_values)
        self.dismiss()

    def delete(self, *args):
        self.on_delete_cb(self.entry_index)
        self.dismiss()


class DiaryScreen(Screen):
    active_tab = NumericProperty(0)  # 0: Nueva entrada, 1: Historial
    history_tab_title = StringProperty("Historial (0)")
    today_diary_title = StringProperty("Tu diario de hoy")

    def on_pre_enter(self, *args):
        self.refresh_diary_view()

    def set_tab(self, tab_index):
        self.active_tab = tab_index
        self.refresh_diary_view()

    def refresh_diary_view(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        entries = store.diary_entries
        self.history_tab_title = f"Historial ({len(entries)})"

        t = datetime.date.today()
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        month_names = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        self.today_diary_title = f"{day_names[t.weekday()]} {t.day} de {month_names[t.month-1]} de {t.year}"

        container = self.ids.get('diary_container')
        if not container:
            return
        container.clear_widgets()

        if self.active_tab == 0:
            # Vista Nueva Entrada
            self.input_widgets = []
            for q in store.diary_questions:
                lbl = Label(text=q, color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                            size_hint_y=None, height='24dp', halign='left', valign='bottom')
                lbl.bind(size=lbl.setter('text_size'))
                txt = make_rounded_input(height='68dp', multiline=True, hint_text="Escribe aquí tu reflexión...")
                self.input_widgets.append(txt)
                container.add_widget(lbl)
                container.add_widget(txt)

            btn_save = make_rounded_btn("Guardar entrada", (0.337, 0.537, 0.910, 1), (0.063, 0.094, 0.153, 1), height='46dp', radius=14)
            btn_save.bind(on_release=lambda x: self.save_new_entry())
            container.add_widget(btn_save)

        else:
            # Vista Historial
            if not entries:
                lbl_empty = Label(text="Aún no hay entradas. Cuando quieras, escribe la primera.",
                                  color=(0.627, 0.682, 0.753, 1), font_size='13sp', size_hint_y=None, height='60dp')
                container.add_widget(lbl_empty)
                return

            for idx, entry in enumerate(entries):
                card = BoxLayout(orientation='vertical', size_hint_y=None, height='92dp', padding=[14, 10], spacing=4)
                with card.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle
                    Color(0.106, 0.149, 0.220, 1)
                    r_c = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                    card.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                              size=lambda obj, val, r=r_c: setattr(r, 'size', val))

                row_t = BoxLayout(size_hint_y=None, height='22dp')
                lbl_date = Label(text=f"[b]{entry.get('d', '')}[/b]", markup=True, halign='left',
                                 color=(0.957, 0.965, 0.980, 1), font_size='14sp')
                lbl_date.bind(size=lbl_date.setter('text_size'))
                lbl_icon = Label(text="", font_name='MaterialIcons', color=(0.545, 0.718, 1.0, 1), size_hint_x=None, width='24dp', font_size='16sp')
                row_t.add_widget(lbl_date)
                row_t.add_widget(lbl_icon)

                first_val = entry.get('v', [''])[0] if entry.get('v') else ''
                logro_val = entry.get('v', ['','','','',''])[4] if len(entry.get('v', [])) > 4 else ''

                lbl_sum = Label(text=first_val, color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                                halign='left', size_hint_y=None, height='20dp')
                lbl_sum.bind(size=lbl_sum.setter('text_size'))

                lbl_logro = Label(text=f"Logro: {logro_val}", color=(0.224, 0.788, 0.541, 1), font_size='12sp',
                                  halign='left', size_hint_y=None, height='20dp')
                lbl_logro.bind(size=lbl_logro.setter('text_size'))

                card.add_widget(row_t)
                card.add_widget(lbl_sum)
                card.add_widget(lbl_logro)

                from kivy.uix.relativelayout import RelativeLayout
                rl = RelativeLayout(size_hint_y=None, height='92dp')
                btn_click = Button(background_color=(0,0,0,0), size_hint=(1, 1))
                btn_click.bind(on_release=lambda x, i=idx: self.open_entry_modal(i))
                rl.add_widget(card)
                rl.add_widget(btn_click)
                container.add_widget(rl)

    def save_new_entry(self):
        answers = [txt.text.strip() for txt in self.input_widgets]
        if not any(answers):
            App.get_running_app().show_toast("Escribe al menos una respuesta")
            return

        store = App.get_running_app().data_store
        t = datetime.date.today()
        month_name = SPANISH_MONTHS[t.month - 1]
        date_str = f"Hoy · {t.day} {month_name} {t.year}"

        new_entry = {'d': date_str, 'v': answers}
        store.diary_entries.insert(0, new_entry)
        store.save_data()

        App.get_running_app().show_toast("Entrada guardada")
        self.set_tab(1)

    def open_entry_modal(self, entry_index):
        modal = DiaryEntryModal(
            entry_index=entry_index,
            on_save_cb=self.update_entry,
            on_delete_cb=self.delete_entry
        )
        modal.open()

    def update_entry(self, entry_index, new_values):
        store = App.get_running_app().data_store
        if entry_index < len(store.diary_entries):
            store.diary_entries[entry_index]['v'] = new_values
            store.save_data()
        self.refresh_diary_view()
        App.get_running_app().show_toast("Cambios guardados")

    def delete_entry(self, entry_index):
        store = App.get_running_app().data_store
        if entry_index < len(store.diary_entries):
            store.diary_entries.pop(entry_index)
            store.save_data()
        self.refresh_diary_view()
        App.get_running_app().show_toast("Entrada eliminada")
