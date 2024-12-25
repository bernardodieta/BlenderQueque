import tkinter as tk
from tkinter import filedialog, messagebox
import re
import json # Importar json

class RenderQueueController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.model.add_observer(self)

    def add_file_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")])
        if file_path:
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
            "selected_camera": self.view.camera_var.get(),
            "start_frame": self.view.frame_start_var.get(),
            "end_frame": self.view.frame_end_var.get(),
            "resolution": self.view.resolution_var.get(),
            "format": self.view.format_var.get(),
            "output_path": self.view.output_path_var.get(),
            "file_prefix": self.view.file_prefix_var.get(),
            "render_engine": self.view.render_engine_var.get(),
            "render_threads": self.view.render_threads_var.get(),
            "shutdown_after_render": self.view.shutdown_var.get(),
            "suspend_after_render": self.view.suspend_var.get(),
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

        return True

    def start_render(self, selected_queue):
        print("Controller start_render called")
        self.model.start_render(selected_queue)

    def stop_render(self):
        print("Controller stop_render called")
        self.model.stop_render()
        
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
                messagebox.showinfo("Config Loaded", "Configuration loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading configuration: {e}")
    

    def set_shutdown_after_render(self):
        self.model.shutdown_after_render = self.view.shutdown_var.get()
        if self.model.shutdown_after_render:
            messagebox.showinfo("Apagado Automático", "La PC se apagará automáticamente cuando se completen los renders.")

    def set_suspend_after_render(self):
        self.model.suspend_after_render = self.view.suspend_var.get()
        if self.model.suspend_after_render:
            messagebox.showinfo("Suspensión Automática", "La PC se suspenderá automáticamente cuando se completen los renders.")

    def update(self, model, event_type=None, data=None):
        if event_type == "error":
            messagebox.showerror("Error", data)
        elif event_type == "render_complete":
            messagebox.showinfo("Render Complete", data)
            self.view.progress['value'] = 0
        elif event_type == "progress_update":
            self.view.update_progress_bar(data, model.queue[data]["progress"])
        else:
            self.view.update_loaded_files_tree(model.loaded_files)
            self.view.update_queue_tree(model.queue)

            if model.loaded_files:
                self.view.update_settings_from_loaded_files(len(model.loaded_files) - 1)