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

    return return_string

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

def run(path=None, generate_pathway=False, pilot='', service=''):
    print('Document successfully received')

    print(path)
    # convert.py
    converted_file = doc2txt.convert_to_txt(path)

    print('Document successfully converted')

    # annotate.py
    sentence_list = to_list(converted_file)

    ner_dict = annotate_transner(sentence_list)
    #ner_dict = annotate_sutime(ner_dict)

    ner_dict = annotator.aggregate_dict(ner_dict)

    #ner_dict = resolve_uri_entities(ner_dict, path)
    print('Document successfully annotated')

    if generate_pathway:
        # aggregate.py
        aggregated_ner_dict = aggregator.aggregate_entities(ner_dict)
        print('Data successfully aggregated')

        # generate.py
        pathway = generator.generate(aggregated_ner_dict)
        json_pathway = pathway.to_json(indent=4, orient='records')
        print('Pathway successfully generated')

        return pathway_to_doccano(json.loads(json_pathway), path, pilot, service)
    
    return annotator.export_to_doccano(ner_dict, path, pilot, service)

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

    
    
