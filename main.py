import cv2
import numpy as np

def resize_image(src, width):
    # Calculate the aspect ratio and resize the image
    height = int(src.shape[0] * (width / src.shape[1]))
    resized_image = cv2.resize(src, (width, height))
    return resized_image

def main():
    filename = "clock12.png"

    # Loads an image
    src = cv2.imread(filename, cv2.IMREAD_COLOR)

    # Check if the image is loaded successfully
    if src is None:
        print("Error opening image")
        print(f"Program Arguments: [image_name -- default {filename}]")
        return

    # Define the desired standard size here
    STANDARD_WIDTH = 600
    src = resize_image(src, STANDARD_WIDTH)

    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1,
                               minDist=gray.shape[0] / 1,
                               param1=100, param2=30, minRadius=200, maxRadius=500)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            center = (circle[0], circle[1])
            radius = circle[2]
            # Draw circle center
            cv2.circle(src, center, 1, (0, 100, 100), 3)
            # Draw circle outline
            cv2.circle(src, center, radius, (255, 0, 255), 3)

            # Detect lines using Hough Line Transform
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=5)

            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if abs(y1 - center[1]) < 20 or abs(y2 - center[1]) < 20:
                        cv2.line(src, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow("detected circles and lines", src)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
