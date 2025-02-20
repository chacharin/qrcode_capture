import cv2  # ใช้สำหรับการตรวจจับ QR Code
import numpy as np  # ใช้สำหรับการจัดการกับอาร์เรย์
import time  # ใช้สำหรับจัดการเวลาสำหรับตั้งชื่อไฟล์
import os  # ใช้สำหรับการจัดการไฟล์และโฟลเดอร์
import re  # ใช้สำหรับการลบอักขระที่ไม่สามารถใช้ในชื่อไฟล์ได้

# ฟังก์ชันสำหรับทำความสะอาดข้อความจาก QR Code ให้เป็นชื่อไฟล์ที่สามารถใช้ได้
def sanitize_filename(text):
    # แทนที่อักขระที่ไม่สามารถใช้ในชื่อไฟล์ด้วย "_"
    return re.sub(r'[\\/*?:"<>|]', "_", text)

# ฟังก์ชันหลักสำหรับตรวจจับ QR Code และบันทึกภาพ
def read_qr_code(frame, detected_codes, last_detected_times):
    qr_detector = cv2.QRCodeDetector()  # สร้างอ็อบเจ็กต์ QRCodeDetector เพื่อใช้ตรวจจับ QR Code
    
    # ตรวจจับและถอดรหัส QR Code หลายๆ ตัวจากเฟรม
    retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(frame)
    
    # ใช้เวลาในการตรวจสอบเวลาห่างจากการตรวจจับครั้งล่าสุด
    current_time = time.time()  # เวลาปัจจุบัน
    time_gap = 5  # กำหนดให้มีช่องว่าง 5 วินาทีระหว่างการพิมพ์ข้อความจาก QR Code เดิม

    # ตรวจสอบว่ามี QR Code ที่ถูกตรวจพบหรือไม่
    if points is not None and decoded_info:
        for i, bbox in enumerate(points):  # ทำการวนลูปตรวจจับ QR Code ในแต่ละตำแหน่ง
            text = decoded_info[i] if i < len(decoded_info) else "Unknown"  # ถอดรหัสข้อความจาก QR Code
            if text:
                last_time = last_detected_times.get(text, 0)  # ตรวจสอบเวลาครั้งสุดท้ายที่ QR Code นี้ถูกตรวจพบ
                if current_time - last_time > time_gap:  # ถ้าเวลาห่างจากการตรวจพบก่อนหน้าเกิน 5 วินาที
                    # สร้าง timestamp ในรูปแบบ "วัน-เดือน(3ตัว)-ปี ชั่วโมง:นาที:วินาที"
                    timestamp = time.strftime("%d-%b-%Y %H-%M-%S")  # รูปแบบวันที่และเวลา
                    sanitized_text = sanitize_filename(text)  # ทำความสะอาดข้อความจาก QR Code
                    detected_codes[text] = timestamp  # เก็บ timestamp ที่ตรวจพบสำหรับ QR Code นี้
                    last_detected_times[text] = current_time  # อัปเดตเวลาการตรวจพบครั้งล่าสุด
                    print(f"Detected QR Code: {text} at {timestamp}")  # พิมพ์ข้อความเมื่อ QR Code ถูกตรวจพบ
                    
                    # สร้างโฟลเดอร์สำหรับบันทึกภาพ
                    image_folder = r'.\saved_images'  # กำหนดตำแหน่งโฟลเดอร์ในการบันทึกภาพ
                    os.makedirs(image_folder, exist_ok=True)  # สร้างโฟลเดอร์ถ้ายังไม่มี
                    
                    # สร้างชื่อไฟล์ที่ใช้ในการบันทึกภาพ
                    image_path = os.path.join(image_folder, f"{timestamp}_{sanitized_text}.png")
                    
                    # พิมพ์ path ของไฟล์สำหรับการดีบัก
                    print(f"Attempting to save image to: {image_path}")
                    
                    # ตรวจสอบว่าเฟรมมีข้อมูลหรือไม่
                    if frame is not None and frame.size > 0:
                        success = cv2.imwrite(image_path, frame)  # บันทึกภาพ
                        if success:
                            print(f"Image successfully saved to {image_path}")  # พิมพ์เมื่อบันทึกสำเร็จ
                        else:
                            print("Error: Failed to save image.")  # หากบันทึกไม่สำเร็จ
                    else:
                        print("Error: Empty frame, skipping save.")  # หากเฟรมว่างเปล่าไม่สามารถบันทึกได้
            
            # แปลงจุด Bounding Box ให้เป็นเลขจำนวนเต็ม
            bbox = bbox.astype(int)
            for j in range(len(bbox)):
                point1 = tuple(bbox[j])
                point2 = tuple(bbox[(j + 1) % len(bbox)])
                cv2.line(frame, point1, point2, (0, 255, 0), 2)  # วาดเส้นรอบๆ QR Code
                
            # วาดสี่เหลี่ยมรอบ QR Code
            x, y, w, h = cv2.boundingRect(bbox)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # แสดงข้อความที่ถอดรหัสจาก QR Code บนภาพ
            display_text = f"{text} ({detected_codes.get(text, 'No Time')})"
            cv2.putText(frame, display_text, (x, y - 10),  # แสดงข้อความตรงจุดที่ QR Code ถูกตรวจพบ
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame

# ฟังก์ชันหลักสำหรับการเปิดกล้องและตรวจจับ QR Code
def main():
    cap = cv2.VideoCapture(0)  # เปิดกล้องเพื่อจับภาพ
    detected_codes = {}  # ใช้เก็บ QR Code ที่ถูกตรวจพบและเวลา
    last_detected_times = {}  # เก็บเวลาของการตรวจพบครั้งสุดท้าย

    # ลูปตรวจจับ QR Code จากกล้อง
    while True:
        ret, frame = cap.read()  # อ่านภาพจากกล้อง
        if not ret:  # หากไม่สามารถจับภาพได้
            print("Error: Unable to capture video frame.")
            break

        frame = read_qr_code(frame, detected_codes, last_detected_times)  # ตรวจจับ QR Code
        cv2.imshow('QR Code Scanner', frame)  # แสดงภาพที่ตรวจจับ QR Code

        # หากกด 'q' ออกจากลูป
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()  # ปิดการใช้งานกล้อง
    cv2.destroyAllWindows()  # ปิดหน้าต่างแสดงผล

if __name__ == "__main__":
    main()  # เรียกใช้ฟังก์ชันหลัก
