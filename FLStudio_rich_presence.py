import time
import psutil
import win32gui
import win32api
import os
import subprocess
from pypresence import Presence, exceptions

DISCORD_CLIENT_ID = "605597262999191552"  # Discord application client ID

# Get the title of the FL Studio window
def get_fl_window_title():
    def callback(hwnd, extra):
        title = win32gui.GetWindowText(hwnd)
        if title and win32gui.IsWindowVisible(hwnd):
            extra.append(title)

    titles = []
    win32gui.EnumWindows(callback, titles)

    # Check if the title contains "FL Studio"
    for t in titles:
        if "FL Studio" in t:
            return t
    return None

# Get the project name from the window title
def get_project_name_from_title(title):
    if title and ".flp" in title:
        return title.split(".flp")[0] + ".flp"
    return "Unknown Project"

# Check if FL Studio is running
def is_fl_studio_running():
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        if "FL64" in proc.info['name']:
            return True
    return False

# Get the version of FL Studio
def get_fl_studio_version():
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            if "FL64" in proc.info['name']:
                exe_path = proc.info['exe']
                if exe_path and os.path.exists(exe_path):
                    info = win32api.GetFileVersionInfo(exe_path, "\\")
                    ms = info['FileVersionMS']
                    ls = info['FileVersionLS']
                    version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
                    version_parts = version.split('.')
                    version = '.'.join(version_parts[:3])
                    return version
        except Exception as e:
            print("Error obteniendo la versión desde el ejecutable:", e)
    return "Unknown Version"

# Get the processor name
def get_processor_name():
    try:
        output = subprocess.check_output('wmic cpu get Name', shell=True).decode(errors='ignore')
        lines = output.strip().split('\n')
        if len(lines) >= 2:
            name = lines[1].strip()
            name = name.replace("AMD ", "").replace("Intel(R) ", "").replace("CPU ", "")
            name = name.split(" @")[0].split(" with")[0]
            return name
        return None
    except Exception as e:
        print("Error obteniendo el nombre del procesador:", e)
        return None

def main():
    print("FL Studio Discord Rich Presence started...")

    processor_name = get_processor_name()

    timeout = 60
    waited = 0

    print("Esperando que FL Studio inicie.")
    # Wait for FL Studio to start
    while not is_fl_studio_running():
        time.sleep(5)
        waited += 5
        if waited >= timeout:
            print("Tiempo de espera finalizado. FL Studio no se inició.")
            return

    fl_studio_version = get_fl_studio_version()

    print("FL Studio detectado. Conectando a Discord.")
    rpc = Presence(DISCORD_CLIENT_ID)

    start_time = time.time()
    while True:
        try:
            rpc.connect()
            print("Conectado a Discord")
            break
        except exceptions.DiscordNotFound:
            print("Discord no está en ejecución.")
            time.sleep(3)

        if time.time() - start_time >= 12:
            print("No se pudo conectar a Discord, cerrando Rich Presence..")
            return

    start_time = int(time.time())

    # Keep updating while FL Studio is running
    while is_fl_studio_running():
        title = get_fl_window_title()

        if title:
            try:
                project_name = get_project_name_from_title(title)

                if processor_name:
                    large_image_description = f"FL Studio {fl_studio_version} | {processor_name}"
                else:
                    large_image_description = f"FL Studio {fl_studio_version}"

                rpc.update(
                    state="Working on project",
                    details=f"{project_name}",
                    large_image="flstudio20_mastericon",
                    large_text=large_image_description,
                    start=start_time,
                )
            except Exception as e:
                print("Error actualizando Discord:", e)
        else:
            print("No se pudo obtener el título de la ventana de FL Studio.")

        time.sleep(3)  # Update every 3 seconds


    print("FL Studio cerrado. Cerrando Rich Presence.")
    try:
         rpc.clear()
         rpc.close()
         print("Rich Presence cerrado correctamente.")
    except Exception as e:
         print(f"Error al cerrar la conexión con Discord: {e}")

if __name__ == "__main__":
    main()
