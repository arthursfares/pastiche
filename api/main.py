import io
from contextlib import asynccontextmanager

import matplotlib.pyplot as plt
import tensorflow as tf
from fastapi import FastAPI
from fastapi.responses import Response

from .image_processing import load_image, predict_style, preprocess_image, transform_style
from .models import BlendingRatioModel, ImageModel

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models["style_predict_path"] = tf.keras.utils.get_file('style_predict.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/prediction/1?lite-format=tflite')
    ml_models["style_transform_path"] = tf.keras.utils.get_file('style_transform.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/transfer/1?lite-format=tflite')
    yield
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Welcome to Pastiche 🖼️"}


def load_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.io.decode_image(image, channels=3)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = image[tf.newaxis, :]
    return image

def preprocess_image(image, target_dimension):
    shape = tf.cast(tf.shape(image)[1:-1], tf.float32)
    short_dimension = min(shape)
    scale = target_dimension / short_dimension
    new_shape = tf.cast(shape * scale, tf.int32)
    image = tf.image.resize(image, new_shape)
    image = tf.image.resize_with_crop_or_pad(image, target_dimension, target_dimension)
    return image

def predict_style(preprocessed_style_image):
    interpreter = tf.lite.Interpreter(model_path=ml_models["style_predict_path"])
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]["index"], preprocessed_style_image)
    interpreter.invoke()
    style_bottleneck = interpreter.tensor(
        interpreter.get_output_details()[0]["index"]
    )()
    return style_bottleneck

def transform_style(style_bottleneck, preprocessed_content_image):
    interpreter = tf.lite.Interpreter(model_path=ml_models["style_transform_path"])
    input_details = interpreter.get_input_details()
    interpreter.allocate_tensors()
    interpreter.set_tensor(input_details[0]["index"], preprocessed_content_image)
    interpreter.set_tensor(input_details[1]["index"], style_bottleneck)
    interpreter.invoke()
    stylized_image = interpreter.tensor(
        interpreter.get_output_details()[0]["index"]
    )()
    return stylized_image

@app.post("/images/")
async def transform_image_style(content: ImageModel, style: ImageModel, content_blending_ratio: float = 0.0):
    
    content_path = tf.keras.utils.get_file(content.file_name, content.url)
    style_path = tf.keras.utils.get_file(style.file_name, style.url)
    
    content_image = load_image(content_path)
    style_image = load_image(style_path)

    preprocessed_content_image = preprocess_image(content_image, 384)
    preprocessed_style_image = preprocess_image(style_image, 256)

    style_bottleneck = predict_style(preprocessed_style_image)
    style_bottleneck_content = predict_style(preprocess_image(content_image, 256))

    # Define content blending ratio between [0..1].
    # 0.0: 0% style extracts from content image.
    # 1.0: 100% style extracted from content image.
    if content_blending_ratio < 0.0 or content_blending_ratio > 1.0:
        content_blending_ratio = 0.0
        print("[!] content blend ratio should be between 0.0 and 1.0")
        print("[!] reseting it to 0.0")

    style_bottleneck_blended = content_blending_ratio * style_bottleneck_content \
                                + (1 - content_blending_ratio) * style_bottleneck

    stylized_image = transform_style(style_bottleneck_blended, preprocessed_content_image)
    stylized_image = stylized_image[0]  # reduce the dimensionality of the array
    stylized_image = Image.fromarray(stylized_image, "RGB")  # convert to PIL image
    stylized_image_bytes = io.BytesIO()
    stylized_image.save(stylized_image_bytes, format="JPEG")
    stylized_image_bytes = stylized_image_bytes.getvalue()

    return Response(content=stylized_image_bytes, media_type="image/jpeg")
