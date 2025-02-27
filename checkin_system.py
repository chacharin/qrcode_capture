import cv2
import numpy as np
import time
import os
import re
import sounddevice as sd
import wavio

# Function to sanitize filename from QR Code text
def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", text)

# Function to draw text with background on image
def draw_text_with_background(image, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.7, 
                              text_color=(0, 255, 255), bg_color=(0, 0, 0), padding=10):
    text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
    x, y = position
    rect_x1, rect_y1 = x, y - text_size[1] - padding
    rect_x2, rect_y2 = x + text_size[0] + padding, y + padding

    cv2.rectangle(image, (rect_x1, rect_y1), (rect_x2, rect_y2), bg_color, -1)  # Draw black background
    cv2.putText(image, text, (x + padding // 2, y), font, font_scale, text_color, 2)  # Draw text

# Function to play a notification sound
def play_sound():
    try:
        wav_file = "beep.wav"  # Ensure this is a valid .wav file
        wav = wavio.read(wav_file)
        data = wav.data.astype("float32")
        rate = wav.rate
        sd.play(data, rate)
        sd.wait()  # Wait until the sound finishes
    except Exception as e:
        print(f"Error playing sound: {e}")

# Function to detect and save QR Code image
def read_qr_code(frame, detected_codes, last_detected_times):
    qr_detector = cv2.QRCodeDetector()
    retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(frame)

    current_time = time.time()
    time_gap = 15  # Prevent saving the same QR code within 5 seconds

    if points is not None and decoded_info:
        for i, bbox in enumerate(points):
            text = decoded_info[i] if i < len(decoded_info) else "Unknown"
            if text:
                last_time = last_detected_times.get(text, 0)
                if current_time - last_time > time_gap:
                    timestamp = time.strftime("%d-%b-%Y %H-%M-%S")
                    sanitized_text = sanitize_filename(text)
                    detected_codes[text] = timestamp
                    last_detected_times[text] = current_time

                    print(f"Detected QR Code: {text} at {timestamp}")
                    
                    # Create folder to save images
                    image_folder = r'.\saved_images'
                    os.makedirs(image_folder, exist_ok=True)

                    # Generate filename and path
                    image_path = os.path.join(image_folder, f"{timestamp}_{sanitized_text}.png")

                    # Draw text on image before saving
                    text_overlay = f"{text} - {timestamp}"
                    draw_text_with_background(frame, text_overlay, (20, frame.shape[0] - 20))

                    if frame is not None and frame.size > 0:
                        success = cv2.imwrite(image_path, frame)
                        if success:
                            print(f"Image successfully saved to {image_path}")
                            play_sound()  # 🔊 Play beep sound when image is saved
                        else:
                            print("Error: Failed to save image.")
                    else:
                        print("Error: Empty frame, skipping save.")

            # Draw bounding box around QR Code
            bbox = bbox.astype(int)
            for j in range(len(bbox)):
                point1 = tuple(bbox[j])
                point2 = tuple(bbox[(j + 1) % len(bbox)])
                cv2.line(frame, point1, point2, (0, 255, 0), 2)

            x, y, w, h = cv2.boundingRect(bbox)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            display_text = f"{text} ({detected_codes.get(text, 'Stamp Time')})"
            cv2.putText(frame, display_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame

# Main function to capture video and detect QR Code
def main():
    cap = cv2.VideoCapture(0)
    detected_codes = {}
    last_detected_times = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture video frame.")
            break

        frame = read_qr_code(frame, detected_codes, last_detected_times)
        cv2.imshow('QR Code Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
