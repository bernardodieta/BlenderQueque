import os
import subprocess
import platform
import re
from threading import Thread, Event
import json
import datetime
import smtplib
from email.mime.text import MIMEText

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
        self.use_custom_alerts = False

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
            "output_format": "",
            "render_engine": "CYCLES",
            "file_prefix": "",
            "progress": 0,
            "render_threads": "Auto",
            "output_file_name": "",
        }
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
            file_data["progress"] = 0
            self.queue.append(file_data)
            self.notify_observers()

    def remove_from_queue(self, index):
        if index < len(self.queue):
            file_data = self.queue.pop(index)
            self.loaded_files.append(file_data)
            self.notify_observers()

    def update_file_settings(self, index, settings):
        if index < len(self.loaded_files):
            self.loaded_files[index].update(settings)
            self.notify_observers()

    def start_render(self, selected_queue, progress_bar):  # <--- Recibe progress_bar
        print("Model start_render called")
        self.is_rendering = True
        self.stop_event.clear()
        render_thread = Thread(target=self.process_queue, args=(selected_queue, progress_bar))  # <--- Pasa progress_bar
        render_thread.start()

    def stop_render(self):
        print("Model stop_render called")
        if self.is_rendering:
            self.is_rendering = False
            self.stop_event.set()
            if self.current_process:
                print("Terminating current Blender process")
                self.current_process.terminate()

    def process_queue(self, queue_to_render, progress_bar):
        print("process_queue started")
        total_frames_to_render = sum((int(item["end_frame"]) - int(item["start_frame"]) + 1) for item in queue_to_render)
        total_frames_rendered = 0

        # Inicializar variables fuera del bucle
        blend_file = None
        output_path = None
        resolution = None
        format_type = None
        camera = None
        start_frame = None
        end_frame = None
        file_prefix = None
        render_engine = None
        render_threads = None
        output_file_name = None

        for index, item in enumerate(queue_to_render):
            if self.stop_event.is_set():
                print("Rendering stopped by user")
                break

            print(f"Processing item: {item}")

            # Asignar valores a las variables solo si no se ha detenido el renderizado
            blend_file = item["file"]
            output_path = item["output_path"]
            resolution = item["resolution"]
            format_type = item["format"]
            camera = item["selected_camera"]
            start_frame = int(item["start_frame"])
            end_frame = int(item["end_frame"])
            file_prefix = item.get("file_prefix", "")
            render_engine = item.get("render_engine", "CYCLES")
            render_threads = item.get("render_threads", "Auto")
            output_file_name = item.get("output_file_name", "")

            output_dir = output_path.replace("\\", "/")
            output_file = f"{output_dir}/{file_prefix}{index:04}.{format_type.lower()}"
            
            if output_file_name:
                base_name, _ = os.path.splitext(output_file_name)
                output_file = f"{output_dir}/{base_name}"
            else:
                # Si no, usar el prefijo
                output_file = f"{output_dir}/{file_prefix}"

            command = [
                "blender",
                "--background",
                blend_file,
                "--python",
                "script_blender.py",
                "--",
                blend_file,
                output_file,  # Ahora output_file es la ruta base sin el número de frame NI la extensión
                camera,
                render_engine,
                str(start_frame),
                str(end_frame),
                render_threads,
                format_type,
            ]
            print(f"Running command: {' '.join(command)}")

            try:
                self.current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, encoding="utf-8")

                for line in iter(self.current_process.stdout.readline, ""):
                    if self.stop_event.is_set():
                        break
                    print(line, end="")
                    match = re.search(r"Fra:(\d+), Mem:.*, Time:(.*), (.*)", line)
                    if match:
                        frame_done = int(match.group(1))
                        frames_in_current_item = int(item["end_frame"]) - int(item["start_frame"]) + 1
                        progress_current_item = int((frame_done / frames_in_current_item) * 100)

                        item["progress"] = progress_current_item

                        # Calcular progreso global
                        total_frames_rendered_temp = total_frames_rendered + frame_done
                        global_progress = int((total_frames_rendered_temp / total_frames_to_render) * 100)

                        # Actualizar barra de progreso
                        progress_bar["value"] = global_progress

                        self.notify_observers("progress_update", index)

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
                self.notify_observers("render_complete_item", f"Rendering {blend_file} has been completed")

                # Actualizar el conteo de frames renderizados después de completar cada item
                total_frames_rendered += int(item["end_frame"]) - int(item["start_frame"]) + 1

            except FileNotFoundError:
                self.notify_observers(
                    "error",
                    f"Blender executable not found. Please make sure Blender is installed and accessible in your system path."
                )
            except subprocess.CalledProcessError as e:
                if self.stop_event.is_set():
                    print("Rendering stopped by user during an error")
                    self.notify_observers("error", f"Rendering stopped by user during an error: {e.stderr}")
                    return
                self.notify_observers("error", f"Error rendering {blend_file}:\n{e.stderr}")
            except Exception as e:
                self.notify_observers("error", f"An unexpected error occurred: {e}")
                return

        self.is_rendering = False
        self.notify_observers("render_complete", "All renders have been processed.")

        if self.shutdown_after_render:
            self.shutdown_pc()
        if self.suspend_after_render:
            self.suspend_pc()

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

    def to_dict(self):
        return {
            "loaded_files": self.loaded_files,
            "queue": self.queue,
            "shutdown_after_render": self.shutdown_after_render,
            "suspend_after_render": self.suspend_after_render,
            "use_custom_alerts": self.use_custom_alerts,
        }

    @classmethod
    def from_dict(cls, data):
        model = cls()
        model.loaded_files = data.get("loaded_files", [])
        model.queue = data.get("queue", [])
        model.shutdown_after_render = data.get("shutdown_after_render", False)
        model.suspend_after_render = data.get("suspend_after_render", False)
        model.use_custom_alerts = data.get("use_custom_alerts", False)
        model.notify_observers()
        return model

    def sort_queue(self, sort_by):
        if sort_by == "File Name":
            self.queue.sort(key=lambda item: os.path.basename(item["file"]))
        elif sort_by == "Start Frame":
            self.queue.sort(key=lambda item: item["start_frame"])
        elif sort_by == "End Frame":
            self.queue.sort(key=lambda item: item["end_frame"])
        elif sort_by == "Output Path":
            self.queue.sort(key=lambda item: item["output_path"])
        elif sort_by == "Camera":
            self.queue.sort(key=lambda item: item["selected_camera"])
        elif sort_by == "Format":
            self.queue.sort(key=lambda item: item["format"])
        elif sort_by == "Resolution":
            self.queue.sort(key=lambda item: item["resolution"])
        self.notify_observers()

    def filter_loaded_files(self, filter_text):
        if not filter_text:
            return self.loaded_files
        filter_text = filter_text.lower()
        return [
            file
            for file in self.loaded_files
            if filter_text in os.path.basename(file["file"]).lower()
        ]

    def send_alerts(self):
        print("Sending alerts...")

        if True:
            sender_email = "your_email@example.com"
            sender_password = "your_password"
            receiver_email = "receiver_email@example.com"

            message = MIMEText("The rendering is done!")
            message["Subject"] = "Render Complete"
            message["From"] = sender_email
            message["To"] = receiver_email

            try:
                with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(message)
                    print("Alerta de correo enviada correctamente")
            except Exception as e:
                print(f"Error sending email alert: {e}")