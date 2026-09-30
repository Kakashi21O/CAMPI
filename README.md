# CAMPI — Camera Gesture Control (V1)

Minimal, reliable camera gesture control system built with Python, OpenCV, MediaPipe, and pynput following the Ponytail philosophy (simple, boring, minimal code).

## Controls

* **Q**: Quit application
* **ESC**: Immediately disable gesture control (safety cutoff)
* **🖐 Open Palm**: Enable gesture control (`CONTROL: ON`)
* **✊ Closed Fist**: Disable gesture control (`CONTROL: OFF`)
* **Hand Up**: Scroll Up
* **Hand Down**: Scroll Down
* **☝ Index Finger**: Cursor control
* **Pinch (Thumb + Index)**: Single Left Click

## Supported Gestures

| Gesture | Action |
|---|---|
| 🖐 Open Palm | Start / Enable Control |
| ✊ Closed Fist | Stop / Disable Control |
| ⬆ Hand Up | Scroll Up |
| ⬇ Hand Down | Scroll Down |
| ☝ Index Tip | Move Cursor |
| 🤏 Pinch | Left Click |

## Requirements

* Python 3.9+
* Webcam
* Dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Usage

```bash
python main.py
```

### Debug Mode

In `main.py`:
```python
DEBUG = False  # Set to True for debug overlay & metrics
```

## Troubleshooting

* **Camera not opening**: Check `CAMERA_INDEX` in `camera.py` (default: 0). Ensure no other application is using the camera.
* **Input control blocked**: On macOS or specific Windows configurations, accessibility / input simulation permissions may be required.
