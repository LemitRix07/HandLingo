
import cv2
import mediapipe as mp
import pickle
import os
import numpy as np
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sign_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Trained model not found. Train the model first.")

with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Cannot open webcam.")

predicted_letter = ""
confidence = 0
last_prediction = ""

while True:
    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    predicted_letter = "No hand detected"
    confidence = 0

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            points = hand_landmarks.landmark

            xs = [p.x for p in points]
            ys = [p.y for p in points]
            zs = [p.z for p in points]

            features = np.array([xs + ys + zs])

            probabilities = model.predict_proba(features)[0]
            best_index = np.argmax(probabilities)

            confidence = probabilities[best_index]
            last_prediction = model.classes_[best_index]

            if confidence >= 0.75:
                
                predicted_letter = last_prediction
            else:
                predicted_letter = "Uncertain"

    cv2.rectangle(frame, (0, 0), (640, 100), (30, 30, 30), -1)

    cv2.putText(
        frame,
        f"Detected: {predicted_letter}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    if confidence > 0:
        cv2.putText(
            frame,
            f"Confidence: {confidence * 100:.1f}%",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    cv2.imshow("HandLingo - Sign Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
hands.close()
cv2.destroyAllWindows()
