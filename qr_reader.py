#pip install numpy
#pip install opencv-python
#pip install opencv-contrib-python

import cv2 #version 4.11
import numpy as np
import time

def read_qr_code(frame, detected_codes, last_detected_times):
    qr_detector = cv2.QRCodeDetector()
    
    # Detect and decode multiple QR codes
    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(frame)

    current_time = time.time()
    time_gap = 5  # 5 seconds gap before allowing a QR code to be printed again

    if points is not None and decoded_info:
        for i in range(len(points)):
            text = decoded_info[i] if i < len(decoded_info) else "Unknown"
            if text:
                last_time = last_detected_times.get(text, 0)
                if current_time - last_time > time_gap:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    detected_codes[text] = timestamp  # Store timestamp
                    last_detected_times[text] = current_time  # Update last detected time
                    print(f"Detected QR Code: {text} at {timestamp}")  # Print to console
            
            bbox = points[i].astype(int)  # Convert bounding box points to integers
            for j in range(len(bbox)):
                point1 = tuple(bbox[j])
                point2 = tuple(bbox[(j + 1) % len(bbox)])
                cv2.line(frame, point1, point2, (0, 255, 0), 2)
            
            # Draw a rectangle around each QR code
            x, y, w, h = cv2.boundingRect(bbox)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Display the decoded text with timestamp
            display_text = f"{text} ({detected_codes.get(text, 'No Time')})"
            cv2.putText(frame, display_text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame

def main():
    cap = cv2.VideoCapture(0)  # Open webcam
    detected_codes = {}  # Dictionary to store detected QR codes and timestamps
    last_detected_times = {}  # Dictionary to store last detected timestamps

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = read_qr_code(frame, detected_codes, last_detected_times)
        cv2.imshow('QR Code Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
