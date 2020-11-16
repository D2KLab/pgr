### IMPORT
# il file di run da importare è nella cartella pgr/, padre di quella corrente 
import sys
sys.path.append('../pgr')
import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
import zipfile
import json
from pgr import PathwayGenerator
from logger import CustomLogger
import logging
from logstash_formatter import LogstashFormatterV1
from flask_cors import CORS

### CONFIGURATION
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 #10MB
app.config['UPLOAD_EXTENSIONS'] = ['.docx', '.doc', '.pdf', '.txt']
app.config['UPLOAD_PATH'] = 'api/uploads'

cors    = CORS(app)
os.makedirs('log/', exist_ok=True)
flasklog    = open('log/flask.log', 'a+')
handler     = logging.StreamHandler(stream=flasklog)
handler.setFormatter(LogstashFormatterV1())
logging.basicConfig(handlers=[handler], level=logging.INFO)

from doccano_api_client import DoccanoClient
from config import doccano_client_params, pilots_legend
doccano_client = DoccanoClient(
   doccano_client_params['endpoint'],
   doccano_client_params['username'],
   doccano_client_params['password'] 
)

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

    
        result_pathway = run.run(os.path.join(app.config['UPLOAD_PATH'], filename), generate_pathway=True)
        print(result_pathway)

    return '', 204

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

def get_project_by_name(name):
    project_list = doccano_client.get_project_list()

    try:
        project = [prj for prj in project_list if prj['name'] == name][0]
    except Exception as e:
        raise(Exception('The project {} does not exists!'.format(name)))

    return project

def get_document(metadata, project_id):
    document_list = doccano_client.get_document_list(project_id=project_id)

    document = []

    for doc in document_list['results']:
        if doc['meta'].startswith("'") and doc['meta'].endswith("'"):
            meta = doc['meta'].replace('"', '')
        if doc['meta'].startswith('"') and doc['meta'].endswith('"'):
            meta = doc['meta'].replace('"', '')
        if meta == metadata:
            document.append(doc)

    if len(document) > 0:
        app.config['logger'].log({'message': 'The document {} already exists.'.format(metadata.split('-')[-1].strip())})
        return document[0]
    
    return False

def refactor_export_annotations(document_dict, project_id):
    doccano_dict = {}
    doccano_dict['text'] = document_dict['text']
    doccano_dict['labels'] = []
    doccano_dict['meta'] = document_dict['meta']

    for item in document_dict['annotations']:
        label_type = doccano_client.get_label_detail(project_id=project_id, label_id=item['label'])['text']
        doccano_dict['labels'].append([item['start_offset'], item['end_offset'], label_type])

    return doccano_dict

def refactor_export_generations(document_list):
    pathway_jsonl = []
    for document in document_list:
        tmp_dict = {'text': document['text'], 'labels': [], 'meta': document['meta']}
        for annotation in document['annotations']:
            tmp_dict['labels'].append(annotation['text'])

        pathway_jsonl.append(tmp_dict)

    return_string = ''
    for element in pathway_jsonl:
        string_element = str(json.dumps(element, ensure_ascii=False))

        return_string = return_string + string_element + '\n'

    return return_string

def doccano_to_dict_format(annotation_list, document, project_id):
    # ner_dict = {'text': 'tutto il testo', 'entities': [{'start, end, value, type, confidence}]}
    ner_dict = {}
    ner_dict['text'] = document['text']
    ner_dict['entities'] = []
    for annotation in annotation_list:
        element_dict = {}
        #annotation_detail = doccano_client.get_annotation_detail(project_id, annotation['document'], annotation['id'])
        label = doccano_client.get_label_detail(project_id, annotation['label'])

        element_dict['start_offset'] = annotation['start_offset']
        element_dict['end_offset'] = annotation['end_offset']
        element_dict['confidence'] = 0.8
        element_dict['type'] = label['text']

        element_dict['value'] = ner_dict['text'][annotation['start_offset']:annotation['end_offset']]

        ner_dict['entities'].append(element_dict)
        
    return ner_dict

# curl -i -F data='{"pilot"="Malaga","service"="Asylum Request"}' -F 'file=@/home/rizzo/Workspace/pgr/documentation/es/Asylum_and_Employment_Procedimiento_plazas.pdf' http://localhost:5000/v0.1/annotate
@app.route('/v0.2/annotate', methods=['POST'])
def annotate():

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] :
            return "Invalid file", 400

        app.config['logger'].log({'file': 'test'})

        data = json.loads(request.form['data'])

        file_path = os.path.join('documentation/' + data['pilot'] + '/', filename)
        uploaded_file.save(file_path)

        # Instantiate PathwayGeneration object
        pgr = PathwayGenerator(path=file_path, pilot=data['pilot'], service=data['service'], use_cuda=False)

        # Check for annotation project
        project = get_project_by_name('ER ' + pilots_legend[data['pilot']] + ' Annotated Documents')
        #app.config['logger'].log()

        # Check if document already exists: if so, return annotations. Otherwise, create a new one
        document = get_document(pgr.annotation_metadata, project['id'])
        if document:
            return refactor_export_annotations(document, project['id'])

        converted_file = pgr.do_convert()
        #app.config['logger'].log()

        ner_dict = pgr.do_annotate()
        #app.config['logger'].log()
        print(ner_dict)

        doccano_dict, ner_path = pgr.export_annotation_to_doccano()
        #app.config['logger'].log()

        # WARNING: current issue of file upload/download Response -> https://github.com/doccano/doccano-client/issues/13
        try:
            doccano_client.post_doc_upload(project_id=project['id'], file_format='json', file_name=ner_path)
        except json.decoder.JSONDecodeError:
            pass

        return doccano_dict

    return 'NOK', 400

# curl -i -F data='{"pilot"="Malaga","service"="Asylum Request"}' -F 'file=@/home/rizzo/Workspace/pgr/documentation/es/Asylum_and_Employment_Procedimiento_plazas.pdf' http://localhost:5000/v0.1/generate
@app.route('/v0.2/generate', methods=['POST'])
def generate():

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] :
            return "Invalid file", 400

        data = json.loads(request.form['data'])

        file_path = os.path.join('documentation/' + data['pilot'] + '/', filename)
        uploaded_file.save(file_path)

        # Instantiate PathwayGeneration object
        pgr = PathwayGenerator(path=file_path, pilot=data['pilot'], service=data['service'], use_cuda=False)

        # Check for projects
        generation_project = get_project_by_name('ER ' + pilots_legend[data['pilot']] + ' Pathways')
        annotation_project = get_project_by_name('ER ' + pilots_legend[data['pilot']] + ' Annotated Documents')
        #app.config['logger'].log()

        # Check if document already exists: if so, return annotations. Otherwise, create a new one
        document_annotation = get_document(pgr.annotation_metadata, annotation_project['id'])
        document_generation = get_document(pgr.generation_metadata['where'], generation_project['id'])
        if document_generation:
            document_where = get_document(pgr.generation_metadata['where'], generation_project['id']) 
            document_when = get_document(pgr.generation_metadata['when'], generation_project['id'])
            document_how = get_document(pgr.generation_metadata['how'], generation_project['id'])
            
            return refactor_export_generations([document_where, document_when, document_how])


        # Check if document already exists: if so, return annotations. Otherwise, create a new one
        if document_annotation:
            #ner_dict = refactor_export_annotations(document_annotation, project['id'])
            annotations = doccano_client.get_annotation_list(annotation_project['id'], document_annotation['id'])
            
            pgr.ner_dict = doccano_to_dict_format(annotations, document_annotation, annotation_project['id'])
            
        else:
            converted_file = pgr.do_convert()
            #app.config['logger'].log()

            ner_dict = pgr.do_annotate()
            #app.config['logger'].log()

            #if not document_annotation:
            #    doccano_dict, ner_path = pgr.export_annotation_to_doccano()
            #    #app.config['logger'].log()

            try:
                doccano_client.post_doc_upload(project_id=annotation_project['id'], file_format='json', file_name=ner_path)
            except json.decoder.JSONDecodeError:
                pass

        pathway = pgr.do_generate()
        #app.config['logger'].log()

        pathway_dict, pathway_path = pgr.export_generation_to_doccano()

        try:
            print('trying to upload documents')
            doccano_client.post_doc_upload(project_id=generation_project['id'], file_format='json', file_name=pathway_path)
        except json.decoder.JSONDecodeError:
            pass

        return pathway_dict

    return 'NOK', 400

if __name__ == '__main__':
    app.config['logger'] = CustomLogger('log/pgr.log')
    app.run(host='0.0.0.0', debug=True, port=5000)
