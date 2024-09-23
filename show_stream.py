import cv2
cap = cv2.VideoCapture("rtsp://test:test@192.168.1.91:8554/streaming/live/1")

while(cap.isOpened()):
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
