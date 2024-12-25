import tkinter as tk  # <--- Importar tkinter como tk
from RenderQueueModel import RenderQueueModel
from RenderQueueController import RenderQueueController
from RenderQueueView import RenderQueueView

if __name__ == "__main__":
    root = tk.Tk()
    model = RenderQueueModel()
    controller = RenderQueueController(model, None)
    view = RenderQueueView(root, controller)
    controller.view = view
    root.mainloop()