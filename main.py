from libraries.image_processor import * # Functions for process the image
from os import environ
from sys import argv
import pdb

DEFAULT_IMAGE_PATH = "./images/clock.jpeg"

def image_path():
    if len(argv) > 1:
        return argv[1]
    else:
        return DEFAULT_IMAGE_PATH


def main():
    filename = image_path()
    # Loads an image
    src = load_image(filename)

    # Check if the image is loaded successfully
    if src is None:
        print("Error opening image")
        print(f"Program Arguments: [image_name -- default {filename}]")
        return

    # Define the desired standard size here
    src = resize_image(src)
    gray = to_gray(src)
    circles = process_circles(gray)

    # Processing Image
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            src = detect_line(circle, src, gray)

   # Detect clock hands
    filtered_lines = []  # Initialize an empty list to store filtered lines

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            src = detect_line(circle, src, gray)

   # After detecting clock hands
    clock_hands = detect_clock_hands(filtered_lines)

    # Calculate the angles for the clock hands
    hour_hand_angle = clock_hands['hour']['angle']
    minutes_hand_angle = clock_hands['minutes']['angle']
    seconds_hand_angle = clock_hands['seconds']['angle']

    # Calculate the exact time
    exact_time = detect_exact_time(clock_hands)
    print("Exact Time:", exact_time)

    # Showing results
    print('salio todo bien!')
    if environ.get('DOCKER_ENV'):
        return
    cv2.imshow("detected circles and lines", src)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
