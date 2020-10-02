import argparse
import os 
import re
import json

from Transner import Transner
from doc2txt import doc2txt

from tools import annotator, aggregator, generator

import importlib
sutime_mod = importlib.import_module("python-sutime.sutime")

def pathway_to_doccano(json_pathway, path):
    filename = os.path.splitext(path)[0]
    pathway_jsonl = []
    where_dict = {"text": "where", "labels": [], "meta": filename}
    how_dict = {"text": "how", "labels": [], "meta": filename}
    when_dict = {"text": "when", "labels": [], "meta": filename}

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
    model = Transner(pretrained_path='Transner/transner/multilang_uncased', use_cuda=False, cuda_device=2)
    return model.ner(sentence_list, apply_regex=True)

def annotate_sutime(ner_dict):
    for item in ner_dict:
        text = item['sentence']
        jar_files = os.path.join('python-sutime/', 'jars')
        sutime = sutime_mod.SUTime(jars=jar_files, mark_time_ranges=True)

        json = sutime.parse(text)
        
        for item_sutime in json:
            item['entities'].append({'type': 'TIME', 'value': item_sutime['text'], 'confidence': 0.8, 'offset': item_sutime['start']})

    return ner_dict

def main(path=None):

    # convert.py
    converted_file = doc2txt.convert_to_txt(path)

    # annotate.py
    sentence_list = to_list(converted_file)

    ner_dict = annotate_transner(sentence_list)
    ner_dict = annotate_sutime(ner_dict)

    ner_dict = annotator.aggregate_dict(ner_dict)

    #ner_dict = resolve_uri_entities(ner_dict, path)

    annotator.export_to_doccano(ner_dict, os.path.splitext(path)[0])

    # aggregate.py
    aggregated_ner_dict = aggregator.aggregate_entities(ner_dict)

    # generate.py
    pathway = generator.generate(aggregated_ner_dict)
    json_pathway = pathway.to_json(orient='records')

    pathway_to_doccano(json.loads(json_pathway), path)

def run(path=None, generate_pathway=False):
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

        return pathway_to_doccano(json.loads(json_pathway), path)
    
    return annotator.export_to_doccano(ner_dict, os.path.splitext(path)[0])

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
        '--encoding',
        help='Specify encoding. Default is UTF-8.',
        required=False
    )
    args = parser.parse_args()


    main(path=args.path)

    
    
