import cv2
import mediapipe as mp
import pyautogui
import time


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
print("  HandLingo | Media Controller")
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
print(" [*] Open Palm: Play/Pause | Swipe Right: Next | Swipe Left: Prev | 'Q' quits.\n")


# =========================================================
# SETTINGS
# =========================================================

WINDOW_NAME = "HandLingo - Media Controller"

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

SWIPE_DISTANCE = 100
SWIPE_COOLDOWN = 1.0

PLAY_PAUSE_COOLDOWN = 1.0


# =========================================================
# VARIABLES
# =========================================================

previous_x = None
last_swipe_time = 0
last_play_pause_time = 0


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
    global last_play_pause_time

    while True:

        # =================================================
        # CAMERA
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

            index = hand.landmark[8]

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
            # INDEX FINGERTIP
            # =================================================

            cv2.circle(
                frame,
                (index_x, index_y),
                10,
                (60, 60, 255),
                -1
            )


            # =================================================
            # FINGER STATE
            # =================================================

            finger_state = fingers_up(hand)

            index_up = finger_state[0]
            middle_up = finger_state[1]
            ring_up = finger_state[2]
            pinky_up = finger_state[3]


            current_time = time.time()


            # =================================================
            # OPEN PALM → PLAY / PAUSE
            # =================================================

            if (
                index_up
                and middle_up
                and ring_up
                and pinky_up
            ):

                status = "PLAY / PAUSE"
                status_color = (90, 220, 130)

                if (
                    current_time - last_play_pause_time
                    > PLAY_PAUSE_COOLDOWN
                ):

                    pyautogui.press("playpause")

                    last_play_pause_time = current_time

                    print("Play / Pause")

                previous_x = None


            # =================================================
            # INDEX FINGER → SWIPE
            # =================================================

            elif (
                index_up
                and not middle_up
                and not ring_up
                and not pinky_up
            ):

                status = "MEDIA CONTROL"
                status_color = (255, 200, 80)


                # ---------------------------------------------
                # SWIPE DETECTION
                # ---------------------------------------------

                if previous_x is not None:

                    movement = index_x - previous_x

                    if (
                        abs(movement) > SWIPE_DISTANCE
                        and
                        current_time - last_swipe_time
                        > SWIPE_COOLDOWN
                    ):

                        # RIGHT → NEXT TRACK

                        if movement > 0:

                            pyautogui.press(
                                "nexttrack"
                            )

                            status = "NEXT TRACK"
                            status_color = (90, 220, 130)

                            print("Next Track")


                        # LEFT → PREVIOUS TRACK

                        else:

                            pyautogui.press(
                                "prevtrack"
                            )

                            status = "PREVIOUS TRACK"
                            status_color = (90, 220, 130)

                            print("Previous Track")


                        last_swipe_time = current_time


                previous_x = index_x


            # =================================================
            # OTHER HAND POSITION
            # =================================================

            else:

                status = "HAND DETECTED"
                status_color = (90, 220, 130)

                previous_x = None


        # =================================================
        # NO HAND
        # =================================================

        else:

            previous_x = None


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
            "MEDIA CONTROL",
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
            "Open Palm  :  Play / Pause",
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
            "Swipe Right  :  Next Track",
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
            "Swipe Left  :  Previous Track",
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


    # =================================================
    # CLEANUP
    # =================================================

    camera.release()

    cv2.destroyAllWindows()

    hands.close()

    print(
        "HandLingo Media Controller stopped."
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()