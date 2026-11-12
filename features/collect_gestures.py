
import cv2
import mediapipe as mp
import csv
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
CSV_PATH = os.path.join(DATASET_DIR, "landmarks.csv")

os.makedirs(DATASET_DIR, exist_ok=True)

LABEL = input("Enter alphabet (A-Z): ").upper()

if len(LABEL) != 1 or LABEL not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    raise ValueError("Enter a valid alphabet.")

TARGET = 100
INTERVAL = 0.2

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam.")

count = 0
last_capture = 0

file_exists = os.path.exists(CSV_PATH)

try:
    with open(CSV_PATH, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                ["label"] +
                [f"x{i}" for i in range(21)] +
                [f"y{i}" for i in range(21)] +
                [f"z{i}" for i in range(21)]
            )

        print(f"Show the ASL gesture for {LABEL}.")
        print("Collection starts automatically.")

        while count < TARGET:
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                landmark = results.multi_hand_landmarks[0]

                mp_draw.draw_landmarks(
                    frame, landmark, mp_hands.HAND_CONNECTIONS
                )

                if time.time() - last_capture >= INTERVAL:
                    points = landmark.landmark

                    xs = [p.x for p in points]
                    ys = [p.y for p in points]
                    zs = [p.z for p in points]

                    writer.writerow([LABEL] + xs + ys + zs)
                    file.flush()

                    count += 1
                    last_capture = time.time()

            cv2.putText(
                frame, f"Letter: {LABEL} | Samples: {count}/{TARGET}",
                (10, 35), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 255, 0), 2
            )

            cv2.putText(
                frame, "Hold gesture steady | Q = Quit",
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2
            )

            cv2.imshow("HandLingo Auto Collection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    cap.release()
    hands.close()
    cv2.destroyAllWindows()

print(f"Saved {count} samples for letter {LABEL}.")
