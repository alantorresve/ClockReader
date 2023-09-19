import cv2
import numpy as np

def resize_image(src, width = 600):
    # Calculate the aspect ratio and resize the image
    height = int(src.shape[0] * (width / src.shape[1]))
    resized_image = cv2.resize(src, (width, height))
    return resized_image


def load_image(filename):
    return cv2.imread(filename, cv2.IMREAD_COLOR)


def to_gray(image):
    return cv2.medianBlur(
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 5
    )


def process_circles(gray_image):
    return cv2.HoughCircles(gray_image, cv2.HOUGH_GRADIENT, dp=1,
                               minDist=gray_image.shape[0] / 1,
                               param1=100, param2=30, minRadius=200, maxRadius=500)


def detect_line(circle, source_image, gray_image):
    center = (circle[0], circle[1])
    radius = circle[2]
    # Draw circle center
    cv2.circle(source_image, center, 1, (0, 100, 100), 3)
    # Draw circle outline
    cv2.circle(source_image, center, radius, (255, 0, 255), 3)

    # Detect lines using Hough Line Transform
    edges = cv2.Canny(gray_image, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=5)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - center[1]) < 20 or abs(y2 - center[1]) < 20:
                cv2.line(source_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return source_image
