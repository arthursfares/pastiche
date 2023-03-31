import tensorflow as tf

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

def predict_style(preprocessed_style_image, style_prediction_model):
    interpreter = tf.lite.Interpreter(model_path=style_prediction_model)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]["index"], preprocessed_style_image)
    interpreter.invoke()
    style_bottleneck = interpreter.tensor(
        interpreter.get_output_details()[0]["index"]
    )()
    return style_bottleneck

def transform_style(style_bottleneck, preprocessed_content_image, style_transform_model):
    interpreter = tf.lite.Interpreter(model_path=style_transform_model)
    input_details = interpreter.get_input_details()
    interpreter.allocate_tensors()
    interpreter.set_tensor(input_details[0]["index"], preprocessed_content_image)
    interpreter.set_tensor(input_details[1]["index"], style_bottleneck)
    interpreter.invoke()
    stylized_image = interpreter.tensor(
        interpreter.get_output_details()[0]["index"]
    )()
    return stylized_image