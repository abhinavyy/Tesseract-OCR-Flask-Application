from flask import Flask, request, render_template, redirect, url_for
import os
import cv2
import pytesseract
from gtts import gTTS #Use gTTS to convert the translated text into an audio file.
from googletrans import Translator
#Pillow is versatile and widely used for tasks ranging from simple image manipulations to complex image processing workflows.
from PIL import Image
import numpy as np

# Set the path for the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

# Ensure the uploads and audio directories exist
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

def preprocess_image(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #The bilateral filter is effective for applications where you need to reduce noise while preserving important features like edges.
    noise_removed = cv2.bilateralFilter(gray, d=5, sigmaColor=75, sigmaSpace=75)
    #Adaptive thresholding is particularly useful for images with varying illumination, allowing for more accurate segmentation and analysis.
    thresh = cv2.adaptiveThreshold(noise_removed, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 
                                   blockSize=15, 
                                   C=2)
    return thresh

def extract_text(img_path, lang='eng'):
    processed_image = preprocess_image(img_path)
    text = pytesseract.image_to_string(processed_image, lang=lang)
    return text

def translate_text(text, dest_lang):
    translator = Translator()
    translated = translator.translate(text, dest=dest_lang)
    return translated.text

def text_to_speech(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        # Save the uploaded file
        filepath = os.path.join('static/uploads', file.filename)
        file.save(filepath)

        # Get the selected language for OCR
        lang = request.form.get('language', 'eng')

        # Extract text from the image
        extracted_text = extract_text(filepath, lang)

        # Get translation language
        translate_to = request.form.get('translate_to', 'en')
        translated_text = translate_text(extracted_text, translate_to)

        # Convert extracted text to speech
        audio_filename = os.path.join('static/audio', 'output.mp3')
        text_to_speech(translated_text, audio_filename)

        return render_template('index.html', extracted_text=extracted_text, 
                               translated_text=translated_text, 
                               lang=lang, audio_file='audio/output.mp3')

    return render_template('index.html', extracted_text=None, translated_text=None, lang=None, audio_file=None)

if __name__ == '__main__':
    app.run(debug=True)
