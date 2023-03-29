import io
from contextlib import asynccontextmanager

import numpy as np
import tensorflow as tf
from fastapi import FastAPI
from fastapi.responses import Response
from PIL import Image
from pydantic import BaseModel

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models["style_predict_path"] = tf.keras.utils.get_file('style_predict.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/prediction/1?lite-format=tflite')
    ml_models["style_transform_path"] = tf.keras.utils.get_file('style_transform.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/transfer/1?lite-format=tflite')
    yield
    ml_models.clear()

class Image(BaseModel):
    file_name: str | None = None
    url: str


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

@app.post("/images/")
async def load_images(content: Image, style: Image):
    
    content_path = tf.keras.utils.get_file(content.file_name, content.url)
    style_path = tf.keras.utils.get_file(style.file_name, style.url)
    
    content_image = load_image(content_path)
    style_image = load_image(style_path)

    preprocessed_content_image = preprocess_image(content_image, 384)
    preprocessed_style_image = preprocess_image(style_image, 256)

    return {
        "content": str(preprocessed_content_image.shape),
        "style": str(preprocessed_style_image.shape)
    }
