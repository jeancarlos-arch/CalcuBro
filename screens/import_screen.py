from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.app import App


class ImportScreen(Screen):
    current_step = NumericProperty(0)  # 0, 1, 2, 3
    step_subtitle = StringProperty("Paso 1 de 4")

    # Datos reconocidos
    recognized_classes = []

    def on_pre_enter(self, *args):
        self.set_step(0)

    def set_step(self, step):
        self.current_step = step
        self.step_subtitle = f"Paso {min(step + 1, 4)} de 4"
        self.build_step_view()

    def build_step_view(self):
        app = App.get_running_app()
        container = self.ids.get('step_container')
        if not container:
            return
        container.clear_widgets()

        card_bg = app.card_color if app else (0.106, 0.149, 0.220, 1)
        card_border = app.card_border if app else (0.173, 0.227, 0.322, 1)
        input_bg = app.input_bg if app else (0.063, 0.094, 0.153, 1)
        text_p = app.text_primary if app else (0.957, 0.965, 0.980, 1)
        text_s = app.text_secondary if app else (0.627, 0.682, 0.753, 1)
        primary_c = app.primary_color if app else (0.337, 0.537, 0.910, 1)
        primary_txt = app.primary_text if app else (0.063, 0.094, 0.153, 1)
        accent_b = app.accent_blue if app else (0.545, 0.718, 1.0, 1)
        orange_hex = app.orange_color_hex if app else 'f2a65a'

        if self.current_step == 0:
            # Paso 0: Selección de archivo / foto
            btn_gal = Button(text="[font=MaterialIcons][/font]   Elegir de la galería", markup=True,
                             size_hint_y=None, height='54dp',
                             background_normal='', background_color=card_bg,
                             color=accent_b, bold=True, font_size='15sp')
            with btn_gal.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r1 = RoundedRectangle(pos=btn_gal.pos, size=btn_gal.size, radius=[12])
                Color(*card_border)
                l1 = Line(rounded_rectangle=[btn_gal.x, btn_gal.y, btn_gal.width, btn_gal.height, 12], width=1)
                btn_gal.bind(pos=lambda obj, val, r=r1, l=l1: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                             size=lambda obj, val, r=r1, l=l1: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))
            btn_gal.bind(on_release=lambda x: self.set_step(1))

            btn_cam = Button(text="[font=MaterialIcons][/font]   Tomar una fotografía", markup=True,
                             size_hint_y=None, height='54dp',
                             background_normal='', background_color=card_bg,
                             color=accent_b, bold=True, font_size='15sp')
            with btn_cam.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r2 = RoundedRectangle(pos=btn_cam.pos, size=btn_cam.size, radius=[12])
                Color(*card_border)
                l2 = Line(rounded_rectangle=[btn_cam.x, btn_cam.y, btn_cam.width, btn_cam.height, 12], width=1)
                btn_cam.bind(pos=lambda obj, val, r=r2, l=l2: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                             size=lambda obj, val, r=r2, l=l2: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))
            btn_cam.bind(on_release=lambda x: self.set_step(1))

            lbl_tip = Label(text="Consejo: una foto nítida y de frente mejora el reconocimiento.",
                            color=text_s, font_size='12sp', size_hint_y=None, height='30dp')

            container.add_widget(btn_gal)
            container.add_widget(btn_cam)
            container.add_widget(lbl_tip)

        elif self.current_step == 1:
            # Paso 1: Previsualización
            preview_card = BoxLayout(orientation='vertical', size_hint_y=None, height='170dp', padding=12, spacing=6)
            with preview_card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_c = RoundedRectangle(pos=preview_card.pos, size=preview_card.size, radius=[12])
                Color(*card_border)
                l_c = Line(rounded_rectangle=[preview_card.x, preview_card.y, preview_card.width, preview_card.height, 12], width=1)
                preview_card.bind(pos=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                                 size=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))

            lbl_pv = Label(text="Vista previa · horario_clases.jpg", color=text_s,
                           font_size='12sp', size_hint_y=None, height='20dp', halign='left')
            lbl_pv.bind(size=lbl_pv.setter('text_size'))

            sample_text = ("Viernes\n08:00 – 10:00 Cálculo Diferencial · B-204\n"
                           "10:30 – 12:30 Programación II · Lab 8\n"
                           "Miércoles\n10:30 – 12:00 Ética Profesional · A-205")
            lbl_body = Label(text=sample_text, color=text_p, font_size='12sp',
                             halign='left', valign='top')
            lbl_body.bind(size=lbl_body.setter('text_size'))

            body_box = BoxLayout(padding=8)
            with body_box.canvas.before:
                from kivy.graphics import Color as BColor, RoundedRectangle as BRect, Line as BLine
                BColor(*input_bg)
                b_r = BRect(pos=body_box.pos, size=body_box.size, radius=[8])
                BColor(*card_border)
                b_l = BLine(rounded_rectangle=[body_box.x, body_box.y, body_box.width, body_box.height, 8], width=1)
                body_box.bind(pos=lambda obj, val, r=b_r, l=b_l: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 8])),
                              size=lambda obj, val, r=b_r, l=b_l: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 8])))
            body_box.add_widget(lbl_body)

            preview_card.add_widget(lbl_pv)
            preview_card.add_widget(body_box)

            btn_ocr = Button(text="Reconocer horario", size_hint_y=None, height='46dp',
                             background_normal='', background_color=primary_c,
                             color=primary_txt, bold=True, font_size='15sp')
            with btn_ocr.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(*primary_c)
                r_o = RoundedRectangle(pos=btn_ocr.pos, size=btn_ocr.size, radius=[12])
                btn_ocr.bind(pos=lambda obj, val, r=r_o: setattr(r, 'pos', val),
                             size=lambda obj, val, r=r_o: setattr(r, 'size', val))
            btn_ocr.bind(on_release=lambda x: self.start_ocr())

            container.add_widget(preview_card)
            container.add_widget(btn_ocr)

        elif self.current_step == 2:
            # Paso 2: Procesamiento
            proc_card = BoxLayout(orientation='vertical', size_hint_y=None, height='140dp', padding=20)
            with proc_card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_c = RoundedRectangle(pos=proc_card.pos, size=proc_card.size, radius=[12])
                Color(*card_border)
                l_c = Line(rounded_rectangle=[proc_card.x, proc_card.y, proc_card.width, proc_card.height, 12], width=1)
                proc_card.bind(pos=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                               size=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))

            lbl_proc = Label(text="Reconociendo materias, días, horas y aulas...\n\nPor favor espera unos segundos.",
                             color=accent_b, font_size='14sp', halign='center', valign='middle')
            lbl_proc.bind(size=lbl_proc.setter('text_size'))
            proc_card.add_widget(lbl_proc)
            container.add_widget(proc_card)

        elif self.current_step == 3:
            # Paso 3: Revisión y confirmación
            lbl_rev = Label(text="Revisa y corrige los datos. Nada se guarda hasta que confirmes.",
                            color=text_s, font_size='12sp', size_hint_y=None, height='24dp', halign='left')
            lbl_rev.bind(size=lbl_rev.setter('text_size'))
            container.add_widget(lbl_rev)

            self.form_inputs = []
            days_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

            for i, q in enumerate(self.recognized_classes):
                c_card = BoxLayout(orientation='vertical', size_hint_y=None, height='190dp', padding=12, spacing=6)
                with c_card.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle, Line
                    Color(*card_bg)
                    r_c = RoundedRectangle(pos=c_card.pos, size=c_card.size, radius=[12])
                    Color(*card_border)
                    l_c = Line(rounded_rectangle=[c_card.x, c_card.y, c_card.width, c_card.height, 12], width=1)
                    c_card.bind(pos=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                                size=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))

                if q.get('fl'):
                    lbl_warn = Label(text=f"[color={orange_hex}][b]Revisar: baja confianza en el aula[/b][/color]",
                                     markup=True, font_size='11sp', size_hint_y=None, height='16dp', halign='left')
                    lbl_warn.bind(size=lbl_warn.setter('text_size'))
                    c_card.add_widget(lbl_warn)

                # Materia
                c_card.add_widget(Label(text="Materia", font_size='11sp', color=text_s, size_hint_y=None, height='16dp', halign='left'))
                txt_n = TextInput(text=q.get('n', ''), multiline=False, size_hint_y=None, height='34dp',
                                  background_normal='', background_color=input_bg, foreground_color=text_p, cursor_color=accent_b)
                c_card.add_widget(txt_n)

                # Fila Día y Aula
                row_mid = BoxLayout(size_hint_y=None, height='34dp', spacing=10)
                sp_day = Spinner(text=days_names[q.get('d', 0)], values=days_names, size_hint_x=0.5,
                                 background_color=card_bg, color=text_p)
                txt_a = TextInput(text=q.get('a', ''), multiline=False, size_hint_x=0.5,
                                  background_normal='', background_color=input_bg, foreground_color=text_p, cursor_color=accent_b)
                row_mid.add_widget(sp_day)
                row_mid.add_widget(txt_a)
                c_card.add_widget(row_mid)

                # Horario
                c_card.add_widget(Label(text="Horario", font_size='11sp', color=text_s, size_hint_y=None, height='16dp', halign='left'))
                txt_h = TextInput(text=q.get('h', ''), multiline=False, size_hint_y=None, height='34dp',
                                  background_normal='', background_color=input_bg, foreground_color=text_p, cursor_color=accent_b)
                c_card.add_widget(txt_h)

                self.form_inputs.append({'n': txt_n, 'd': sp_day, 'a': txt_a, 'h': txt_h})
                container.add_widget(c_card)

            btn_conf = Button(text="Confirmar y guardar horario", size_hint_y=None, height='46dp',
                              background_normal='', background_color=primary_c,
                              color=primary_txt, bold=True, font_size='15sp')
            with btn_conf.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(*primary_c)
                r_cf = RoundedRectangle(pos=btn_conf.pos, size=btn_conf.size, radius=[12])
                btn_conf.bind(pos=lambda obj, val, r=r_cf: setattr(r, 'pos', val),
                              size=lambda obj, val, r=r_cf: setattr(r, 'size', val))
            btn_conf.bind(on_release=lambda x: self.confirm_save())

            btn_disc = Button(text="Descartar", size_hint_y=None, height='40dp',
                              background_normal='', background_color=card_bg,
                              color=accent_b)
            with btn_disc.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_dc = RoundedRectangle(pos=btn_disc.pos, size=btn_disc.size, radius=[12])
                Color(*card_border)
                l_dc = Line(rounded_rectangle=[btn_disc.x, btn_disc.y, btn_disc.width, btn_disc.height, 12], width=1)
                btn_disc.bind(pos=lambda obj, val, r=r_dc, l=l_dc: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                              size=lambda obj, val, r=r_dc, l=l_dc: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))
            btn_disc.bind(on_release=lambda x: self.discard())

            container.add_widget(btn_conf)
            container.add_widget(btn_disc)

    def start_ocr(self):
        self.set_step(2)
        Clock.schedule_once(self.finish_ocr, 1.0)

    def finish_ocr(self, dt):
        self.recognized_classes = [
            {'n': 'Cálculo Diferencial', 'd': 4, 'h': '08:00 – 10:00', 'a': 'B-204', 'fl': 0},
            {'n': 'Programación II', 'd': 4, 'h': '10:30 – 12:30', 'a': 'Lab 8', 'fl': 1},
            {'n': 'Ética Profesional', 'd': 2, 'h': '10:30 – 12:00', 'a': 'A-205', 'fl': 0}
        ]
        self.set_step(3)

    def confirm_save(self):
        days_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        store = App.get_running_app().data_store

        for form in self.form_inputs:
            name = form['n'].text.strip() or "Materia"
            day_text = form['d'].text
            day_idx = days_names.index(day_text) if day_text in days_names else 0
            room = form['a'].text.strip() or "Aula"
            hours = form['h'].text.strip() or "08:00 – 10:00"

            if day_idx < len(store.schedule):
                store.schedule[day_idx].append({'n': name, 'h': hours, 'a': room})
                store.schedule[day_idx].sort(key=lambda x: x.get('h', ''))

        store.save_data()
        App.get_running_app().show_toast("Horario importado y guardado")
        App.get_running_app().go_screen('schedule', clear_history=True)

    def discard(self):
        App.get_running_app().go_screen('schedule')
