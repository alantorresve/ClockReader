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

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = (np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi - 90) % 360  # Adjusted angle calculation
            if abs(y1 - center[1]) < 20 or abs(y2 - center[1]) < 20:
                line_with_angle = np.append(line[0], angle)  # Add the angle to the line
                
                # Existing line filtering logic
                found = False
                if len(filtered_lines) > 0:
                    for existing_line in filtered_lines:
                        if abs(angle - existing_line[-1]) < 10:
                            length = np.sqrt((x2 - x1) * 2 + (y2 - y1) * 2)
                            length_ = np.sqrt(
                                (existing_line[2] - existing_line[0]) ** 2 +
                                (existing_line[3] - existing_line[1]) ** 2
                            )
                            if length_ > length:
                                existing_line[0], existing_line[1] = x1, y1
                                existing_line[2], existing_line[3] = x2, y2
                                existing_line[-1] = angle
                            found = True
                            break
                if not found:
                    filtered_lines.append([x1, y1, x2, y2, angle])

    for line in filtered_lines:
        x1, y1, x2, y2, angle = line
        cv2.line(source_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return source_image

# def detect_clock_hands(filtered_lines):
#     # Sort the lines by length from longest to shortest
#     sorted_lines = sorted(filtered_lines, key=lambda x: np.sqrt((x[2] - x[0])*2 + (x[3] - x[1])*2), reverse=True)

#     clock_hands = {
#         'hour': None,
#         'minutes': None,
#         'seconds': None
#     }

#     # Take the three longest lines (seconds, minutes, and hour)
#     for i, line in enumerate(sorted_lines[:3]):
#         x1, y1, x2, y2, angle = line
#         if i == 0:
#             clock_hands['seconds'] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'angle': angle}
#         elif i == 1:
#             clock_hands['minutes'] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'angle': angle}
#         elif i == 2:
#             clock_hands['hour'] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'angle': angle}

#     return clock_hands

# def verify_hands_by_length(hands_data):
#     # Calculate length for each hand and store in the dictionary
#     for hand, data in hands_data.items():
#         coords = data.get('coords', (0, 0, 0, 0))
#         x1, y1, x2, y2 = coords
#         length = np.sqrt((x2 - x1)*2 + (y2 - y1)*2)
#         hands_data[hand]['length'] = length

#     # Print hands_data for debugging
#     print(hands_data)

#     # Sort hands based on their length
#     sorted_hands = sorted(hands_data.items(), key=lambda item: item[1].get('length', 0), reverse=True)
#     # Assign hands based on lengths
#     clock_hands = {
#         'seconds': sorted_hands[0][1],
#         'minutes': sorted_hands[1][1],
#         'hour': sorted_hands[2][1]
#     }
#     return clock_hands

# def check_180_degree_shift(clock_hands):
#     # Extract the angles
#     hour_hand_angle = clock_hands['hour']['angle']
#     minutes_hand_angle = clock_hands['minutes']['angle']

#     # Calculate expected hours from the minute hand
#     hour_from_minute = int(minutes_hand_angle / 30.0)
#     hour_from_hour = int(hour_hand_angle / 30.0)

#     # Check for a 180-degree shift
#     if abs(hour_from_hour - hour_from_minute) == 6:
#         # Adjust the angles by 180 degrees
#         clock_hands['hour']['angle'] = (hour_hand_angle + 180) % 360

#     return clock_hands
def identify_clock_hands(filtered_lines):
    # Compute lengths for each line in the filtered_lines list
    for line in filtered_lines:
        x1, y1, x2, y2 = line[:4]
        length = np.sqrt((x2 - x1)*2 + (y2 - y1)*2)
        line.append(length)

    # Sort lines based on their lengths
    sorted_hands = sorted(filtered_lines, key=lambda x: x[5], reverse=True)

    hands = {
        'hour': sorted_hands[2],
        'minute': sorted_hands[1],
        'second': sorted_hands[0]
    }

    # Find the expected minute angle based on the hours hand
    expected_minute_angle = (hands['hour'][4] * 12) % 360
    if abs(expected_minute_angle - hands['minute'][4]) > 15:
        hands['minute'], hands['second'] = hands['second'], hands['minute']

    return hands
def detect_exact_time(clock_hands):
    if all(clock_hands.values()):
        hour_hand = clock_hands['hour']
        minutes_hand = clock_hands['minute']
        seconds_hand = clock_hands['second']

        angle_seconds = seconds_hand[4]
        angle_minutes = minutes_hand[4]
        angle_hour = hour_hand[4]

        hours_fractional = (angle_hour / 30) % 12
        hours_whole = int(hours_fractional)
        minutes_from_hour = (hours_fractional - hours_whole) * 60
        minutes_from_minute_hand = (angle_minutes / 6) % 60

        # Consistency check
        if abs(minutes_from_hour - minutes_from_minute_hand) <= 1:
            print("Minute detection is consistent between the hour and minute hands.")
        else:
            print("Inconsistency detected in minute hand calculation.")
        
        seconds = int((angle_seconds / 6) % 60)

        formatted_time = f"{hours_whole:02d}:{int(minutes_from_minute_hand):02d}:{seconds:02d}"

        return formatted_time

    else:
        return "Clock hands not detected"
def draw_detected_hands(src, clock_hands):
    src_duplicate = src.copy()
    # BGR format for OpenCV
    COLOR_HOUR = (0, 0, 255)  # Red
    COLOR_MINUTE = (0, 255, 0)  # Green
    COLOR_SECOND = (255, 0, 0)  # Blue

    # Drawing hour hand
    cv2.line(src_duplicate, 
             (clock_hands['hour'][0], clock_hands['hour'][1]),  # x1, y1
             (clock_hands['hour'][2], clock_hands['hour'][3]),  # x2, y2
             COLOR_HOUR, 2)
    
    # Drawing minute hand
    cv2.line(src_duplicate, 
             (clock_hands['minute'][0], clock_hands['minute'][1]), 
             (clock_hands['minute'][2], clock_hands['minute'][3]), 
             COLOR_MINUTE, 2)
    
    # Drawing second hand
    cv2.line(src_duplicate, 
             (clock_hands['second'][0], clock_hands['second'][1]), 
             (clock_hands['second'][2], clock_hands['second'][3]), 
             COLOR_SECOND, 2)

    return src_duplicate