############################################
# Design based on nishantprj splash screen #
############################################
from src.logics.Detector import *
from tkinter import *
from tkinter import font
from PIL import ImageTk, Image
import time
import os
import yaml
import threading
from pathlib import Path

def create_splash_screen():
    global loader_running
    global w
    global label2
    global image_a
    global image_b
    global animation_labels
    w = Tk()
    #Using piece of code from old splash screen
    width_of_window = 427
    height_of_window = 250
    screen_width = w.winfo_screenwidth()
    screen_height = w.winfo_screenheight()
    x_coordinate = (screen_width/2)-(width_of_window/2)
    y_coordinate = (screen_height/2)-(height_of_window/2)
    w.geometry("%dx%d+%d+%d" %(width_of_window, height_of_window, x_coordinate, y_coordinate))
    # w.configure(bg='#ED1B76')
    w.overrideredirect(1) # for hiding titlebar

    Frame(w, width=427, height=250, bg='#272727').place(x=0,y=0)
    label1 = Label(w, text='FSD - Research Project', fg='white', bg='#272727') # decorate it 
    label1.configure(font=("Game Of Squids", 24, "bold"))   # You need to install this font in your PC or try another one
    label1.place(x=30,y=90)

    label2=Label(w, text='Loading...', fg='white', bg='#272727') #decorate it 
    label2.configure(font=("Calibri", 11))
    label2.place(x=10,y=215)

    loader_running = True
    loader_thread = threading.Thread(target=loader)
    loader_thread.start()

    check_loader_status()

    w.mainloop()

    loader_thread.join()
    
def check_loader_status():
    if loader_running:
        w.after(100, check_loader_status)
    else:
        print("finished.")
        w.destroy()

def loader():
    global loader_running
    global w
    global label2

    detector = Detector()

    label2.configure(text="Loading... loading config...")
    dir = 'src/assets'
    filename = 'settings.yml'
    filepath = os.path.join(dir, filename)

    with open(filepath, 'r') as yaml_file:
        loaded_data = yaml.safe_load(yaml_file)

    config = loaded_data.get('config', {})
    lang = config.get('lang', None)
    gpu_type = config.get('gpu_type', None)

    if gpu_type == 1:
        MODEL_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8.tar.gz"
    else:
        MODEL_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/mask_rcnn_inception_resnet_v2_1024x1024_coco17_gpu-8.tar.gz"

    if lang == "Spanish":
        dir = 'src/assets/locale'
        filename = 'es.yml'
        filepath = os.path.join(dir, filename)

        with open(filepath, 'r') as yaml_file:
            locale = yaml.safe_load(yaml_file)
    if lang == "English":
        dir = 'src/assets/locale'
        filename = 'en.yml'
        filepath = os.path.join(dir, filename)

        with open(filepath, 'r') as yaml_file:
            locale = yaml.safe_load(yaml_file)

    label2.configure(text=locale.get('download_model', None))
    detector.downloadModel(MODEL_URL)

    #current_dir = Path(__file__).resolve().parent.parent
    #classFile = os.path.join(current_dir, "assets", "models", "coco.names")
    #label2.configure(text=locale.get('loading_coco', None))
    #detector.readClasses(classFile)

    #label2.configure(text=locale.get('load_model', None))
    #detector.load_model()
    

    loader_running = False