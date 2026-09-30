import cv2


class Camera:
    def __init__(self, index=0, width=1280, height=720):
        self.index = index
        self.width = width
        self.height = height
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {self.index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        success, frame = self.cap.read()
        if not success or frame is None:
            return False, None
        return True, cv2.flip(frame, 1)

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
