from src.logics.Detector import *
from src.gui.installer import create_gui_installer
from src.gui.splash_screen import create_splash_screen
from src.gui.main import create_main_gui
from src.utils.get_cameras import get_available_cameras
'''
#MODEL_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8.tar.gz" # low end GPU
MODEL_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/mask_rcnn_inception_resnet_v2_1024x1024_coco17_gpu-8.tar.gz" # high end GPU

IMAGE_PATH = "__mocks__/images/test_5.jpg"
VIDEO_PATH = "__mocks__/videos/test.mp4"
THRESHOLD = 0.5

classFile = "./src/assets/models/coco.names"
detector = Detector()
detector.readClasses(classFile)

detector.downloadModel(MODEL_URL)

detector.load_model()

detector.predictImage(IMAGE_PATH, THRESHOLD)
'''

# Check if the program is installed.
import os
settings_file_path = "src/assets/settings.yml"

if os.path.exists(settings_file_path):
    create_splash_screen()
    create_main_gui()
else:
    create_gui_installer()

#detector.predictVideo(VIDEO_PATH, THRESHOLD)