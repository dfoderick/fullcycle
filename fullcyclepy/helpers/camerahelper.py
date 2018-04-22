'''camera functions'''
import time
try:
    import picamera
except BaseException:
    try:
        import cv2
    except BaseException:
        pass

def take_picture(image_name):
    try:
        with picamera.PiCamera() as camera:
            #todo: make configurable
            camera.resolution = (640, 480)
            camera.start_preview()
            # Camera warm-up time
            time.sleep(2)
            camera.capture(image_name)
            return image_name
    except BaseException:
        #the problem with cv2 is that is appears to not work on rpi with python3
        camera = cv2.VideoCapture(0)
        for _ in range(30):
            camera.read()
        _, frame = camera.read()
        cv2.imwrite(image_name, frame)
        camera.release()
        return image_name
