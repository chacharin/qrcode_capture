import streamlit as st
import cv2
import numpy as np
import pandas as pd
import time
import os
import re
import sounddevice as sd
import wavio
import csv

# Full-Screen Layout
st.set_page_config(page_title="QR Code Check-in", layout="wide")

CSV_FILE = "checkin.csv"
IMAGE_FOLDER = "saved_images"

# Ensure checkin.csv and image folder exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "ID"])

# Function to sanitize filenames
def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", text)

# Function to play a beep sound
def play_sound():
    try:
        wav_file = "beep.wav"
        wav = wavio.read(wav_file)
        data = wav.data.astype("float32")
        rate = wav.rate
        sd.play(data, rate)
        sd.wait()
    except Exception as e:
        st.error(f"Error playing sound: {e}")

# Function to log QR Code scans
def log_scan_to_csv(timestamp, qr_id):
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, qr_id])

# Function to draw text on an image
def draw_text_on_image(image, text, position=(20, 40), font_scale=0.7):
    """Draws text on an image with a black background for visibility."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (0, 255, 255)  # Yellow
    bg_color = (0, 0, 0)  # Black
    thickness = 2

    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    x, y = position
    rect_x1, rect_y1 = x - 5, y - text_size[1] - 5
    rect_x2, rect_y2 = x + text_size[0] + 10, y + 10

    cv2.rectangle(image, (rect_x1, rect_y1), (rect_x2, rect_y2), bg_color, -1)  # Draw black background
    cv2.putText(image, text, (x, y), font, font_scale, text_color, thickness)

# Function to save captured image
def save_captured_image(frame, qr_text, timestamp):
    sanitized_text = sanitize_filename(qr_text)
    image_filename = f"{timestamp}_{sanitized_text}.png"
    image_path = os.path.join(IMAGE_FOLDER, image_filename)

    # ✅ Draw text on image before saving
    display_text = f"{qr_text} - {timestamp}"
    draw_text_on_image(frame, display_text, position=(20, frame.shape[0] - 20))

    cv2.imwrite(image_path, frame)  # Save mirrored image with text
    st.success(f"📸 Image saved: {image_filename}")

# Function to get available cameras
def get_available_cameras():
    camera_list = []
    for index in range(10):  # Check up to 10 cameras
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            camera_list.append(f"Camera {index}")
            cap.release()
    return camera_list if camera_list else ["No camera found"]

# Streamlit app layout
st.title("📸 Real-Time QR Code Check-in System")

# Adjust Column Ratio (Expand Camera Size)
col1, col2 = st.columns([0.7, 1])  # Camera is wider than records

# Left Column (Live Video)
with col1:
    st.subheader("📷 Live Camera Feed")
    camera_list = get_available_cameras()
    
    # Select Camera Dropdown
    selected_camera = st.selectbox("Select Camera", camera_list, index=0)

    # Extract camera index from selected string
    camera_index = int(selected_camera.split()[-1]) if "Camera" in selected_camera else None

    frame_placeholder = st.empty()
    status_placeholder = st.empty()

# Right Column (Check-in Table)
with col2:
    st.subheader("📜 Check-in Records")
    table_placeholder = st.empty()

# Session state for camera
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False

# Button to start/stop the camera
if st.button("🎥 Start/Stop Camera") and camera_index is not None:
    st.session_state.camera_active = not st.session_state.camera_active

# OpenCV Webcam Capture (Only runs if camera is active)
if st.session_state.camera_active and camera_index is not None:
    cap = cv2.VideoCapture(camera_index)
    qr_detector = cv2.QRCodeDetector()
    detected_codes = {}
    last_detected_times = {}
    time_gap = 5  # Prevent duplicate scans within 5 seconds

    while st.session_state.camera_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Error: Unable to access webcam.")
            break

        # ✅ Flip the camera feed (Mirror Effect)
        frame = cv2.flip(frame, 1)  # Flip Left-Right

        # Detect QR Code
        retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(frame)
        current_time = time.time()

        timestamp = None  

        if points is not None and decoded_info:
            for i, bbox in enumerate(points):
                text = decoded_info[i] if i < len(decoded_info) else "Unknown"
                if text:
                    last_time = last_detected_times.get(text, 0)
                    if current_time - last_time > time_gap:
                        timestamp = time.strftime("%d-%b-%Y %H-%M-%S")
                        detected_codes[text] = timestamp
                        last_detected_times[text] = current_time

                        log_scan_to_csv(timestamp, text)
                        play_sound()  # Play beep when successfully scanned

                        # ✅ Save mirrored image with text
                        save_captured_image(frame, text, timestamp)

                        # Show check-in success message (disappears after 3 sec)
                        status_placeholder.success(f"✅ Check-in Recorded: {text} at {timestamp}")
                        time.sleep(3)
                        status_placeholder.empty()  # Clear message

        # ✅ Convert BGR to RGB before displaying in Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)  # ✅ FIXED


        # ✅ Update Check-in Table (New Records Appear at the TOP, No Index Column)
        df = pd.read_csv(CSV_FILE, dtype={"ID": str})  # ✅ Ensure ID is displayed as a string
        df = df[::-1].reset_index(drop=True)  # ✅ Reverse DataFrame so new records appear first

        # ✅ Hide index column from table
        table_placeholder.table(df)  # ✅ No index column

        # Break loop if stop button is pressed
        if not st.session_state.camera_active:
            break

    cap.release()
    cv2.destroyAllWindows()
