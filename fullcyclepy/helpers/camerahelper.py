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

def take_picture(image_name, size="small", quality=10, brightness=50, contrast=50):
    try:
        with picamera.PiCamera() as camera:
            camera.start_preview()
            try:
                camera.resolution = (1280, 1024)
                camera.brightness = brightness
                camera.contrast = contrast
                #camera.anotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Camera warm-up time
                time.sleep(2)
                resize = (320, 240)
                if size.startswith('m'):
                    resize = (640, 480)
                if size.startswith('l'):
                    resize = (1024, 768)
                if size.startswith('x'):
                    resize = (1280, 1024)

                camera.capture(image_name, resize=resize, quality=quality)
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
