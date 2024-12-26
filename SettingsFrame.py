import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

class SettingsFrame(tk.LabelFrame):
    def __init__(self, parent, controller, bg_color, fg_color):
        super().__init__(parent, text="Settings", padx=20, pady=20, bg=bg_color, fg=fg_color, bd=2, relief="groove")
        self.controller = controller
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.entry_bg_color = "#3F3F3F"
        self.entry_fg_color = "#FFFFFF"
        self.button_bg_color = "#505050"
        self.button_fg_color = "#EEEEEE"
        self.output_preview_label = tk.Label(self, text="", bg=self.bg_color, fg=self.fg_color)
        self.output_preview_label.grid(row=6, column=0, columnspan=2, sticky="w", padx=5)
        self.create_settings_entries()
        
    def create_output_format_buttons(self, row):
        # Frame para los botones de formato
        format_frame = tk.Frame(self, bg=self.bg_color)
        format_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

        # Placeholder para el formato de salida
        tk.Label(format_frame, text="Format:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=2)
        self.output_format_entry = tk.Entry(format_frame, textvariable=self.output_format_var, width=25, bg=self.entry_bg_color, fg=self.entry_fg_color)
        self.output_format_entry.pack(side="left", fill='x', expand=True)
        self.output_format_var.trace("w", lambda name, index, mode: self.update_output_preview())
        self.add_placeholder_to(self.output_format_entry, "e.g., image_{{frame}}")

        # Botones para seleccionar el formato
        formats = ["PNG", "JPEG", "TIFF", "EXR","MP4"]
        self.format_dropdown = ttk.Combobox(format_frame, textvariable=self.format_var, state="readonly", width=8)
        self.format_dropdown["values"] = formats
        self.format_dropdown.pack(side="left", padx=2)
        self.format_var.trace("w", lambda *args: self.update_output_format_from_dropdown())

    def create_settings_entries(self):
        # Etiquetas de grupo
        ttk.Label(self, text="Output Settings:", background=self.bg_color, foreground=self.fg_color, font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        ttk.Label(self, text="Render Settings:", background=self.bg_color, foreground=self.fg_color, font=("Arial", 14, "bold")).grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 5))

        # Campos de entrada
        self.file_prefix_var = tk.StringVar()
        self.resolution_var = tk.StringVar(value="1920x1080")
        self.format_var = tk.StringVar(value="PNG")
        self.output_path_var = tk.StringVar()
        self.camera_var = tk.StringVar()
        self.frame_start_var = tk.IntVar(value=1)
        self.frame_end_var = tk.IntVar(value=250)
        self.render_engine_var = tk.StringVar(value="CYCLES")
        self.render_threads_var = tk.StringVar(value="Auto")
        self.output_format_var = tk.StringVar()
        self.output_file_name_var = tk.StringVar()
        self.use_custom_alerts_var = tk.BooleanVar(value=False)

        current_row = 1  # Empezamos en la fila 1 después del título "Output Settings"
        self.create_setting_entry("File Name Prefix:", self.file_prefix_var, current_row)
        current_row += 1
        self.create_setting_entry("Resolution:", self.resolution_var, current_row)
        current_row += 1
        self.create_output_format_buttons(row=current_row)  # La fila para los botones de formato
        current_row += 1
        
        # Campo para el formato de salida personalizado
        tk.Label(self, text="Output Path:", bg=self.bg_color, fg=self.fg_color).grid(row=current_row, column=0, sticky="w", padx=5, pady=(10, 5))
        output_path_frame = tk.Frame(self, bg=self.bg_color)
        output_path_frame.grid(row=current_row, column=1, sticky="ew", padx=5, pady=(10, 5))
        
        self.output_path_entry = tk.Entry(output_path_frame, textvariable=self.output_path_var, width=25, bg=self.entry_bg_color, fg=self.entry_fg_color)
        self.output_path_entry.pack(side="left", fill='x', expand=True)
        self.output_path_var.trace("w", lambda name, index, mode: self.update_output_preview())
        self.add_placeholder_to(self.output_path_entry, "e.g., /path/to/output")

        self.output_path_button = tk.Button(output_path_frame, text="Browse", command=self.browse_output_path, bg=self.button_bg_color, fg=self.button_fg_color)
        self.output_path_button.pack(side="left", padx=5)

        current_row += 1
        tk.Label(self, text="Output Format:", bg=self.bg_color, fg=self.fg_color).grid(row=current_row, column=0, sticky="w", padx=5, pady=(10, 5))
        self.output_format_entry = tk.Entry(self, textvariable=self.output_format_var, width=25, bg=self.entry_bg_color, fg=self.entry_fg_color)
        self.output_format_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        self.output_format_var.trace("w", lambda name, index, mode: self.update_output_preview())
        self.add_placeholder_to(self.output_format_entry,"e.g., out_{{frame}}")
        current_row+=1
        self.output_preview_label = tk.Label(self, text="Preview:", bg=self.bg_color, fg=self.fg_color)
        self.output_preview_label.grid(row=current_row, column=0, columnspan=2, sticky="w", padx=5) # Espacio adicional para la vista previa

        current_row += 1  # Incrementamos para el siguiente grupo de configuraciones
        
        # Campo para el nombre del archivo de salida
        self.create_setting_entry("Output File Name:", self.output_file_name_var, current_row)
        current_row += 1

        current_row = 8  # Empezamos en la fila 8 después del título "Render Settings"
        self.create_setting_entry("Camera:", self.camera_var, current_row)
        current_row += 1
        self.create_setting_entry("Start Frame:", self.frame_start_var, current_row, entry_type="int")
        current_row += 1
        self.create_setting_entry("End Frame:", self.frame_end_var, current_row, entry_type="int")
        current_row += 1
        self.create_setting_entry("Render Engine:", self.render_engine_var, current_row)
        current_row += 1
        self.create_setting_entry("Render Threads:", self.render_threads_var, current_row)
        current_row += 1

        # Checkbox para apagar la PC al finalizar
        self.shutdown_var = tk.BooleanVar(value=False)
        self.shutdown_check = tk.Checkbutton(self, text="Shutdown After Render", variable=self.shutdown_var, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color)
        self.shutdown_check.grid(row=current_row + 1, column=0, columnspan=2, sticky="w", pady=(10, 0))
        current_row += 1

        # Checkbox para suspender la PC al finalizar
        self.suspend_var = tk.BooleanVar(value=False)
        self.suspend_check = tk.Checkbutton(self, text="Suspend After Render", variable=self.suspend_var, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color)
        self.suspend_check.grid(row=current_row + 1, column=0, columnspan=2, sticky="w")
        
        current_row += 1
        self.use_custom_alerts_check = tk.Checkbutton(self, text="Use Custom Alerts", variable=self.use_custom_alerts_var, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color)
        self.use_custom_alerts_check.grid(row=current_row + 1, column=0, columnspan=2, sticky="w")

    def create_output_format_buttons(self, row):
      # Frame para los botones de formato
      format_frame = tk.Frame(self, bg=self.bg_color)
      format_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

      # Botones para seleccionar el formato
      formats = ["PNG", "JPEG", "TIFF", "EXR","MP4"]
      self.format_dropdown = ttk.Combobox(format_frame, textvariable=self.format_var, state="readonly", width=8)
      self.format_dropdown["values"] = formats
      self.format_dropdown.pack(side="left", padx=2)

    def create_setting_entry(self, label_text, variable, row, entry_type="text"):
        # Crear etiqueta en la fila actual, columna 0
        tk.Label(self, text=label_text, bg=self.bg_color, fg=self.fg_color).grid(row=row, column=0, sticky="w", padx=5, pady=(10, 5)) # Ajustamos el pady

        # Crear y posicionar el campo de entrada en la misma fila, columna 1
        entry_font = ("Arial", 10)  # Puedes ajustar el tamaño de la fuente aquí
        entry_pady = 5  # Ajustamos el padding vertical del entry

        if entry_type == "int":
            entry = tk.Entry(self, textvariable=variable, width=25, bg=self.entry_bg_color, fg=self.entry_fg_color, font=entry_font)
        elif label_text == "Camera:":
            self.camera_dropdown = ttk.Combobox(self, textvariable=variable, state="readonly", width=27, font=entry_font)
            entry = self.camera_dropdown
        elif label_text == "Render Engine:":
            self.render_engine_dropdown = ttk.Combobox(self, textvariable=self.render_engine_var, state="readonly", width=27, font=entry_font)
            self.render_engine_dropdown["values"] = ["CYCLES", "BLENDER_EEVEE", "BLENDER_WORKBENCH"]
            entry = self.render_engine_dropdown
        else:
            entry = tk.Entry(self, textvariable=variable, width=25, bg=self.entry_bg_color, fg=self.entry_fg_color, font=entry_font)

        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=entry_pady) # Ajustamos el pady del entry

        if entry_type == "text":
            if label_text == "Resolution:":
                self.add_placeholder_to(entry, "e.g., 1920x1080")
            #elif label_text == "Output Path:":
                #self.add_placeholder_to(entry, "e.g., /path/to/output")
            elif label_text == "File Name Prefix:":
                self.add_placeholder_to(entry, "e.g., MyProject_")
        elif entry_type == "int":
            if label_text == "Start Frame:":
                self.add_placeholder_to(entry, "Start")
            elif label_text == "End Frame:":
                self.add_placeholder_to(entry, "End")
        elif label_text == "Render Threads:":
            self.add_placeholder_to(entry, "e.g., Auto, 4, 8")
        elif label_text == "Output File Name:":
            self.add_placeholder_to(entry, "e.g., render_name")
    
    def update_output_preview(self):
        output_path = self.output_path_var.get()
        output_format = self.output_format_var.get()
        if output_path and output_format:
            # Simula un nombre de archivo final
            preview = self.controller.process_output_format(output_path, output_format, self.output_file_name_var.get() or "preview")
            # Eliminar caracteres especiales como \f
            preview = preview.replace("\f", "_")
            self.output_preview_label.config(text=f"Preview: {os.path.basename(preview)}")
        else:
            self.output_preview_label.config(text="Preview:")
    
    def browse_output_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path_var.set(directory)
            self.update_output_preview()

    def add_placeholder_to(self, entry, placeholder):
        padded_placeholder = "  " + placeholder + "  "  # Añadimos dos espacios a cada lado
        entry.insert(0, padded_placeholder)
        entry.config(foreground='grey')

        def focus_in(_):
            if entry.get() == padded_placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground=self.entry_fg_color)

        def focus_out(_):
            if not entry.get():
                entry.insert(0, padded_placeholder)
                entry.config(foreground='grey')

        entry.bind('<FocusIn>', focus_in)
        entry.bind('<FocusOut>', focus_out)
    
    def update_settings_from_loaded_files(self, index):
        if index < len(self.controller.model.loaded_files):
            item = self.controller.model.loaded_files[index]
            self.camera_dropdown["values"] = item["cameras"]
            self.camera_var.set(item["selected_camera"])
            self.frame_start_var.set(item["start_frame"])
            self.frame_end_var.set(item["end_frame"])
            self.resolution_var.set(item["resolution"])
            self.format_var.set(item["format"])
            self.output_path_var.set(item["output_path"])
            if "file_prefix" in item:
                self.file_prefix_var.set(item["file_prefix"])
            else:
                self.file_prefix_var.set("")
            if "render_engine" in item:
                self.render_engine_var.set(item["render_engine"])
            else:
                self.render_engine_var.set("CYCLES")
            if "render_threads" in item:
                self.render_threads_var.set(item["render_threads"])
            else:
                self.render_threads_var.set("Auto")
            if "output_format" in item:
                 self.output_format_var.set(item["output_format"])
            else:
                 self.output_format_var.set("")
            if "output_file_name" in item:
                self.output_file_name_var.set(item["output_file_name"])
            else:
                 self.output_file_name_var.set("")
            self.update_output_preview()
            
    def set_output_format(self, format):
        self.format_var.set(format)
        messagebox.showinfo("Formato Seleccionado", f"Formato de salida establecido en: {format}")

    def set_shutdown_after_render(self):
        self.controller.set_shutdown_after_render()

    def set_suspend_after_render(self):
        self.controller.set_suspend_after_render()
        
        
    def update_output_format_from_dropdown(self):
        selected_format = self.format_var.get()
        if selected_format == "MP4":
            self.output_format_var.set("video_{{date}}_{{time}}")
        elif selected_format:
            self.output_format_var.set(f"image_{{frame}}.{selected_format.lower()}")
        self.update_output_preview()