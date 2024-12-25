import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]

blend_file = argv[0]
output_path = argv[1]
camera_name = argv[2]
render_engine = argv[3]  # Obtener el motor de render
start_frame = int(argv[4])
end_frame = int(argv[5])

print(f"Motor de render seleccionado: {render_engine}")

bpy.ops.wm.open_mainfile(filepath=blend_file)

# Establecer la cámara
bpy.context.scene.camera = bpy.data.objects[camera_name]

# Establecer el rango de frames
bpy.context.scene.frame_start = start_frame
bpy.context.scene.frame_end = end_frame

# Establecer la ruta de salida
bpy.context.scene.render.filepath = output_path

# Establecer el formato de salida a PNG
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Establecer el motor de render
bpy.context.scene.render.engine = render_engine

# Renderizar la animación
bpy.ops.render.render(animation=True)