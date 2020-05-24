#Image Processor
import tensorflow as tf
import cv2
#from PIL import Image
import numpy as np

#Server Back-End
import flask
#import io

app = flask.Flask(__name__)
real = ["Dental Plaque", "Tooth Loss", "Cracked Teeth", "Dental Caries"]

def preprocess(image):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    rows, cols = image.shape[:2]

    base = min(rows, cols)
    offsetW = int((cols - base) / 2)
    offsetH = int((rows - base) / 2)

    cropped = image[offsetH:base+offsetH, offsetW:base+offsetW]
    cilik = cv2.resize(cropped, (224, 224), interpolation=cv2.INTER_LINEAR)

    image_array = np.asarray(cilik)

    norm_img = image_array / 255.0

    data[0] = norm_img
    return data

@app.route("/predict", methods=["POST"])
def predict():
    global model

    r = {}
    result = {
        "success": False
    }

    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            image = flask.request.files["image"].read()
            image = cv2.imdecode(np.fromstring(image, np.uint8), cv2.IMREAD_UNCHANGED)
            #image = Image.open(io.BytesIO(image))

            data = preprocess(image)
            preds = model.predict(data)

            tot = np.sum(preds[0])
            for i in range(len(real)):
                proba = round((preds[0][i] / tot) * 100, 2)
                r[real[i]] = proba

            result["result"] = r
            result["success"] = True

    return flask.jsonify(result)

if __name__ == "__main__":
    print("[INFO] Loading the model....")
    model = tf.keras.models.load_model("model/keras_model.h5", compile=False)
    print("[INFO] Model Loaded, start the service")
    app.run(host='0.0.0.0', debug=True)