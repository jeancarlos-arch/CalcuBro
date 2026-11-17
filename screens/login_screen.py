from kivy.uix.screenmanager import Screen
from kivy.app import App


class LoginScreen(Screen):
    def navigate(self, screen_name):
        app = App.get_running_app()
        if app:
            app.go_screen(screen_name)

    def save_data(self):
        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            store = app.data_store
            
            # Capturamos nombre y carrera de forma segura
            if 'name_input' in self.ids:
                store.student_name = self.ids.name_input.text.strip()
            if 'career_input' in self.ids:
                store.student_career = self.ids.career_input.text.strip()
            
            # Capturamos el semestre seleccionado del Spinner
            if 'semester_spinner' in self.ids:
                sem = self.ids.semester_spinner.text
                store.student_semester = "" if sem == "Selecciona tu semestre" else sem
            
            if hasattr(app, 'show_toast'):
                app.show_toast("¡Datos guardados con éxito!")
        
        if app:
            app.go_screen('home')
