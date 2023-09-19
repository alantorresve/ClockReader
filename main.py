from libraries.image_processor import * # Functions for process the image
from os import environ
import pdb

def main():
    filename = "/app/images/clock.jpeg"

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

    # Showing results
    print('salio todo bien!')
    if environ.get('DOCKER_ENV'):
        return
    cv2.imshow("detected circles and lines", src)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
