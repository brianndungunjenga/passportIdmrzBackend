import os
from flask import Flask, redirect, request, render_template, send_from_directory, safe_join, flash, jsonify
from werkzeug.utils import secure_filename
from passporteye import read_mrz
import datetime
import country_converter as coco
from flask_cors import CORS, cross_origin
import flask_cors

# UPLOAD_FOLDER stores uploaded files
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'
CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_AUTOMATIC_OPTIONS'] = True
app.config['CORS_ORIGINS'] = ['http://127.0.0.1/upload']

now = datetime.datetime.now()

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')

def main():
    return render_template('index.html')

@app.route('/upload', methods=["GET", "POST"])

def upload_file():
    if request.method == 'POST':
        # Check if the post has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # if user does not select file. browser
        # also submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # secure_filename secures a filename before storing it directly to the filesystem.
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # redirect() returns a response object and redirects the user to another target location with specified
            # status code.
            filename1 = safe_join(app.config['UPLOAD_FOLDER'], filename)
            mrz1 = read_mrz(filename1, save_roi=True)
            mrz = mrz1.to_dict()

            # Converting Sex Output
            if mrz['sex'] == 'F':
                mrz['sex'] = 'Female'
            elif mrz['sex'] == 'M':
                mrz['sex'] = 'Male'
            else:
                mrz['sex'] = 'Unknown'

            # Converting country output
            if coco.convert(names=mrz['country'], to='name_short') == 'not found':
                mrz['country'] = mrz['country']
            else:
                mrz['country'] = coco.convert(names=mrz['country'], to="name_short")

            # Converting nationality  output
            if coco.convert(names=mrz['nationality'], to='name_short') == 'not found':
                mrz['nationality'] = mrz['nationality']
            else:
                mrz['nationality'] = coco.convert(names=mrz['nationality'], to='name_short')

            # Converting date of birth output
            try:
                dd = datetime.datetime.strptime(mrz['date_of_birth'], '%y%m%d').date()
                if dd.year > now.year:
                    mrz['date_of_birth'] = dd.replace(year=dd.year - 100)
                else:
                    mrz['date_of_birth'] = dd
                    print(dd)
            except ValueError:
                mrz['date_of_birth'] = 'Unknown' 

            # Converting expiration output
            try:
                dd = datetime.datetime.strptime(mrz['expiration_date'], '%y%m%d').date()
                if dd.year > now.year:
                    mrz['expiration_date'] = dd
                else:
                    mrz['expiration_date'] = dd
                    print(dd)
            except ValueError:
                mrz['expiration_date'] = 'Unknown'

            print(mrz['date_of_birth'])

            return jsonify(mrz)


if __name__ == '__main__':
    app.run(debug=True)

# flask_cors.CORS(app, expose_headers='Authorization')
