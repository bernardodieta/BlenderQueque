import bpy
import sys
import os

def render_animation(blend_file, output_path, camera_name, render_engine, start_frame, end_frame, render_threads, format_type):
    """
    Abre un archivo .blend, establece la configuración de renderizado y renderiza una animación.

    Args:
        blend_file (str): Ruta al archivo .blend.
        output_path (str): Ruta para guardar los fotogramas renderizados.
        camera_name (str): Nombre de la cámara a utilizar para el renderizado.
        render_engine (str): Motor de renderizado a utilizar ('CYCLES', 'BLENDER_EEVEE', etc.).
        start_frame (int): Fotograma inicial de la animación.
        end_frame (int): Fotograma final de la animación.
        render_threads (str): Número de hilos a utilizar para el renderizado.
        format_type (str): Formato de imagen para la salida ('PNG', 'JPEG', etc.).
    """
    try:
        bpy.ops.wm.open_mainfile(filepath=blend_file)

        # Establecer la cámara
        if camera_name not in bpy.data.objects:
            raise ValueError(f"La cámara '{camera_name}' no se encontró en el archivo .blend.")
        bpy.context.scene.camera = bpy.data.objects[camera_name]

        # Establecer el rango de fotogramas
        scene = bpy.context.scene
        scene.frame_start = start_frame
        scene.frame_end = end_frame

        # Establecer la ruta de salida base sin el número de frame
        # Blender agregará automáticamente el número de frame y la extensión
        scene.render.filepath = output_path

        # Establecer el formato de salida
        if format_type in ['PNG', 'JPEG', 'TIFF', 'BMP', 'EXR']:
            scene.render.image_settings.file_format = format_type
            if format_type == 'JPEG':
                scene.render.image_settings.quality = 90  # Ajusta la calidad del JPEG si es necesario
        else:
            raise ValueError(f"Formato de salida '{format_type}' no soportado.")

        # Establecer el motor de renderizado
        scene.render.engine = render_engine

        # Establecer los hilos de renderizado
        if render_threads.isdigit():
            scene.render.threads_mode = 'FIXED'
            scene.render.threads = int(render_threads)
        else:
            scene.render.threads_mode = 'AUTO'

        # Crear un directorio para previsualizaciones si no existe
        preview_dir = os.path.join(os.path.dirname(output_path), "previews")
        os.makedirs(preview_dir, exist_ok=True)

        # Renderizar cada fotograma y guardar una previsualización
        for frame in range(start_frame, end_frame + 1):
            scene.frame_set(frame)

            # Establecer la ruta de salida para el frame actual
            scene.render.filepath = os.path.join(output_path, f"{os.path.basename(output_path)}_{frame:04}")
            # Renderizar el fotograma
            bpy.ops.render.render(write_still=True)

            # Guardar una imagen de previsualización (cada 5 fotogramas)
            if frame % 5 == 0:
                preview_path = os.path.join(preview_dir, f"preview_{frame:04}.jpg")
                bpy.data.images['Render Result'].save_render(filepath=preview_path)
                print(f"Previsualización guardada en {preview_path}")

    except Exception as e:
        print(f"Error durante el renderizado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]

    if len(argv) != 8:
        print("Uso: blender --background --python script_blender.py -- <blend_file> <output_path> <camera_name> <render_engine> <start_frame> <end_frame> <render_threads> <format_type>")
        sys.exit(1)

    blend_file = argv[0]
    output_path = argv[1]
    camera_name = argv[2]
    render_engine = argv[3]
    start_frame = int(argv[4])
    end_frame = int(argv[5])
    render_threads = argv[6]
    format_type = argv[7].upper()  # Convertir a mayúsculas para coincidir con las constantes de Blender

    print(f"Motor de renderizado seleccionado: {render_engine}")
    render_animation(blend_file, output_path, camera_name, render_engine, start_frame, end_frame, render_threads, format_type)