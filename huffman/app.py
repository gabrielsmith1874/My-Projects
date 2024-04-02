from flask import Flask, request, send_file, url_for
from werkzeug.utils import secure_filename, redirect
import os

application = Flask(__name__)
import compress2

@application.route('/')
def home():
    """
    Home page of the web application. Should include a form to upload a file and a submit button.
    Submit button should compress file and send user the compressed file
    :return:
    """
    return """
    <!doctype html>
    <title>File Upload</title>
    <h1>Upload a file</h1>
    <form method=post enctype=multipart/form-data action='/upload'>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """

@application.route('/upload', methods=['POST'])
def upload():
    """
    Uploads a file and compresses it using the Huffman encoding algorithm.
    If the file is a .huff file, it decompresses it.
    :return:
    """
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        save_path = "/path/to/save"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file.save(os.path.join(save_path, filename))

        if filename.endswith('.huff'):
            original_filename = filename.rsplit('.', 1)[0]  # Remove the .huff extension
            compress2.decompress_file(os.path.join(save_path, filename),
                                      os.path.join(save_path, original_filename))
            return redirect(url_for('download', filename=original_filename))
        else:
            compress2.compress_file(os.path.join(save_path, filename), os.path.join(save_path, filename + ".huff"))
            return redirect(url_for('download', filename=filename + ".huff"))
    else:
        return "No file uploaded!"


@application.route('/download/<filename>')
def download(filename):
    # Ensure the file exists.
    if os.path.exists(os.path.join("/path/to/save", filename)):
        return send_file(os.path.join("/path/to/save", filename), as_attachment=True)
    else:
        return "File not found!"

if __name__ == '__main__':
    application.run(debug=True)