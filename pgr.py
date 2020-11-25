import argparse
import os 
import re
import json
import pdb

from transner import Transner
from doc2txt import doc2txt

from tools import annotator, aggregator, generator

import importlib
sutime_mod = importlib.import_module("python-sutime.sutime")

def pathway_to_doccano(json_pathway, path, pilot='', service=''):
    metadata = os.path.basename(path) if pilot == '' else pilot + ' - ' + service + ' - ' + os.path.basename(path)
    filename = os.path.splitext(path)[0]
    pathway_jsonl = []
    where_dict = {"text": "where", "labels": [], "meta": metadata + ' where'}
    how_dict = {"text": "how", "labels": [], "meta": metadata + ' how'}
    when_dict = {"text": "when", "labels": [], "meta": metadata + ' when'}

    for entity in json_pathway:
        if len(entity["entity"].strip()) > 0:
            if entity["step"] == "where":
                if entity["entity"].strip() not in where_dict["labels"]:
                    where_dict["labels"].append(entity["entity"].strip())
            elif entity["step"] == "how":
                if entity["entity"].strip() not in how_dict["labels"]:
                    how_dict["labels"].append(entity["entity"].strip())
            elif entity["step"] == "when":
                if entity["entity"].strip() not in when_dict["labels"]:
                    when_dict["labels"].append(entity["entity"].strip())
    
    pathway_jsonl.append(where_dict)
    pathway_jsonl.append(when_dict)
    pathway_jsonl.append(how_dict)
    file_out = open(filename + '_pathway.jsonl', 'w', encoding='utf-8')

    return_string = ''

    for element in pathway_jsonl:
        string_element = str(json.dumps(element, ensure_ascii=False))
        file_out.write(string_element)
        file_out.write('\n')

        return_string = return_string + string_element + '\n'

    return return_string, filename + '_pathway.jsonl'

def export_to_json(ner_dict, path):
    json_file = json.dumps(ner_dict, indent=4)
    filename = re.sub('_ner.json', '_cluster.json', path)
    f = open(filename, 'w')
    f.write(json_file)
    f.close()

def to_list(data):
    element_list = [] # Make an empty list

    for element in re.split('[.\n]', data):
        stripped_element = element.strip()
        if stripped_element != '':	    
            element_list.append(stripped_element) #Append to list the striped element
    
    return element_list

def annotate_transner(sentence_list):
    model = Transner(pretrained_model='bert_uncased_base_easyrights_v0.1', use_cuda=False, cuda_device=2, language_detection=True)
    ner_dict = model.ner(sentence_list, apply_regex=True)
    ner_dict = model.find_dates(ner_dict)
    return ner_dict

def annotate_sutime(ner_dict):
    for item in ner_dict:
        text = item['sentence']
        jar_files = os.path.join('python-sutime/', 'jars')
        sutime = sutime_mod.SUTime(jars=jar_files, mark_time_ranges=True)

        json = sutime.parse(text)
        
        for item_sutime in json:
            item['entities'].append({'type': 'TIME', 'value': item_sutime['text'], 'confidence': 0.8, 'offset': item_sutime['start']})

    return ner_dict

def document_exists(metadata, project_id):
    document_list = doccano_client.get_document_list(project_id=project_id)

    document = []

    for doc in document_list['results']:
        if doc['meta'].startswith("'") and doc['meta'].endswith("'"):
            meta = doc['meta'].replace('"', '')
        if doc['meta'].startswith('"') and doc['meta'].endswith('"'):
            meta = doc['meta'].replace('"', '')
        print(meta)
        print(metadata)
        if meta == metadata:
            document.append(doc)

    if len(document) > 0:
        print('The document uploaded already exists. Returning the annotation related.')
        return document[0]
    
    return False

def get_project_by_name(name):
    project_list = doccano_client.get_project_list()

    try:
        project = [prj for prj in project_list if prj['name'] == name][0]
    except IndexError as e:
        raise(Exception(e))

    return project

def main(path=None, empty=False, convert=True):

    # convert.py
    if convert:
        converted_file = doc2txt.convert_to_txt(path)
    else:
        converted_file = open(path, 'r').read()

    # annotate.py
    sentence_list = to_list(converted_file)

    if empty:
        ner_dict = {'text': '', 'entities': []}
        for sentence in sentence_list:
            ner_dict['text'] = ner_dict['text'] + sentence +'.\n'

        annotator.export_to_doccano(ner_dict, os.path.splitext(path)[0])

    else:
        ner_dict = annotate_transner(sentence_list)
        #ner_dict = annotate_sutime(ner_dict)

        ner_dict = annotator.aggregate_dict(ner_dict)

        #ner_dict = resolve_uri_entities(ner_dict, path)

        annotator.export_to_doccano(ner_dict, os.path.splitext(path)[0])

        # aggregate.py
        aggregated_ner_dict = aggregator.aggregate_entities(ner_dict)

        # generate.py
        pathway = generator.generate(aggregated_ner_dict)
        json_pathway = pathway.to_json(orient='records')

        pathway_to_doccano(json.loads(json_pathway), path)

if __name__ == '__main__':
    """Input example:

        $python usage.py --strings \
            "Mario è nato a Milano" \
            "The war of Orleans"
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f',
        '--path',
        help='List of files to be converted before transner',
        required=True
    )

    parser.add_argument(
        '-e',
        '--empty',
        help='Specify if the jsonl output for doccano needs to be empty. Default is false.',
        required=False
    )
    parser.add_argument(
        '-c',
        '--convert',
        help='Specify if you need the file conversion. Default is true.',
        required=False
    )
    args = parser.parse_args()


    main(path=args.path, empty=args.empty, convert=args.convert)

    
class PathwayGenerator():

    def __init__(self, path, pilot, service, use_cuda, cuda_device=-1):
        ''' PathwayGenerator object constructor

        Args:
            path (str): path of the file from which the pathway is generated.
            pilot (str): name of the pilot.
            service (str): name of the service considered.
            use_cuda (bool): flag to use gpu model.
            cuda_device (int, optional): Id of the gpu device to use. Defaults to -1.
        '''

        assert path is not None, "A file path is required"

        languages = {
            'Larissa': 'el',
            'Birmingham': 'en',
            'Malaga': 'es',
            'Palermo': 'it'
        }

        self.path = path
        self.use_cuda = use_cuda
        self.cuda_device = cuda_device
        self.language = languages[pilot]
        # TODO: language detection param?
        self.model = Transner(pretrained_model='bert_uncased_base_easyrights_v0.1', use_cuda=use_cuda, cuda_device=cuda_device, language_detection=True, threshold=0.8)

        self.annotation_metadata = metadata = pilot + ' - ' + service + ' - ' + os.path.basename(path)
        self.generation_metadata = {
            'where': pilot + ' - ' + service + ' - ' + 'Where - ' + os.path.basename(path),
            'when': pilot + ' - ' + service + ' - ' + 'When - ' + os.path.basename(path),
            'how': pilot + ' - ' + service + ' - ' + 'How - ' + os.path.basename(path)
        }

    def to_list(self):
        element_list = [] # Make an empty list

        for element in re.split('[.\n]', self.converted_file):
            stripped_element = element.strip()
            if stripped_element != '':	    
                element_list.append(stripped_element) #Append to list the striped element
        
        return element_list

    def do_convert(self):
        self.converted_file = doc2txt.convert_to_txt(self.path)
        return self.converted_file

    def do_annotate(self):
        sentence_list = self.to_list()

        self.ner_dict = self.model.ner(sentence_list, apply_regex=True)
        if self.language in ['es', 'en']:
            self.ner_dict = self.annotate_sutime(self.ner_dict)
        else:
            self.ner_dict = self.model.find_dates(self.ner_dict)

        self.ner_dict = annotator.aggregate_dict(self.ner_dict)

        self.ner_dict['entities'] = sorted(self.ner_dict['entities'], key=lambda ner: ner['start_offset'])

        #print(self.ner_dict)

        self.ner_dict = annotator.resolve_uri_entities(self.ner_dict, self.path)

        return self.ner_dict

    def do_generate(self):
        aggregated_ner_dict = aggregator.aggregate_entities(self.ner_dict)

        pathway_tmp = generator.generate(aggregated_ner_dict)
        json_pathway = pathway_tmp.to_json(indent=4, orient='records')
        mapped_entities = json.loads(json_pathway)

        dict_pathway = json.load(open("tools/dict_pathway.json", 'r'))

        self.pathway = {}

        #{'physical_office': [{'start', 'end'}...]}
        for key, sub_types in dict_pathway.items():
            self.pathway[key] = {}
            for sub_type in sub_types:
                self.pathway[key][sub_type] = []

        for entity in mapped_entities:
            self.pathway[self.keys_of_value(dict_pathway, entity['step'])][entity['step']].append(entity)  
        
        # {'dove': [], 'come': [], 'quando': []}

        #todo: remove return because we can read the value in the pgr object
        return self.pathway

    def export_annotation_to_doccano(self, add_confidence=False):
        filename = os.path.splitext(self.path)[0]

        doccano_dict = {}
        doccano_dict['text'] = self.ner_dict['text']
        doccano_dict['labels'] = []

        doccano_dict['meta'] = self.annotation_metadata

        for item in self.ner_dict['entities']:
            if add_confidence:
                doccano_dict['labels'].append([item['start_offset'], item['end_offset'], item['type'], item['confidence']])
            else:
                doccano_dict['labels'].append([item['start_offset'], item['end_offset'], item['type']])

        file_out = open(filename +'_ner.jsonl', 'w', encoding='utf-8')
        file_out.write(json.dumps(doccano_dict))
        file_out.write('\n')

        return doccano_dict, filename +'_ner.jsonl'

    def export_generation_to_doccano(self):
        dict_translations = json.load(open("tools/dict_translations.json", 'r'))

        filename = os.path.splitext(self.path)[0]
        pathway_jsonl = []

        for key in self.pathway:
            tmp_dict = {"text": '', "labels": [], "meta": ''}
            tmp_dict["text"] = dict_translations[self.language][key]
            tmp_dict["meta"] = self.generation_metadata[key]

            for sub_type, entities in self.pathway[key].items():
                label = dict_translations[self.language][sub_type] + ': '
                if not entities:
                    label = label + '-'
                    tmp_dict['labels'].append(label)
                else:
                    for entity in entities:
                        label = label + entity['entity'].strip() + ' , '

                    tmp_dict['labels'].append(label[:-2].strip())
            
            pathway_jsonl.append(tmp_dict)

        file_out = open(filename + '_pathway.jsonl', 'w', encoding='utf-8')

        return_string = ''

        for element in pathway_jsonl:
            string_element = str(json.dumps(element, ensure_ascii=False))
            file_out.write(string_element)
            file_out.write('\n')

            return_string = return_string + string_element + '\n'

        return return_string, filename + '_pathway.jsonl'

    def keys_of_value(self, dct, value):
        for k in dct:
            if isinstance(dct[k], list):
                if value in dct[k]:
                    return k
            else:
                if value == dct[k]:
                    return k

    def annotate_sutime(self, ner_dict):
        for item in ner_dict:
            text = item['sentence']
            jar_files = os.path.join('python-sutime/', 'jars')
            sutime = sutime_mod.SUTime(jars=jar_files, mark_time_ranges=True)

            json = sutime.parse(text)
            
            for item_sutime in json:
                item['entities'].append({'type': 'TIME', 'value': item_sutime['text'], 'confidence': 0.8, 'offset': item_sutime['start']})

        return ner_dict