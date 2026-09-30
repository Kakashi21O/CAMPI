import math


def is_finger_open(landmarks, tip_idx, pip_idx):
    """Returns True if fingertip is above PIP joint (lower Y in image coords)."""
    return landmarks.landmark[tip_idx].y < landmarks.landmark[pip_idx].y


def is_thumb_open(landmarks):
    """Checks thumb extension by relative x/y distance between thumb tip (4) and MCP (2)."""
    tip = landmarks.landmark[4]
    ip = landmarks.landmark[3]
    mcp = landmarks.landmark[2]
    # In mirrored image, thumb extension is measured horizontally relative to MCP
    return abs(tip.x - mcp.x) > abs(ip.x - mcp.x)


def get_palm_center(landmarks):
    """Computes normalized (x, y) center using wrist (0) and middle MCP (9)."""
    wrist = landmarks.landmark[0]
    middle_mcp = landmarks.landmark[9]
    return ((wrist.x + middle_mcp.x) / 2.0, (wrist.y + middle_mcp.y) / 2.0)


def get_finger_states(landmarks):
    """
    Returns boolean states: [thumb, index, middle, ring, pinky]
    """
    return [
        is_thumb_open(landmarks),
        is_finger_open(landmarks, 8, 6),
        is_finger_open(landmarks, 12, 10),
        is_finger_open(landmarks, 16, 14),
        is_finger_open(landmarks, 20, 18),
    ]


def detect_pinch(landmarks, threshold=0.06):
    """Detects pinch if distance between thumb tip (4) and index tip (8) is below threshold."""
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]
    dist = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
    return dist < threshold, dist


def detect_gesture(landmarks):
    """
    Identifies V1 gestures:
    - OPEN_PALM
    - FIST
    - PINCH
    - INDEX
    - NONE
    """
    if landmarks is None:
        return "NONE"

    is_pinch, _ = detect_pinch(landmarks)
    states = get_finger_states(landmarks)
    _, index_open, middle_open, ring_open, pinky_open = states

    # 1. Pinch takes priority for click
    if is_pinch:
        return "PINCH"

    # 2. Open palm: 4 or 5 fingers open
    if sum(states[1:]) == 4:
        return "OPEN_PALM"

    # 3. Fist: all fingers closed
    if sum(states[1:]) == 0:
        return "FIST"

    # 4. Index only: index open, other three closed
    if index_open and not middle_open and not ring_open and not pinky_open:
        return "INDEX"

    return "NONE"
