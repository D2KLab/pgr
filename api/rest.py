import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename

import sys
sys.path.append('../')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 #10MB
app.config['UPLOAD_EXTENSIONS'] = ['.docx', '.doc', '.pdf', '.txt']
app.config['UPLOAD_PATH'] = 'uploads'

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():
     
    files = os.listdir(app.config['UPLOAD_PATH'])

    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] :
            return "Invalid file", 400
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        usage.main(uploaded_file)
    return '', 204

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

# curl -i -F data='{"pilot"="Malaga","service"="Asylum Request"}' -F 'file=@/home/rizzo/Workspace/pgr/documentation/es/Asylum_and_Employment_Procedimiento_plazas.pdf' http://localhost:5000/v0.1/annotate
@app.route('/v0.1/annotate', methods=['POST'])
def annotate():

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] :
            return "Invalid file", 400

        uploaded_file.save(os.path.join('/tmp/', filename))


    data = request.form['data']
    print (data)

    ## TODO
    ## mongodb saving

    return 'OK'

# curl -i -F data='{"pilot"="Malaga","service"="Asylum Request"}' -F 'file=@/home/rizzo/Workspace/pgr/documentation/es/Asylum_and_Employment_Procedimiento_plazas.pdf' http://localhost:5000/v0.1/generate
@app.route('/v0.1/generate', methods=['POST'])
def generate():

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] :
            return "Invalid file", 400

        uploaded_file.save(os.path.join('/tmp/', filename))


    data = request.form['data']
    print (data)

    ## TODO
    ## mongodb saving

	return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
