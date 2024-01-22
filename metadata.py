import os
from flask import Flask, render_template, request, jsonify
from PIL import Image
import PyPDF2

app = Flask(__name__)

def has_been_edited(image_path):
    try:
        with Image.open(image_path) as img:
            metadata = img.info
            return 'Photoshop' in metadata.get('Software', '') or 'GIMP' in metadata.get('Software', '')
    except Exception as e:
        print("Error:", e)
        return False

def has_pdf_been_edited(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            if '/ModDate' in reader.getDocumentInfo():
                return True
    except Exception as e:
        print("Error:", e)
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Save the uploaded file to the server
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)

        # Check if the file has been edited
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            edited = has_been_edited(file_path)
        elif file.filename.lower().endswith('.pdf'):
            edited = has_pdf_been_edited(file_path)
        else:
            return jsonify({'error': 'Invalid file format'}), 400

        # Return the result
        # Instead of using 'file.info', directly return 'metadata' based on the file type
        metadata = {'edited': edited}
        return jsonify(metadata)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
