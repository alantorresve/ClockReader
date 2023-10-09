from libraries.image_processor import *  # Functions for process the image
from os import environ
from sys import argv

DEFAULT_IMAGE_PATH = 'images\clock10.jpg'

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
            src = detect_line_and_draw_circle(circle, src, gray, filtered_lines)  # Pass filtered_lines as an argument
    else:
        print("Failed to detect circles in the image.")
        return
    
    lines_and_center = []

    lines_and_center = determine_closest_point_to_center(circle, filtered_lines, lines_and_center)

    hands = hands_angle(lines_and_center)
        
    exact_time = detect_exact_time(hands)
    
    
    
    # Showing results
    if environ.get('DOCKER_ENV'):
        return
    print("Exact Time:", exact_time)
    cv2.imshow("detected circles and lines", src)
    display_time(exact_time)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()