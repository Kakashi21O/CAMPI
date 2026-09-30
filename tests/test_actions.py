from actions import ActionController


def test_action_controller_initial_state():
    act = ActionController()
    assert not act.control_enabled
    assert act.prev_palm_x is None
    assert act.prev_palm_y is None


def test_action_controller_safety_cutoff():
    act = ActionController()
    act.enable_control()
    assert act.control_enabled
    act.disable_control()
    assert not act.control_enabled


def test_action_controller_state_stability():
    act = ActionController()
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
    act = ActionController()
    # Control is off
    assert act.handle_scroll((0.5, 0.4)) is None


def test_actions_vertical_scroll():
    act = ActionController()
    act.enable_control()
    # Baseline
    act.handle_scroll((0.50, 0.50))

    # Hand moves UP (Y decreases)
    up_act = act.handle_scroll((0.50, 0.40))
    assert up_act is not None and "SCROLL_UP" in up_act

    # Hand moves DOWN (Y increases)
    down_act = act.handle_scroll((0.50, 0.52))
    assert down_act is not None and "SCROLL_DOWN" in down_act


def test_actions_swing_scroll():
    act = ActionController()
    act.enable_control()
    # Baseline
    act.handle_scroll((0.50, 0.50))

    # Swing Right (X increases) -> Scroll Down
    right_act = act.handle_scroll((0.62, 0.50))
    assert right_act is not None and "SCROLL_DOWN" in right_act

    # Swing Left (X decreases) -> Scroll Up
    left_act = act.handle_scroll((0.40, 0.50))
    assert left_act is not None and "SCROLL_UP" in left_act
