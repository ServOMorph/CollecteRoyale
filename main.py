import json
import tkinter as tk
from tkinter import messagebox
import subprocess
import importlib
from network_manager import fast_connect, connect_normal

def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

def launch_script(script_name):
    try:
        subprocess.Popen(["python", script_name])
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lancer {script_name}: {e}")

def execute_function():
    module_name = file_entry.get()
    function_name = func_entry.get()
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, function_name)
        func()
    except Exception as e:
        messagebox.showerror("Erreur", f"Problème lors de l'exécution : {e}")

def dev_mode_window():
    root = tk.Tk()
    root.title("Mode Développeur")
    
    tk.Button(root, text="Jeu Normal", command=lambda:connect_normal()).pack(pady=5)
    tk.Button(root, text="Fast Connect", command=lambda:fast_connect()).pack(pady=5)
    
    global file_entry, func_entry
    file_entry = tk.Entry(root, width=30)
    file_entry.pack(pady=5)
    file_entry.insert(0, "Nom du fichier (sans .py)")
    
    func_entry = tk.Entry(root, width=30)
    func_entry.pack(pady=5)
    func_entry.insert(0, "Nom de la fonction")
    
    tk.Button(root, text="Lancer la fonction", command=execute_function).pack(pady=5)
    tk.Button(root, text="Quitter", command=root.quit).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    config = load_config()
    if config.get("mode_dev", False):
        dev_mode_window()
    else:
        connect()
