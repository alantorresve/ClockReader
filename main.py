from libraries.image_processor import *  # Functions for process the image
from os import environ
from sys import argv

DEFAULT_IMAGE_PATH = 'images\clock6.png'

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

    filtered_lines = []  # Initialize an empty list

    # Processing Image
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            src = detect_line(circle, src, gray, filtered_lines)  # Pass filtered_lines as an argument
    else:
        print("Failed to detect circles in the image.")
        return
    
    lines_and_center = []

    lines_and_center = determine_closest_point_to_center(circle, filtered_lines, lines_and_center)
    
    duplicate = draw_clock_hands_circles(src, lines_and_center)
    
    hands_angles = []

    hands = hands_angle(lines_and_center)
    

    #clock_hands = identify_clock_hands(hands_angles)
    
    exact_time = detect_exact_time(hands)
    
    print("Exact Time:", exact_time)

    # visual_debug_image = draw_detected_hands(src, clock_hands)
    
    
    # Showing results
    if environ.get('DOCKER_ENV'):
        return
    cv2.imshow("detected circles and lines", src)
    cv2.imshow("detected circles and lines", duplicate)
    # cv2.imshow("Debug Image with Detected Hands", visual_debug_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()