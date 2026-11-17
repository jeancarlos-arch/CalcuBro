from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.app import App
from kivy.properties import BooleanProperty


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


def make_rounded_switch(active=False):
    """Crea un toggle switch redondeado estilo iOS/Material."""
    from kivy.metrics import dp
    from kivy.uix.widget import Widget

    container = BoxLayout(size_hint=(None, None), size=(dp(52), dp(28)), padding=dp(2))
    container.active = active

    def _redraw(cont, *args):
        cont.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle, Ellipse
        with cont.canvas.before:
            if cont.active:
                Color(0.337, 0.537, 0.910, 1)
            else:
                Color(0.173, 0.227, 0.322, 1)
            RoundedRectangle(pos=cont.pos, size=cont.size, radius=[dp(14)])
            # Thumb
            if cont.active:
                Color(0.957, 0.965, 0.980, 1)
                Ellipse(pos=(cont.x + cont.width - dp(24), cont.y + dp(3)), size=(dp(22), dp(22)))
            else:
                Color(0.627, 0.682, 0.753, 1)
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

        store = App.get_running_app().data_store
        item = store.reminders[reminder_index] if 0 <= reminder_index < len(store.reminders) else {}

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        title = "Editar recordatorio" if reminder_index >= 0 else "Nuevo recordatorio"
        root.add_widget(Label(text=f"[b]{title}[/b]", markup=True, font_size='18sp',
                              size_hint_y=None, height='32dp'))

        # Título / Actividad
        root.add_widget(Label(text="Título de la actividad *", size_hint_y=None, height='18dp',
                              halign='left', color=(0.627, 0.682, 0.753, 1), font_size='12sp'))
        self.txt_title = TextInput(
            text=str(item.get('t', '')),
            hint_text="Ej: Deber 4 de Programación II, Examen de Cálculo",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=(0.063, 0.094, 0.153, 1),
            foreground_color=(0.957, 0.965, 0.980, 1), cursor_color=(0.545, 0.718, 1.0, 1)
        )
        root.add_widget(self.txt_title)

        # Fecha y Hora
        root.add_widget(Label(text="Fecha y hora (ej: Hoy · 20:00, Vie 20 nov · 08:00)", size_hint_y=None, height='18dp',
                              halign='left', color=(0.627, 0.682, 0.753, 1), font_size='12sp'))
        self.txt_date = TextInput(
            text=str(item.get('d', 'Hoy · 20:00')),
            hint_text="Ej: Hoy · 20:00",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=(0.063, 0.094, 0.153, 1),
            foreground_color=(0.957, 0.965, 0.980, 1), cursor_color=(0.545, 0.718, 1.0, 1)
        )
        root.add_widget(self.txt_date)

        # Switch Recordarme
        row_sw = BoxLayout(size_hint_y=None, height='38dp')
        row_sw.add_widget(Label(text="Aviso activo", halign='left', valign='middle'))
        self.sw_active = make_rounded_switch(active=bool(item.get('on', 1)))
        row_sw.add_widget(self.sw_active)
        root.add_widget(row_sw)

        # Spinner Cuánto antes
        root.add_widget(Label(text="Cuánto antes alertar", font_size='12sp', color=(0.627, 0.682, 0.753, 1),
                              size_hint_y=None, height='18dp', halign='left'))
        options_map = {10: '10 minutos', 30: '30 minutos', 60: '1 hora', 1440: '1 día'}
        rev_map = {v: k for k, v in options_map.items()}
        current_m = item.get('m', 30)
        curr_text = options_map.get(current_m, '30 minutos')

        self.sp_time = Spinner(text=curr_text, values=list(rev_map.keys()), size_hint_y=None, height='38dp')
        root.add_widget(self.sp_time)

        btn_save = make_rounded_btn("Guardar", (0.337, 0.537, 0.910, 1), (0.063, 0.094, 0.153, 1), height='44dp')
        btn_save.bind(on_release=lambda x: self.save(rev_map))
        root.add_widget(btn_save)

        if reminder_index >= 0:
            btn_del = make_rounded_btn("Eliminar recordatorio", (0.173, 0.227, 0.322, 0.7), (0.949, 0.651, 0.353, 1), height='38dp', bold=False)
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = make_rounded_btn("Cancelar", (0.106, 0.149, 0.220, 1), (0.545, 0.718, 1.0, 1), height='38dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def save(self, rev_map):
        app = App.get_running_app()
        title = self.txt_title.text.strip()
        if not title:
            app.show_toast("Escribe el título de la actividad")
            return
        date_str = self.txt_date.text.strip() or "Hoy · 20:00"
        is_on = 1 if self.sw_active.active else 0
        minutes = rev_map.get(self.sp_time.text, 30)
        self.on_save_cb(self.reminder_index, title, date_str, is_on, minutes)
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

        if not store.reminders:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[16, 16], spacing=6)
            with empty_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 0.6)
                r_c = RoundedRectangle(pos=empty_box.pos, size=empty_box.size, radius=[12])
                empty_box.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                               size=lambda obj, val, r=r_c: setattr(r, 'size', val))

            lbl1 = Label(text="[b]Sin recordatorios programados[/b]", markup=True,
                         color=(0.957, 0.965, 0.980, 1), font_size='14sp', size_hint_y=None, height='24dp')
            lbl1.bind(size=lbl1.setter('text_size'))
            lbl2 = Label(text="Toca '+ Agregar recordatorio' para no olvidar tus deberes o exámenes.",
                         color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_y=None, height='36dp')
            lbl2.bind(size=lbl2.setter('text_size'))
            empty_box.add_widget(lbl1)
            empty_box.add_widget(lbl2)
            container.add_widget(empty_box)
            return

        for idx, item in enumerate(store.reminders):
            card = BoxLayout(orientation='horizontal', size_hint_y=None, height='74dp', padding=[14, 10], spacing=8)
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                r_c = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                card.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                          size=lambda obj, val, r=r_c: setattr(r, 'size', val))

            # Columna Izquierda (Título y Fecha)
            col_l = BoxLayout(orientation='vertical', spacing=2)
            lbl_title = Label(text=f"[b]{item.get('t', '')}[/b]", markup=True, halign='left', valign='middle',
                              color=(0.957, 0.965, 0.980, 1), font_size='14sp')
            lbl_title.bind(size=lbl_title.setter('text_size'))
            lbl_date = Label(text=item.get('d', ''), halign='left', valign='middle',
                             color=(0.627, 0.682, 0.753, 1), font_size='12sp')
            lbl_date.bind(size=lbl_date.setter('text_size'))
            col_l.add_widget(lbl_title)
            col_l.add_widget(lbl_date)

            # Columna Derecha (Icono y Aviso)
            col_r = BoxLayout(orientation='vertical', size_hint_x=None, width='90dp', spacing=2)
            is_on = bool(item.get('on', 0))
            bell_color = "8bb7ff" if is_on else "a0aec0"
            m = item.get('m', 30)
            if is_on:
                time_str = "1 día antes" if m == 1440 else (f"{m} min antes" if m < 60 else "1 hora antes")
            else:
                time_str = "Sin aviso"

            lbl_bell = Label(text=f"[color={bell_color}][font=MaterialIcons][/font][/color]", markup=True, halign='right', font_size='18sp')
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

    def save_reminder(self, index, title, date_str, is_on, minutes):
        store = App.get_running_app().data_store
        new_rem = {'t': title, 'd': date_str, 'on': is_on, 'm': minutes}
        if 0 <= index < len(store.reminders):
            store.reminders[index] = new_rem
            App.get_running_app().show_toast("Recordatorio actualizado")
        else:
            store.reminders.append(new_rem)
            App.get_running_app().show_toast("Recordatorio creado")

        store.save_data()
        self.refresh_reminders()

    def delete_reminder(self, index):
        store = App.get_running_app().data_store
        if 0 <= index < len(store.reminders):
            store.reminders.pop(index)
            store.save_data()
            App.get_running_app().show_toast("Recordatorio eliminado")
        self.refresh_reminders()
