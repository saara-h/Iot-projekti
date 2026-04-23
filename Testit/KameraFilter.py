import cv2
import time

capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
capture.set(cv2.CAP_PROP_FPS, 30)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Print actual settings
print("Actual W,H,FPS:",
      capture.get(cv2.CAP_PROP_FRAME_WIDTH),
      capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
      capture.get(cv2.CAP_PROP_FPS))

bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=16, detectShadows=False)

mode = "threshold"

prev_time = time.time()
fps = 0.0

save_fps = 15.0
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter("output.avi", fourcc, save_fps, (640, 480))

while True:
    ret, frame = capture.read()
    if not ret:
        print("Failed to read frame")
        break

    frame = cv2.flip(frame, 1)
    display_frame = frame.copy()

    if mode == "threshold":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        display_frame = cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

    elif mode == "edge":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        display_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    elif mode == "bg_sub":
        fg_mask = bg_subtractor.apply(frame)
        fg_mask = cv2.medianBlur(fg_mask, 5)
        display_frame = cv2.bitwise_and(frame, frame, mask=fg_mask)

    elif mode == "contour":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        display_frame = frame.copy()
        cv2.drawContours(display_frame, contours, -1, (0, 255, 0), 2)

    curr_time = time.time()
    dt = curr_time - prev_time
    inst_fps = 1.0 / dt if dt > 0 else 0.0
    fps = 0.9 * fps + 0.1 * inst_fps
    prev_time = curr_time

    cv2.putText(display_frame, f"FPS: {fps:.1f} Mode: {mode}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    out.write(display_frame)
    cv2.imshow("Live Video", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("t"):
        mode = "threshold"
    elif key == ord("e"):
        mode = "edge"
    elif key == ord("b"):
        mode = "bg_sub"
    elif key == ord("c"):
        mode = "contour"
    elif key == ord("n"):
        mode = "normal"
    elif key == ord("q"):
        break

capture.release()
out.release()
cv2.destroyAllWindows()
