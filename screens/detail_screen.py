from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty, NumericProperty
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


class EvaluationModal(ModalView):
    def __init__(self, categories, category_index, item_index, on_save_cb, on_delete_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.72)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.75)

        self.categories = categories
        self.cat_idx = category_index
        self.item_idx = item_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        app = App.get_running_app()
        card_bg = app.card_color if app else (0.106, 0.149, 0.220, 1)
        card_border = app.card_border if app else (0.173, 0.227, 0.322, 1)
        input_bg = app.input_bg if app else (0.063, 0.094, 0.153, 1)
        text_p = app.text_primary if app else (0.957, 0.965, 0.980, 1)
        text_s = app.text_secondary if app else (0.627, 0.682, 0.753, 1)
        primary_c = app.primary_color if app else (0.337, 0.537, 0.910, 1)
        primary_txt = app.primary_text if app else (0.063, 0.094, 0.153, 1)
        orange_c = app.orange_color if app else (0.949, 0.651, 0.353, 1)
        accent_b = app.accent_blue if app else (0.545, 0.718, 1.0, 1)

        item_data = {}
        if 0 <= category_index < len(self.categories):
            items = self.categories[category_index].get('it', [])
            if 0 <= item_index < len(items):
                item_data = items[item_index]

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

        title_text = "Editar evaluación" if item_index >= 0 else "Registrar evaluación"
        root.add_widget(Label(text=f"[b]{title_text}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp', color=text_p))

        # Selector de Categoría
        root.add_widget(Label(text="Categoría / Rubro *", size_hint_y=None, height='18dp', halign='left', color=text_s))
        cat_names = [c.get('n', f'Cat {i}') for i, c in enumerate(self.categories)] or ["General"]
        init_cat = cat_names[category_index] if 0 <= category_index < len(cat_names) else cat_names[0]
        self.sp_category = Spinner(
            text=init_cat,
            values=cat_names,
            size_hint_y=None,
            height='38dp',
            background_color=card_bg,
            color=text_p
        )
        root.add_widget(self.sp_category)

        # Nombre de la evaluación
        root.add_widget(Label(text="Nombre de la evaluación *", size_hint_y=None, height='18dp', halign='left', color=text_s))
        self.txt_name = TextInput(
            text=str(item_data.get('n', '')),
            hint_text="Ej: Deber 1, Lección 2, Proyecto Parcial",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_name)

        # Calificación
        root.add_widget(Label(text="Calificación obtenida (vacío = pendiente)", size_hint_y=None, height='18dp', halign='left', color=text_s))
        g_val = item_data.get('g')
        self.txt_grade = TextInput(
            text=str(g_val) if g_val is not None else '',
            hint_text="Ej: 8.5 (o déjalo vacío)",
            multiline=False, size_hint_y=None, height='38dp', input_filter='float',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_grade)

        # Botones
        btn_save = make_rounded_btn("Guardar", primary_c, primary_txt, height='44dp')
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        if item_index >= 0:
            btn_del = make_rounded_btn("Eliminar evaluación", card_bg, orange_c, height='40dp', bold=False)
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = make_rounded_btn("Cancelar", card_bg, accent_b, height='40dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def save(self, *args):
        app = App.get_running_app()
        name = self.txt_name.text.strip()
        if not name:
            app.show_toast("Escribe el nombre de la evaluación")
            return

        g_str = self.txt_grade.text.strip()
        grade = None
        if g_str:
            try:
                grade = float(g_str)
                if grade < 0.0 or grade > 10.0:
                    app.show_toast("La calificación debe estar entre 0.0 y 10.0")
                    return
            except ValueError:
                app.show_toast("La nota ingresada no es un número válido")
                return

        target_cat_name = self.sp_category.text
        target_cat_idx = self.cat_idx
        for i, c in enumerate(self.categories):
            if c.get('n') == target_cat_name:
                target_cat_idx = i
                break

        if self.on_save_cb:
            self.on_save_cb(self.cat_idx, self.item_idx, target_cat_idx, name, grade)
        self.dismiss()

    def delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.cat_idx, self.item_idx)
        self.dismiss()


class CategoryModal(ModalView):
    def __init__(self, current_total_weight, on_save_cb, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.58)
        self.auto_dismiss = True
        self.current_total_weight = float(current_total_weight)
        self.on_save_cb = on_save_cb

        app = App.get_running_app()
        card_bg = app.card_color if app else (0.106, 0.149, 0.220, 1)
        card_border = app.card_border if app else (0.173, 0.227, 0.322, 1)
        input_bg = app.input_bg if app else (0.063, 0.094, 0.153, 1)
        text_p = app.text_primary if app else (0.957, 0.965, 0.980, 1)
        text_s = app.text_secondary if app else (0.627, 0.682, 0.753, 1)
        primary_c = app.primary_color if app else (0.337, 0.537, 0.910, 1)
        primary_txt = app.primary_text if app else (0.063, 0.094, 0.153, 1)
        accent_b = app.accent_blue if app else (0.545, 0.718, 1.0, 1)
        green_hex = app.green_color_hex if app else '39c98a'

        avail = max(0.0, round(100.0 - self.current_total_weight, 1))

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

        root.add_widget(Label(text="[b]Nueva categoría / Rubro[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp', color=text_p))

        root.add_widget(Label(text="Nombre del rubro *", size_hint_y=None, height='18dp', halign='left', color=text_s))
        self.txt_name = TextInput(
            hint_text="Ej: Parciales, Deberes, Talleres, Proyecto", multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_name)

        lbl_w = Label(
            text=f"Peso en la nota final (%) *  [color={green_hex}](Disponible: {avail:.1f}%)[/color]",
            markup=True, size_hint_y=None, height='18dp', halign='left', color=text_s, font_size='12sp'
        )
        root.add_widget(lbl_w)

        self.txt_weight = TextInput(
            hint_text=f"Máx {avail:.1f}", multiline=False, size_hint_y=None, height='38dp', input_filter='float',
            background_normal='', background_color=input_bg,
            foreground_color=text_p, cursor_color=accent_b
        )
        root.add_widget(self.txt_weight)

        btn_create = make_rounded_btn("Crear categoría", primary_c, primary_txt, height='44dp')
        btn_create.bind(on_release=self.create_cat)
        root.add_widget(btn_create)

        btn_cancel = make_rounded_btn("Cancelar", card_bg, accent_b, height='38dp', bold=False)
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def create_cat(self, *args):
        app = App.get_running_app()
        name = self.txt_name.text.strip()
        if not name:
            app.show_toast("Escribe el nombre de la categoría")
            return

        try:
            w = float(self.txt_weight.text.strip() or 0)
        except ValueError:
            w = 0.0

        if w <= 0:
            app.show_toast("El peso porcentual debe ser mayor a 0%")
            return

        avail = max(0.0, round(100.0 - self.current_total_weight, 1))
        if w > avail:
            app.show_toast(f"No puede superar 100%. Solo queda {avail:.1f}% disponible")
            return

        self.on_save_cb(name, w)
        self.dismiss()


class DetailScreen(Screen):
    subject_title = StringProperty("Materia")
    teacher_name = StringProperty("")
    current_avg = NumericProperty(0.0)
    evaluated_percent = NumericProperty(0.0)
    pending_percent = NumericProperty(100.0)
    min_note = NumericProperty(7.0)
    goal_note = NumericProperty(8.5)
    goal_status_text = StringProperty("")
    min_status_text = StringProperty("")

    def on_pre_enter(self, *args):
        self.refresh_detail()

    def get_current_subject(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return None
        return app.data_store.get_active_subject_obj()

    def refresh_detail(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        subj = self.get_current_subject()
        if not subj:
            self.subject_title = "Sin materia seleccionada"
            return

        self.subject_title = subj.get('n', 'Materia')
        self.teacher_name = subj.get('teacher', '')
        self.min_note = float(subj.get('pmin', 7.0))
        self.goal_note = float(subj.get('pgoal', 8.5))

        container = self.ids.get('categories_container')
        if not container:
            return
        container.clear_widgets()

        categories = subj.setdefault('categories', [])
        store = app.data_store
        pc = store.calc_categories_for(categories)

        self.current_avg = (pc['pts'] / pc['ev'] * 100.0) if pc['ev'] > 0 else 0.0
        self.evaluated_percent = pc['ev']
        self.pending_percent = pc['pend']

        # Proyecciones
        _, g_msg = store.calc_need(self.goal_note, pc['pts'], pc['pend'], 10.0)
        _, m_msg = store.calc_need(self.min_note, pc['pts'], pc['pend'], 10.0)
        self.goal_status_text = f"Objetivo ({self.goal_note:.1f}): {g_msg}"
        self.min_status_text = f"Para aprobar ({self.min_note:.1f}): {m_msg}"

        card_bg = app.card_color
        card_border = app.card_border
        text_p = app.text_primary
        text_s = app.text_secondary
        input_bg = app.input_bg
        sec_hex = app.text_secondary_hex

        if not categories:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[16, 16], spacing=6)
            with empty_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_c = RoundedRectangle(pos=empty_box.pos, size=empty_box.size, radius=[12])
                Color(*card_border)
                l_c = Line(rounded_rectangle=[empty_box.x, empty_box.y, empty_box.width, empty_box.height, 12], width=1)
                empty_box.bind(pos=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'pos', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])),
                               size=lambda obj, val, r=r_c, l=l_c: (setattr(r, 'size', val), setattr(l, 'rounded_rectangle', [obj.x, obj.y, obj.width, obj.height, 12])))

            lbl1 = Label(text="[b]Sin categorías de evaluación todavía[/b]", markup=True,
                         color=text_p, font_size='14sp', size_hint_y=None, height='24dp')
            lbl1.bind(size=lbl1.setter('text_size'))
            lbl2 = Label(text="Pulsa '+ Nueva categoría' para definir cómo se divide tu nota (ej. Parciales 50%, Deberes 20%, Proyecto 30%).",
                         color=text_s, font_size='12sp', size_hint_y=None, height='42dp')
            lbl2.bind(size=lbl2.setter('text_size'))
            empty_box.add_widget(lbl1)
            empty_box.add_widget(lbl2)
            container.add_widget(empty_box)
            return

        for c_idx, cat in enumerate(categories):
            cat_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=[14, 10], spacing=6)
            cat_box.bind(minimum_height=cat_box.setter('height'))
            with cat_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Line
                Color(*card_bg)
                r_cat = RoundedRectangle(pos=cat_box.pos, size=cat_box.size, radius=[12])
                Color(*card_border)
                l_cat = Line(rounded_rectangle=[cat_box.x, cat_box.y, cat_box.width, cat_box.height, 12], width=1)
                def _update_cat(obj, val, r=r_cat, l=l_cat):
                    r.pos = obj.pos
                    r.size = obj.size
                    l.rounded_rectangle = [obj.x, obj.y, obj.width, obj.height, 12]
                cat_box.bind(pos=_update_cat, size=_update_cat)

            # Fila de Encabezado de categoría con botón para borrar categoría
            header_row = BoxLayout(size_hint_y=None, height='28dp', spacing=6)
            cat_items = cat.get('it', [])
            graded = [it for it in cat_items if it.get('g') is not None]
            avg_str = f"promedio {sum(float(it['g']) for it in graded)/len(graded):.2f}" if graded else "sin calificar"
            header_text = f"[b]{cat.get('n', '')}[/b]  [color={sec_hex}][size=12sp]{cat.get('w', 0)}% · {avg_str}[/size][/color]"

            lbl_h = Label(text=header_text, markup=True, halign='left', valign='middle', color=text_p)
            lbl_h.bind(size=lbl_h.setter('text_size'))

            btn_del_cat = Button(
                text="", font_name='MaterialIcons', size_hint=(None, None), size=('26dp', '26dp'),
                background_normal='', background_color=(0, 0, 0, 0),
                color=app.orange_color, font_size='16sp'
            )
            btn_del_cat.bind(on_release=lambda x, ci=c_idx: self.delete_category(ci))

            header_row.add_widget(lbl_h)
            header_row.add_widget(btn_del_cat)
            cat_box.add_widget(header_row)

            if not cat_items:
                lbl_empty = Label(text="Sin evaluaciones aún en este rubro.", color=text_s,
                                  font_size='12sp', size_hint_y=None, height='24dp', halign='left')
                lbl_empty.bind(size=lbl_empty.setter('text_size'))
                cat_box.add_widget(lbl_empty)
            else:
                for it_idx, it in enumerate(cat_items):
                    row = BoxLayout(size_hint_y=None, height='36dp', spacing=10)
                    g_val = it.get('g')
                    g_display = f"{float(g_val):.2f}" if g_val is not None else f"[color={sec_hex}]Pendiente[/color]"
                    btn_row = make_rounded_btn(
                        f"  {it.get('n', '')}   [font=MaterialIcons][/font]   {g_display}",
                        input_bg, text_p,
                        height='36dp', radius=10, bold=False
                    )
                    btn_row.markup = True
                    btn_row.bind(on_release=lambda instance, ci=c_idx, ii=it_idx: self.open_evaluation_modal(ci, ii))
                    row.add_widget(btn_row)
                    cat_box.add_widget(row)

            container.add_widget(cat_box)

    def on_goal_changed(self, text):
        try:
            val = float(text)
            self.goal_note = val
            subj = self.get_current_subject()
            if subj:
                subj['pgoal'] = val
                App.get_running_app().data_store.save_data()
            self.refresh_detail()
        except ValueError:
            pass

    def on_min_changed(self, text):
        try:
            val = float(text)
            self.min_note = val
            subj = self.get_current_subject()
            if subj:
                subj['pmin'] = val
                App.get_running_app().data_store.save_data()
            self.refresh_detail()
        except ValueError:
            pass

    def on_teacher_changed(self, text):
        subj = self.get_current_subject()
        if subj:
            subj['teacher'] = text.strip()
            App.get_running_app().data_store.save_data()

    def open_new_category_modal(self):
        subj = self.get_current_subject()
        if not subj:
            return
        categories = subj.get('categories', [])
        tot = sum(float(c.get('w', 0)) for c in categories)
        modal = CategoryModal(
            current_total_weight=tot,
            on_save_cb=self.add_category
        )
        modal.open()

    def add_category(self, name, weight):
        subj = self.get_current_subject()
        if not subj:
            return
        categories = subj.setdefault('categories', [])
        categories.append({'n': name, 'w': weight, 'm': 'a', 'it': []})
        App.get_running_app().data_store.save_data()
        App.get_running_app().show_toast(f"Rubro '{name}' ({weight:.0f}%) creado")
        self.refresh_detail()

    def delete_category(self, cat_idx):
        subj = self.get_current_subject()
        if not subj:
            return
        categories = subj.get('categories', [])
        if 0 <= cat_idx < len(categories):
            removed = categories.pop(cat_idx)
            App.get_running_app().data_store.save_data()
            App.get_running_app().show_toast(f"Categoría '{removed.get('n', '')}' eliminada")
            self.refresh_detail()

    def open_evaluation_modal(self, category_index=0, item_index=-1):
        subj = self.get_current_subject()
        if not subj:
            return
        categories = subj.setdefault('categories', [])
        if not categories:
            App.get_running_app().show_toast("Crea al menos una categoría primero")
            return
        modal = EvaluationModal(
            categories=categories,
            category_index=category_index,
            item_index=item_index,
            on_save_cb=self.save_evaluation,
            on_delete_cb=self.delete_evaluation
        )
        modal.open()

    def save_evaluation(self, orig_cat_idx, orig_item_idx, target_cat_idx, name, grade):
        subj = self.get_current_subject()
        if not subj:
            return
        categories = subj.setdefault('categories', [])

        if orig_item_idx >= 0 and 0 <= orig_cat_idx < len(categories):
            orig_items = categories[orig_cat_idx].setdefault('it', [])
            if orig_item_idx < len(orig_items):
                orig_items.pop(orig_item_idx)

        if 0 <= target_cat_idx < len(categories):
            target_items = categories[target_cat_idx].setdefault('it', [])
            target_items.append({'n': name, 'g': grade})
            App.get_running_app().data_store.save_data()
            App.get_running_app().show_toast(f"Evaluación '{name}' guardada")
            self.refresh_detail()

    def delete_evaluation(self, cat_idx, item_idx):
        subj = self.get_current_subject()
        if not subj:
            return
        categories = subj.get('categories', [])
        if 0 <= cat_idx < len(categories):
            items = categories[cat_idx].get('it', [])
            if 0 <= item_idx < len(items):
                removed = items.pop(item_idx)
                App.get_running_app().data_store.save_data()
                App.get_running_app().show_toast(f"Evaluación '{removed.get('n', '')}' eliminada")
                self.refresh_detail()
