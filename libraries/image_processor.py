import cv2
import numpy as np

def resize_image(src, width=600):
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

def detect_line(circle, source_image, gray_image, filtered_lines):
    center = (circle[0], circle[1])
    radius = circle[2]
    # Draw circle center
    cv2.circle(source_image, center, 1, (0, 100, 100), 3)
    # Draw circle outline
    cv2.circle(source_image, center, radius, (255, 0, 255), 3)

    # Detect lines using Hough Line Transform
    edges = cv2.Canny(gray_image, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=60, maxLineGap=5)

    line_angle_array = []  # Initialize an empty list to store all lines with angles

    if lines is not None:
        for line in lines:
            found = False
            x1, y1, x2, y2 = line[0]
            if abs(y1 - center[1]) < 20 or abs(y2 - center[1]) < 20:
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi  # Calculate the angle of the line
                line_with_angle = np.append(line[0], angle)  # Add the angle to the line
                line_angle_array.append(line_with_angle)  # Add the line to the list
            
            if len(filtered_lines) > 0:
                for existing_line in filtered_lines:  # Iterate over existing lines
                    if abs(angle - existing_line[-1]) < 10:  # Compare the angle (last element)
                        # If the angle is similar, compare and keep the longer line
                        length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                        length_ = np.sqrt(
                            (existing_line[2] - existing_line[0]) ** 2 +
                            (existing_line[3] - existing_line[1]) ** 2
                        )
                        if length_ > length:
                            # Update the existing line
                            existing_line[0], existing_line[1] = x1, y1
                            existing_line[2], existing_line[3] = x2, y2
                            existing_line[-1] = angle
                        found = True
                        break

            # If no similar line was found, add the current line as a new filtered line
            if not found:
                filtered_lines.append([x1, y1, x2, y2, angle])

    for line in filtered_lines:
        x1, y1, x2, y2, angle = line
        cv2.line(source_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # print(line_angle_array)
    # print(filtered_lines)
    return source_image


def detect_clock_hands(filtered_lines):
    # Sort the lines by length from longest to shortest
    sorted_lines = sorted(filtered_lines, key=lambda x: np.sqrt((x[2] - x[0])**2 + (x[3] - x[1])**2), reverse=True)

    clock_hands = {
        'hour': None,
        'minutes': None,
        'seconds': None
    }

    # Take the three longest lines (seconds, minutes, and hour)
    for i, line in enumerate(sorted_lines[:3]):
        if i == 0:
            clock_hands['seconds'] = {'x1': line[0], 'y1': line[1], 'x2': line[2], 'y2': line[3], 'angle': line[4]}
        elif i == 1:
            clock_hands['minutes'] = {'x1': line[0], 'y1': line[1], 'x2': line[2], 'y2': line[3], 'angle': line[4]}
        elif i == 2:
            clock_hands['hour'] = {'x1': line[0], 'y1': line[1], 'x2': line[2], 'y2': line[3], 'angle': line[4]}

    return clock_hands

def detect_exact_time(clock_hands):
    # Check if all three clock hands are available
    if all(clock_hands.values()):
        hour_hand = clock_hands['hour']
        minutes_hand = clock_hands['minutes']
        seconds_hand = clock_hands['seconds']

        # Calculate the angle between the hour and minute hands
        angle_hour_minutes = abs(hour_hand['angle'] - minutes_hand['angle'])

        # Calculate the angle for each hand
        angle_seconds = seconds_hand['angle']
        angle_minutes = minutes_hand['angle']
        angle_hour = hour_hand['angle']

        # Calculate the exact time
        hours = int(angle_hour / 30)  # Assuming 360 degrees for 12 hours
        minutes = int((angle_minutes / 6) % 60)  # Assuming 360 degrees for 60 minutes
        seconds = int((angle_seconds / 6) % 60)  # Assuming 360 degrees for 60 seconds

        # Format the time as "hh:mm:ss"
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return formatted_time

    else:
        return "Clock hands not detected"


