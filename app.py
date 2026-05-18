import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import mediapipe as mp
import numpy as np
import time

# ---------------- PAGE ----------------

st.set_page_config(
    page_title="PoseAI Pro",
    page_icon="🏋️",
    layout="centered"
)

# ---------------- CSS ----------------

st.markdown("""

<style>

/* ---------------- APP ---------------- */

.stApp {

    background:
    linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #111827
    );

    color: white;
}

/* ---------------- REMOVE HEADER ---------------- */

header {

    visibility: hidden;
}

/* ---------------- MAIN CONTAINER ---------------- */

.block-container {

    padding-top: 1rem !important;

    max-width: 100% !important;

    text-align: center;
}

/* ---------------- TITLE ---------------- */

.main-title {

    text-align: center;

    font-size: 50px;

    font-weight: 600;

    background:
    linear-gradient(
        90deg,
        #38bdf8,
        #06b6d4
    );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

    margin-bottom: 5px;
}

/* ---------------- SUBTITLE ---------------- */

.subtitle {

    text-align: center;

    color: #94a3b8;

    font-size: 18px;

    margin-bottom: 25px;
}

/* ---------------- STREAMLIT WEBRTC ---------------- */

[data-testid="stVideo"] {

    display: flex !important;

    justify-content: center !important;

    width: 100% !important;
}

/* ---------------- VIDEO WRAPPER ---------------- */

[data-testid="stVideo"] {

    width: 420px !important;

    margin: auto !important;
}

video {

    width: 420px !important;

    height: 240px !important;

    object-fit: cover !important;

    border-radius: 18px !important;
}

/* ---------------- BUTTON ---------------- */

button {

    border-radius: 12px !important;

    margin-top: 10px !important;
}

</style>

""", unsafe_allow_html=True)

# ---------------- TITLE ----------------

st.markdown(
    '<div class="main-title">🏋️ PoseAI Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Real-Time Body Posture & Squat Detection</div>',
    unsafe_allow_html=True
)

# ---------------- LAYOUT ----------------

left_col = st.container()

# ---------------- MEDIAPIPE ----------------

mp_pose = mp.solutions.pose

mp_drawing = mp.solutions.drawing_utils

# ---------------- ANGLE FUNCTION ----------------

def calculate_angle(a, b, c):

    a = np.array(a)

    b = np.array(b)

    c = np.array(c)

    radians = np.arctan2(
        c[1] - b[1],
        c[0] - b[0]
    ) - np.arctan2(
        a[1] - b[1],
        a[0] - b[0]
    )

    angle = np.abs(
        radians * 180.0 / np.pi
    )

    if angle > 180:

        angle = 360 - angle

    return angle

# ---------------- VIDEO PROCESSOR ----------------

class PoseProcessor(VideoProcessorBase):

    def __init__(self):

        self.pose = mp_pose.Pose(

            min_detection_confidence=0.6,

            min_tracking_confidence=0.6
        )

        self.counter = 0

        self.stage = "UP"

        self.last_squat_time = 0

        self.previous_avg_angle = 180

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        img = cv2.flip(img, 1)

        rgb = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        results = self.pose.process(rgb)

        status = "READY"

        try:

            if results.pose_landmarks:

                landmarks = results.pose_landmarks.landmark

                # ---------------- LEFT LEG ----------------

                left_hip = [

                    landmarks[
                        mp_pose.PoseLandmark.LEFT_HIP.value
                    ].x,

                    landmarks[
                        mp_pose.PoseLandmark.LEFT_HIP.value
                    ].y
                ]

                left_knee = [

                    landmarks[
                        mp_pose.PoseLandmark.LEFT_KNEE.value
                    ].x,

                    landmarks[
                        mp_pose.PoseLandmark.LEFT_KNEE.value
                    ].y
                ]

                left_ankle = [

                    landmarks[
                        mp_pose.PoseLandmark.LEFT_ANKLE.value
                    ].x,

                    landmarks[
                        mp_pose.PoseLandmark.LEFT_ANKLE.value
                    ].y
                ]

                # ---------------- RIGHT LEG ----------------

                right_hip = [

                    landmarks[
                        mp_pose.PoseLandmark.RIGHT_HIP.value
                    ].x,

                    landmarks[
                        mp_pose.PoseLandmark.RIGHT_HIP.value
                    ].y
                ]

                right_knee = [

                    landmarks[
                        mp_pose.PoseLandmark.RIGHT_KNEE.value
                    ].x,

                    landmarks[
                        mp_pose.PoseLandmark.RIGHT_KNEE.value
                    ].y
                ]

                right_ankle = [

                    landmarks[
                        mp_pose.PoseLandmark.RIGHT_ANKLE.value
                    ].x,

                    landmarks[
                        mp_pose.PoseLandmark.RIGHT_ANKLE.value
                    ].y
                ]

                # ---------------- VISIBILITY ----------------

                left_visibility = landmarks[
                    mp_pose.PoseLandmark.LEFT_KNEE.value
                ].visibility

                right_visibility = landmarks[
                    mp_pose.PoseLandmark.RIGHT_KNEE.value
                ].visibility

                # ---------------- ANGLES ----------------

                left_angle = int(
                    calculate_angle(
                        left_hip,
                        left_knee,
                        left_ankle
                    )
                )

                right_angle = int(
                    calculate_angle(
                        right_hip,
                        right_knee,
                        right_ankle
                    )
                )

                # ---------------- AVG ANGLE ----------------

                raw_avg_angle = (
                    left_angle + right_angle
                ) / 2

                avg_angle = (

                    self.previous_avg_angle * 0.7

                    +

                    raw_avg_angle * 0.3
                )

                self.previous_avg_angle = avg_angle

                current_time = time.time()

                # ---------------- SQUAT DETECTION ----------------

                if (

                    left_visibility > 0.65

                    and

                    right_visibility > 0.65
                ):

                    # STAND

                    if avg_angle > 155:

                        self.stage = "UP"

                    # GO DOWN

                    if (

                        avg_angle < 95

                        and self.stage == "UP"
                    ):

                        self.stage = "DOWN"

                    # COMPLETE REP

                    if (

                        avg_angle > 145

                        and self.stage == "DOWN"

                        and current_time -
                        self.last_squat_time > 1
                    ):

                        self.counter += 1

                        self.last_squat_time = current_time

                        self.stage = "UP"

                    # STATUS

                    if avg_angle < 90:

                        status = "PERFECT"

                    elif avg_angle < 120:

                        status = "GOOD"

                    else:

                        status = "READY"

                # ---------------- DRAW BODY ----------------

                mp_drawing.draw_landmarks(

                    img,

                    results.pose_landmarks,

                    mp_pose.POSE_CONNECTIONS
                )

                # ---------------- AI PANEL ----------------

                cv2.rectangle(
                    img,
                    (0,0),
                    (145,130),
                    (15,23,42),
                    -1
                )

                cv2.putText(
                    img,
                    f"Squats: {self.counter}",
                    (10,25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (56,189,248),
                    2
                )

                cv2.putText(
                    img,
                    f"Left Knee: {left_angle}",
                    (10,55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255,255,255),
                    1
                )

                cv2.putText(
                    img,
                    f"Right Knee: {right_angle}",
                    (10,80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255,255,255),
                    1
                )

                cv2.putText(
                    img,
                    f"Status: {status}",
                    (10,105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0,255,0),
                    1
                )

        except Exception as e:

            print(e)

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24"
        )

# ---------------- CAMERA ----------------

with left_col:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        webrtc_streamer(

            key="poseai",

            video_processor_factory=PoseProcessor,

            media_stream_constraints={
                "video": True,
                "audio": False
            },

            async_processing=True
        )