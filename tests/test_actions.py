from actions import ActionController


def test_action_controller_initial_state():
    act = ActionController(screen_w=1920, screen_h=1080)
    assert not act.control_enabled
    assert act.prev_palm_y is None
    assert not act.is_pinched


def test_action_controller_safety_cutoff():
    act = ActionController(screen_w=1920, screen_h=1080)
    act.enable_control()
    assert act.control_enabled
    act.disable_control()
    assert not act.control_enabled


def test_action_controller_state_stability():
    act = ActionController(screen_w=1920, screen_h=1080)
    # Needs stable_threshold frames (3)
    assert act.update_state("OPEN_PALM") == "IDLE"
    assert act.update_state("OPEN_PALM") == "IDLE"
    assert act.update_state("OPEN_PALM") == "CONTROL_ENABLED"
    assert act.control_enabled

    # Fist to disable
    assert act.update_state("FIST") == "IDLE"
    assert act.update_state("FIST") == "IDLE"
    assert act.update_state("FIST") == "CONTROL_DISABLED"
    assert not act.control_enabled


def test_actions_disabled_when_control_off():
    act = ActionController(screen_w=1920, screen_h=1080)
    # Control is off
    assert act.handle_click(True) is None
    assert act.handle_scroll(0.4) is None


def test_actions_scroll_up_and_down():
    act = ActionController(screen_w=1920, screen_h=1080)
    act.enable_control()
    # Baseline
    act.handle_scroll(0.50)
    # Hand moves UP (palm Y decreases from 0.50 to 0.40)
    up_action = act.handle_scroll(0.40)
    assert up_action is not None and "SCROLL_UP" in up_action

    # Hand moves DOWN (palm Y increases from 0.40 to 0.52)
    down_action = act.handle_scroll(0.52)
    assert down_action is not None and "SCROLL_DOWN" in down_action
