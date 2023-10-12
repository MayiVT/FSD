from pathlib import Path

import tkinter as tk
import customtkinter as ctk
import yaml
import os

def create_gui_installer():

    # System settings
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # App Settings
    app = ctk.CTk()
    app.geometry("500x300")
    app.title("FSD - Research Project - Installer")

    # Functions
    def button_callback():
        lang = combobox_1.get()
        gpu_type = combobox_2.get()
        if(lang == "Language" or gpu_type == "GPU Type"):
            tk.messagebox.showerror(title="Installer", message="Please fill all the required options.")
        else:
            if gpu_type == "High End":
                gpu_type = 0
            else:
                gpu_type = 1
            data = {
                'config': {
                    'lang': lang,
                    'gpu_type': gpu_type
                }
            }
            dir = 'src/assets'
            filename = 'settings.yml'
            filepath = os.path.join(dir, filename)

            if not os.path.exists(dir):
                os.makedirs(dir)

            with open(filepath, 'w') as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)

            print(f"Data has been written to {filepath}")
            if(lang == "Spanish"):
                tk.messagebox.showinfo(title="Instalador.", message="El programa se ha instalado con éxito.")
            else:
                tk.messagebox.showinfo(title="Installer.", message="The program has been successfully installed.")
            app.destroy()
            


    # Options
    lang_options = [
        'English',
        'Spanish'
    ]

    gpu_options = [
        'High End',
        'Low End'
    ]

    # UI Elements
    frame_1 = ctk.CTkFrame(master=app)
    frame_1.pack(pady=20, padx=60, fill="both", expand=True)

    label_1 = ctk.CTkLabel(master=frame_1, justify=ctk.LEFT, text="FSD Installer", font=("Inter", 15))
    label_1.pack(pady=10, padx=10)

    combobox_1 = ctk.CTkComboBox(frame_1, values=lang_options)
    combobox_1.pack(pady=10, padx=10)
    combobox_1.set("Language")

    combobox_2 = ctk.CTkComboBox(frame_1, values=gpu_options)
    combobox_2.pack(pady=10, padx=10)
    combobox_2.set("GPU Type")

    button_1 = ctk.CTkButton(master=frame_1, command=button_callback, text="Install")
    button_1.pack(pady=10, padx=10)

    # Run app
    app.mainloop()
