
// =========================================================
// HANDLINGO - CLIENT SCRIPT
// =========================================================

let cameraStream = null;
let predictionTimer = null;
let predictionInProgress = false;

const cameraFeed = document.getElementById("cameraFeed");
const cameraPlaceholder = document.getElementById("cameraPlaceholder");
const startCameraBtn = document.getElementById("startCamera");
const stopCameraBtn = document.getElementById("stopCamera");


// =========================================================
// LIVE SIGN RECOGNITION
// =========================================================

const predictionCanvas = document.createElement("canvas");
const predictionContext = predictionCanvas.getContext("2d");

async function predictSign() {

    if (!cameraFeed || !cameraStream || predictionInProgress) {
        return;
    }

    if (cameraFeed.readyState < 2 || !cameraFeed.videoWidth) {
        return;
    }

    predictionInProgress = true;

    try {
        // Capture a frame from the browser camera
        predictionCanvas.width = 640;
        predictionCanvas.height = 480;

        predictionContext.drawImage(
            cameraFeed,
            0,
            0,
            predictionCanvas.width,
            predictionCanvas.height
        );

        const imageData = predictionCanvas.toDataURL("image/jpeg", 0.7);

        // Send frame to Flask prediction API
        const response = await fetch("/predict-sign", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                image: imageData
            })
        });

        const data = await response.json();

        const detectedSignElem = document.getElementById("detectedSign");
        const confidenceElem = document.getElementById("confidence");

        if (!data.success) {
            console.error("Prediction error:", data.message);
            return;
        }

        if (data.detected) {

            if (detectedSignElem) {
                detectedSignElem.textContent = data.label;
            }

            if (confidenceElem) {
                confidenceElem.textContent =
                    `Confidence: ${data.confidence}%`;
            }

        } else {

            if (detectedSignElem) {
                detectedSignElem.textContent = "—";
            }

            if (confidenceElem) {
                confidenceElem.textContent = "No hand detected";
            }
        }

    } catch (error) {
        console.error("Sign recognition error:", error);

    } finally {
        predictionInProgress = false;
    }
}


function startPrediction() {

    stopPrediction();

    // Run recognition approximately every 300 milliseconds
    predictionTimer = setInterval(predictSign, 300);
}


function stopPrediction() {

    if (predictionTimer) {
        clearInterval(predictionTimer);
        predictionTimer = null;
    }

    predictionInProgress = false;
}


// =========================================================
// HELPER: STOP BROWSER WEBCAM
// =========================================================

function stopBrowserCamera() {

    stopPrediction();

    if (cameraStream) {
        cameraStream.getTracks().forEach(function (track) {
            track.stop();
        });

        cameraStream = null;
    }

    if (cameraFeed) {
        cameraFeed.srcObject = null;
        cameraFeed.style.display = "none";
    }

    if (cameraPlaceholder) {
        cameraPlaceholder.style.display = "block";
    }

    const detectedSignElem = document.getElementById("detectedSign");
    const confidenceElem = document.getElementById("confidence");

    if (detectedSignElem) {
        detectedSignElem.textContent = "—";
    }

    if (confidenceElem) {
        confidenceElem.textContent = "Waiting for gesture...";
    }
}


// =========================================================
// OPEN BROWSER CAMERA
// =========================================================

if (startCameraBtn) {

    startCameraBtn.addEventListener("click", async function () {

        try {

            // Prevent multiple camera sessions
            if (cameraStream) {
                stopBrowserCamera();
            }

            // Stop background OpenCV feature
            try {
                await fetch("/stop-feature", {
                    method: "POST"
                });
            } catch (err) {
                console.warn("Could not reach stop-feature endpoint:", err);
            }

            if (!navigator.mediaDevices ||
                !navigator.mediaDevices.getUserMedia) {

                alert(
                    "Webcam access requires HTTPS or localhost.\n" +
                    "Please open https://localhost:5000"
                );

                return;
            }

            cameraStream = await navigator.mediaDevices.getUserMedia({

                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },

                audio: false
            });

            if (cameraFeed) {

                cameraFeed.srcObject = cameraStream;
                cameraFeed.style.display = "block";

                await cameraFeed.play();
            }

            if (cameraPlaceholder) {
                cameraPlaceholder.style.display = "none";
            }

            // Start AI sign recognition
            startPrediction();

        } catch (error) {

            console.error("Camera access error:", error);

            stopBrowserCamera();

            if (error.name === "NotAllowedError" ||
                error.name === "PermissionDeniedError") {

                alert("Camera permission was denied. Please allow camera access.");

            } else if (error.name === "NotReadableError" ||
                error.name === "TrackStartError") {

                alert("Camera is currently being used by another application.");

            } else {

                alert(
                    "Camera error: " + error.message +
                    "\nIf using HTTP, please use HTTPS or localhost."
                );
            }
        }
    });
}


// =========================================================
// STOP BROWSER CAMERA
// =========================================================

if (stopCameraBtn) {

    stopCameraBtn.addEventListener("click", function () {
        stopBrowserCamera();
    });
}


// =========================================================
// ABOUT MODAL
// =========================================================

const aboutBtn = document.getElementById("aboutBtn");
const aboutModal = document.getElementById("aboutModal");
const aboutClose = document.getElementById("aboutClose");
const aboutOverlay = document.getElementById("aboutOverlay");

if (aboutBtn && aboutModal) {

    aboutBtn.addEventListener("click", function (event) {
        event.preventDefault();
        aboutModal.classList.add("show");
        document.body.style.overflow = "hidden";
    });
}

if (aboutClose && aboutModal) {

    aboutClose.addEventListener("click", function () {
        aboutModal.classList.remove("show");
        document.body.style.overflow = "";
    });
}

if (aboutOverlay && aboutModal) {

    aboutOverlay.addEventListener("click", function () {
        aboutModal.classList.remove("show");
        document.body.style.overflow = "";
    });
}


// =========================================================
// FEATURES MODAL
// =========================================================

const featuresBtn = document.getElementById("featuresBtn");
const featuresModal = document.getElementById("featuresModal");
const featuresClose = document.getElementById("featuresClose");
const featuresOverlay = document.getElementById("featuresOverlay");

if (featuresBtn && featuresModal) {

    featuresBtn.addEventListener("click", function (event) {
        event.preventDefault();
        featuresModal.classList.add("show");
        document.body.style.overflow = "hidden";
    });
}

if (featuresClose && featuresModal) {

    featuresClose.addEventListener("click", function () {
        featuresModal.classList.remove("show");
        document.body.style.overflow = "";
    });
}

if (featuresOverlay && featuresModal) {

    featuresOverlay.addEventListener("click", function () {
        featuresModal.classList.remove("show");
        document.body.style.overflow = "";
    });
}


// Global Escape key handler
document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {

        if (aboutModal) {
            aboutModal.classList.remove("show");
        }

        if (featuresModal) {
            featuresModal.classList.remove("show");
        }

        document.body.style.overflow = "";
    }
});


// =========================================================
// TOAST NOTIFICATIONS
// =========================================================

function showToast(message, isError = false) {

    let toast = document.getElementById("handlingoToast");

    if (!toast) {

        toast = document.createElement("div");
        toast.id = "handlingoToast";

        toast.style.position = "fixed";
        toast.style.bottom = "28px";
        toast.style.right = "28px";
        toast.style.backgroundColor = isError ? "#ef4444" : "#18181b";
        toast.style.color = "#ffffff";
        toast.style.padding = "14px 22px";
        toast.style.borderRadius = "12px";
        toast.style.boxShadow = "0 10px 30px rgba(0,0,0,0.45)";
        toast.style.border = isError
            ? "1px solid #dc2626"
            : "1px solid rgba(255,255,255,0.15)";
        toast.style.fontFamily = "'Inter', sans-serif";
        toast.style.fontSize = "14px";
        toast.style.zIndex = "99999";
        toast.style.transition = "all 0.3s ease";

        document.body.appendChild(toast);

    } else {

        toast.style.backgroundColor = isError ? "#ef4444" : "#18181b";
        toast.style.border = isError
            ? "1px solid #dc2626"
            : "1px solid rgba(255,255,255,0.15)";
    }

    toast.textContent = message;
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";

    setTimeout(() => {

        if (toast) {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(10px)";
        }

    }, 4500);
}


// =========================================================
// GESTURE FEATURES LAUNCHER
// =========================================================

async function startGestureFeature(endpoint, featureName) {

    // Release browser webcam
    stopBrowserCamera();

    await new Promise(resolve => setTimeout(resolve, 400));

    showToast(
        `Launching ${featureName}... Camera window is opening! Press Q to exit.`
    );

    try {

        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();

        if (data.success) {

            console.log(`${featureName} started successfully.`);

            showToast(
                `${featureName} is running! Press Q inside the camera window to close.`,
                false
            );

        } else {

            console.error(`Error starting ${featureName}:`, data.message);

            showToast(
                `Could not start ${featureName}: ${data.message}`,
                true
            );
        }

    } catch (error) {

        console.error(`${featureName} request failed:`, error);

        showToast(
            `Failed to launch ${featureName}. Make sure the server is running.`,
            true
        );
    }
}


// =========================================================
// FEATURE BUTTONS & TRANSLATOR CONTROLS
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    // Feature 01: Volume Control
    const volumeBtn = document.querySelector('[data-feature="volume"]');

    if (volumeBtn) {
        volumeBtn.addEventListener("click", function () {
            startGestureFeature(
                "/start-volume-control",
                "Gesture Volume Control"
            );
        });
    }

    // Feature 02: Air Drawing
    const drawingBtn = document.querySelector('[data-feature="drawing"]');

    if (drawingBtn) {
        drawingBtn.addEventListener("click", function () {
            startGestureFeature("/start-air-drawing", "Air Drawing");
        });
    }

    // Feature 03: Presentation Controller
    const presentationBtn = document.querySelector('[data-feature="presentation"]');

    if (presentationBtn) {
        presentationBtn.addEventListener("click", function () {
            startGestureFeature(
                "/start-presentation-controller",
                "Presentation Controller"
            );
        });
    }

    // Feature 05: Media Controller
    const mediaBtn = document.querySelector('[data-feature="media"]');

    if (mediaBtn) {
        mediaBtn.addEventListener("click", function () {
            startGestureFeature("/start-media-controller", "Media Controller");
        });
    }

    // Feature 06: Sign Language Learning
    const learningBtn = document.querySelector('[data-feature="learning"]');

    if (learningBtn) {
        learningBtn.addEventListener("click", function () {
            showToast("Sign Language Learning is currently in development.");
        });
    }

    // Feature 07: Custom Gestures
    const customBtn = document.querySelector('[data-feature="custom"]');

    if (customBtn) {
        customBtn.addEventListener("click", function () {
            showToast("Custom Gestures tool is currently in development.");
        });
    }


    // =====================================================
    // TRANSLATOR SECTION CONTROLS
    // =====================================================

    const detectedSignElem = document.getElementById("detectedSign");
    const sentenceBox = document.getElementById("sentenceBox");
    const addSignBtn = document.getElementById("addSign");
    const clearSentenceBtn = document.getElementById("clearSentence");
    const speakSentenceBtn = document.getElementById("speakSentence");

    let sentenceWords = [];

    // Add recognized sign to sentence
    if (addSignBtn && sentenceBox) {

        addSignBtn.addEventListener("click", function () {

            const sign = detectedSignElem
                ? detectedSignElem.textContent.trim()
                : "";

            if (
                sign &&
                sign !== "—" &&
                sign !== "Uncertain"
            ) {

                sentenceWords.push(sign);

                sentenceBox.textContent = sentenceWords.join(" ");

            } else {

                showToast("No reliable sign is currently detected.");
            }
        });
    }

    // Clear sentence
    if (clearSentenceBtn && sentenceBox) {

        clearSentenceBtn.addEventListener("click", function () {

            sentenceWords = [];

            sentenceBox.textContent = "Start making your sentence...";
        });
    }

    // Speak sentence
    if (speakSentenceBtn && sentenceBox) {

        speakSentenceBtn.addEventListener("click", function () {

            const textToSpeak =
                sentenceWords.join(" ") ||
                (
                    sentenceBox.textContent !== "Start making your sentence..."
                        ? sentenceBox.textContent
                        : ""
                );

            if (textToSpeak && "speechSynthesis" in window) {

                const utterance = new SpeechSynthesisUtterance(textToSpeak);

                utterance.rate = 0.95;

                window.speechSynthesis.speak(utterance);

            } else {

                showToast("Please build a sentence first to speak.");
            }
        });
    }
});


// =========================================================
// LIGHT / DARK THEME
// =========================================================

const themeToggle = document.getElementById("themeToggle");

if (themeToggle) {

    themeToggle.addEventListener("click", () => {

        document.body.classList.toggle("light-mode");

        if (document.body.classList.contains("light-mode")) {

            localStorage.setItem("handLingoTheme", "light");

        } else {

            localStorage.setItem("handLingoTheme", "dark");
        }
    });
}


// Load saved theme
const savedTheme = localStorage.getItem("handLingoTheme");

if (savedTheme === "light") {
    document.body.classList.add("light-mode");
}
