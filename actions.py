import pyautogui
from pynput.mouse import Controller as MouseController, Button

# Disable PyAutoGUI fail-safe pause for smooth interactions
pyautogui.PAUSE = 0


class ActionController:
    def __init__(self, screen_w=None, screen_h=None):
        self.mouse = MouseController()
        size = pyautogui.size()
        self.screen_w = screen_w or size.width
        self.screen_h = screen_h or size.height

        self.control_enabled = False
        self.prev_palm_y = None
        self.is_pinched = False

        # Stability counters
        self.fist_frames = 0
        self.palm_frames = 0
        self.stable_threshold = 3

        # Sensitivity thresholds
        self.scroll_threshold = 0.04
        self.smooth_factor = 0.3
        self.prev_cursor_x = None
        self.prev_cursor_y = None

    def enable_control(self):
        self.control_enabled = True

    def disable_control(self):
        self.control_enabled = False
        self.prev_palm_y = None
        self.is_pinched = False
        self.fist_frames = 0
        self.palm_frames = 0
        self.prev_cursor_x = None
        self.prev_cursor_y = None

    def update_state(self, gesture):
        """State transitions for OPEN_PALM (Start) and FIST (Stop)."""
        action = "IDLE"

        if gesture == "FIST":
            self.fist_frames += 1
            self.palm_frames = 0
            if self.fist_frames >= self.stable_threshold and self.control_enabled:
                self.disable_control()
                action = "CONTROL_DISABLED"
        elif gesture == "OPEN_PALM":
            self.palm_frames += 1
            self.fist_frames = 0
            if self.palm_frames >= self.stable_threshold and not self.control_enabled:
                self.enable_control()
                action = "CONTROL_ENABLED"
        else:
            self.fist_frames = 0
            self.palm_frames = 0

        return action

    def handle_scroll(self, palm_y):
        """Scrolls up or down if vertical movement crosses threshold."""
        if not self.control_enabled or palm_y is None:
            self.prev_palm_y = palm_y
            return None

        action = None
        if self.prev_palm_y is not None:
            diff = self.prev_palm_y - palm_y
            if diff > self.scroll_threshold:
                # Upward in image coordinate space = smaller Y
                self.mouse.scroll(0, 2)
                action = "SCROLL_UP"
                self.prev_palm_y = palm_y
            elif diff < -self.scroll_threshold:
                # Downward in image coordinate space = larger Y
                self.mouse.scroll(0, -2)
                action = "SCROLL_DOWN"
                self.prev_palm_y = palm_y
        else:
            self.prev_palm_y = palm_y

        return action

    def handle_click(self, is_pinch):
        """
        Single click latch:
        released -> pinched -> CLICK -> wait -> released
        """
        if not self.control_enabled:
            self.is_pinched = False
            return None

        action = None
        if is_pinch:
            if not self.is_pinched:
                self.mouse.click(Button.left)
                self.is_pinched = True
                action = "LEFT_CLICK"
        else:
            self.is_pinched = False

        return action

    def handle_cursor(self, index_tip):
        """Moves cursor smoothly with index finger tip."""
        if not self.control_enabled or index_tip is None:
            self.prev_cursor_x = None
            self.prev_cursor_y = None
            return None

        target_x = index_tip.x * self.screen_w
        target_y = index_tip.y * self.screen_h

        if self.prev_cursor_x is None:
            curr_x, curr_y = target_x, target_y
        else:
            curr_x = self.prev_cursor_x + (target_x - self.prev_cursor_x) * self.smooth_factor
            curr_y = self.prev_cursor_y + (target_y - self.prev_cursor_y) * self.smooth_factor

        self.mouse.position = (int(curr_x), int(curr_y))
        self.prev_cursor_x = curr_x
        self.prev_cursor_y = curr_y
        return "CURSOR_MOVE"
