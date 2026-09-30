from camera import Camera
import pytest


def test_camera_init():
    cam = Camera(index=0, width=640, height=480)
    assert cam.index == 0
    assert cam.width == 640
    assert cam.height == 480
    assert cam.cap is None


def test_camera_read_before_start():
    cam = Camera()
    success, frame = cam.read()
    assert success is False
    assert frame is None


def test_camera_release_unstarted():
    cam = Camera()
    cam.release()
    assert cam.cap is None
