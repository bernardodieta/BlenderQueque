import os
import subprocess
import platform
import re
from threading import Thread, Event

class RenderQueueModel:
    def __init__(self):
        self.queue = []
        self.loaded_files = []
        self.is_rendering = False
        self.observers = []
        self.shutdown_after_render = False
        self.suspend_after_render = False
        self.stop_event = Event()
        self.current_process = None
        self.waiting_files = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type=None, message=None):
        for observer in self.observers:
            observer.update(self, event_type, message)

    def add_file(self, file_path, cameras):
        default_output_path = os.path.dirname(file_path)
        new_file = {
            "file": file_path,
            "cameras": cameras,
            "selected_camera": cameras[0],
            "start_frame": 1,
            "end_frame": 250,
            "resolution": "1920x1080",
            "format": "PNG",
            "output_path": default_output_path,
            "render_engine": "CYCLES",
            "file_prefix": "",
            "progress": 0
        }
        if self.is_rendering:
            self.waiting_files.append(new_file)
            self.notify_observers("waiting_files_update") 
        else:
            self.loaded_files.append(new_file)
            self.notify_observers()

    def remove_file(self, index):
        if index < len(self.loaded_files):
            self.loaded_files.pop(index)
            self.notify_observers()

    def add_to_queue(self, index, settings):
        if index < len(self.loaded_files):
            file_data = self.loaded_files.pop(index)
            file_data.update(settings)
            file_data["progress"] = 0  # Agregar un campo para el progreso
            self.queue.append(file_data)
            self.notify_observers()

    def remove_from_queue(self, index):
        if index < len(self.queue):
            self.queue.pop(index)
            self.notify_observers()

    def update_file_settings(self, index, settings):
        if index < len(self.loaded_files):
            self.loaded_files[index].update(settings)
            self.notify_observers()

    def start_render(self, selected_queue):
        print("Model start_render called")
        self.is_rendering = True
        self.stop_event.clear()
        render_thread = Thread(target=self.process_queue, args=(selected_queue,))
        render_thread.start()

    def stop_render(self):
        print("Model stop_render called")
        if self.is_rendering:
            self.is_rendering = False
            self.stop_event.set()
            if self.current_process:
                print("Terminating current Blender process")
                self.current_process.terminate()

    def process_queue(self, queue_to_render):
        print("process_queue started")
        for index, item in enumerate(queue_to_render):
            if self.stop_event.is_set():
                print("Rendering stopped by user")
                break

            print(f"Processing item: {item}")

            blend_file = item["file"]
            output_path = item["output_path"]
            resolution = item["resolution"]
            format_type = item["format"]
            camera = item["selected_camera"]
            start_frame = int(item["start_frame"]) # Convertir a entero
            end_frame = int(item["end_frame"]) # Convertir a entero
            file_prefix = item.get("file_prefix", "")
            render_engine = item.get("render_engine", "CYCLES")

            output_dir = output_path.replace("\\", "/")
            output_file = f"{output_dir}/{file_prefix}{index:04}.png"

            command = [
                "blender",
                "--background",
                blend_file,
                "--python",
                "script_blender.py",
                "--",
                blend_file,
                output_file,
                camera,
                render_engine,
                str(start_frame),
                str(end_frame),
            ]

            print(f"Running command: {' '.join(command)}")

            try:
                self.current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, encoding="utf-8")

                # Monitorear la salida de Blender para obtener el progreso
                for line in iter(self.current_process.stdout.readline, ""):
                    if self.stop_event.is_set():
                        break
                    print(line, end="")
                    match = re.search(r"Fra:(\d+), Mem:.*, Time:(.*), (.*)", line)
                    if match:
                        frame_done = int(match.group(1))
                        total_frames = end_frame - start_frame + 1
                        progress = int((frame_done / total_frames) * 100)
                        print(f"Progress for {blend_file}: {progress}%")

                        # Actualizar el progreso en la cola
                        item["progress"] = progress
                        self.notify_observers("progress_update", index) # Notificar a los observers sobre la actualización del progreso, usando un tipo de evento

                for line in iter(self.current_process.stderr.readline, ""):
                    if self.stop_event.is_set():
                        break
                    print(line, end="")

                self.current_process.wait()
                stdout, stderr = self.current_process.communicate()

                if self.current_process.returncode != 0:
                    if self.stop_event.is_set():
                        print("Rendering stopped by user during an error")
                        self.notify_observers("error", f"Rendering stopped by user during an error: {stderr}")
                        return
                    self.notify_observers("error", f"Error rendering {blend_file}\n{stderr}")
                    return

                self.current_process = None

            except Exception as e:
                self.notify_observers("error", f"An error occurred: {e}")
                return

        self.is_rendering = False
        self.notify_observers("render_complete", "All renders have been processed.")
        self.notify_observers()
    def add_waiting_files_to_queue(self):
        # Añade los archivos en espera a la cola principal y limpia la lista de espera
        while self.waiting_files:
            file_data = self.waiting_files.pop(0)
            self.loaded_files.append(file_data)
        self.notify_observers()
        
    def shutdown_pc(self):
        os_name = platform.system()
        if os_name == "Windows":
            os.system("shutdown /s /t 0")
        elif os_name == "Linux":
            os.system("sudo shutdown -h now")
        elif os_name == "Darwin":
            os.system("sudo shutdown -h now")
        else:
            self.notify_observers("error", "Sistema operativo no soportado para apagado automático.")

    def suspend_pc(self):
        os_name = platform.system()
        if os_name == "Windows":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif os_name == "Linux":
            os.system("systemctl suspend")
        elif os_name == "Darwin":
            os.system("pmset sleepnow")
        else:
            self.notify_observers("error", "Sistema operativo no soportado para suspensión automática.")

    def get_cameras_from_blend(self, blend_file):
        command = [
            "blender",
            "--background",
            blend_file,
            "--python-expr",
            (
                "import bpy;"
                "camera_names = [obj.name for obj in bpy.data.objects if obj.type == 'CAMERA'];"
                "print('CAMERAS:', camera_names)"
            ),
        ]
        print(f"Command: {' '.join(command)}")

        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            print("STDOUT:", stdout)
            print("STDERR:", stderr)

            cameras_line = None

            for line in stdout.splitlines():
                if "CAMERAS:" in line:
                    cameras_line = line

            if cameras_line:
                cameras = cameras_line.split(":")[1].strip()[1:-1].replace("'", "").split(", ")
                return cameras
            else:
                self.notify_observers("error", "No cameras found in the blend file.")
                return []
        except Exception as e:
            self.notify_observers("error", f"An error occurred while retrieving cameras: {e}")
            return []