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
    cv2.circle(source_image, center, 1, (255, 0, 0), 3)
    
    cv2.circle(source_image, (129, 408), 5, (255, 0, 0), 3)
    cv2.circle(source_image, (455, 406), 5, (0, 255, 0), 3)
    cv2.circle(source_image, (267, 159), 5, (0, 0, 255), 3)
    # cv2.circle(source_image, (100,0), 20, (255, 0, 0), 3)
    
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


# 
def determine_closest_point_to_center(circle, filtered_lines, lines_and_center):

    center_x, center_y = circle[0], circle[1]
   
    for line in filtered_lines: 
        x1, y1, x2, y2 = line[:4]
        dist_to_point1 = np.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
        dist_to_point2 = np.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)

        if dist_to_point1 < dist_to_point2:
            closest_point = (x1, y1)
        else:
            closest_point = (x2, y2)

        # Append the closest point to the line as new columns
        line_with_closest_point = np.append(line, closest_point)
        lines_and_center.append(line_with_closest_point)

    lines_and_center = np.array(lines_and_center) 

    return lines_and_center


def draw_clock_hands_circles(source_image, lines_and_centers):

    src_duplicate = source_image.copy()

    for line in lines_and_centers:
        x1, y1, x2, y2, angle, center_x, center_y = line[:7] 
        radius = int(np.sqrt((x1 - x2)**2 + (y1 - y2)**2))
        cv2.ellipse(src_duplicate, (int(center_x), int(center_y)), (radius, radius), angle, 0, 360, (0, 0, 255), 2)  # REVISAR!!!!!!!!!!
    
    return src_duplicate


################################################

def hands_angle(lines_and_center):
    
    for line in lines_and_center:
        x1, y1, x2, y2, angle, center_x, center_y = line[:7]
        
        if (x1 == center_x and y1 == center_y):
            pointer_x, pointer_y = x2, y2
        else:
            pointer_x, pointer_y = x1, y1
        
        print(int(pointer_x), int(pointer_y))

        radius = np.sqrt((x1 - x2)**2 + (y1 - y2)**2) #le saque un int pq me parecia innecesario
        start_x, start_y = center_x, center_y + radius
        vector_pointer = np.array([pointer_x - center_x, pointer_y - center_y])
        vector_start = np.array([start_x - center_x, start_y - center_y])
        
        magnitude_pointer = np.linalg.norm(vector_pointer)
        magnitude_start = np.linalg.norm(vector_start)
    
        #FALTA PARA NAN!!!!!
        
        #to find cosine
        dot_product = np.dot(vector_pointer, vector_start)
        cos_angle = (dot_product/(magnitude_pointer*magnitude_start))
        
        #to find sine
        matrix = np.array([vector_pointer, vector_start])
        determinant = np.linalg.det(matrix)
        sin_angle = (determinant/(magnitude_pointer*magnitude_start))
        
        #to find arctan
        angle_pointer = np.degrees(np.arctan2(cos_angle, sin_angle))
        
        #angle_pointer = np.degrees(np.arctan2(pointer_x - center_x, pointer_y - center_y))
        
        if 0 <= angle_pointer < 360:
            orientation_angle = 90 + angle_pointer
        elif -90 < angle_pointer < 0:
            orientation_angle = 90 + angle_pointer
        else:
            orientation_angle = angle_pointer + 450
        
        print(orientation_angle)
                  

    return orientation_angle 

################################################


def identify_clock_hands(lines_and_center):
    # Compute lengths for each line in the filtered_lines list
    for line in lines_and_center:
        x1, y1, x2, y2, angle, center_x, center_y = line[:7]
        vector_length = np.array([x1 - x2, y1 - y2])
        length = np.linalg.norm(vector_length)
        length_array = []
        length_array.append(length)

    # Sort lines based on their lengths
    sorted_hands = sorted(length_array, key=lambda x: x[5], reverse=True)

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