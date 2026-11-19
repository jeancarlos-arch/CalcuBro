import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


def make_rounded_btn(text, bg_rgba, text_rgba=None, height='44dp', radius=14, bold=True):
    app = App.get_running_app()
    if text_rgba is None:
        text_rgba = app.primary_text if app else (0.063, 0.094, 0.153, 1)
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


def make_rounded_input(text="", hint_text="", height='60dp', multiline=True):
    from kivy.metrics import dp
    app = App.get_running_app()
    input_bg = app.input_bg if app else (0.063, 0.094, 0.153, 1)
    border_c = app.card_border if app else (0.173, 0.227, 0.322, 1)
    text_p = app.text_primary if app else (0.957, 0.965, 0.980, 1)
    accent_b = app.accent_blue if app else (0.545, 0.718, 1.0, 1)
    text_s = app.text_secondary if app else (0.627, 0.682, 0.753, 1)

    txt = TextInput(
        text=text,
        hint_text=hint_text,
        multiline=multiline,
        size_hint_y=None,
        height=height,
        background_normal='',
        background_active='',
        background_color=(0, 0, 0, 0),
        foreground_color=text_p,
        cursor_color=accent_b,
        hint_text_color=text_s,
        padding=[dp(12), dp(8)],
        font_size='13sp'
    )
    with txt.canvas.before:
        from kivy.graphics import Color, RoundedRectangle, Line
        Color(*input_bg)
        r = RoundedRectangle(pos=txt.pos, size=txt.size, radius=[dp(12)])
        Color(*border_c)
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

        app = App.get_running_app()
        store = app.data_store if app else None
        entry = store.diary_entries[entry_index] if (store and entry_index < len(store.diary_entries)) else {'d': '', 'v': []}
        questions = store.diary_questions if store else []

        card_bg = app.card_color if app else (0.106, 0.149, 0.220, 1)
        card_border = app.card_border if app else (0.173, 0.227, 0.322, 1)
        text_p = app.text_primary if app else (0.957, 0.965, 0.980, 1)
        text_s = app.text_secondary if app else (0.627, 0.682, 0.753, 1)
        primary_c = app.primary_color if app else (0.337, 0.537, 0.910, 1)
        primary_txt = app.primary_text if app else (0.063, 0.094, 0.153, 1)
        orange_c = app.orange_color if app else (0.949, 0.651, 0.353, 1)
        accent_b = app.accent_blue if app else (0.545, 0.718, 1.0, 1)

        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation='vertical', padding=14, spacing=8, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle, Line
            Color(*card_bg)
            rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            Color(*card_border)
            line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 16], width=1)
            def update_root(obj, val, r=rect, l=line):
                r.pos = obj.pos
                r.size = obj.size
                l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, 16]
            self.bind(pos=update_root, size=update_root)

        root.add_widget(Label(text=f"[b]{entry.get('d', '')}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp', color=text_p))

        self.inputs = []
        for i, q in enumerate(questions):
            root.add_widget(Label(text=q, color=text_s, font_size='12sp',
                                  size_hint_y=None, height='20dp', halign='left'))
            ans = entry.get('v', [])[i] if i < len(entry.get('v', [])) else ''
            txt = make_rounded_input(text=ans, height='64dp', multiline=True)
            self.inputs.append(txt)
            root.add_widget(txt)

        btn_save = make_rounded_btn("Guardar cambios", primary_c, primary_txt, height='44dp')
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        btn_del = make_rounded_btn("Eliminar entrada", card_bg, orange_c, height='40dp', bold=False)
        btn_del.bind(on_release=self.delete)
        root.add_widget(btn_del)

        btn_cancel = make_rounded_btn("Cancelar", card_bg, accent_b, height='40dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def save(self, *args):
        new_values = [inp.text.strip() for inp in self.inputs]
        if not any(new_values):
            App.get_running_app().show_toast("Escribe al menos una respuesta")
            return
        if self.on_save_cb:
            self.on_save_cb(self.entry_index, new_values)
        self.dismiss()

    def delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.entry_index)
        self.dismiss()


class DiaryScreen(Screen):
    today_diary_title = StringProperty("Fecha de hoy")
    active_tab = NumericProperty(0)  # 0: Nueva entrada, 1: Historial
    history_tab_title = StringProperty("Historial (0)")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.new_inputs = []

    def on_pre_enter(self, *args):
        months_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        t = datetime.date.today()
        self.today_diary_title = f"{days_es[t.weekday()]} {t.day} de {months_es[t.month - 1]} de {t.year}"
        self.refresh_diary()

    def set_tab(self, tab_idx):
        self.active_tab = tab_idx
        self.refresh_diary()

    def refresh_diary(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        entries = store.diary_entries
        self.history_tab_title = f"Historial ({len(entries)})"

        container = self.ids.get('diary_container')
        if not container:
            return
        container.clear_widgets()

        card_bg = app.card_color
        card_border = app.card_border
        text_p = app.text_primary
        text_s = app.text_secondary
        accent_b = app.accent_blue
        primary_c = app.primary_color
        primary_txt = app.primary_text
        green_c = app.green_color

        if self.active_tab == 0:
            # Formulario Nueva Entrada
            self.new_inputs = []
            questions = store.diary_questions
            for q in questions:
                lbl = Label(text=q, font_size='13sp', color=text_s, size_hint_y=None, height='24dp', halign='left')
                lbl.bind(size=lbl.setter('text_size'))
                container.add_widget(lbl)
                txt = make_rounded_input(hint_text="Escribe aquí tu respuesta reflexiva...", height='68dp', multiline=True)
                self.new_inputs.append(txt)
                container.add_widget(txt)

            btn_save = make_rounded_btn("Guardar entrada", primary_c, primary_txt, height='46dp', radius=14)
            btn_save.bind(on_release=lambda x: self.save_new_entry())
            container.add_widget(btn_save)

        else:
            # Vista Historial
            if not entries:
                lbl_empty = Label(text="Aún no hay entradas. Cuando quieras, escribe la primera.",
                                  color=text_s, font_size='13sp', size_hint_y=None, height='60dp')
                container.add_widget(lbl_empty)
                return

            for idx, entry in enumerate(entries):
                card = BoxLayout(orientation='vertical', size_hint_y=None, height='92dp', padding=[14, 10], spacing=4)
                with card.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle, Line
                    Color(*card_bg)
                    r_c = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                    Color(*card_border)
                    l_c = Line(rounded_rectangle=[card.x, card.y, card.width, card.height, 12], width=1)
                    def _update_card(obj, val, r=r_c, l=l_c):
                        r.pos = obj.pos
                        r.size = obj.size
                        l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, 12]
                    card.bind(pos=_update_card, size=_update_card)

                row_t = BoxLayout(size_hint_y=None, height='22dp')
                lbl_date = Label(text=f"[b]{entry.get('d', '')}[/b]", markup=True, halign='left',
                                 color=text_p, font_size='14sp')
                lbl_date.bind(size=lbl_date.setter('text_size'))
                lbl_icon = Label(text="", font_name='MaterialIcons', color=accent_b, size_hint_x=None, width='24dp', font_size='16sp')
                row_t.add_widget(lbl_date)
                row_t.add_widget(lbl_icon)

                first_val = entry.get('v', [''])[0] if entry.get('v') else ''
                logro_val = entry.get('v', ['','','','',''])[4] if len(entry.get('v', [])) > 4 else ''

                lbl_sum = Label(text=first_val, color=text_s, font_size='12sp',
                                halign='left', size_hint_y=None, height='20dp')
                lbl_sum.bind(size=lbl_sum.setter('text_size'))

                lbl_logro = Label(text=f"Logro: {logro_val}", color=green_c, font_size='12sp',
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
        app = App.get_running_app()
        values = [inp.text.strip() for inp in self.new_inputs]
        if not any(values):
            app.show_toast("Escribe al menos una respuesta para guardar")
            return

        months_short = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        t = datetime.date.today()
        date_str = f"{t.day} {months_short[t.month - 1]} {t.year}"

        store = app.data_store
        store.diary_entries.insert(0, {'d': date_str, 'v': values})
        store.save_data()

        app.show_toast("¡Entrada guardada en tu diario!")
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
            App.get_running_app().show_toast("Entrada actualizada")
            self.refresh_diary()

    def delete_entry(self, entry_index):
        store = App.get_running_app().data_store
        if entry_index < len(store.diary_entries):
            store.diary_entries.pop(entry_index)
            store.save_data()
            App.get_running_app().show_toast("Entrada eliminada")
            self.refresh_diary()
