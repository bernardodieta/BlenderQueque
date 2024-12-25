import tkinter as tk
from tkinter import filedialog, messagebox

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
            "render_engine": self.view.render_engine_var.get()
        }

    def start_render(self, selected_queue):
        print("Controller start_render called")  # Mensaje de depuración
        self.model.start_render(selected_queue)
        
    def stop_render(self):
        self.model.stop_render()
        
    def set_shutdown_after_render(self):
        self.model.shutdown_after_render = True
        self.model.suspend_after_render = False
        messagebox.showinfo("Apagado Automático", "La PC se apagará automáticamente cuando se completen los renders.")

    def set_suspend_after_render(self):
        self.model.shutdown_after_render = False
        self.model.suspend_after_render = True
        messagebox.showinfo("Suspensión Automática", "La PC se suspenderá automáticamente cuando se completen los renders.")

    def update(self, model, event_type=None, data=None):
        if event_type == "error":
            messagebox.showerror("Error", data)
        elif event_type == "render_complete":
            messagebox.showinfo("Render Complete", data)
            self.view.progress['value'] = 0
        elif event_type == "progress_update":
            # Actualizar la barra de progreso del ítem específico
            self.view.update_progress_bar(data, model.queue[data]["progress"])
        elif event_type == "waiting_files_update":
            messagebox.showinfo("Info", "Files added to the waiting list. They will be processed after the current render is finished.")
        else:
            # Actualizar la vista
            self.view.update_loaded_files_tree(model.loaded_files)
            self.view.update_queue_tree(model.queue)

            if model.loaded_files:
                self.view.update_settings_from_loaded_files(len(model.loaded_files) - 1)