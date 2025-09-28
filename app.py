# app.py
from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Cấu hình
UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg"}
MODEL_PATH = "best_weather_model.h5"  # sửa nếu model của bạn ở chỗ khác
IMG_SIZE = (150, 150)  # theo train.py của bạn

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load model một lần khi khởi động server
model = load_model(MODEL_PATH)

# class labels theo dataset/training của bạn
CLASS_NAMES = ["Cloudy", "Rainy", "Sunny"]

# mapping khuyến nghị
RECOMMENDATIONS = {
    "Sunny": ["Mang kính râm", "Uống nhiều nước", "Đội nón / bôi kem chống nắng nếu ra ngoài lâu"],
    "Cloudy": ["Chuẩn bị áo khoác nhẹ", "Có thể mang theo áo khoác mỏng"],
    "Rainy": ["Mang ô / áo mưa", "Tránh ra ngoài nếu không cần thiết"]
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=IMG_SIZE)
    x = image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0)
    return x

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/predict", methods=["POST"])
def predict():
    # nhận file từ form-data với key "image"
    if "image" not in request.files:
        return jsonify({"error": "Không tìm thấy file 'image' trong request"}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "File không hợp lệ. Chấp nhận: jpg, jpeg, png"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    # tiền xử lý & dự đoán
    x = preprocess_image(save_path)
    preds = model.predict(x)[0]  # shape (3,)
    # đảm bảo cùng thứ tự classnames (Cloudy,Rainy,Sunny)
    probs = {CLASS_NAMES[i]: float(preds[i]) for i in range(len(CLASS_NAMES))}
    # label dự đoán
    pred_label = CLASS_NAMES[int(np.argmax(preds))]
    # gợi ý
    recs = RECOMMENDATIONS.get(pred_label, [])

    # trả về đường dẫn ảnh để frontend hiển thị
    img_url = f"/uploads/{filename}"

    return jsonify({
        "image_url": img_url,
        "pred_label": pred_label,
        "probabilities": probs,
        "recommendations": recs
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
