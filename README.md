
# QR Code Detection and Image Capture Project

This project is designed to detect QR codes using OpenCV and save images from the webcam when a QR code is detected. The images are saved with filenames containing the current timestamp and the sanitized QR code text.

## Features
- Detects multiple QR codes in real-time.
- Captures images from the webcam when a QR code is detected.
- Saves images with filenames in the format:
  ```
  {day-month-year hour:minute:second_"sanitized encoding text"}.png
  ```
- Creates a folder named `saved_images` to store the captured images.

## Installation

### 1. Clone the repository
First, clone this repository to your local machine.

```bash
git clone https://github.com/chacharin/qrcode_capture.git
```

### 2. Set up a Virtual Environment
It is recommended to use a virtual environment to manage the project dependencies.

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Make sure you have the required libraries installed. You can do this by using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This will install the following libraries:
- `opencv-python`
- `opencv-contrib-python`
- `numpy`

## Usage

### 1. Run the Application
Once the environment is set up and dependencies are installed, you can run the QR code detection script.

```bash
python qr-reader-capture.py
```

This will open your webcam and start scanning for QR codes. When a QR code is detected, the image will be saved in the `saved_images` folder, with a filename containing the timestamp and the QR code text.

### 2. Exit the Application
To stop the application, simply press the `q` key while the webcam window is active.

## File Structure

```
.
├── qr.py                    # Main script for QR code detection and image capture
├── requirements.txt          # List of project dependencies
├── saved_images/             # Folder where captured images will be saved
└── README.md                 # Project documentation
```

## License
This project is licensed under the MIT License

## Acknowledgements
- OpenCV: The primary library used for QR code detection and image capture.
- NumPy: Used for numerical operations and image data handling.
