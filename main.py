from flask import Flask, jsonify, request, render_template
import os
from PIL import Image
import pytesseract

# Define a folder to store and later serve the images
UPLOAD_FOLDER = '/static/Test_Images/'

# Allow files of a specific type
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'tiff', 'tif']

# Initialize our API via FLASK app
app = Flask(__name__)


# Get file extension
def allowed_file(filename):
    """Check file extension according to allowed file type in the list ALLOWED_EXTENSIONS and return it in lower case"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_file_size(file):
    """Check if file size is less than 10 MB and return True"""

    # Seek to the end of the file to get its size
    file.seek(0, os.SEEK_END)  # Move the pointer to the end of the file
    file_size = file.tell()  # Get the file size in bytes

    # Reset the pointer to the start of the file
    file.seek(0)  # Move the pointer back to the start of the file

    if file_size < 10000000:
        return True


# API_CORE
def api_core(file):
    """Open the file, resize and save it in a temporary name and return the extracted text"""

    # Open image using PIL
    image = Image.open(file)

    # Perform OCR using pytesseract
    text = pytesseract.image_to_string(image)

    # Get the current size of the image
    width, height = image.size

    # Resize the image
    new_size = (int(width / 3), int(height / 3))
    image = image.resize(new_size)

    # Save the image
    image.save('static/temporary-img/temporary.png')

    # Return extracted text
    return text


@app.route('/')
def home():
    """Route home leading to the API documentation"""
    return render_template('index.html')


@app.route('/api', methods=['GET', 'POST'])
def upload():
    """Upload the file sent by the client and call the API_CORE to proceed tesseract rendering."""

    try:
        if request.method == "POST":
            if 'file' in request.files:
                file = request.files['file']

                if not file.filename == "":

                    if allowed_file(file.filename):

                        # check file size (if less than 10MB)
                        if check_file_size(file):

                            # call API_CORE to proceed tesseract
                            extracted_text = api_core(file=file)

                            if not extracted_text == "":
                                # let return result
                                return jsonify({"response": {"text": extracted_text}}), 200
                            else:
                                # let inform no text found
                                return jsonify({"response": {"text": "No text found on this image"}}), 200

                        else:
                            return jsonify({"response": {"error": "File size should be less than 10MB"}}), 406

                    else:
                        return jsonify({"response": {"error": f"Only files of type {ALLOWED_EXTENSIONS} are allowed."}}), 406
                else:
                    return jsonify({"response": {"error": "No file selected. Please, select a file image"}}), 404

            else:
                return jsonify({"response": {"error": "No file selected. Please, select a file image"}}), 404
        else:
            return jsonify({"response": {"error": "Method Not Allowed"}}), 405
    except Exception as e:
        return jsonify({"response": {"error": str(e)}}), 400


if __name__ == "__main__":
    # run app in debug mode to auto-load our server
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
