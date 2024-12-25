import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

class RenderQueueView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Render Queue Manager")

        # Configurar el ícono de la ventana
        icon_path = "blender_icon.ico"
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                print("Error al cargar el ícono.")

        # Colores del tema oscuro
        self.bg_color = "#282828"
        self.fg_color = "#EEEEEE"
        self.entry_bg_color = "#3F3F3F"
        self.entry_fg_color = "#FFFFFF"
        self.button_bg_color = "#505050"
        self.button_fg_color = "#EEEEEE"
        self.label_bg_color = "#282828"
        self.label_fg_color = "#EEEEEE"
        self.treeview_bg_color = "#3F3F3F"
        self.treeview_fg_color = "#EEEEEE"
        self.treeview_selected_bg_color = "#194D80"
        self.treeview_header_bg_color = "#505050"
        self.progressbar_trough_color = "#282828"
        self.progressbar_bar_color = "#194D80"

        # Configuración de estilos
        self.style = ttk.Style()
        self.style = ttk.Style(root)
        self.style.theme_use("clam")

        # Estilo para Treeview
        self.style.configure("Treeview",
            background=self.treeview_bg_color,
            foreground=self.treeview_fg_color,
            fieldbackground=self.treeview_bg_color,
            fieldforeground=self.treeview_fg_color,
            borderwidth=0,
            rowheight=25
        )
        self.style.map("Treeview",
            background=[("selected", self.treeview_selected_bg_color)],
            foreground=[("selected", self.treeview_fg_color)]
        )
        self.style.configure("Treeview.Heading",
            background=self.treeview_header_bg_color,
            foreground=self.treeview_fg_color,
            borderwidth=0,
            relief="flat"
        )
        self.style.map("Treeview.Heading",
            background=[("active", self.treeview_header_bg_color)]
        )
        # Estilo para botones redondeados sin borde
        self.style.configure('TRounded.TButton',
                             borderwidth=0,
                             padding=6,
                             relief="flat",
                             background=self.button_bg_color,
                             foreground=self.button_fg_color,
                             font=('Arial', 10)) # Ajusta la fuente si es necesario
        self.style.map('TRounded.TButton',
                         background=[('active', '#5a5a5a')]) # Color al hacer clic

        # Estilo para Progressbar
        self.style.configure("Horizontal.TProgressbar",
            troughcolor=self.progressbar_trough_color,
            background=self.progressbar_bar_color,
            darkcolor=self.progressbar_bar_color,
            lightcolor=self.progressbar_bar_color,
            bordercolor=self.progressbar_trough_color,
            borderwidth=0,
            relief="flat"
        )
        self.style.map("Horizontal.TProgressbar",
            background=[("active", self.progressbar_bar_color)]
        )

        # Estilo para Combobox
        self.style.configure("TCombobox",
            fieldbackground=self.entry_bg_color,
            background=self.entry_bg_color,
            foreground=self.entry_fg_color,
            padding=5,
            arrowcolor=self.entry_fg_color
        )

        # Configurar la ventana principal
        self.root.configure(bg=self.bg_color)

        self.selected_loaded_files = set()
        self.selected_items = set()

        # Crear widgets
        self.create_widgets()

    def create_widgets(self):
        
        # Frame para los botones Add y Remove
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        self.add_button = ttk.Button(button_frame, text="Add .blend File", command=self.add_file, style='TRounded.TButton')
        self.add_button.pack(side="left", padx=5)

        self.remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.remove_file, style='TRounded.TButton')
        self.remove_button.pack(side="left", padx=5)

        # Frame para configuraciones
        self.settings_frame = tk.LabelFrame(self.root, text="Settings", padx=20, pady=20, bg=self.label_bg_color, fg=self.label_fg_color, bd=2, relief="groove")
        self.settings_frame.grid(row=0, column=1, rowspan=3, padx=(0, 10), pady=10, sticky="nsew")

        # Frame para los Treeviews
        treeviews_frame = tk.Frame(self.root, bg=self.bg_color)
        treeviews_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Treeview para archivos cargados
        self.loaded_files_tree = ttk.Treeview(treeviews_frame, columns=("File"), show="headings")
        self.loaded_files_tree.heading("File", text="Loaded Files")
        self.loaded_files_tree.column("File", anchor="center", stretch=True)
        self.loaded_files_tree.grid(row=0, column=0, sticky="nsew")
        self.loaded_files_tree.bind("<Button-1>", self.on_loaded_files_tree_click)

        # Scrollbar para el Treeview de archivos cargados
        loaded_scrollbar = ttk.Scrollbar(treeviews_frame, orient="vertical", command=self.loaded_files_tree.yview)
        loaded_scrollbar.grid(row=0, column=1, sticky="ns")
        self.loaded_files_tree.configure(yscrollcommand=loaded_scrollbar.set)

        # Treeview para la cola de render
        self.queue_tree = ttk.Treeview(
            treeviews_frame,
            columns=("File", "Start", "End", "Output", "Camera", "Format", "Resolution", "Progress"),
            show="headings",
        )
        self.queue_tree.heading("File", text="File")
        self.queue_tree.heading("Start", text="Start Frame")
        self.queue_tree.heading("End", text="End Frame")
        self.queue_tree.heading("Output", text="Output Path")
        self.queue_tree.heading("Camera", text="Camera")
        self.queue_tree.heading("Format", text="Format")
        self.queue_tree.heading("Resolution", text="Resolution")
        self.queue_tree.heading("Progress", text="Progress")
        for col in (
            "File",
            "Start",
            "End",
            "Output",
            "Camera",
            "Format",
            "Resolution",
            "Progress",
        ):
            self.queue_tree.column(col, anchor="center", stretch=True)
        self.queue_tree.grid(row=1, column=0, sticky="nsew")
        self.queue_tree.bind("<Button-1>", self.on_tree_click)

        # Scrollbar para el Treeview de la cola de render
        queue_scrollbar = ttk.Scrollbar(treeviews_frame, orient="vertical", command=self.queue_tree.yview)
        queue_scrollbar.grid(row=1, column=1, sticky="ns")
        self.queue_tree.configure(yscrollcommand=queue_scrollbar.set)

        # Configurar el redimensionamiento de los Treeviews y su frame
        treeviews_frame.grid_rowconfigure(0, weight=1)
        treeviews_frame.grid_rowconfigure(1, weight=1)
        treeviews_frame.grid_columnconfigure(0, weight=1)

        # Frame para los botones de la cola
        queue_button_frame = tk.Frame(self.root, bg=self.bg_color)
        queue_button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.add_to_queue_button = ttk.Button(queue_button_frame, text="Add to Queue", command=self.add_to_render_queue, style='TRounded.TButton')
        self.add_to_queue_button.pack(side="left", padx=5)

        self.remove_from_queue_button = ttk.Button(queue_button_frame, text="Remove from Queue", command=self.remove_from_render_queue, style='TRounded.TButton')
        self.remove_from_queue_button.pack(side="left", padx=5)
        
        # Botones para Guardar y Cargar la configuracion
        config_button_frame = tk.Frame(self.root, bg=self.bg_color)
        config_button_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.save_config_button = ttk.Button(config_button_frame, text="Save Config", command=self.save_config, style='TRounded.TButton')
        self.save_config_button.pack(side="left", padx=5)

        self.load_config_button = ttk.Button(config_button_frame, text="Load Config", command=self.load_config, style='TRounded.TButton')
        self.load_config_button.pack(side="left", padx=5)

        # Botones para iniciar y detener renderizado
        self.start_button = ttk.Button(self.root, text="Start Render", command=self.start_render, style='TRounded.TButton')
        self.start_button.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.stop_button = ttk.Button(self.root, text="Stop Render", command=self.stop_render, style='TRounded.TButton')
        self.stop_button.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Configuraciones
        self.create_settings_entries()

        # Configurar el redimensionamiento de las columnas
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_rowconfigure(4, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def create_settings_entries(self):
        # Etiquetas de grupo
        ttk.Label(self.settings_frame, text="Output Settings:", background=self.label_bg_color, foreground=self.label_fg_color, font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        ttk.Label(self.settings_frame, text="Render Settings:", background=self.label_bg_color, foreground=self.label_fg_color, font=("Arial", 14, "bold")).grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 5))

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

        current_row = 1  # Empezamos en la fila 1 después del título "Output Settings"
        self.create_setting_entry("File Name Prefix:", self.file_prefix_var, current_row)
        current_row += 1
        self.create_setting_entry("Resolution:", self.resolution_var, current_row)
        current_row += 1
        self.create_output_format_buttons(row=current_row)  # La fila para los botones de formato
        current_row += 1
        self.create_setting_entry("Output Path:", self.output_path_var, current_row)
        current_row += 1
        self.output_path_button = tk.Button(self.settings_frame, text="Browse", command=self.browse_output_path, bg=self.button_bg_color, fg=self.button_fg_color)
        self.output_path_button.grid(row=current_row + 1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5)) # Lo dejamos en la siguiente fila abarcando ambas columnas
        current_row += 2 # Incrementamos para el siguiente grupo de configuraciones

        current_row = 8 # Empezamos en la fila 8 después del título "Render Settings"
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
        self.shutdown_check = tk.Checkbutton(self.settings_frame, text="Shutdown After Render", variable=self.shutdown_var, bg=self.label_bg_color, fg=self.label_fg_color, selectcolor=self.bg_color)
        self.shutdown_check.grid(row=current_row + 1, column=0, columnspan=2, sticky="w", pady=(10, 0))
        current_row += 1

        # Checkbox para suspender la PC al finalizar
        self.suspend_var = tk.BooleanVar(value=False)
        self.suspend_check = tk.Checkbutton(self.settings_frame, text="Suspend After Render", variable=self.suspend_var, bg=self.label_bg_color, fg=self.label_fg_color, selectcolor=self.bg_color)
        self.suspend_check.grid(row=current_row + 1, column=0, columnspan=2, sticky="w")

    def create_output_format_buttons(self, row):
      # Frame para los botones de formato
      format_frame = tk.Frame(self.settings_frame, bg=self.label_bg_color)
      format_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

      # Botones para seleccionar el formato
      tk.Button(format_frame, text="PNG", command=lambda: self.set_output_format("PNG"), bg=self.button_bg_color, fg=self.button_fg_color).pack(side="left", padx=2)
      tk.Button(format_frame, text="JPG", command=lambda: self.set_output_format("JPEG"), bg=self.button_bg_color, fg=self.button_fg_color).pack(side="left", padx=2)
      tk.Button(format_frame, text="TIFF", command=lambda: self.set_output_format("TIFF"), bg=self.button_bg_color, fg=self.button_fg_color).pack(side="left", padx=2)
      tk.Button(format_frame, text="SVG", command=lambda: self.set_output_format("SVG"), bg=self.button_bg_color, fg=self.button_fg_color).pack(side="left", padx=2)


    def create_setting_entry(self, label_text, variable, row, entry_type="text"):
        # Crear etiqueta en la fila actual, columna 0
        tk.Label(self.settings_frame, text=label_text, bg=self.label_bg_color, fg=self.label_fg_color).grid(row=row, column=0, sticky="w", padx=5, pady=(10, 5)) # Ajustamos el pady

        # Crear y posicionar el campo de entrada en la misma fila, columna 1
        entry_font = ("Arial", 10)  # Puedes ajustar el tamaño de la fuente aquí
        entry_pady = 5  # Ajustamos el padding vertical del entry

        if entry_type == "int":
            entry = tk.Entry(self.settings_frame, textvariable=variable, width=25, bg=self.entry_bg_color, fg=self.entry_fg_color, font=entry_font)
        elif label_text == "Camera:":
            self.camera_dropdown = ttk.Combobox(self.settings_frame, textvariable=variable, state="readonly", width=27, font=entry_font)
            entry = self.camera_dropdown
        elif label_text == "Render Engine:":
            self.render_engine_dropdown = ttk.Combobox(self.settings_frame, textvariable=self.render_engine_var, state="readonly", width=27, font=entry_font)
            self.render_engine_dropdown["values"] = ["CYCLES", "BLENDER_EEVEE", "BLENDER_WORKBENCH"]
            entry = self.render_engine_dropdown
        else:
            entry = tk.Entry(self.settings_frame, textvariable=variable, width=25, bg=self.entry_bg_color, fg=self.entry_fg_color, font=entry_font)

        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=entry_pady) # Ajustamos el pady del entry

        if entry_type == "text":
            if label_text == "Resolution:":
                self.add_placeholder_to(entry, "e.g., 1920x1080")
            elif label_text == "Output Path:":
                self.add_placeholder_to(entry, "e.g., /path/to/output")
            elif label_text == "File Name Prefix:":
                self.add_placeholder_to(entry, "e.g., MyProject_")
        elif entry_type == "int":
            if label_text == "Start Frame:":
                self.add_placeholder_to(entry, "Start")
            elif label_text == "End Frame:":
                self.add_placeholder_to(entry, "End")
        elif label_text == "Render Threads:":
            self.add_placeholder_to(entry, "e.g., Auto, 4, 8")

    def add_file(self):
        self.controller.add_file_dialog()

    def remove_file(self):
        selected_items = list(self.selected_loaded_files)
        for item_id in selected_items:
            index = self.loaded_files_tree.index(item_id)
            self.controller.remove_file(index)
            self.loaded_files_tree.delete(item_id)
            self.selected_loaded_files.remove(item_id)

    def on_loaded_files_tree_click(self, event):
        region = self.loaded_files_tree.identify_region(event.x, event.y)
        if region == "cell":
            item_id = self.loaded_files_tree.identify_row(event.y)
            if item_id:
                if item_id in self.selected_loaded_files:
                    self.selected_loaded_files.remove(item_id)
                    self.loaded_files_tree.item(item_id, tags=[])
                else:
                    self.selected_loaded_files.add(item_id)
                    self.loaded_files_tree.item(item_id, tags=["selected"])

                self.loaded_files_tree.tag_configure("selected", background=self.treeview_selected_bg_color)

                for item in self.loaded_files_tree.get_children():
                    if item in self.selected_loaded_files:
                        self.loaded_files_tree.item(item, tags=["selected"])
                    else:
                        self.loaded_files_tree.item(item, tags=[])

                index = self.loaded_files_tree.index(item_id)
                self.update_settings_from_loaded_files(index)

    def on_tree_click(self, event):
        region = self.queue_tree.identify_region(event.x, event.y)
        if region == "cell":
            item_id = self.queue_tree.identify_row(event.y)
            if item_id:
                if item_id in self.selected_items:
                    self.selected_items.remove(item_id)
                    self.queue_tree.item(item_id, tags=[])
                else:
                    self.selected_items.add(item_id)
                    self.queue_tree.item(item_id, tags=["selected"])

                self.queue_tree.tag_configure("selected", background=self.treeview_selected_bg_color)

                for item in self.queue_tree.get_children():
                    if item in self.selected_items:
                        self.queue_tree.item(item, tags=["selected"])
                    else:
                        self.queue_tree.item(item, tags=[])

    def add_to_render_queue(self):
        if not self.selected_loaded_files:
            messagebox.showerror("Error", "No files selected to add to the render queue.")
            return

        for item_id in list(self.selected_loaded_files):
            index = self.loaded_files_tree.index(item_id)
            self.controller.add_to_queue(index)

        self.selected_loaded_files.clear()  # Limpiar la lista después de añadir a la cola
        for item in self.loaded_files_tree.get_children():
            self.loaded_files_tree.item(item, tags=[])  # Quitar el tag "selected" de los items

    def remove_from_render_queue(self):
        selected_items = list(self.selected_items)
        for item_id in selected_items:
            index = self.queue_tree.index(item_id)
            self.controller.remove_from_queue(index)

    def start_render(self):
        print("Start Render button clicked")
        if not self.controller.model.queue:
            messagebox.showerror("Error", "Queue is empty!")
            return

        selected_queue = [
            item
            for i, item in enumerate(self.controller.model.queue)
            if self.queue_tree.get_children()[i] in self.selected_items
        ]
        print("Selected queue:", selected_queue)
        if not selected_queue:
            messagebox.showerror("Error", "No items selected for rendering!")
            return

        self.controller.start_render(selected_queue)

    def stop_render(self):
        print("Stop Render button clicked")
        self.controller.stop_render()
        
    def save_config(self):
        self.controller.save_config()
        
    def load_config(self):
        self.controller.load_config()

    def update_loaded_files_tree(self, loaded_files):
        self.loaded_files_tree.delete(*self.loaded_files_tree.get_children())
        for item in loaded_files:
            self.loaded_files_tree.insert("", tk.END, values=(os.path.basename(item["file"]),))

    def update_queue_tree(self, queue):
        self.queue_tree.delete(*self.queue_tree.get_children())
        for item in queue:
            progress = item.get("progress", 0)
            self.queue_tree.insert(
                "",
                tk.END,
                values=(
                    os.path.basename(item["file"]),
                    item["start_frame"],
                    item["end_frame"],
                    item["output_path"],
                    item["selected_camera"],
                    item["format"],
                    item["resolution"],
                    f"{progress}%",
                ),
            )

    def update_progress_bar(self, index, progress):
        item_id = self.queue_tree.get_children()[index]
        values = list(self.queue_tree.item(item_id, "values"))
        values[-1] = f"{progress}%"
        self.queue_tree.item(item_id, values=values)

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

    def set_output_format(self, format):
        self.format_var.set(format)
        messagebox.showinfo("Formato Seleccionado", f"Formato de salida establecido en: {format}")

    def set_shutdown_after_render(self):
        self.controller.set_shutdown_after_render()

    def set_suspend_after_render(self):
        self.controller.set_suspend_after_render()

    def browse_output_path(self):
        selected_items = self.loaded_files_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a file from the loaded files first.")
            return

        directory = filedialog.askdirectory()
        if directory:
            index = self.loaded_files_tree.index(selected_items[0])
            self.controller.model.loaded_files[index]["output_path"] = directory
            self.update_settings_from_loaded_files(index)

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