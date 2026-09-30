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
