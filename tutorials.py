import cv2
import matplotlib.pyplot as plt
import numpy as np


def tutorial_one():
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_GRAYSCALE)
    cv2.imshow('img' ,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def tutorial_two():
    cap = cv2.VideoCapture(-1)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out.write(frame)
        cv2.imshow('frame', frame)
        cv2.imshow('gray', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def tutorial_three():
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_COLOR)

    cv2.line(img, (0, 0), (30, 150), (0, 0, 0), 5)
    cv2.rectangle(img, (40,0), (60, 20), (0, 255, 0), 5)
    cv2.circle(img, (60, 60), 30, (0, 0, 255), -1)

    pts = np.array([[10,5], [40,21], [30,90]], np.int32)
    cv2.polylines(img, [pts], True, (255, 255, 0), 3)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'OpenCV', (0, 100), font, 1, (200, 120, 30), 2, cv2.LINE_AA)

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def tutorial_four():
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_COLOR)

    px = img[55, 55]
    print(px)

    img[55, 55] = [255, 255, 255]
    print(img[55, 55])

    roi = img[10: 30][10: 60]
    print(roi)

    img[10: 30][10: 60] = (0, 0, 0)
    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    tutorial_four()
