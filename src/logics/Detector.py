import cv2, time, os, tensorflow as tf
import numpy as np
import time
import yaml

from tensorflow.python.keras.utils.data_utils import get_file

np.random.seed(20)

class Detector:
    def __init__(self):
        pass

    def readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classesList = f.read().splitlines()

        # Colors list
        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList), 3))

        print(len(self.classesList), len(self.colorList))

    def downloadModel(self, modelURL):
        fileName = os.path.basename(modelURL)
        self.modelName = fileName[:fileName.index('.')]
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.cacheDir = os.path.join(current_dir, "..", "assets", "models", "pretrained_models")

        os.makedirs(self.cacheDir, exist_ok=True)

        get_file(fname=fileName,
                 origin=modelURL,
                 cache_dir=self.cacheDir,
                 cache_subdir="checkpoints",
                 extract=True)
        
    def load_model(self):
        print("Loading model: " + self.modelName)
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(os.path.join(self.cacheDir, "checkpoints", self.modelName, "saved_model"))
        print("Model loaded...")

    def createBoundingBoxes(self, image, threshold):
        inputTensor = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
        inputTensor = tf.convert_to_tensor(inputTensor, dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis, ...]
        
        detections = self.model(inputTensor)

        bboxs = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()

        imgHeigh, imgWidth, imgChannels = image.shape

        bboxIdx = tf.image.non_max_suppression(bboxs, classScores, max_output_size=50, iou_threshold=threshold, score_threshold=threshold)
        
        API_ARR = {
            "image_width": imgWidth,
            "image_height": imgHeigh,
            "detections": []
        }

        if len(bboxIdx) != 0:
            for i in bboxIdx:
                bbox = tuple(bboxs[i].tolist())
                
                classConfidence = round(100*classScores[i])
                classIndex = classIndexes[i]

                classLabelText = self.classesList[classIndex].upper()
                classColor = self.colorList[classIndex]

                displayText = '{}: {}%'.format(classLabelText, classConfidence)

                ymin, xmin, ymax, xmax = bbox
                xmin, xmax, ymin, ymax = (xmin * imgWidth, xmax * imgWidth, ymin * imgHeigh, ymax * imgHeigh)
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)
                
                detection = {
                    "name": classLabelText,
                    "confidence": classConfidence,
                    "coords": {
                        "xmin": xmin,
                        "xmax": xmax,
                        "ymin": ymin,
                        "ymax": ymax
                    }
                }

                API_ARR["detections"].append(detection)

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color=classColor, thickness=1)
                cv2.putText(image, displayText, (xmin, ymin - 10), cv2.FONT_HERSHEY_PLAIN, 1, classColor, 2)

                lineWidth = min(int((xmax - xmin) * 0.2), int((ymax - ymin) * 0.2))
                cv2.line(image, (xmin, ymin), (xmin + lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmin, ymin), (xmin, ymin + lineWidth), classColor, thickness=5)

                cv2.line(image, (xmax, ymin), (xmax - lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmax, ymin), (xmax, ymin + lineWidth), classColor, thickness=5)

                cv2.line(image, (xmin, ymax), (xmin + lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmin, ymax), (xmin, ymax - lineWidth), classColor, thickness=5)

                cv2.line(image, (xmax, ymax), (xmax - lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmax, ymax), (xmax, ymax - lineWidth), classColor, thickness=5)

        #print(API_ARR)

        return image, API_ARR


    def predictImage(self, imagePath, threshold=0.5):
#        image = cv2.imread(imagePath)
        imagePath = imagePath.split()
        cam = int(imagePath[-1])
        print(cam)
        cap = cv2.VideoCapture(cam)

        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            exit()

        
    
        bboxImg, api_data = self.createBoundingBoxes(frame, threshold)

        cv2.imwrite("src/assets/gui/results/result" + ".jpg", bboxImg)
        cap.release()
        #cv2.imshow("Result", bboxImg)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        return bboxImg, api_data

    def predictVideo(self, videoPath, threshold=0.5):

        videoPath = videoPath.split()
        cam = int(videoPath[-1])
        print(f"Started predictVideo: {cam}")
        cap = cv2.VideoCapture(cam)

        if(cap.isOpened() == False):
            print("Error opening file...")
            return
        
        (success, image) = cap.read()

        startTime = 0

        while success:
            dir = 'src/assets/gui/results'
            filename = 'is_stopped.yml'
            filepath = os.path.join(dir, filename)

            with open(filepath, 'r') as yaml_file:
                loaded_data = yaml.safe_load(yaml_file)

            config = loaded_data.get('config', {})
            stopped = config.get('stopped', None)
            print(f"Predicting {stopped}")
            stopped = config.get('stopped', None)
            if stopped == 1:
                print("stopped")
                cap.release()
                break
            currentTime = time.time()

            fps = 1/(currentTime - startTime)
            startTime = currentTime

            bboxImage, api_data = self.createBoundingBoxes(image, threshold)

            cv2.putText(bboxImage, "FPS: " + str(int(fps)), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
            #cv2.imshow("Result", bboxImage)

            #key = cv2.waitKey(1) & 0xFF
            #if key == ord("q"):
            #    break

            (success, image) = cap.read()
            cv2.imwrite("src/assets/gui/results/result" + ".jpg", bboxImage)
            print(api_data)

            # save api data
            api_ymldata = {
                'config': {
                    'data': api_data
                }
            }
            dir = 'src/assets/gui/results'
            filename = 'api_result.yml'
            filepath = os.path.join(dir, filename)

            if not os.path.exists(dir):
                os.makedirs(dir)

            with open(filepath, 'w') as yaml_file:
                yaml.dump(api_ymldata, yaml_file, default_flow_style=False)


            #time.sleep(0.5)

        cap.release()
