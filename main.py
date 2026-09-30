import time
import cv2
from camera import Camera
from hand import HandDetector
from gestures import detect_gesture, get_palm_center, detect_pinch
from actions import ActionController

DEBUG = False


def debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")


def main():
    camera_index = 0
    cam = Camera(index=camera_index, width=1280, height=720)
    detector = HandDetector(max_hands=1)
    actions = ActionController()

    try:
        cam.start()
        print("Camera started")
        print("Control: OFF")

        prev_time = time.time()
        last_action = "READY"

        while True:
            success, frame = cam.read()
            if not success:
                print("Failed to grab frame")
                break

            now = time.time()
            fps = 1.0 / (now - prev_time) if (now - prev_time) > 0 else 0
            prev_time = now

            # Process hand
            landmarks = detector.process(frame)
            gesture = "NONE"
            palm_pos = None

            if landmarks:
                detector.draw(frame, landmarks)
                gesture = detect_gesture(landmarks)
                palm_pos = get_palm_center(landmarks)

                # State update (FIST / OPEN_PALM)
                state_action = actions.update_state(gesture)
                if state_action != "IDLE":
                    last_action = state_action
                    debug(f"State transition: {state_action}")

                if actions.control_enabled:
                    # 1. Pinch click
                    is_pinch, _ = detect_pinch(landmarks)
                    click_act = actions.handle_click(is_pinch)
                    if click_act:
                        last_action = click_act

                    # 2. Index cursor
                    if gesture == "INDEX":
                        cursor_act = actions.handle_cursor(landmarks.landmark[8])
                        if cursor_act:
                            last_action = cursor_act
                    else:
                        actions.prev_cursor_x = None
                        actions.prev_cursor_y = None

                    # 3. Vertical Scroll
                    if gesture in ["OPEN_PALM", "NONE"] and not is_pinch:
                        scroll_act = actions.handle_scroll(palm_pos[1] if palm_pos else None)
                        if scroll_act:
                            last_action = scroll_act
            else:
                actions.prev_palm_y = None
                actions.prev_cursor_x = None
                actions.prev_cursor_y = None

            # On-screen HUD
            control_str = "ON" if actions.control_enabled else "OFF"
            color = (0, 255, 0) if actions.control_enabled else (0, 0, 255)

            cv2.putText(
                frame,
                f"CONTROL: {control_str}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2,
            )
            cv2.putText(
                frame,
                f"GESTURE: {gesture}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                frame,
                f"ACTION: {last_action}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                frame,
                f"FPS: {int(fps)}",
                (20, 145),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (200, 200, 200),
                2,
            )

            # Debug overlay
            if DEBUG and landmarks:
                h, w, _ = frame.shape
                cv2.rectangle(frame, (w - 280, 20), (w - 20, 180), (30, 30, 30), -1)
                cv2.putText(frame, "DEBUG", (w - 260, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Palm: {palm_pos[0]:.2f}, {palm_pos[1]:.2f}", (w - 260, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, f"Control: {actions.control_enabled}", (w - 260, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, f"Pinched: {actions.is_pinched}", (w - 260, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("CAMPI - Camera Gesture Control", frame)

            # Keys: Q = quit, ESC = disable control
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                actions.disable_control()
                last_action = "EMERGENCY_STOP"
                debug("Safety cutoff: Control disabled by ESC")
            elif key == ord("q") or key == ord("Q"):
                break

    finally:
        cam.release()
        detector.close()
        print("Camera released")


if __name__ == "__main__":
    main()
