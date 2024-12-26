import tkinter as tk
from tkinter import ttk
import os

class TreeviewsFrame(tk.Frame):
    def __init__(self, parent, controller, bg_color, fg_color, entry_bg_color, entry_fg_color):
        super().__init__(parent, bg=bg_color)
        self.controller = controller
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.entry_bg_color = entry_bg_color
        self.entry_fg_color = entry_fg_color
        self.selected_loaded_files = set()
        self.selected_items = set()
        self.create_treeviews()

    def create_treeviews(self):
        # Treeview para archivos cargados
        self.loaded_files_tree = ttk.Treeview(self, columns=("File"), show="headings")
        self.loaded_files_tree.heading("File", text="Loaded Files")
        self.loaded_files_tree.column("File", anchor="center", stretch=True)
        self.loaded_files_tree.grid(row=0, column=0, sticky="nsew")
        self.loaded_files_tree.bind("<Button-1>", self.on_loaded_files_tree_click)
        
        # Campo para filtrar los archivos cargados
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(self, textvariable=self.filter_var, bg=self.entry_bg_color, fg=self.entry_fg_color)
        self.filter_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.filter_var.trace("w", lambda name, index, mode: self.controller.filter_loaded_files(self.filter_var.get()))

        # Scrollbar para el Treeview de archivos cargados
        loaded_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.loaded_files_tree.yview)
        loaded_scrollbar.grid(row=0, column=2, sticky="ns")
        self.loaded_files_tree.configure(yscrollcommand=loaded_scrollbar.set)

        # Treeview para la cola de render
        self.queue_tree = ttk.Treeview(
            self,
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
        self.queue_tree.grid(row=1, column=0, sticky="nsew", columnspan=2)
        self.queue_tree.bind("<Button-1>", self.on_tree_click)

        # Scrollbar para el Treeview de la cola de render
        queue_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.queue_tree.yview)
        queue_scrollbar.grid(row=1, column=2, sticky="ns")
        self.queue_tree.configure(yscrollcommand=queue_scrollbar.set)

        # Configurar el redimensionamiento de los Treeviews y su frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Menu contextual para la cola de render
        self.queue_menu = tk.Menu(self, tearoff=0)
        self.queue_menu.add_command(label="Sort by File Name", command=lambda: self.controller.sort_queue("File Name"))
        self.queue_menu.add_command(label="Sort by Start Frame", command=lambda: self.controller.sort_queue("Start Frame"))
        self.queue_menu.add_command(label="Sort by End Frame", command=lambda: self.controller.sort_queue("End Frame"))
        self.queue_menu.add_command(label="Sort by Output Path", command=lambda: self.controller.sort_queue("Output Path"))
        self.queue_menu.add_command(label="Sort by Camera", command=lambda: self.controller.sort_queue("Camera"))
        self.queue_menu.add_command(label="Sort by Format", command=lambda: self.controller.sort_queue("Format"))
        self.queue_menu.add_command(label="Sort by Resolution", command=lambda: self.controller.sort_queue("Resolution"))
        self.queue_tree.bind("<Button-3>", self.show_queue_menu)

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

                self.loaded_files_tree.tag_configure("selected", background=self.controller.view.treeview_selected_bg_color)

                for item in self.loaded_files_tree.get_children():
                    if item in self.selected_loaded_files:
                        self.loaded_files_tree.item(item, tags=["selected"])
                    else:
                        self.loaded_files_tree.item(item, tags=[])

                index = self.loaded_files_tree.index(item_id)
                self.controller.view.update_settings_from_loaded_files(index)

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

                self.queue_tree.tag_configure("selected", background=self.controller.view.treeview_selected_bg_color)

                for item in self.queue_tree.get_children():
                    if item in self.selected_items:
                        self.queue_tree.item(item, tags=["selected"])
                    else:
                        self.queue_tree.item(item, tags=[])

    def show_queue_menu(self, event):
        self.queue_menu.post(event.x_root, event.y_root)