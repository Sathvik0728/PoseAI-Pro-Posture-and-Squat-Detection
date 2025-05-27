# Real-Time Body Posture Detection

## Overview
This project uses a webcam to detect and visualize human body posture in real-time, leveraging OpenCV for video capture and MediaPipe for pose estimation. It identifies 33 key landmarks on the body (e.g., shoulders, elbows, hips, knees) and displays them as dots with skeletal connections. The system is ideal for applications like fitness tracking, posture correction, and interactive systems.

## Prerequisites
- Python 3.8+ installed on your system
- A functional webcam (default device, index 0) to capture live video
- Required Python libraries:
  - `opencv-python` (for webcam access and video display)
  - `mediapipe` (for body landmark detection and visualization)
- Install dependencies manually:
  ```bash
  pip install opencv-python mediapipe
  ```

## How to Run
1. Ensure your webcam is connected and functional.
2. Save the project code in a file named `body_posture.py`.
3. Open a terminal or command prompt.
4. Navigate to the directory containing the project file.
5. Install the required libraries (see Prerequisites).
6. Run the program:
   ```bash
   python body_posture.py
   ```
7. The webcam will activate, displaying a live feed with body landmarks overlaid.
8. Press the `ESC` key to exit.

## Application Flow
- The program opens the default webcam using OpenCV to capture live video.
- Each frame is converted from BGR to RGB for MediaPipe compatibility.
- MediaPipe’s Pose model detects a human body and identifies 33 landmarks (x, y, z coordinates).
- Landmarks (e.g., shoulders, knees) and skeletal connections (e.g., elbow to wrist) are drawn on the frame using default styles.
- The processed frame is flipped horizontally for a mirror-like effect and displayed in a window named "MediaPipe Pose".
- The loop continues until the `ESC` key is pressed, with resources cleaned up on exit.

## Code Structure
- **Imports**: `cv2` (OpenCV) for webcam video capture/display, `mediapipe` for pose detection.
- **MediaPipe Setup**: Initializes `mp.solutions.drawing_utils`, `mp.solutions.drawing_styles`, `mp.solutions.pose` for landmark detection and visualization.
- **Webcam Capture**: Uses `cv2.VideoCapture(0)` to access the default webcam.
- **Pose Model**: Configures `Pose()` with 50% confidence thresholds for detection and tracking.
- **Processing Loop**: Reads webcam frames, preprocesses (color conversion), detects body landmarks, draws visualizations, and displays output.
- **Exit and Cleanup**: Terminates on `ESC` key press and releases webcam resources.

## Example Output
```
[Webcam Window: "MediaPipe Pose"]
- Displays live webcam feed
- Overlays 33 landmarks on detected body (dots at shoulders, elbows, hips, etc.)
- Draws skeletal lines connecting landmarks (e.g., shoulder to elbow, hip to knee)
```

## Limitations
- Requires a functional webcam; fails if no camera is detected.
- Detects only one person at a time (MediaPipe Pose limitation).
- Performance may degrade with occlusion (e.g., hidden body parts) or poor lighting.
- No posture analysis (e.g., detecting slouching or specific poses).
- Uses default visualization styles without customization.

## Potential Improvements
- Add webcam availability check:
  ```python
  if not cap.isOpened():
      print("Error: Webcam not detected")
      exit()
  ```
- Implement posture analysis (e.g., calculate shoulder-hip angles for slouching detection).
- Support multiple people by extending the model or using alternative solutions.
- Customize visualization (e.g., change landmark colors via `mp_drawing_styles`).
- Save output video for analysis:
  ```python
  out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
  out.write(image)
  out.release()
  ```

## License
This project is unlicensed and free to use or modify.