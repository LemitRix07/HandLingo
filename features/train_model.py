
import os
import pandas as pd
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_PATH = os.path.join(BASE_DIR, "dataset", "landmarks.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "sign_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

print("Loading gesture dataset...")

data = pd.read_csv(CSV_PATH)

if data.empty:
    raise ValueError("Dataset is empty!")

X = data.drop("label", axis=1)
y = data["label"]

if y.nunique() < 2:
    raise ValueError(
        "Please collect at least two different alphabet classes before training."
    )

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training Random Forest model...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nTraining completed!")
print(f"Model accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, predictions))

with open(MODEL_PATH, "wb") as file:
    pickle.dump(model, file)

print("\nModel saved successfully!")
print(MODEL_PATH)
