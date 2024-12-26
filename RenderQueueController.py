import tkinter as tk
from tkinter import filedialog, messagebox
import re
import json
import psutil  # Importar psutil
import datetime
import os

class RenderQueueController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.model.add_observer(self)
        self.is_monitoring = False # Bandera para indicar si se esta monitoreando o no.
    def add_file_dialog(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Blender Files", "*.blend")])
        if file_paths:
            for file_path in file_paths:
                cameras = self.model.get_cameras_from_blend(file_path)
                if cameras:
                    self.model.add_file(file_path, cameras)
                else:
                    messagebox.showerror("Error", f"No cameras found in {file_path}")

    def remove_file(self, index):
        self.model.remove_file(index)

    def add_to_queue(self, index):
        settings = self.get_settings()
        if self.validate_settings(settings):  # Validar configuraciones antes de agregar a la cola
            self.model.add_to_queue(index, settings)

    def remove_from_queue(self, index):
        self.model.remove_from_queue(index)

    def update_file_settings(self, index, settings):
        self.model.update_file_settings(index, settings)

    def get_settings(self):
        return {
            "selected_camera": self.view.settings_frame.camera_var.get(), # <--- Acceder a través de settings_frame
            "start_frame": self.view.settings_frame.frame_start_var.get(), # <--- Acceder a través de settings_frame
            "end_frame": self.view.settings_frame.frame_end_var.get(), # <--- Acceder a través de settings_frame
            "resolution": self.view.settings_frame.resolution_var.get(), # <--- Acceder a través de settings_frame
            "format": self.view.settings_frame.format_var.get(), # <--- Acceder a través de settings_frame
            "output_path": self.view.settings_frame.output_path_var.get(), # <--- Acceder a través de settings_frame
            "output_format": self.view.settings_frame.output_format_var.get(), # <--- Acceder a través de settings_frame
            "file_prefix": self.view.settings_frame.file_prefix_var.get(), # <--- Acceder a través de settings_frame
            "render_engine": self.view.settings_frame.render_engine_var.get(), # <--- Acceder a través de settings_frame
            "render_threads": self.view.settings_frame.render_threads_var.get(), # <--- Acceder a través de settings_frame
            "shutdown_after_render": self.view.settings_frame.shutdown_var.get(), # <--- Acceder a través de settings_frame
            "suspend_after_render": self.view.settings_frame.suspend_var.get(), # <--- Acceder a través de settings_frame
            "output_file_name": self.view.settings_frame.output_file_name_var.get(), # <--- Acceder a través de settings_frame
            "use_custom_alerts": self.view.settings_frame.use_custom_alerts_var.get(), # <--- Acceder a través de settings_frame
        }

    def validate_settings(self, settings):
        # Validar resolución usando una expresión regular
        resolution_pattern = re.compile(r'^\d+x\d+$')
        if not resolution_pattern.match(settings["resolution"]):
            messagebox.showerror("Error", "Invalid resolution format. Please use format like '1920x1080'.")
            return False

        # Validar frames
        try:
            start_frame = int(settings["start_frame"])
            end_frame = int(settings["end_frame"])
            if start_frame < 0 or end_frame < 0 or start_frame > end_frame:
                 messagebox.showerror("Error", "Invalid frame range. Start and end frames must be positive integers, and the start frame must be less than or equal to the end frame.")
                 return False
        except ValueError:
            messagebox.showerror("Error", "Invalid frame values. Please enter integers for start and end frames.")
            return False

        # Validar la ruta de salida
        if not settings["output_path"]:
            messagebox.showerror("Error", "Output path cannot be empty.")
            return False

        # Validar que el numero de hilos sea Auto o un numero
        threads_pattern = re.compile(r'^(Auto|\d+)$', re.IGNORECASE)
        if not threads_pattern.match(settings["render_threads"]):
            messagebox.showerror("Error", "Invalid number of threads, must be 'Auto' or a number")
            return False
    
        if not self.validate_output_format(settings["output_format"]):
             messagebox.showerror("Error", "Invalid output format. Check if all variables are correctly used")
             return False

        return True

    def start_render(self, selected_queue, progress_bar): # <--- Añadir progress_bar como parámetro
        print("Controller start_render called")
        for item in selected_queue:
            item["output_path"] = self.process_output_format(item["output_path"], item["output_format"], item.get("output_file_name",""))
        self.model.start_render(selected_queue, progress_bar) # <--- Pasa la barra de progreso al modelo
        self.start_monitoring()

    def stop_render(self):
        print("Controller stop_render called")
        self.model.stop_render()
        self.stop_monitoring()  # Detener el monitoreo al detener el render
        
    def save_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            config_data = self.model.to_dict()
            try:
                 with open(file_path, "w") as f:
                    json.dump(config_data, f, indent=4)
                 messagebox.showinfo("Config Saved", "Configuration saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving configuration: {e}")

    def load_config(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                   config_data = json.load(f)
                
                self.model.from_dict(config_data)
                self.view.update_loaded_files_tree(self.model.loaded_files)
                self.view.update_queue_tree(self.model.queue)
                self.view.update_output_preview()
                messagebox.showinfo("Config Loaded", "Configuration loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading configuration: {e}")

    def sort_queue(self, sort_by):
        self.model.sort_queue(sort_by)

    def filter_loaded_files(self, filter_text):
        filtered_files = self.model.filter_loaded_files(filter_text)
        self.view.update_loaded_files_tree(filtered_files)

    def set_shutdown_after_render(self):
        self.model.shutdown_after_render = self.view.shutdown_var.get()
        if self.model.shutdown_after_render:
            messagebox.showinfo("Apagado Automático", "La PC se apagará automáticamente cuando se completen los renders.")

    def set_suspend_after_render(self):
        self.model.suspend_after_render = self.view.suspend_var.get()
        if self.model.suspend_after_render:
            messagebox.showinfo("Suspensión Automática", "La PC se suspenderá automáticamente cuando se completen los renders.")

    def process_output_format(self, output_path, output_format, output_file_name):
            now = datetime.datetime.now()
            output = output_format
            output = output.replace("{{date}}", now.strftime("%Y-%m-%d"))
            output = output.replace("{{time}}", now.strftime("%H-%M-%S"))
            output = output.replace("{{frame}}", "//") # <---- Esto es para que genere frames intermedios

            if output_file_name:
                output = f"{output_path}/{output_file_name}"
            else:
                output = f"{output_path}/{output}"

            return output
    
    def update(self, model, event_type=None, data=None):
            if event_type == "error":
                messagebox.showerror("Error", data)
            elif event_type == "render_complete":
                messagebox.showinfo("Render Complete", data)
                self.view.progress_bar['value'] = 0
                self.stop_monitoring()
                if self.model.shutdown_after_render:
                    self.model.shutdown_pc()
                if self.model.suspend_after_render:
                    self.model.suspend_pc()
            elif event_type == "progress_update":
                self.view.update_progress_bar(data, model.queue[data]["progress"])
                # Intenta mostrar la última imagen generada
                if model.queue:
                    last_rendered_image = self.get_last_rendered_image(model.queue[data]["output_path"])
                    if last_rendered_image:
                        self.view.show_preview(last_rendered_image)
            elif event_type == "render_complete_item":
                if self.model.use_custom_alerts:
                    self.model.send_alerts()
            else:
                self.view.update_loaded_files_tree(model.loaded_files)
                self.view.update_queue_tree(model.queue)

                if model.loaded_files:
                    self.view.update_settings_from_loaded_files(len(model.loaded_files) - 1)
    
    def get_last_rendered_image(self, output_path):
        """
        Obtiene la última imagen de previsualización renderizada de la ruta de salida.
        Ahora busca en el subdirectorio 'previews'.
        """
        try:
            # Construye la ruta al directorio de previsualizaciones
            preview_dir = os.path.join(output_path, "previews")
            
            # Lista de archivos en el directorio de previsualizaciones
            files = [f for f in os.listdir(preview_dir) if os.path.isfile(os.path.join(preview_dir, f))]

            # Filtrar por extensiones de imagen
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

            # Ordenar por fecha de modificación (la última modificada es la más reciente)
            image_files.sort(key=lambda x: os.path.getmtime(os.path.join(preview_dir, x)), reverse=True)

            if image_files:
                # Retorna la ruta completa de la última imagen de previsualización
                return os.path.join(preview_dir, image_files[0])
            else:
                return None
        except Exception as e:
            print(f"Error al obtener la última imagen renderizada: {e}")
            return None
    
    def start_monitoring(self):
         self.is_monitoring = True
         self.update_monitoring()

    def stop_monitoring(self):
        self.is_monitoring = False
    
    def update_monitoring(self):
        if self.is_monitoring:
            cpu_percent = psutil.cpu_percent()
            ram_percent = psutil.virtual_memory().percent
            self.view.update_monitoring_labels(cpu_percent, ram_percent)
            self.view.root.after(1000, self.update_monitoring)  # Actualizar cada segundo
    
    def validate_output_format(self, output_format):
        # Usamos una expresión regular para verificar si las llaves están balanceadas
        pattern = r"{{[^}]*}}"
        matches = re.findall(pattern, output_format)
        
        for match in matches:
            variable = match[2:-2].strip()
            if variable not in ["date", "time", "frame"]:
               return False

        return True
    
    def process_output_format(self, output_path, output_format, output_file_name):
        now = datetime.datetime.now()
        output = output_format
        output = output.replace("{{date}}", now.strftime("%Y-%m-%d"))
        output = output.replace("{{time}}", now.strftime("%H-%M-%S"))
        output = output.replace("{{frame}}", str(0)) # Esto lo actualiza Blender después.
        
        if output_file_name:
             output = f"{output_path}/{output_file_name}"
        else:
            output = f"{output_path}/{output}"

        return output