import cv2

def get_available_cameras():
    camera_names = []

    for i in range(10):
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            camera_name = f"Camera {i}"
            camera_names.append(camera_name)
            #ret, frame = camera.read()
            #cv2.imshow(f'Camera {i}', frame)
            camera.release()
            
        else:
            print("")
    return camera_names