from flask import Flask, render_template, request
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model
model = load_model(r"D:\\Weather AI\\project 2\\best_weather_model.h5")
classes = ["Cloudy", "Rainy", "Sunny"]

@app.route("/", methods=["GET", "POST"])
def index():
    pred_label = None
    pred_probs = None
    img_path = None

    if request.method == "POST":
        file = request.files['file']
        if file:
            img_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(img_path)

            # Xử lý ảnh
            img = image.load_img(img_path, target_size=(150,150))
            img_array = image.img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Dự đoán
            pred = model.predict(img_array)
            pred_label = classes[np.argmax(pred)]
            pred_probs = {classes[i]: round(pred[0][i]*100, 2) for i in range(len(classes))}

    return render_template("index.html", pred_label=pred_label, pred_probs=pred_probs, img_path=img_path)

if __name__ == "__main__":
    app.run(debug=True)