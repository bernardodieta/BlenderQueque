import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from SettingsFrame import SettingsFrame
from TreeviewsFrame import TreeviewsFrame

class RenderQueueView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Render Queue Manager")

        # Configurar el ícono de la ventana (si existe)
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
        self.style = ttk.Style(root)
        self.style.theme_use("clam")
        self.configure_styles()

        # Crear widgets
        self.create_widgets()

    def configure_styles(self):
        # Estilo para Treeview
        self.style.configure("Treeview",
            background=self.bg_color,
            foreground=self.fg_color,
            fieldbackground=self.bg_color,
            fieldforeground=self.fg_color,
            borderwidth=0,
            rowheight=25
        )
        self.style.map("Treeview",
            background=[("selected", "#194D80")],
            foreground=[("selected", self.fg_color)]
        )
        self.style.configure("Treeview.Heading",
            background="#505050",
            foreground=self.fg_color,
            borderwidth=0,
            relief="flat"
        )
        self.style.map("Treeview.Heading",
            background=[("active", "#505050")]
        )
        # Estilo para botones redondeados sin borde
        self.style.configure('TRounded.TButton',
            borderwidth=0,
            padding=6,
            relief="flat",
            background="#505050",
            foreground=self.fg_color,
            font=('Arial', 10)
        )
        self.style.map('TRounded.TButton',
            background=[('active', '#5a5a5a')]
        )
        # Estilo para Progressbar
        self.style.configure("Horizontal.TProgressbar",
            troughcolor="#282828",
            background="#194D80",
            darkcolor="#194D80",
            lightcolor="#194D80",
            bordercolor="#282828",
            borderwidth=0,
            relief="flat"
        )

    def create_widgets(self):
        # Frame para los botones Add y Remove
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        self.add_button = ttk.Button(button_frame, text="Add .blend File", command=self.controller.add_file_dialog, style='TRounded.TButton')
        self.add_button.pack(side="left", padx=5)

        self.remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.remove_file, style='TRounded.TButton')
        self.remove_button.pack(side="left", padx=5)
        
        
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", mode="determinate", style="Horizontal.TProgressbar")
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        # Frame para los botones de la cola
        queue_button_frame = tk.Frame(self.root, bg=self.bg_color)
        queue_button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.add_to_queue_button = ttk.Button(queue_button_frame, text="Add to Queue", command=self.add_to_render_queue, style='TRounded.TButton')
        self.add_to_queue_button.pack(side="left", padx=5)

        self.remove_from_queue_button = ttk.Button(queue_button_frame, text="Remove from Queue", command=self.remove_from_render_queue, style='TRounded.TButton')
        self.remove_from_queue_button.pack(side="left", padx=5)
        # Instanciar SettingsFrame
        self.settings_frame = SettingsFrame(self.root, self.controller, self.bg_color, self.fg_color)
        self.settings_frame.grid(row=0, column=1, rowspan=3, padx=(0, 10), pady=10, sticky="nsew")

        # Instanciar TreeviewsFrame
        self.treeviews_frame = TreeviewsFrame(self.root, self.controller, self.bg_color, self.fg_color, self.entry_bg_color, self.entry_fg_color)
        self.treeviews_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Botones para Guardar y Cargar la configuracion
        config_button_frame = tk.Frame(self.root, bg=self.bg_color)
        config_button_frame.grid(row=3, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.save_config_button = ttk.Button(config_button_frame, text="Save Config", command=self.controller.save_config, style='TRounded.TButton')
        self.save_config_button.pack(side="left", padx=5)

        self.load_config_button = ttk.Button(config_button_frame, text="Load Config", command=self.controller.load_config, style='TRounded.TButton')
        self.load_config_button.pack(side="left", padx=5)

        # Botones para iniciar y detener renderizado
        self.start_button = ttk.Button(self.root, text="Start Render", command=self.start_render, style='TRounded.TButton')
        self.start_button.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.stop_button = ttk.Button(self.root, text="Stop Render", command=self.stop_render, style='TRounded.TButton')
        self.stop_button.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Vista previa
        self.preview_label = tk.Label(self.root, text="Preview", bg=self.bg_color, fg=self.fg_color, bd=2, relief="groove")
        self.preview_label.grid(row=4, column=1, sticky="sew", padx=10, pady=(0, 10)) # <--- Reubicado arriba del monitor de sistema

        # Panel de Monitoreo
        self.monitoring_frame = tk.LabelFrame(self.root, text="System Resources", bg=self.label_bg_color, fg=self.label_fg_color, bd=2, relief="groove")
        self.monitoring_frame.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")

        self.cpu_label = tk.Label(self.monitoring_frame, text="CPU Usage: 0%", bg=self.label_bg_color, fg=self.label_fg_color)
        self.cpu_label.pack(side="left", padx=10, pady=5)

        self.ram_label = tk.Label(self.monitoring_frame, text="RAM Usage: 0%", bg=self.label_bg_color, fg=self.label_fg_color)
        self.ram_label.pack(side="left", padx=10, pady=5)

        # Configurar el redimensionamiento de las columnas
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_rowconfigure(4, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def update_monitoring_labels(self, cpu_percent, ram_percent):
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
        self.ram_label.config(text=f"RAM Usage: {ram_percent:.1f}%")

    def remove_file(self):
        selected_items = list(self.treeviews_frame.selected_loaded_files)
        for item_id in selected_items:
            index = self.treeviews_frame.loaded_files_tree.index(item_id)
            self.controller.remove_file(index)
            self.treeviews_frame.loaded_files_tree.delete(item_id)
            self.treeviews_frame.selected_loaded_files.remove(item_id)

    def show_preview(self, image_path):
            """Muestra la imagen de previsualización."""
            try:
                if image_path.lower().endswith('.mp4'):
                    # Si es un video, muestra un mensaje o un ícono representativo
                    self.preview_label.config(text="Video Preview\n(Click to open)", cursor="hand2")
                    self.preview_label.bind("<Button-1>", lambda e: os.startfile(image_path))
                    self.preview_label.image = None  # Limpia cualquier imagen anterior
                else:
                    # Si es una imagen, intenta mostrarla
                    img = Image.open(image_path)
                    img.thumbnail((200, 200))  # Ajusta el tamaño de la vista previa
                    photo = ImageTk.PhotoImage(img)
                    self.preview_label.config(image=photo, text="")
                    self.preview_label.image = photo
                    self.preview_label.bind("<Button-1>", lambda e: os.startfile(image_path))
            except Exception as e:
                print(f"Error al mostrar la vista previa: {e}")
                self.preview_label.config(text="Preview Error", image=None)

    def start_render(self):
        print("Start Render button clicked")
        if not self.controller.model.queue:
            messagebox.showerror("Error", "Queue is empty!")
            return

        selected_queue = [
            item
            for i, item in enumerate(self.controller.model.queue)
            if self.treeviews_frame.queue_tree.get_children()[i] in self.treeviews_frame.selected_items
        ]
        print("Selected queue:", selected_queue)
        if not selected_queue:
            messagebox.showerror("Error", "No items selected for rendering!")
            return

        self.controller.start_render(selected_queue, self.progress_bar)

    def stop_render(self):
        print("Stop Render button clicked")
        self.controller.stop_render()

    def add_to_render_queue(self):
        if not self.treeviews_frame.selected_loaded_files:
            messagebox.showerror("Error", "No files selected to add to the render queue.")
            return

        for item_id in list(self.treeviews_frame.selected_loaded_files):
            index = self.treeviews_frame.loaded_files_tree.index(item_id)
            self.controller.add_to_queue(index)

        self.treeviews_frame.selected_loaded_files.clear()  # Limpiar la lista después de añadir a la cola
        for item in self.treeviews_frame.loaded_files_tree.get_children():
            self.treeviews_frame.loaded_files_tree.item(item, tags=[]) # Quitar el tag "selected" de los items
    
    def remove_from_render_queue(self):
        selected_items = list(self.treeviews_frame.selected_items)
        for item_id in selected_items:
            index = self.treeviews_frame.queue_tree.index(item_id)
            self.controller.remove_from_queue(index)

    def save_config(self):
        self.controller.save_config()

    def load_config(self):
        self.controller.load_config()
        
    def update_loaded_files_tree(self, loaded_files):
        self.treeviews_frame.loaded_files_tree.delete(*self.treeviews_frame.loaded_files_tree.get_children())
        for item in loaded_files:
            self.treeviews_frame.loaded_files_tree.insert("", tk.END, values=(os.path.basename(item["file"]),))

    def update_queue_tree(self, queue):
        self.treeviews_frame.queue_tree.delete(*self.treeviews_frame.queue_tree.get_children())
        for item in queue:
            progress = item.get("progress", 0)
            self.treeviews_frame.queue_tree.insert(
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
        item_id = self.queue_tree.get_children()[index] # <--- Modificar esta linea
        values = list(self.queue_tree.item(item_id, "values"))
        values[-1] = f"{progress}%"
        self.queue_tree.item(item_id, values=values) # <--- Modificar esta linea
        
    def update_settings_from_loaded_files(self, index):
        if index < len(self.controller.model.loaded_files):
            item = self.controller.model.loaded_files[index]
            self.settings_frame.camera_dropdown["values"] = item["cameras"]
            self.settings_frame.camera_var.set(item["selected_camera"])
            self.settings_frame.frame_start_var.set(item["start_frame"])
            self.settings_frame.frame_end_var.set(item["end_frame"])
            self.settings_frame.resolution_var.set(item["resolution"])
            self.settings_frame.format_var.set(item["format"])
            self.settings_frame.output_path_var.set(item["output_path"])
            if "file_prefix" in item:
                self.settings_frame.file_prefix_var.set(item["file_prefix"])
            else:
                self.settings_frame.file_prefix_var.set("")
            if "render_engine" in item:
                self.settings_frame.render_engine_var.set(item["render_engine"])
            else:
                self.settings_frame.render_engine_var.set("CYCLES")
            if "render_threads" in item:
                self.settings_frame.render_threads_var.set(item["render_threads"])
            else:
                self.settings_frame.render_threads_var.set("Auto")
            if "output_format" in item:
                 self.settings_frame.output_format_var.set(item["output_format"])
            else:
                 self.settings_frame.output_format_var.set("")
            if "output_file_name" in item:
                self.settings_frame.output_file_name_var.set(item["output_file_name"])
            else:
                 self.settings_frame.output_file_name_var.set("")
            self.settings_frame.update_output_preview()