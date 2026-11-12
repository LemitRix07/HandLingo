
from flask import Flask, render_template, jsonify, request
import subprocess
import sys
import os
import pickle
import numpy as np
import cv2
import mediapipe as mp
import base64

app = Flask(__name__)

# =========================================================
# SIGN RECOGNITION MODEL
# =========================================================

MODEL_PATH = os.path.join(app.root_path, "models", "sign_model.pkl")

with open(MODEL_PATH, "rb") as file:
    sign_model = pickle.load(file)

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.65,
    min_tracking_confidence=0.65
)

# =========================================================
# PROCESS TRACKING & PYTHON ENVIRONMENT
# =========================================================

active_process = None
active_feature_name = None

volume_process = None
air_drawing_process = None
presentation_process = None
media_process = None


def get_python_bin():
    venv_python = os.path.join(
        app.root_path, "venv", "Scripts", "python.exe"
    )
    if os.path.isfile(venv_python):
        return venv_python
    return sys.executable


def stop_all_features():
    global active_process, active_feature_name
    global volume_process, air_drawing_process
    global presentation_process, media_process

    processes = [
        active_process,
        volume_process,
        air_drawing_process,
        presentation_process,
        media_process
    ]

    for proc in processes:
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=1.5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    active_process = None
    active_feature_name = None
    volume_process = None
    air_drawing_process = None
    presentation_process = None
    media_process = None


def launch_feature(script_name, display_name):
    global active_process, active_feature_name

    stop_all_features()

    feature_path = os.path.join(
        app.root_path, "features", script_name
    )

    if not os.path.isfile(feature_path):
        return {
            "success": False,
            "message": f"Feature file {script_name} does not exist."
        }

    python_bin = get_python_bin()

    try:
        proc = subprocess.Popen(
            [python_bin, feature_path],
            cwd=app.root_path,
            env=os.environ.copy(),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        active_process = proc
        active_feature_name = display_name

        return {
            "success": True,
            "message": f"{display_name} started successfully."
        }

    except Exception as e:
        print(f"Error launching {display_name}:", e)
        return {
            "success": False,
            "message": str(e)
        }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# SIGN RECOGNITION API
# =========================================================

@app.route("/predict-sign", methods=["POST"])
def predict_sign():

    try:
        data = request.get_json(silent=True) or {}
        image_data = data.get("image", "")

        if not image_data:
            return jsonify({
                "success": False,
                "message": "No image received."
            }), 400

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(
            image_bytes, dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array, cv2.IMREAD_COLOR
        )

        if frame is None:
            return jsonify({
                "success": False,
                "message": "Invalid image."
            }), 400

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        # Detect hand
        results = hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            print("[SIGN DEBUG] No hand detected")

            return jsonify({
                "success": True,
                "detected": False,
                "label": None,
                "confidence": 0
            })

        # Extract landmarks
        landmarks = results.multi_hand_landmarks[0]

        x_values = [point.x for point in landmarks.landmark]
        y_values = [point.y for point in landmarks.landmark]
        z_values = [point.z for point in landmarks.landmark]

        features = np.array(
            x_values + y_values + z_values,
            dtype=np.float32
        ).reshape(1, -1)

        # Model prediction
        probabilities = sign_model.predict_proba(features)[0]

        best_index = int(np.argmax(probabilities))
        confidence = float(probabilities[best_index])
        predicted_label = str(
            sign_model.classes_[best_index]
        )

        # DEBUG OUTPUT
        print(
            f"[SIGN DEBUG] Predicted: {predicted_label} "
            f"| Confidence: {confidence * 100:.2f}%"
        )

        # Show top 3 predictions for diagnosis
        top_indices = np.argsort(probabilities)[-3:][::-1]

        top_predictions = [
            {
                "label": str(sign_model.classes_[i]),
                "confidence": round(float(probabilities[i]) * 100, 2)
            }
            for i in top_indices
        ]

        print("[SIGN DEBUG] Top predictions:", top_predictions)

        # Existing confidence threshold
        if confidence < 0.75:
            return jsonify({
                "success": True,
                "detected": True,
                "label": "Uncertain",
                "confidence": round(confidence * 100, 2),
                "top_predictions": top_predictions
            })

        return jsonify({
            "success": True,
            "detected": True,
            "label": predicted_label,
            "confidence": round(confidence * 100, 2),
            "top_predictions": top_predictions
        })

    except Exception as e:
        print("[SIGN ERROR]", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# START VOLUME CONTROL
# =========================================================

@app.route("/start-volume-control", methods=["POST"])
def start_volume_control():
    global volume_process

    res = launch_feature("volume_control.py", "Volume Control")

    if res.get("success"):
        volume_process = active_process

    return jsonify(res)


# =========================================================
# START AIR DRAWING
# =========================================================

@app.route("/start-air-drawing", methods=["POST"])
def start_air_drawing():
    global air_drawing_process

    res = launch_feature("air_drawing.py", "Air Drawing")

    if res.get("success"):
        air_drawing_process = active_process

    return jsonify(res)


# =========================================================
# START PRESENTATION CONTROLLER
# =========================================================

@app.route("/start-presentation-controller", methods=["POST"])
def start_presentation_controller():
    global presentation_process

    res = launch_feature(
        "presentation_controller.py",
        "Presentation Controller"
    )

    if res.get("success"):
        presentation_process = active_process

    return jsonify(res)


# =========================================================
# START MEDIA CONTROLLER
# =========================================================

@app.route("/start-media-controller", methods=["POST"])
def start_media_controller():
    global media_process

    res = launch_feature("media_controller.py", "Media Controller")

    if res.get("success"):
        media_process = active_process

    return jsonify(res)


# =========================================================
# STOP ACTIVE FEATURE
# =========================================================

@app.route("/stop-feature", methods=["POST"])
def stop_feature():
    stopped = active_feature_name
    stop_all_features()

    return jsonify({
        "success": True,
        "message": f"Feature {stopped or ''} stopped successfully."
    })


# =========================================================
# FEATURE STATUS
# =========================================================

@app.route("/feature-status", methods=["GET"])
def feature_status():
    is_running = (
        active_process is not None
        and active_process.poll() is None
    )

    return jsonify({
        "running": is_running,
        "feature": active_feature_name if is_running else None
    })


# =========================================================
# RUN FLASK WITH HTTPS SUPPORT
# =========================================================

if __name__ == "__main__":

    cert_path = os.path.join(app.root_path, "cert.pem")
    key_path = os.path.join(app.root_path, "key.pem")

    ssl_context = None

    if (
        os.path.isfile(cert_path)
        and os.path.isfile(key_path)
        and not os.environ.get("HANDLINGO_HTTP")
    ):
        ssl_context = (cert_path, key_path)

    print("\n" + "=" * 65)
    print(" HandLingo Server Initialized")
    print("=" * 65)

    if ssl_context:
        print(" [SECURE HTTPS MODE ACTIVE]")
        print(" -> https://localhost:5000")
    else:
        print(" [HTTP MODE ACTIVE]")
        print(" -> http://localhost:5000")

    print("=" * 65 + "\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=ssl_context,
        debug=True
    )
