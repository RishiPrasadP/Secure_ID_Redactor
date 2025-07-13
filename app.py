from flask import Flask, render_template, request, send_file
import pytesseract
import cv2
import os
import re
from PIL import Image
import spacy

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
nlp = spacy.load("en_core_web_sm")

SSN_REGEX = r"\b\d{3}-\d{2}-\d{4}\b"

def mask_sensitive_info(image_path):
    img = cv2.imread(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    for i, word in enumerate(data['text']):
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        if re.fullmatch(SSN_REGEX, word):
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)
        elif "conf" in data and int(data["conf"][i]) > 60:
            doc = nlp(word)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)

    output_path = os.path.join(UPLOAD_FOLDER, "masked.png")
    cv2.imwrite(output_path, img)
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No image uploaded", 400

    file = request.files['image']
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(image_path)

    result_path = mask_sensitive_info(image_path)
    return send_file(result_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
