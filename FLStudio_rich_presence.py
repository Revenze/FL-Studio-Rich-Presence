import time
import psutil
import win32gui
from pypresence import Presence

DISCORD_CLIENT_ID = "605597262999191552"  # Tu Client ID de Discord

# Verifica si FL Studio está corriendo (por nombre de proceso)
def is_fl_studio_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "FL64" in proc.info['name']:
            return True
    return False

# Obtiene el título de la ventana de FL Studio
def get_fl_window_title():
    def callback(hwnd, titles):
        title = win32gui.GetWindowText(hwnd)
        if "FL Studio" in title and win32gui.IsWindowVisible(hwnd):
            titles.append(title)
    titles = []
    win32gui.EnumWindows(callback, titles)
    return titles[0] if titles else None

# Extrae el nombre del proyecto desde el título
def get_project_name_from_title(title):
    if title and ".flp" in title:
        return title.split(".flp")[0] + ".flp"
    return "Untitled Project"

def main():
    print("Esperando que FL Studio se abra...")
    timeout = 60
    waited = 0

    # Espera que FL Studio inicie
    while not is_fl_studio_running():
        time.sleep(5)
        waited += 5
        if waited >= timeout:
            print("FL Studio no se detectó en el tiempo esperado.")
            return

    print("FL Studio detectado. Conectando con Discord...")
    rpc = Presence(DISCORD_CLIENT_ID)
    rpc.connect()
    print("Conectado a Discord.")

    start_time = int(time.time())

    # Loop mientras esté corriendo FL Studio
    while is_fl_studio_running():
        title = get_fl_window_title()
        if title:
            try:
                project_name = get_project_name_from_title(title)
                rpc.update(
                    state="Working on project",
                    details=project_name,
                    large_image="flstudio20_mastericon",
                    large_text="FL Studio 2024",
                    start=start_time,
                )
            except Exception as e:
                print("Error actualizando Rich Presence:", e)
        else:
            print("No se encontró la ventana de FL Studio.")

        time.sleep(3)

    print("FL Studio cerrado. Cerrando Rich Presence.")
    rpc.clear()
    rpc.close()

if __name__ == "__main__":
    main()
