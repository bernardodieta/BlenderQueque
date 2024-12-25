import bpy
import sys

def render_animation(blend_file, output_path, camera_name, render_engine, start_frame, end_frame, render_threads):
    """
    Opens a .blend file, sets render settings, and renders an animation.

    Args:
        blend_file (str): Path to the .blend file.
        output_path (str): Path to save the rendered frames.
        camera_name (str): Name of the camera to use for rendering.
        render_engine (str): Render engine to use ('CYCLES', 'BLENDER_EEVEE', etc.).
        start_frame (int): Starting frame of the animation.
        end_frame (int): Ending frame of the animation.
        render_threads (str): Number of threads to use for rendering
    """
    try:
        bpy.ops.wm.open_mainfile(filepath=blend_file)

        # Set the camera
        if camera_name not in bpy.data.objects:
            raise ValueError(f"Camera '{camera_name}' not found in the .blend file.")
        bpy.context.scene.camera = bpy.data.objects[camera_name]

        # Set the frame range
        bpy.context.scene.frame_start = start_frame
        bpy.context.scene.frame_end = end_frame

        # Set the output path
        bpy.context.scene.render.filepath = output_path

        # Set the output format to PNG
        bpy.context.scene.render.image_settings.file_format = 'PNG'

        # Set the render engine
        bpy.context.scene.render.engine = render_engine

        # Set the render threads
        if render_threads.isdigit():
            bpy.context.scene.render.threads_mode = 'FIXED'
            bpy.context.scene.render.threads = int(render_threads)
        else:
            bpy.context.scene.render.threads_mode = 'AUTO'

        # Render the animation
        bpy.ops.render.render(animation=True)

    except Exception as e:
        print(f"Error during rendering: {e}")
        sys.exit(1)

if __name__ == "__main__":
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]

    if len(argv) != 7:
        print("Usage: blender --background --python script_blender.py -- <blend_file> <output_path> <camera_name> <render_engine> <start_frame> <end_frame> <render_threads>")
        sys.exit(1)

    blend_file = argv[0]
    output_path = argv[1]
    camera_name = argv[2]
    render_engine = argv[3]
    start_frame = int(argv[4])
    end_frame = int(argv[5])
    render_threads = argv[6]

    print(f"Selected render engine: {render_engine}")
    render_animation(blend_file, output_path, camera_name, render_engine, start_frame, end_frame, render_threads)