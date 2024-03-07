
from flask import Flask, render_template, request
import zipfile
import os

app = Flask(__name__)

def read_code_snippets():
    code_snippets = {}
    dtx_filename = 'data.dtx'

    with zipfile.ZipFile(dtx_filename, 'r') as zip_file:
        with zip_file.open('.ids') as ids_file:
            for line in ids_file:
                line = line.decode('utf-8').strip()
                index, filename = line.split(': ')
                code_snippets[index] = {'filename': filename, 'code': None}

    for index, snippet in code_snippets.items():
        with zipfile.ZipFile(dtx_filename, 'r') as zip_file:
            with zip_file.open(snippet['filename']) as code_file:
                code_snippets[index]['code'] = code_file.read().decode('utf-8')

    return code_snippets

@app.route('/')
def index():
    code_snippets = read_code_snippets()
    return render_template('index.html', code_snippets=code_snippets)

@app.route('/code')
def get_code():
    code_id = request.args.get('id')
    code_snippets = read_code_snippets()

    if code_id in code_snippets:
        code = code_snippets[code_id]['code']
        return render_template('code.html', code=code)
    else:
        return "Code snippet not found."

if __name__ == '__main__':
    app.run(debug=True)
