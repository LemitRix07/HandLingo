import cv2
import mediapipe as mp
import pyautogui
import time
import math


pyautogui.FAILSAFE = False


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
print("  HandLingo | Presentation Controller")
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
print(" [*] Pointer: Index finger | Click: Pinch | Slides: Swipe left/right | 'Q' quits.\n")


# =========================================================
# SETTINGS
# =========================================================

WINDOW_NAME = "HandLingo - Presentation Controller"

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

# Swipe
SWIPE_DISTANCE = 100
SWIPE_COOLDOWN = 1.0

# Zoom
ZOOM_STEP_DISTANCE = 20
ZOOM_COOLDOWN = 0.35

# Pointer
POINTER_COOLDOWN = 0.15

# Click
CLICK_DISTANCE = 35
CLICK_COOLDOWN = 0.6


# =========================================================
# VARIABLES
# =========================================================

previous_x = None
last_swipe_time = 0

last_zoom_distance = None
last_zoom_time = 0

last_pointer_time = 0

pinch_active = False
last_click_time = 0


# =========================================================
# FINGER DETECTION
# =========================================================

def fingers_up(hand):

    fingers = []

    # INDEX
    if hand.landmark[8].y < hand.landmark[6].y:
        fingers.append(1)
    else:
        fingers.append(0)

    # MIDDLE
    if hand.landmark[12].y < hand.landmark[10].y:
        fingers.append(1)
    else:
        fingers.append(0)

    # RING
    if hand.landmark[16].y < hand.landmark[14].y:
        fingers.append(1)
    else:
        fingers.append(0)

    # PINKY
    if hand.landmark[20].y < hand.landmark[18].y:
        fingers.append(1)
    else:
        fingers.append(0)

    return fingers


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
# MAIN
# =========================================================

def main():

    global previous_x
    global last_swipe_time
    global last_zoom_distance
    global last_zoom_time
    global last_pointer_time
    global pinch_active
    global last_click_time

    while True:

        # =================================================
        # CAMERA FRAME
        # =================================================

        success, frame = camera.read()

        if not success or frame is None:
            time.sleep(0.02)
            continue

        frame = cv2.resize(frame, (1280, 720))

        frame = cv2.flip(frame, 1)

        height, width, _ = frame.shape


        # =================================================
        # MEDIAPIPE
        # =================================================

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = hands.process(rgb)

        hand_detected = (
            result.multi_hand_landmarks is not None
        )


        # =================================================
        # DEFAULT STATUS
        # =================================================

        status = "SHOW YOUR HAND"
        status_color = (150, 150, 150)


        # =================================================
        # HAND DETECTED
        # =================================================

        if hand_detected:

            hand = result.multi_hand_landmarks[0]


            # =================================================
            # LANDMARKS
            # =================================================

            thumb = hand.landmark[4]
            index = hand.landmark[8]

            thumb_x = int(thumb.x * width)
            thumb_y = int(thumb.y * height)

            index_x = int(index.x * width)
            index_y = int(index.y * height)


            # =================================================
            # HAND BOUNDING BOX & TRACING
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
                (60, 60, 255),
                2
            )

            cv2.putText(
                frame,
                "HAND TRACKING",
                (x_min, max(24, y_min - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (90, 220, 130),
                1,
                cv2.LINE_AA
            )


            # =================================================
            # DRAW HAND
            # =================================================

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )


            # =================================================
            # FINGERTIP MARKERS
            # =================================================

            cv2.circle(
                frame,
                (thumb_x, thumb_y),
                8,
                (255, 255, 255),
                -1
            )

            cv2.circle(
                frame,
                (index_x, index_y),
                10,
                (60, 60, 255),
                -1
            )


            # =================================================
            # PINCH CLICK DETECTION
            # =================================================

            click_distance = math.sqrt(
                (index_x - thumb_x) ** 2 +
                (index_y - thumb_y) ** 2
            )

            current_time = time.time()

            # Thumb + index close together
            if click_distance < CLICK_DISTANCE:

                if (
                    not pinch_active
                    and current_time - last_click_time
                    > CLICK_COOLDOWN
                ):

                    pyautogui.click()

                    pinch_active = True
                    last_click_time = current_time

                    status = "LEFT CLICK"
                    status_color = (90, 220, 130)

                    print("Left Click")

            # Fingers separated again
            else:

                pinch_active = False


            # =================================================
            # FINGER STATE
            # =================================================

            finger_state = fingers_up(hand)

            index_up = finger_state[0]
            middle_up = finger_state[1]
            ring_up = finger_state[2]
            pinky_up = finger_state[3]


            # =================================================
            # 1. POINTER MODE
            # =================================================

            if (
                index_up
                and not middle_up
                and not ring_up
                and not pinky_up
            ):

                status = "POINTER MODE"
                status_color = (255, 200, 80)


                # Pointer circle

                cv2.circle(
                    frame,
                    (index_x, index_y),
                    22,
                    (60, 60, 255),
                    2
                )

                cv2.circle(
                    frame,
                    (index_x, index_y),
                    4,
                    (60, 60, 255),
                    -1
                )


                # =================================================
                # MOVE ACTUAL MOUSE POINTER
                # =================================================

                current_time = time.time()

                if (
                    current_time - last_pointer_time
                    > POINTER_COOLDOWN
                ):

                    screen_width, screen_height = pyautogui.size()

                    mouse_x = int(
                        index_x / width * screen_width
                    )

                    mouse_y = int(
                        index_y / height * screen_height
                    )

                    pyautogui.moveTo(
                        mouse_x,
                        mouse_y,
                        duration=0.05
                    )

                    last_pointer_time = current_time


                # Reset swipe

                previous_x = None


            # =================================================
            # 2. OPEN PALM
            # =================================================

            elif (
                index_up
                and middle_up
                and ring_up
                and pinky_up
            ):

                status = "READY"
                status_color = (90, 220, 130)

                current_time = time.time()


                # =================================================
                # PINCH / ZOOM DISTANCE
                # =================================================

                zoom_distance = math.sqrt(
                    (index_x - thumb_x) ** 2 +
                    (index_y - thumb_y) ** 2
                )


                # =================================================
                # DRAW PINCH LINE
                # =================================================

                cv2.line(
                    frame,
                    (thumb_x, thumb_y),
                    (index_x, index_y),
                    (60, 60, 255),
                    3
                )


                # =================================================
                # ZOOM CONTROL
                # =================================================

                if last_zoom_distance is not None:

                    distance_change = (
                        zoom_distance -
                        last_zoom_distance
                    )

                    if (
                        abs(distance_change)
                        >= ZOOM_STEP_DISTANCE
                        and
                        current_time - last_zoom_time
                        > ZOOM_COOLDOWN
                    ):

                        # Fingers apart → Zoom In

                        if distance_change > 0:

                            pyautogui.hotkey(
                                "ctrl",
                                "+"
                            )

                            status = "ZOOM IN +"
                            status_color = (90, 220, 130)

                            print("Zoom In")


                        # Fingers closer → Zoom Out

                        else:

                            pyautogui.hotkey(
                                "ctrl",
                                "-"
                            )

                            status = "ZOOM OUT -"
                            status_color = (255, 180, 80)

                            print("Zoom Out")


                        last_zoom_time = current_time


                last_zoom_distance = zoom_distance


                # =================================================
                # SWIPE DETECTION
                # =================================================

                if previous_x is not None:

                    movement = index_x - previous_x

                    if (
                        abs(movement) > SWIPE_DISTANCE
                        and
                        current_time - last_swipe_time
                        > SWIPE_COOLDOWN
                    ):

                        # Move Right → Next Slide

                        if movement > 0:

                            pyautogui.press("right")

                            status = "NEXT SLIDE"
                            status_color = (90, 220, 130)

                            print("Next Slide")


                        # Move Left → Previous Slide

                        else:

                            pyautogui.press("left")

                            status = "PREVIOUS SLIDE"
                            status_color = (90, 220, 130)

                            print("Previous Slide")


                        last_swipe_time = current_time


                previous_x = index_x


            # =================================================
            # OTHER HAND POSITION
            # =================================================

            else:

                status = "HAND DETECTED"
                status_color = (90, 220, 130)


        # =================================================
        # NO HAND
        # =================================================

        else:

            previous_x = None
            last_zoom_distance = None
            pinch_active = False


        # =================================================
        # FLOATING HANDLINGO CARD
        # =================================================

        CARD_WIDTH = 360
        CARD_HEIGHT = 190

        CARD_X = 25
        CARD_Y = height - CARD_HEIGHT - 25


        # =================================================
        # SHADOW
        # =================================================

        rounded_rect(
            frame,
            CARD_X + 5,
            CARD_Y + 6,
            CARD_X + CARD_WIDTH + 5,
            CARD_Y + CARD_HEIGHT + 6,
            18,
            (0, 0, 0)
        )


        # =================================================
        # MAIN CARD
        # =================================================

        rounded_rect(
            frame,
            CARD_X,
            CARD_Y,
            CARD_X + CARD_WIDTH,
            CARD_Y + CARD_HEIGHT,
            18,
            (25, 25, 29)
        )


        # =================================================
        # RED ACCENT
        # =================================================

        cv2.rectangle(
            frame,
            (
                CARD_X,
                CARD_Y + 18
            ),
            (
                CARD_X + 4,
                CARD_Y + CARD_HEIGHT - 18
            ),
            (60, 60, 255),
            -1
        )


        # =================================================
        # TITLE
        # =================================================

        cv2.putText(
            frame,
            "PRESENTATION CONTROL",
            (
                CARD_X + 22,
                CARD_Y + 35
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (180, 180, 180),
            1,
            cv2.LINE_AA
        )


        # =================================================
        # STATUS
        # =================================================

        cv2.putText(
            frame,
            status,
            (
                CARD_X + 22,
                CARD_Y + 82
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.70,
            status_color,
            2,
            cv2.LINE_AA
        )


        # =================================================
        # INSTRUCTIONS
        # =================================================

        cv2.putText(
            frame,
            "Left     Right  :  Slides",
            (
                CARD_X + 22,
                CARD_Y + 120
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (170, 170, 170),
            1,
            cv2.LINE_AA
        )


        cv2.putText(
            frame,
            "Index  :  Pointer",
            (
                CARD_X + 22,
                CARD_Y + 145
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (140, 140, 140),
            1,
            cv2.LINE_AA
        )


        cv2.putText(
            frame,
            "Thumb + Index  :  Click",
            (
                CARD_X + 22,
                CARD_Y + 168
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (140, 140, 140),
            1,
            cv2.LINE_AA
        )


        # =================================================
        # CLOSE
        # =================================================

        cv2.putText(
            frame,
            "Q  Close",
            (
                CARD_X + CARD_WIDTH - 72,
                CARD_Y + 168
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (110, 110, 110),
            1,
            cv2.LINE_AA
        )


        # =================================================
        # SHOW CAMERA
        # =================================================

        cv2.imshow(
            WINDOW_NAME,
            frame
        )


        # =================================================
        # KEYBOARD
        # =================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break


    # =========================================================
    # CLEANUP
    # =========================================================

    camera.release()

    cv2.destroyAllWindows()

    hands.close()

    print(
        "HandLingo Presentation Controller stopped."
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()