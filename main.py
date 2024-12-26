import tkinter as tk  # <--- Importar tkinter como tk
from RenderQueueModel import RenderQueueModel
from RenderQueueController import RenderQueueController
from RenderQueueView import RenderQueueView

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#282828")
    model = RenderQueueModel()
    controller = RenderQueueController(model, None)  # Se crea el controlador pero sin la vista
    view = RenderQueueView(root, controller)  # Se crea la vista y se le pasa el controlador
    controller.view = view  # Se asigna la vista al controlador después de que ambos han sido creados
    root.mainloop()