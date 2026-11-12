import cv2
import mediapipe as mp
import math
import numpy as np
import time

from pycaw.pycaw import AudioUtilities


# =========================================================
# HANDLINGO COLORS
# =========================================================

RED = (60, 60, 255)
WHITE = (245, 245, 245)
LIGHT_GRAY = (180, 180, 180)
GRAY = (100, 100, 100)
DARK_CARD = (18, 18, 21)
DARKER = (10, 10, 12)
GREEN = (90, 220, 130)


# =========================================================
# WINDOWS VOLUME
# =========================================================

devices = AudioUtilities.GetSpeakers()
volume = devices.EndpointVolume


# =========================================================
# MEDIAPIPE
# =========================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# =========================================================
# CAMERA
# =========================================================

print("\n" + "=" * 60)
print("  HandLingo | Gesture Volume Control")
print("=" * 60)
print(" [*] Connecting to camera...")

camera = None
for attempt in range(8):
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        ret, test_frame = camera.read()
        if ret:
            print(" [OK] Camera ready!")
            break
        camera.release()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if camera.isOpened():
        ret, test_frame = camera.read()
        if ret:
            print(" [OK] Camera ready via DirectShow!")
            break
        camera.release()
    time.sleep(0.3)

if camera is None or not camera.isOpened():
    print("\n [!] ERROR: Camera could not be opened.")
    print("     Make sure no other application or browser tab is using it.")
    time.sleep(4)
    exit(1)

print(" [*] Tracking hand gesture distance...")
print(" [*] Move thumb & index finger apart or together to change volume.")
print(" [*] Press 'q' in the camera window to close.\n")


# =========================================================
# VOLUME SETTINGS
# =========================================================

MIN_DISTANCE = 35
MAX_DISTANCE = 250

SMOOTHING = 0.08
DEAD_ZONE = 0.5

current_volume = (
    volume.GetMasterVolumeLevelScalar() * 100
)

target_volume = current_volume


# =========================================================
# WINDOW
# =========================================================

WINDOW_NAME = "HandLingo | Gesture Volume Control"

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    WINDOW_NAME,
    1280,
    720
)

try:
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
except Exception:
    pass


# =========================================================
# ROUNDED RECTANGLE
# =========================================================

def rounded_rect(
    img,
    x1,
    y1,
    x2,
    y2,
    radius,
    color
):

    cv2.rectangle(
        img,
        (x1 + radius, y1),
        (x2 - radius, y2),
        color,
        -1
    )

    cv2.rectangle(
        img,
        (x1, y1 + radius),
        (x2, y2 - radius),
        color,
        -1
    )

    cv2.circle(
        img,
        (x1 + radius, y1 + radius),
        radius,
        color,
        -1
    )

    cv2.circle(
        img,
        (x2 - radius, y1 + radius),
        radius,
        color,
        -1
    )

    cv2.circle(
        img,
        (x1 + radius, y2 - radius),
        radius,
        color,
        -1
    )

    cv2.circle(
        img,
        (x2 - radius, y2 - radius),
        radius,
        color,
        -1
    )


# =========================================================
# OUTLINE RECTANGLE
# =========================================================

def rounded_outline(
    img,
    x1,
    y1,
    x2,
    y2,
    radius,
    color,
    thickness=1
):

    # Top
    cv2.line(
        img,
        (x1 + radius, y1),
        (x2 - radius, y1),
        color,
        thickness
    )

    # Bottom
    cv2.line(
        img,
        (x1 + radius, y2),
        (x2 - radius, y2),
        color,
        thickness
    )

    # Left
    cv2.line(
        img,
        (x1, y1 + radius),
        (x1, y2 - radius),
        color,
        thickness
    )

    # Right
    cv2.line(
        img,
        (x2, y1 + radius),
        (x2, y2 - radius),
        color,
        thickness
    )

    # Corners
    cv2.ellipse(
        img,
        (x1 + radius, y1 + radius),
        (radius, radius),
        180,
        0,
        90,
        color,
        thickness
    )

    cv2.ellipse(
        img,
        (x2 - radius, y1 + radius),
        (radius, radius),
        270,
        0,
        90,
        color,
        thickness
    )

    cv2.ellipse(
        img,
        (x1 + radius, y2 - radius),
        (radius, radius),
        90,
        0,
        90,
        color,
        thickness
    )

    cv2.ellipse(
        img,
        (x2 - radius, y2 - radius),
        (radius, radius),
        0,
        0,
        90,
        color,
        thickness
    )


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    success, frame = camera.read()

    if not success or frame is None:
        time.sleep(0.02)
        continue

    frame = cv2.resize(frame, (1280, 720))

    frame = cv2.flip(
        frame,
        1
    )

    height, width, _ = frame.shape


    # =====================================================
    # MEDIAPIPE
    # =====================================================

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    result = hands.process(rgb)

    hand_detected = (
        result.multi_hand_landmarks is not None
    )


    # =====================================================
    # HAND DETECTION
    # =====================================================

    if hand_detected:

        hand = result.multi_hand_landmarks[0]

        thumb = hand.landmark[4]
        index = hand.landmark[8]


        thumb_x = int(
            thumb.x * width
        )

        thumb_y = int(
            thumb.y * height
        )

        index_x = int(
            index.x * width
        )

        index_y = int(
            index.y * height
        )


        # -------------------------------------------------
        # DISTANCE BETWEEN THUMB AND INDEX
        # -------------------------------------------------

        distance = math.sqrt(
            (index_x - thumb_x) ** 2
            +
            (index_y - thumb_y) ** 2
        )


        # -------------------------------------------------
        # DISTANCE → VOLUME
        # -------------------------------------------------

        target_volume = np.interp(
            distance,
            [
                MIN_DISTANCE,
                MAX_DISTANCE
            ],
            [
                0,
                100
            ]
        )


        target_volume = float(
            np.clip(
                target_volume,
                0,
                100
            )
        )


        # -------------------------------------------------
        # SMOOTH VOLUME
        # -------------------------------------------------

        difference = (
            target_volume
            -
            current_volume
        )


        if abs(difference) > DEAD_ZONE:

            current_volume += (
                difference * SMOOTHING
            )


        # -------------------------------------------------
        # APPLY WINDOWS VOLUME
        # -------------------------------------------------

        volume.SetMasterVolumeLevelScalar(
            current_volume / 100,
            None
        )


        # =================================================
        # HAND BOUNDING BOX & FINGER TRACING
        # =================================================

        x_coords = [int(lm.x * width) for lm in hand.landmark]
        y_coords = [int(lm.y * height) for lm in hand.landmark]
        x_min = max(0, min(x_coords) - 20)
        x_max = min(width, max(x_coords) + 20)
        y_min = max(0, min(y_coords) - 20)
        y_max = min(height, max(y_coords) + 20)

        # Tracing bounding box around hand
        cv2.rectangle(
            frame,
            (x_min, y_min),
            (x_max, y_max),
            RED,
            2
        )

        cv2.putText(
            frame,
            f"DISTANCE: {int(distance)}px",
            (x_min, max(24, y_min - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            GREEN,
            1,
            cv2.LINE_AA
        )


        # =================================================
        # HAND LANDMARKS
        # =================================================

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


        # Thumb point

        cv2.circle(
            frame,
            (
                thumb_x,
                thumb_y
            ),
            10,
            WHITE,
            -1
        )


        # Index point

        cv2.circle(
            frame,
            (
                index_x,
                index_y
            ),
            10,
            RED,
            -1
        )


        # Distance line

        cv2.line(
            frame,
            (
                thumb_x,
                thumb_y
            ),
            (
                index_x,
                index_y
            ),
            RED,
            3
        )


    # =====================================================
    # HANDLINGO FLOATING PANEL
    # =====================================================

    CARD_WIDTH = 330
    CARD_HEIGHT = 190

    CARD_X = 24
    CARD_Y = height - CARD_HEIGHT - 24


    # -----------------------------------------------------
    # SHADOW
    # -----------------------------------------------------

    rounded_rect(
        frame,
        CARD_X + 5,
        CARD_Y + 6,
        CARD_X + CARD_WIDTH + 5,
        CARD_Y + CARD_HEIGHT + 6,
        18,
        (0, 0, 0)
    )


    # -----------------------------------------------------
    # MAIN CARD
    # -----------------------------------------------------

    rounded_rect(
        frame,
        CARD_X,
        CARD_Y,
        CARD_X + CARD_WIDTH,
        CARD_Y + CARD_HEIGHT,
        18,
        DARK_CARD
    )


    # -----------------------------------------------------
    # BORDER
    # -----------------------------------------------------

    rounded_outline(
        frame,
        CARD_X,
        CARD_Y,
        CARD_X + CARD_WIDTH,
        CARD_Y + CARD_HEIGHT,
        18,
        (55, 55, 60),
        1
    )


    # -----------------------------------------------------
    # RED SIDE ACCENT
    # -----------------------------------------------------

    cv2.rectangle(
        frame,
        (
            CARD_X,
            CARD_Y + 22
        ),
        (
            CARD_X + 4,
            CARD_Y + CARD_HEIGHT - 22
        ),
        RED,
        -1
    )


    # =====================================================
    # HANDLINGO BRAND
    # =====================================================

    cv2.putText(
        frame,
        "Hand",
        (
            CARD_X + 20,
            CARD_Y + 30
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        WHITE,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "Lingo",
        (
            CARD_X + 78,
            CARD_Y + 30
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        RED,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # FEATURE TITLE
    # =====================================================

    cv2.putText(
        frame,
        "GESTURE VOLUME CONTROL",
        (
            CARD_X + 20,
            CARD_Y + 58
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        LIGHT_GRAY,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # VOLUME NUMBER
    # =====================================================

    cv2.putText(
        frame,
        f"{current_volume:.0f}%",
        (
            CARD_X + 20,
            CARD_Y + 103
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.15,
        WHITE,
        2,
        cv2.LINE_AA
    )


    # =====================================================
    # VOLUME BAR
    # =====================================================

    BAR_X = CARD_X + 20
    BAR_Y = CARD_Y + 120

    BAR_WIDTH = CARD_WIDTH - 40
    BAR_HEIGHT = 10


    # Background

    rounded_rect(
        frame,
        BAR_X,
        BAR_Y,
        BAR_X + BAR_WIDTH,
        BAR_Y + BAR_HEIGHT,
        5,
        (45, 45, 50)
    )


    # Filled amount

    filled = int(
        BAR_WIDTH
        *
        current_volume
        /
        100
    )


    if filled > 5:

        rounded_rect(
            frame,
            BAR_X,
            BAR_Y,
            BAR_X + filled,
            BAR_Y + BAR_HEIGHT,
            5,
            RED
        )


    # =====================================================
    # STATUS
    # =====================================================

    if hand_detected:

        status = "●  HAND DETECTED"
        status_color = GREEN

    else:

        status = "○  SHOW YOUR HAND"
        status_color = LIGHT_GRAY


    cv2.putText(
        frame,
        status,
        (
            CARD_X + 20,
            CARD_Y + 155
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        status_color,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # INSTRUCTION
    # =====================================================

    cv2.putText(
        frame,
        "Move thumb + index finger",
        (
            CARD_X + 20,
            CARD_Y + 177
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.30,
        GRAY,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # CAMERA WINDOW
    # =====================================================

    cv2.imshow(
        WINDOW_NAME,
        frame
    )


    # =====================================================
    # EXIT
    # =====================================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


# =========================================================
# CLEANUP
# =========================================================

camera.release()

cv2.destroyAllWindows()

hands.close()

print("HandLingo Volume Control stopped.")