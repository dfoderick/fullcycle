'''reads the camera'''
#image gets written in parent (startup directory!)

import cv2

CAM = cv2.VideoCapture(0)

cv2.namedWindow("test")

COUNTER = 0

while True:
    RET, FRAME = CAM.read()
    cv2.imshow("test", FRAME)
    if not RET:
        break
    k = cv2.waitKey(1)

    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        IMAGENAME = "fullcycle_{}.png".format(COUNTER)
        cv2.imwrite(IMAGENAME, FRAME)
        print("{} written!".format(IMAGENAME))
        COUNTER += 1

CAM.release()

cv2.destroyAllWindows()
