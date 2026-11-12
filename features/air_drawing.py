import cv2
import mediapipe as mp
import numpy as np
import time


# =========================================================
# HANDLINGO COLORS
# =========================================================

RED = (60, 60, 255)
WHITE = (245, 245, 245)
GRAY = (145, 145, 145)
GREEN = (90, 220, 130)
YELLOW = (0, 220, 255)
DARK = (18, 18, 21)
DARKER = (12, 12, 14)


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
print("  HandLingo | Air Drawing")
print("=" * 60)
print(" [*] Connecting to camera...")

camera = None
for attempt in range(8):
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        ret, test_frame = camera.read()
        if ret:
            print(" [✓] Camera ready!")
            break
        camera.release()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if camera.isOpened():
        ret, test_frame = camera.read()
        if ret:
            print(" [✓] Camera ready via DirectShow!")
            break
        camera.release()
    time.sleep(0.3)

if camera is None or not camera.isOpened():
    print("\n [!] ERROR: Camera could not be opened.")
    print("     Make sure no other application or browser tab is using it.")
    time.sleep(4)
    exit(1)

print(" [*] Hand tracking active!")
print(" [*] Index finger draws | Thumb erases | 'C' clears | 'Q' quits.\n")


# =========================================================
# WINDOW
# =========================================================

WINDOW_NAME = "HandLingo | Air Drawing"

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
# DRAWING SETTINGS
# =========================================================

canvas = None

previous_x = None
previous_y = None

brush_size = 6
eraser_size = 45


# =========================================================
# FINGER DETECTION
# =========================================================

def finger_up(hand, tip, pip):

    return hand.landmark[tip].y < hand.landmark[pip].y


# =========================================================
# RESET DRAWING POSITION
# =========================================================

def reset_position():

    global previous_x, previous_y

    previous_x = None
    previous_y = None


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    success, frame = camera.read()

    if not success or frame is None:
        time.sleep(0.02)
        continue

    frame = cv2.resize(frame, (1280, 720))

    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape


    # Create canvas

    if canvas is None:
        canvas = np.zeros_like(frame)


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

    mode = "IDLE"


    # =====================================================
    # HAND DETECTION
    # =====================================================

    if hand_detected:

        hand = result.multi_hand_landmarks[0]


        # -------------------------------------------------
        # FINGERS
        # -------------------------------------------------

        index_up = finger_up(
            hand,
            8,
            6
        )

        middle_up = finger_up(
            hand,
            12,
            10
        )

        ring_up = finger_up(
            hand,
            16,
            14
        )

        pinky_up = finger_up(
            hand,
            20,
            18
        )


        # -------------------------------------------------
        # INDEX POSITION
        # -------------------------------------------------

        index_x = int(
            hand.landmark[8].x * width
        )

        index_y = int(
            hand.landmark[8].y * height
        )


        # -------------------------------------------------
        # THUMB POSITION
        # -------------------------------------------------

        thumb_x = int(
            hand.landmark[4].x * width
        )

        thumb_y = int(
            hand.landmark[4].y * height
        )


        # =================================================
        # DRAW MODE
        # =================================================

        if (
            index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        ):

            mode = "DRAW"


            if previous_x is not None:

                cv2.line(
                    canvas,
                    (
                        previous_x,
                        previous_y
                    ),
                    (
                        index_x,
                        index_y
                    ),
                    RED,
                    brush_size,
                    cv2.LINE_AA
                )


            previous_x = index_x
            previous_y = index_y


            # Drawing cursor

            cv2.circle(
                frame,
                (
                    index_x,
                    index_y
                ),
                8,
                RED,
                -1
            )


        # =================================================
        # THUMB / ERASER
        # =================================================

        elif (
            not index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        ):

            # Check thumb extension

            thumb_extended = (
                abs(
                    thumb_x -
                    int(hand.landmark[3].x * width)
                ) > 15
            )

            if thumb_extended:

                mode = "ERASER"

                reset_position()


                cv2.circle(
                    canvas,
                    (
                        thumb_x,
                        thumb_y
                    ),
                    eraser_size,
                    (0, 0, 0),
                    -1
                )


                # Eraser cursor

                cv2.circle(
                    frame,
                    (
                        thumb_x,
                        thumb_y
                    ),
                    eraser_size,
                    YELLOW,
                    2
                )

            else:

                reset_position()


        else:

            reset_position()


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
        box_color = RED if mode == "DRAW" else (YELLOW if mode == "ERASER" else GREEN)
        cv2.rectangle(
            frame,
            (x_min, y_min),
            (x_max, y_max),
            box_color,
            2
        )

        cv2.putText(
            frame,
            f"AIR DRAW: {mode}",
            (x_min, max(24, y_min - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            box_color,
            1,
            cv2.LINE_AA
        )


        # =================================================
        # LANDMARKS
        # =================================================

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


    else:

        reset_position()


    # =====================================================
    # COMBINE CAMERA + DRAWING
    # =====================================================

    gray_canvas = cv2.cvtColor(
        canvas,
        cv2.COLOR_BGR2GRAY
    )

    _, mask = cv2.threshold(
        gray_canvas,
        10,
        255,
        cv2.THRESH_BINARY
    )

    inverse_mask = cv2.bitwise_not(mask)


    camera_part = cv2.bitwise_and(
        frame,
        frame,
        mask=inverse_mask
    )

    drawing_part = cv2.bitwise_and(
        canvas,
        canvas,
        mask=mask
    )

    output = cv2.add(
        camera_part,
        drawing_part
    )


    # =====================================================
    # HANDLINGO TOOLBAR
    # =====================================================

    toolbar_width = 330
    toolbar_height = 205

    toolbar_x = 22
    toolbar_y = height - toolbar_height - 22


    # Shadow

    cv2.rectangle(
        output,
        (
            toolbar_x + 4,
            toolbar_y + 4
        ),
        (
            toolbar_x + toolbar_width + 4,
            toolbar_y + toolbar_height + 4
        ),
        (5, 5, 5),
        -1
    )


    # Main panel

    cv2.rectangle(
        output,
        (
            toolbar_x,
            toolbar_y
        ),
        (
            toolbar_x + toolbar_width,
            toolbar_y + toolbar_height
        ),
        DARK,
        -1
    )


    # Border

    cv2.rectangle(
        output,
        (
            toolbar_x,
            toolbar_y
        ),
        (
            toolbar_x + toolbar_width,
            toolbar_y + toolbar_height
        ),
        (55, 55, 60),
        1
    )


    # Red accent

    cv2.rectangle(
        output,
        (
            toolbar_x,
            toolbar_y + 18
        ),
        (
            toolbar_x + 4,
            toolbar_y + toolbar_height - 18
        ),
        RED,
        -1
    )


    # =====================================================
    # TITLE
    # =====================================================

    cv2.putText(
        output,
        "HandLingo",
        (
            toolbar_x + 20,
            toolbar_y + 30
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        WHITE,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        "AIR DRAWING",
        (
            toolbar_x + 20,
            toolbar_y + 52
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        GRAY,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # STATUS
    # =====================================================

    if mode == "DRAW":

        status = "DRAWING"
        status_color = RED

    elif mode == "ERASER":

        status = "ERASER"
        status_color = YELLOW

    elif hand_detected:

        status = "HAND DETECTED"
        status_color = GREEN

    else:

        status = "SHOW YOUR HAND"
        status_color = GRAY


    cv2.putText(
        output,
        "●  " + status,
        (
            toolbar_x + 20,
            toolbar_y + 77
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        status_color,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # BRUSH INFORMATION
    # =====================================================

    cv2.putText(
        output,
        f"Brush       {brush_size}px",
        (
            toolbar_x + 20,
            toolbar_y + 105
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        WHITE,
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        output,
        f"Eraser      {eraser_size}px",
        (
            toolbar_x + 20,
            toolbar_y + 127
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        WHITE,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # CONTROLS
    # =====================================================

    cv2.putText(
        output,
        "INDEX  Draw",
        (
            toolbar_x + 20,
            toolbar_y + 154
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        GRAY,
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        output,
        "THUMB  Erase",
        (
            toolbar_x + 20,
            toolbar_y + 176
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        GRAY,
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        output,
        "C Clear",
        (
            toolbar_x + 200,
            toolbar_y + 154
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        WHITE,
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        output,
        "Q Close",
        (
            toolbar_x + 200,
            toolbar_y + 176
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34,
        WHITE,
        1,
        cv2.LINE_AA
    )


    # =====================================================
    # DISPLAY
    # =====================================================

    cv2.imshow(
        WINDOW_NAME,
        output
    )


    # =====================================================
    # KEYBOARD
    # =====================================================

    key = cv2.waitKey(1) & 0xFF


    # Clear drawing

    if key == ord("c"):

        canvas = np.zeros_like(frame)

        reset_position()


    # Close

    if key == ord("q"):

        break


# =========================================================
# CLEANUP
# =========================================================

camera.release()

cv2.destroyAllWindows()

hands.close()

print("HandLingo Air Drawing stopped.")