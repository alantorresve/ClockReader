import cv2
import numpy as np
import tkinter as tk

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


def detect_line_and_draw_circle(circle, source_image, gray_image, filtered_lines):
    center = (circle[0], circle[1])
    radius = circle[2]
    
    # Draw circle center
    cv2.circle(source_image, center, 1, (255, 0, 0), 3)
    
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


def hands_angle(lines_and_center):
    
    for line in lines_and_center:
        x1, y1, x2, y2, angle, center_x, center_y = line[:7]
        
        if (x1 == center_x and y1 == center_y):
            pointer_x, pointer_y = x2, y2
        else:
            pointer_x, pointer_y = x1, y1
     
        radius = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
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
                        
        if 0 <= angle_pointer < 360:
            orientation_angle = 90 + angle_pointer
        elif -90 < angle_pointer < 0:
            orientation_angle = 90 + angle_pointer
        else:
            orientation_angle = angle_pointer + 450
    
        line[4] = orientation_angle
    
    length = []
    
    for line in lines_and_center:
        x1, y1, x2, y2, orientation_angle, center_x, center_y = line[:7]
        l = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        length.append(l)
        
    result_array = np.column_stack((lines_and_center, length))
    
    # Sort lines based on their lengths
    sorted_hands = sorted(result_array, key=lambda x: x[7], reverse=True)

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
    
    hour_hand = clock_hands['hour']
    minutes_hand = clock_hands['minute']
    seconds_hand = clock_hands['second']

    angle_seconds = seconds_hand[4]
    angle_minutes = minutes_hand[4]
    angle_hour = hour_hand[4]

    hour_read = (angle_hour / 360) * 12
    minutes_read = (angle_minutes / 360) * 60
    seconds_read = (angle_seconds / 360) * 60
       
    formatted_time = f"{int(hour_read):02d}:{int(minutes_read):02d}:{int(seconds_read):02d}"

    return formatted_time 
    

def display_time_in_tkinter(exact_time):
    # Create a tkinter window for displaying the time
    time_window = tk.Toplevel()
    time_window.title('Exact Time')

    # Create a label widget to display the time
    label = tk.Label(time_window, font=('calibri', 20), background='white', foreground='black', text=exact_time)
    label.pack()

    # Start the tkinter main loop
    time_window.mainloop()