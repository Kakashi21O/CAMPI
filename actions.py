from pynput.mouse import Controller as MouseController


class ActionController:
    def __init__(self):
        self.mouse = MouseController()

        self.control_enabled = False
        self.prev_palm_x = None
        self.prev_palm_y = None

        # Stability counters
        self.fist_frames = 0
        self.palm_frames = 0
        self.stable_threshold = 3

        # Sensitivity thresholds
        self.scroll_deadzone = 0.025
        self.scroll_max_delta = 0.15

    def enable_control(self):
        self.control_enabled = True

    def disable_control(self):
        self.control_enabled = False
        self.prev_palm_x = None
        self.prev_palm_y = None
        self.fist_frames = 0
        self.palm_frames = 0

    def update_state(self, gesture):
        """State transitions: OPEN_PALM enables control, FIST disables control."""
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

    def handle_scroll(self, palm_pos):
        """
        Pure scroll controller supporting vertical movements and side-to-side hand swings:
        - Hand UP (Y decreases) -> SCROLL UP
        - Hand DOWN (Y increases) -> SCROLL DOWN
        - Hand Swing RIGHT (X increases in mirrored view) -> SCROLL DOWN
        - Hand Swing LEFT (X decreases in mirrored view) -> SCROLL UP
        """
        if not self.control_enabled or palm_pos is None:
            if palm_pos:
                self.prev_palm_x = palm_pos[0]
                self.prev_palm_y = palm_pos[1]
            return None

        palm_x, palm_y = palm_pos

        if self.prev_palm_x is None or self.prev_palm_y is None:
            self.prev_palm_x = palm_x
            self.prev_palm_y = palm_y
            return None

        # Calculate movements
        diff_y = self.prev_palm_y - palm_y  # Positive = UP, Negative = DOWN
        diff_x = palm_x - self.prev_palm_x  # Positive = RIGHT, Negative = LEFT

        abs_y = abs(diff_y)
        abs_x = abs(diff_x)

        action = None

        # Determine dominant movement: Vertical movement or Horizontal swing
        if abs_y >= abs_x and abs_y > self.scroll_deadzone:
            clamped = min(abs_y, self.scroll_max_delta)
            amount = int(1 + (clamped - self.scroll_deadzone) / (self.scroll_max_delta - self.scroll_deadzone) * 4)

            if diff_y > 0:
                self.mouse.scroll(0, amount)
                action = f"SCROLL_UP (+{amount})"
            else:
                self.mouse.scroll(0, -amount)
                action = f"SCROLL_DOWN (-{amount})"

            self.prev_palm_y = palm_y
            self.prev_palm_x = palm_x

        elif abs_x > abs_y and abs_x > self.scroll_deadzone:
            clamped = min(abs_x, self.scroll_max_delta)
            amount = int(1 + (clamped - self.scroll_deadzone) / (self.scroll_max_delta - self.scroll_deadzone) * 4)

            # Swing Right -> Scroll Down (like page down), Swing Left -> Scroll Up
            if diff_x > 0:
                self.mouse.scroll(0, -amount)
                action = f"SWING_RIGHT -> SCROLL_DOWN (-{amount})"
            else:
                self.mouse.scroll(0, amount)
                action = f"SWING_LEFT -> SCROLL_UP (+{amount})"

            self.prev_palm_x = palm_x
            self.prev_palm_y = palm_y
        else:
            # Subtle anchor decay while hand is resting
            self.prev_palm_x += (palm_x - self.prev_palm_x) * 0.1
            self.prev_palm_y += (palm_y - self.prev_palm_y) * 0.1

        return action
