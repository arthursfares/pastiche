import io
import os
from contextlib import asynccontextmanager

import matplotlib.pyplot as plt
import tensorflow as tf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Allow requests from any origin and with any headers/methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Pastiche 🖼️"}


@app.post("/transfer-style/")
async def transform_image_style(content: ImageModel, style: ImageModel, content_blending_ratio: BlendingRatioModel):
    
    content_path = tf.keras.utils.get_file(content.file_name, content.url)
    style_path = tf.keras.utils.get_file(style.file_name, style.url)
    
    content_image = load_image(content_path)
    style_image = load_image(style_path)

    preprocessed_content_image = preprocess_image(content_image, 384)
    preprocessed_style_image = preprocess_image(style_image, 256)

    style_bottleneck = predict_style(preprocessed_style_image, ml_models["style_predict_path"])
    style_bottleneck_content = predict_style(preprocess_image(content_image, 256), ml_models["style_predict_path"])

    # Define content blending ratio between [0..1].
    # 0.0: 0% style extracts from content image.
    # 1.0: 100% style extracted from content image.
    if content_blending_ratio.value < 0.0 or content_blending_ratio.value > 1.0:
        content_blending_ratio.value = 0.0
        print("[!] content blend ratio should be between 0.0 and 1.0")
        print("[!] reseting it to 0.0")

    style_bottleneck_blended = content_blending_ratio.value * style_bottleneck_content + (1 - content_blending_ratio.value) * style_bottleneck

    stylized_image = transform_style(style_bottleneck_blended, preprocessed_content_image, ml_models["style_transform_path"])
    stylized_image = stylized_image[0]
    stylized_image_bytes = io.BytesIO()
    plt.imsave(stylized_image_bytes, stylized_image, format="png")
    stylized_image_bytes = stylized_image_bytes.getvalue()

    # delete the file from the cache
    cache_dir = os.path.join(os.path.expanduser('~'), '.keras', 'datasets')
    cache_content_file = os.path.join(cache_dir, content.file_name)
    cache_style_file = os.path.join(cache_dir, style.file_name)
    os.remove(cache_content_file)
    os.remove(cache_style_file)

    return Response(content=stylized_image_bytes, media_type="image/png")
