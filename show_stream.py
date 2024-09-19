import cv2

# RTMP stream URL
rtmp_url = 'rtmp://localhost/live/vd'

# Open the video capture stream
cap = cv2.VideoCapture(rtmp_url, cv2.CAP_FFMPEG)

# Check if the stream opened successfully
if not cap.isOpened():
    print("Error: Could not open stream.")
    exit()

# Loop to read and display frames
while True:
    ret, frame = cap.read()

    # If frame was not captured properly, break the loop
    if not ret:
        print("Failed to grab frame.")
        break

    # Display the frame
    cv2.imshow('RTMP Stream', frame)

    # Press 'q' to quit the video stream
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
