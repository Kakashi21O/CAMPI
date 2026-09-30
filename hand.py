import cv2
import mediapipe as mp
import numpy as np


class HandDetector:
    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process(self, frame):
        """Processes RGB frame and returns detected landmarks list or None."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if not results.multi_hand_landmarks:
            return None
        return results.multi_hand_landmarks[0]

    def draw(self, frame, landmarks):
        """Draws hand skeleton and landmarks on the frame."""
        if landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                landmarks,
                self.mp_hands.HAND_CONNECTIONS,
            )

    def close(self):
        if self.hands:
            self.hands.close()
