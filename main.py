import json
import cv2
import datetime
import numpy as np
from ultralytics import YOLO
import csv
import zmq

# ZeroMQ Setup
context = zmq.Context()
socket = context.socket(zmq.PUSH)

# Load configuration from JSON file
with open('config.json', 'r') as file:
    config = json.load(file)
socket.bind("tcp://*:" + str(config["sender_port"]))  # Bind to the socket
# Initialize drawing variables
drawing = False
recording = False
ix, iy = -1, -1
line_coords = []
video_writer = None


# Initialize OpenCV VideoWriter
def init_video_writer(frame_width, frame_height, fps):
    fourcc = cv2.VideoWriter_fourcc(*config["output_video_codec"])
    return cv2.VideoWriter(config["output_video_name"], fourcc, fps, (frame_width, frame_height))


# Function for drawing lines
def draw_line(event, x, y, flags, param):
    global ix, iy, drawing, line_coords, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            frame_copy = frame.copy()
            cv2.line(frame_copy, (ix, iy), (x, y), config["line_color"], config["line_thickness"])
            cv2.imshow("RGB", frame_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.line(frame, (ix, iy), (x, y), config["line_color"], config["line_thickness"])
        line_coords = [(ix, iy), (x, y)]


# Intersection and direction functions
def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def direction(point, line):
    px, py = point
    (x1, y1), (x2, y2) = line
    if x1 == x2:
        return config["message_right"] if px > x1 else config["message_left"]
    else:
        slope = (y2 - y1) / (x2 - x1)
        y_intercept = y1 - (slope * x1)
        line_y = (slope * px) + y_intercept
        return config["message_down"] if py > line_y else config["message_up"]


# Load YOLO model and video
model = YOLO(config["model_path"])
cap = cv2.VideoCapture(config["video_path"])
if not cap.isOpened():
    exit()

# Tracking and logging variables
track_history = {}

# Set up window and mouse callback
cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', draw_line)

ret, frame = cap.read()
pause = False

# Main video processing loop
while ret:
    if not pause:
        ret, frame = cap.read()

    if ret:
        if len(line_coords) == 2:
            cv2.line(frame, line_coords[0], line_coords[1], config["line_color"], config["line_thickness"])
        key = cv2.waitKey(1) & 0xFF
        if key == ord(config["pause_key"]):
            pause = True
        elif key == ord(config["resume_key"]):
            pause = False

        if pause:
            cv2.imshow("RGB", frame)
            continue

        results = model.track(frame, persist=True)
        for detection in results[0].boxes.data:
            x1, y1, x2, y2, id, conf, class_id = map(int, detection)
            if class_id == 0:
                cv2.rectangle(frame, (x1, y1), (x2, y2), config["tracklet_color"], config["tracklet_thickness"])
                text = f'ID: {id}'
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, config["text_font"], config["text_color"], config["text_thickness"])

                center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                if id in track_history:
                    track_history[id].append(center)
                    track_history[id] = track_history[id][-config["tracklet_history_frames"]:]
                    for i in range(1, len(track_history[id])):
                        if track_history[id][i - 1] is None or track_history[id][i] is None:
                            continue
                        cv2.line(frame, track_history[id][i - 1], track_history[id][i], config["tracklet_color"], config["tracklet_thickness"])

                    if len(track_history[id]) >= 2 and len(line_coords) == 2:
                        prev_point = track_history[id][-2]
                        curr_point = track_history[id][-1]
                        if intersect(prev_point, curr_point, line_coords[0], line_coords[1]):
                            dir = direction(curr_point, line_coords)
                            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            log_message = f"{timestamp}, Person {id}, {dir}"
                            socket.send_string(log_message)  # Send log data to client

                else:
                    track_history[id] = [center]
        if recording:
            video_writer.write(frame)
            cv2.putText(frame, "REC", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("RGB", frame)

        # Check for recording start/stop keys
        if key == ord(config["start_record_key"]):
            if not recording:
                video_writer = init_video_writer(frame.shape[1], frame.shape[0], config["output_video_fps"])
                recording = True
        elif key == ord(config["stop_record_key"]):
            if recording:
                video_writer.release()
                recording = False
        if key == config["exit_key"]:
            break

cap.release()
if recording:
    video_writer.release()
cv2.destroyAllWindows()
context.term()
