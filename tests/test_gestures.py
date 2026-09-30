from unittest.mock import MagicMock
from gestures import detect_gesture, detect_pinch, get_palm_center, get_finger_states


class DummyLandmark:
    def __init__(self, x=0.5, y=0.5, z=0.0):
        self.x = x
        self.y = y
        self.z = z


def make_hand(finger_tips_up=True):
    # 21 landmarks
    # tips: 4 (thumb), 8 (index), 12 (middle), 16 (ring), 20 (pinky)
    # pips: 2, 6, 10, 14, 18
    lms = [DummyLandmark(0.5, 0.7) for _ in range(21)]
    # Wrist = 0 (y=0.8), Middle MCP = 9 (y=0.6) -> center = (0.5, 0.7)
    lms[0] = DummyLandmark(0.5, 0.8)
    lms[9] = DummyLandmark(0.5, 0.6)

    # Thumb MCP(2)=(0.4, 0.7), IP(3)=(0.3, 0.65), Tip(4)=(0.2, 0.6)
    lms[2] = DummyLandmark(0.4, 0.7)
    lms[3] = DummyLandmark(0.3, 0.65)
    lms[4] = DummyLandmark(0.2, 0.6)

    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        lms[pip] = DummyLandmark(0.5, 0.5)
        lms[tip] = DummyLandmark(0.5, 0.3 if finger_tips_up else 0.7)
    return lms


def test_palm_center():
    lms = make_hand()
    center = get_palm_center(lms)
    assert round(center[0], 2) == 0.5
    assert round(center[1], 2) == 0.7


def test_detect_open_palm():
    lms = make_hand(finger_tips_up=True)
    gesture = detect_gesture(lms)
    assert gesture == "OPEN_PALM"


def test_detect_fist():
    lms = make_hand(finger_tips_up=False)
    # Thumb tip close to MCP
    lms[4] = DummyLandmark(0.4, 0.7)
    gesture = detect_gesture(lms)
    assert gesture == "FIST"


def test_detect_index():
    lms = make_hand(finger_tips_up=False)
    # Open index tip only
    lms[8] = DummyLandmark(0.5, 0.2)
    # Thumb close
    lms[4] = DummyLandmark(0.4, 0.7)
    gesture = detect_gesture(lms)
    assert gesture == "INDEX"


def test_detect_pinch():
    lms = make_hand(finger_tips_up=True)
    # Put thumb tip (4) and index tip (8) extremely close
    lms[4] = DummyLandmark(0.5, 0.3)
    lms[8] = DummyLandmark(0.51, 0.31)
    is_pinch, dist = detect_pinch(lms)
    assert is_pinch is True
    assert detect_gesture(lms) == "PINCH"
