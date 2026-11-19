from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.app import App
from kivy.properties import BooleanProperty


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


def make_rounded_switch(active=False):
    """Crea un toggle switch redondeado estilo iOS/Material."""
    from kivy.metrics import dp
    app = App.get_running_app()
    green_c = app.green_color if app else (0.224, 0.788, 0.541, 1)
    border_c = app.card_border if app else (0.173, 0.227, 0.322, 1)
    sec_c = app.text_secondary if app else (0.627, 0.682, 0.753, 1)

    container = BoxLayout(size_hint=(None, None), size=(dp(52), dp(28)), padding=dp(2))
    container.active = active

    def _redraw(cont, *args):
        cont.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle, Ellipse
        _app = App.get_running_app()
        _green = _app.green_color if _app else (0.224, 0.788, 0.541, 1)
        _border = _app.card_border if _app else (0.173, 0.227, 0.322, 1)
        _sec = _app.text_secondary if _app else (0.627, 0.682, 0.753, 1)
        with cont.canvas.before:
            if cont.active:
                Color(*_green)
            else:
                Color(*_border)
            RoundedRectangle(pos=cont.pos, size=cont.size, radius=[dp(14)])
            if cont.active:
                Color(1, 1, 1, 1)
                Ellipse(pos=(cont.x + cont.width - dp(24), cont.y + dp(3)), size=(dp(22), dp(22)))
            else:
                Color(*_sec)
                Ellipse(pos=(cont.x + dp(2), cont.y + dp(3)), size=(dp(22), dp(22)))

    def _toggle(inst):
        container.active = not container.active
        _redraw(container)

    _redraw(container)
    container.bind(pos=_redraw, size=_redraw)

    btn_overlay = Button(background_color=(0, 0, 0, 0), size_hint=(1, 1))
    btn_overlay.bind(on_release=lambda x: _toggle(x))
    container.add_widget(btn_overlay)

    return container


class ReminderModal(ModalView):
    def __init__(self, reminder_index, on_save_cb, on_delete_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.72)
        self.auto_dismiss = True
        self.reminder_index = reminder_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        app = App.get_running_app()
        store = app.data_store if app else None
        item = store.reminders[reminder_index] if (store and 0 <= reminder_index < len(store.reminders)) else {}

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
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            Color(*card_border)
            line = Line(rounded_rectangle=[root.x, root.y, root.width, root.height, 16], width=1)
            def update_root(obj, val, r=rect, l=line):
                r.pos = obj.pos
                r.size = obj.size
                l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, 16]
            root.bind(pos=update_root, size=update_root)

        title = "Editar recordatorio" if reminder_index >= 0 else "Nuevo recordatorio"
        root.add_widget(Label(text=f"[b]{title}[/b]", markup=True, font_size='18sp',
                              size_hint_y=None, height='32dp', color=text_p))

        # Título / Actividad
        root.add_widget(Label(text="Título de la actividad *", size_hint_y=None, height='18dp',
                              halign='left', color=text_s, font_size='12sp'))
        self.txt_title = TextInput(
            text=str(item.get('t', '')),
            hint_text="Ej: Deber 4 de Programación II, Examen de Cálculo",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_title)

        # Fecha y Hora descriptiva
        root.add_widget(Label(text="Fecha y hora (ej: Hoy · 20:00 o Lun 9 nov · 10:00) *",
                              size_hint_y=None, height='18dp', halign='left',
                              color=text_s, font_size='12sp'))
        self.txt_desc = TextInput(
            text=str(item.get('d', 'Hoy · 20:00')),
            hint_text="Hoy · 20:00",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_desc)

        # Fila Switch Notificar
        row_sw = BoxLayout(size_hint_y=None, height='36dp')
        row_sw.add_widget(Label(text="Activar recordatorio", color=text_p, font_size='13sp', halign='left'))
        self.sw_active = make_rounded_switch(active=bool(item.get('on', 1)))
        row_sw.add_widget(self.sw_active)
        root.add_widget(row_sw)

        # Fila Tiempo antes
        root.add_widget(Label(text="Cuánto tiempo antes avisar:", size_hint_y=None, height='18dp',
                              halign='left', color=text_s, font_size='12sp'))
        m_map = {10: "10 minutos antes", 30: "30 minutos antes", 60: "1 hora antes", 1440: "1 día antes"}
        cur_m = item.get('m', 30)
        default_val = m_map.get(cur_m, "30 minutos antes")
        self.sp_time = Spinner(
            text=default_val,
            values=["10 minutos antes", "30 minutos antes", "1 hora antes", "1 día antes"],
            size_hint_y=None, height='38dp',
            background_color=card_bg, color=text_p
        )
        root.add_widget(self.sp_time)

        # Botones
        btn_save = make_rounded_btn("Guardar recordatorio", primary_c, primary_txt, height='44dp')
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        if reminder_index >= 0:
            btn_del = make_rounded_btn("Eliminar", card_bg, orange_c, height='38dp', bold=False)
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = make_rounded_btn("Cancelar", card_bg, accent_b, height='38dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def save(self, *args):
        t = self.txt_title.text.strip()
        d = self.txt_desc.text.strip()
        if not t:
            App.get_running_app().show_toast("Escribe el título de la actividad")
            return

        is_on = 1 if self.sw_active.active else 0
        txt_m = self.sp_time.text
        if "10 min" in txt_m:
            m = 10
        elif "1 hora" in txt_m:
            m = 60
        elif "1 día" in txt_m:
            m = 1440
        else:
            m = 30

        if self.on_save_cb:
            self.on_save_cb(self.reminder_index, t, d, is_on, m)
        self.dismiss()

    def delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.reminder_index)
        self.dismiss()


class RemindScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh_reminders()

    def refresh_reminders(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        container = self.ids.get('reminders_container')
        if not container:
            return
        container.clear_widgets()

        card_bg = app.card_color
        card_border = app.card_border
        text_p = app.text_primary
        text_s = app.text_secondary
        blue_hex = app.accent_blue_hex
        sec_hex = app.text_secondary_hex

        if not store.reminders:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[16, 16], spacing=6)
            with empty_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_c = RoundedRectangle(pos=empty_box.pos, size=empty_box.size, radius=[12])
                Color(*card_border)
                l_c = Line(rounded_rectangle=[empty_box.x, empty_box.y, empty_box.width, empty_box.height, 12], width=1)
                empty_box.bind(pos=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                               size=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))

            lbl1 = Label(text="[b]Sin recordatorios programados[/b]", markup=True,
                         color=text_p, font_size='14sp', size_hint_y=None, height='24dp')
            lbl1.bind(size=lbl1.setter('text_size'))
            lbl2 = Label(text="Toca '+ Agregar recordatorio' para no olvidar tus deberes o exámenes.",
                         color=text_s, font_size='12sp', size_hint_y=None, height='36dp')
            lbl2.bind(size=lbl2.setter('text_size'))
            empty_box.add_widget(lbl1)
            empty_box.add_widget(lbl2)
            container.add_widget(empty_box)
            return

        for idx, item in enumerate(store.reminders):
            card = BoxLayout(orientation='horizontal', size_hint_y=None, height='74dp', padding=[14, 10], spacing=8)
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

            # Columna Izquierda (Título y Fecha)
            col_l = BoxLayout(orientation='vertical', spacing=2)
            lbl_title = Label(text=f"[b]{item.get('t', '')}[/b]", markup=True, halign='left', valign='middle',
                              color=text_p, font_size='14sp')
            lbl_title.bind(size=lbl_title.setter('text_size'))
            lbl_date = Label(text=item.get('d', ''), halign='left', valign='middle',
                             color=text_s, font_size='12sp')
            lbl_date.bind(size=lbl_date.setter('text_size'))
            col_l.add_widget(lbl_title)
            col_l.add_widget(lbl_date)

            # Columna Derecha (Icono campana outline y Aviso)
            col_r = BoxLayout(orientation='vertical', size_hint_x=None, width='90dp', spacing=2)
            is_on = bool(item.get('on', 0))
            bell_color = blue_hex if is_on else sec_hex
            m = item.get('m', 30)
            if is_on:
                time_str = "1 día antes" if m == 1440 else (f"{m} min antes" if m < 60 else "1 hora antes")
            else:
                time_str = "Sin aviso"

            lbl_bell = Label(text=f"[color={bell_color}][font=MaterialIcons][/font][/color]", markup=True, halign='right', font_size='18sp')
            lbl_bell.bind(size=lbl_bell.setter('text_size'))
            lbl_time = Label(text=f"[color={bell_color}]{time_str}[/color]", markup=True, halign='right', font_size='11sp')
            lbl_time.bind(size=lbl_time.setter('text_size'))
            col_r.add_widget(lbl_bell)
            col_r.add_widget(lbl_time)

            card.add_widget(col_l)
            card.add_widget(col_r)

            from kivy.uix.relativelayout import RelativeLayout
            rl = RelativeLayout(size_hint_y=None, height='74dp')
            btn_click = Button(background_color=(0,0,0,0), size_hint=(1, 1))
            btn_click.bind(on_release=lambda x, i=idx: self.open_reminder_modal(i))
            rl.add_widget(card)
            rl.add_widget(btn_click)
            container.add_widget(rl)

    def open_new_reminder_modal(self):
        self.open_reminder_modal(-1)

    def open_reminder_modal(self, reminder_index):
        modal = ReminderModal(
            reminder_index=reminder_index,
            on_save_cb=self.save_reminder,
            on_delete_cb=self.delete_reminder
        )
        modal.open()

    def save_reminder(self, idx, title, desc, is_on, minutes):
        store = App.get_running_app().data_store
        obj = {'t': title, 'd': desc, 'on': is_on, 'm': minutes}
        if 0 <= idx < len(store.reminders):
            store.reminders[idx] = obj
            App.get_running_app().show_toast(f"Recordatorio '{title}' actualizado")
        else:
            store.reminders.insert(0, obj)
            App.get_running_app().show_toast(f"Recordatorio '{title}' creado")
        store.save_data()
        self.refresh_reminders()

    def delete_reminder(self, idx):
        store = App.get_running_app().data_store
        if 0 <= idx < len(store.reminders):
            removed = store.reminders.pop(idx)
            store.save_data()
            App.get_running_app().show_toast(f"Recordatorio '{removed.get('t', '')}' eliminado")
            self.refresh_reminders()
