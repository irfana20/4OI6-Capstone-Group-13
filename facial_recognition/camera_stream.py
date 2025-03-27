from flask import Flask, Response
from picamera2 import Picamera2
import cv2

# Initialize Flask app
app = Flask(__name__)

# Initialize Picamera2
picam2 = Picamera2()

# Configure camera resolution and format (adjust size if needed)
picam2.configure(picam2.create_video_configuration
                 (main={"size": (640, 480), "format": "RGB888"}))

# # Set Auto White Balance (fix blue tint)
# picam2.set_controls({"AwbMode":1}) # 0 = Auto White Balance
# #, "ColourGains":(2.5,0.8)

# Start the camera
picam2.start()

def generate_frames():
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 1)

        # Convert to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame in byte format for MJPEG streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Stream the frames using multipart MIME type
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Run Flask on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000)

