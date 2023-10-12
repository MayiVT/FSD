import customtkinter
import os
import yaml
import tkinter as tk
import cv2

from PIL import Image
from pathlib import Path
from src.logics.Detector import *
from src.utils.get_cameras import get_available_cameras
from src.utils.messageBox import showMessage
import threading
import requests

def create_main_gui():
    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

    '''
    0 = not sending data
    1 = sending data
    '''
    global detector
    global MODEL_LOADED
    global THRESHOLD
    global API_BUTTON
    global CAMERA_SEL
    MODEL_LOADED = 0
    detector = 0
    API_BUTTON = 0
    API_PORT = 27424
    API_IP = "127.0.0.1"

    predicting_thread = None
    global video_thread
    video_thread = None
    global is_predicting
    is_predicting = False
    
    ## Config Load
    dir = 'src/assets'
    filename = 'settings.yml'
    filepath = os.path.join(dir, filename)

    with open(filepath, 'r') as yaml_file:
        loaded_data = yaml.safe_load(yaml_file)
    global configuration
    configuration = loaded_data.get('config', {})
    lang = configuration.get('lang', None)
    gpu_type = configuration.get('gpu_type', None)
    if gpu_type == 1:
        gpu_type = "Low End"
    else:
        gpu_type = "High End"


    ## Load lang ##
    if lang == "Spanish":
        print(":D")
        dir = 'src/assets/locale'
        filename = 'es.yml'
        filepath = os.path.join(dir, filename)

        with open(filepath, 'r') as yaml_file:
            l_data = yaml.safe_load(yaml_file)
    if lang == "English":
        dir = 'src/assets/locale'
        filename = 'en.yml'
        filepath = os.path.join(dir, filename)

        with open(filepath, 'r') as yaml_file:
            l_data = yaml.safe_load(yaml_file)
    locale = l_data.get('main', {})

    ## Functions ##
    def start_stop_api_button_callback():
        global API_BUTTON
        if API_BUTTON == 0:
            API_BUTTON = 1
            button_start_stop_api.configure(border_color="green", text=locale.get("api_started", None))
            entry_ip.configure(state="disabled", fg_color="#565b5e")
            entry_port.configure(state="disabled", fg_color="#565b5e")

        elif API_BUTTON == 1:
            API_BUTTON = 0
            button_start_stop_api.configure(border_color="red", text=locale.get("api_stopped", None))
            entry_ip.configure(state="normal", fg_color="#d6d6d6")
            entry_port.configure(state="normal", fg_color="#d6d6d6")

    def api_status():
        status = switch_api.get()

        if status:
            entry_ip.configure(state="normal", fg_color="#d6d6d6")
            entry_port.configure(state="normal", fg_color="#d6d6d6")
            button_start_stop_api.configure(state="normal", border_width=1.5)
        else:
            if API_BUTTON:
                start_stop_api_button_callback()
            entry_ip.configure(state="disabled", fg_color="#565b5e")
            entry_port.configure(state="disabled", fg_color="#565b5e")
            button_start_stop_api.configure(state="disabled", border_width=0)

    def save_config():
        new_gpu_type = config_cb_gpu.get()
        new_lang = config_cb_lang.get()
        dir = 'src/assets'
        filename = 'settings.yml'
        filepath = os.path.join(dir, filename)
        with open(filepath, 'w') as yaml_file:
            if new_gpu_type == "High End":
                new_gpu_type = 0
            else: 
                new_gpu_type = 1

            data = {
                'config': {
                    'lang': new_lang,
                    'gpu_type': new_gpu_type
                }
            }
            yaml.dump(data, yaml_file, default_flow_style=False)

            if new_lang == "Spanish":
                dir = 'src/assets/locale'
                filename = 'es.yml'
                filepath = os.path.join(dir, filename)

                with open(filepath, 'r') as yaml_file:
                    loaded_data = yaml.safe_load(yaml_file)
            if new_lang == "English":
                dir = 'src/assets/locale'
                filename = 'en.yml'
                filepath = os.path.join(dir, filename)

                with open(filepath, 'r') as yaml_file:
                    loaded_data = yaml.safe_load(yaml_file)

            nlocale = loaded_data.get('main', {})

            print(f"Data has been written to {filepath}")
            tk.messagebox.showinfo(title="FSD Admin Panel.", message=nlocale.get('config_saved', None))

    def predicting_func():
        global predicting
        global image_button
        global API_BUTTON
        global video_thread
        global is_predicting


        while predicting:
            print("[IMAGE/API] Predicting...")
            dir = 'src/assets/gui/results'
            filename = 'is_stopped.yml'
            filepath = os.path.join(dir, filename)

            with open(filepath, 'r') as yaml_file:
                loaded_data = yaml.safe_load(yaml_file)

            config = loaded_data.get('config', {})
            stopped = config.get('stopped', None)

            dir_api = 'src/assets/gui/results'
            filename_api = 'is_stopped.yml'
            filepath_api = os.path.join(dir_api, filename_api)

            with open(filepath_api, 'r') as yaml_file:
                loaded_data_api = yaml.safe_load(yaml_file)

            config = loaded_data_api.get('config', {})
            api_data = config.get('data', None)
            if stopped == 1:
                print("[IMAGE/API] Stopping predicting...")
                break
            try:
                my_image = customtkinter.CTkImage(Image.open("src/assets/gui/results/result.jpg"), size=(1000, 900))
                image_button.configure(image=my_image)
            except:
                print("Error on getting the image...")
                pass

            if API_BUTTON:
                url = entry_ip.get() + ":" + entry_port.get()
                response = requests.post(url, json=api_data)

                if response.status_code == 200:
                    print(response.json())
                else:
                    print(response.status_code())
            time.sleep(0.5)

    def predictVideo():
        pred, api_data = detector.predictVideo(CAMERA_SEL, THRESHOLD)


    def start_predicting_func():
        global predicting
        global camera_selector
        global CAMERA_SEL
        global THRESHOLD
        global predicting_thread
        global image_button
        global video_thread
        global is_predicting

        print(pred_var.get())  
        if pred_var.get() == "on":
            data = {
                'config': {
                    'stopped': 0,
                }
            }
            dir = 'src/assets/gui/results'
            filename = 'is_stopped.yml'
            filepath = os.path.join(dir, filename)

            with open(filepath, 'w') as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)


            THRESHOLD = 0.5
            predicting = True
            CAMERA_SEL = camera_selector.get()
                        
            my_image = customtkinter.CTkImage(Image.open("src/assets/gui/results/result.jpg"), size=(1000, 900))
            image_button = customtkinter.CTkButton(master=tabview_1.tab(locale.get("view", None)), text="", image=my_image, state="disabled", fg_color="transparent")
            image_button.pack()

            predicting_thread = threading.Thread(target=predicting_func)
            predicting_thread.start()

            video_thread = threading.Thread(target=predictVideo)
            video_thread.start() 

        else:
            print("Started stopping prediction...")
            image_button.destroy()
            data = {
                'config': {
                    'stopped': 1,
                }
            }
            print("[main] data: " + str(data))
            dir = 'src/assets/gui/results'
            filename = 'is_stopped.yml'
            filepath = os.path.join(dir, filename)
            print("[main] filepath: " + str(filepath))
            with open(filepath, 'w') as yaml_file:
                yaml.dump(data, yaml_file, default_flow_style=False)
            print("[main] Stopped prediction...")

            print("[main] Stopped stopping prediction threads...")
            video_thread.join()
            print("[main] Stopped stopping prediction threads 1...")
            predicting = False
            predicting_thread.join()
            print("[main] Stopped stopping prediction threads 2...")
            

    def start_model():
        global CAMERA_SEL
        global detector
        global MODEL_LOADED
        if MODEL_LOADED:
            showMessage(locale.get('error_model_loaded', None), type="error", timeout=4000)
        else:
            MODEL_LOADED = 1
            showMessage(locale.get('start_model_msgbox', None), type="warning", timeout=4000)
            current_dir = Path(__file__).resolve().parent.parent
            classFile = os.path.join(current_dir, "assets", "models", "coco.names")
        
            dir_settings = 'src/assets'
            filename_settings = 'settings.yml'
            filepath_settings = os.path.join(dir_settings, filename_settings)

            with open(filepath_settings, 'r') as yaml_file:
                loaded_data_gpu = yaml.safe_load(yaml_file)

            config_gpu = loaded_data_gpu.get('config', {})
            gpu_type = config_gpu.get('gpu_type', None)
        
            if gpu_type == 1:
                MODEL_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8.tar.gz"
            else:
                MODEL_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/mask_rcnn_inception_resnet_v2_1024x1024_coco17_gpu-8.tar.gz"
        


            detector = Detector()

            detector.downloadModel(MODEL_URL)
            detector.readClasses(classFile)

            detector.load_model()
            showMessage(locale.get('model_started_msgbox', None), type="warning", timeout=4000)
            
            start_model_btn.configure(state="disabled")

            cameras_available = get_available_cameras()
            #print(cameras_available)

            global camera_selector
            camera_selector = customtkinter.CTkComboBox(master=tabview_1.tab(locale.get("home", None)), values=cameras_available)
            camera_selector.pack(pady=20)
            CAMERA_SEL = cameras_available[0]

            global pred_var
            pred_var = customtkinter.StringVar(value="off")
            start_predicting = customtkinter.CTkSwitch(master=tabview_1.tab(locale.get("home", None)), text=locale.get('start_predicting_btn', None), command=start_predicting_func, variable=pred_var, onvalue="on", offvalue="off")
            start_predicting.pack(pady=10)

            switch_api.configure(state="normal")
    ## End of functions ##


    ## Load app
    app = customtkinter.CTk()
    app.geometry("1680x780")
    app.title("FSD - Research Project Admin Panel")

    #start_model()
    #get_predicted_img()
    #print(get_available_cameras())
    # save this into an array to then do a for loop and generate all the things uk

    frame_1 = customtkinter.CTkFrame(master=app)
    frame_1.pack(pady=20, padx=60, fill="both", expand=True)

    label_1 = customtkinter.CTkLabel(master=frame_1, justify=customtkinter.LEFT, text=locale.get("title", None), font=("Inter", 25))
    label_1.pack(pady=20, padx=10)

    tabview_1 = customtkinter.CTkTabview(master=frame_1, width=1300)
    tabview_1.pack(pady=10, padx=10)
    tabview_1.add(locale.get("home", None))
    tabview_1.add(locale.get("config", None))
    tabview_1.add(locale.get("view", None))
    tabview_1.add(locale.get("API", None))
    tabview_1.set(locale.get("home", None))

    ### HOME TAB ###
    start_model_btn = customtkinter.CTkButton(master=tabview_1.tab(locale.get("home", None)), text=locale.get("start_model"), command=start_model)
    start_model_btn.pack(pady=20)

    ### VIEW TAB ###
    #my_image = customtkinter.CTkImage(Image.open("src/assets/gui/results/result.jpg"), size=get_image_size())
    #image_button = customtkinter.CTkButton(master=tabview_1.tab(locale.get("view", None)), text="", image=my_image, state="disabled", fg_color="transparent")
    #image_button.pack()

    ### CONFIG TAB ###

    config_label_lang = customtkinter.CTkLabel(master=tabview_1.tab(locale.get("config", None)), justify=customtkinter.LEFT, text=locale.get("language", None))
    config_label_lang.pack(pady=10, padx=10)

    config_cb_lang = customtkinter.CTkComboBox(master=tabview_1.tab(locale.get("config", None)), values=["Spanish", "English"])
    config_cb_lang.pack(pady=3, padx=10)
    config_cb_lang.set(lang)

    config_label_gpu = customtkinter.CTkLabel(master=tabview_1.tab(locale.get("config", None)), justify=customtkinter.LEFT, text=locale.get("gpu_type", None))
    config_label_gpu.pack(pady=10, padx=10)

    config_cb_gpu = customtkinter.CTkComboBox(master=tabview_1.tab(locale.get("config", None)), values=["High End", "Low End"])
    config_cb_gpu.pack(pady=3, padx=10)
    config_cb_gpu.set(gpu_type)

    config_button_save = customtkinter.CTkButton(master=tabview_1.tab(locale.get("config", None)), text=locale.get("save", None), command=save_config)
    config_button_save.pack(pady=10, padx=10)


    #### API TAB ####

    switch_api = customtkinter.CTkSwitch(master=tabview_1.tab(locale.get("API", None)), text=locale.get("enable_api", None), command=api_status, state="disabled")
    switch_api.pack(pady=10, padx=10)

    label_ip = customtkinter.CTkLabel(master=tabview_1.tab(locale.get("API", None)), justify=customtkinter.LEFT, text=locale.get("ip", None))
    label_ip.pack(pady=10, padx=10)

    entry_ip = customtkinter.CTkEntry(master=tabview_1.tab(locale.get("API", None)), placeholder_text="127.0.0.1", state="disabled", text_color="#000")
    entry_ip.pack(pady=5, padx=10)

    label_port = customtkinter.CTkLabel(master=tabview_1.tab(locale.get("API", None)), justify=customtkinter.LEFT, text=locale.get("port", None))
    label_port.pack(pady=10, padx=10)

    entry_port = customtkinter.CTkEntry(master=tabview_1.tab(locale.get("API", None)), placeholder_text="27424", state="disabled", text_color="#000")
    entry_port.pack(pady=5, padx=10)

    button_start_stop_api = customtkinter.CTkButton(master=tabview_1.tab(locale.get("API", None)), text=locale.get("api_stopped", None), command=start_stop_api_button_callback, state="disabled", border_color="red", border_width=0)
    button_start_stop_api.pack(pady=10, padx=10)

    app.mainloop()