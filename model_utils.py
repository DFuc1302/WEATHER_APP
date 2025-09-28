# model_utils.py
# (tùy chọn) để bạn đặt các chức năng tiền xử lý / load model dùng chung
from tensorflow.keras.preprocessing import image
import numpy as np

IMG_SIZE = (150,150)

def preprocess_from_file(path):
    img = image.load_img(path, target_size=IMG_SIZE)
    arr = image.img_to_array(img) / 255.0
    return np.expand_dims(arr, axis=0)
