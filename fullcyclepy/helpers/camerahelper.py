'''camera functions'''
import time
#import datetime
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
            camera.start_preview()
            try:
                #todo: make configurable
                camera.resolution = (1280, 720)
                camera.brightness = 50
                camera.contrast = 50
                #camera.anotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Camera warm-up time
                time.sleep(2)
                camera.capture(image_name, resize=(320, 240), quality=10)
            finally:
                camera.stop_preview()
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
