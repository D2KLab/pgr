import argparse
from transner import Transner
import os
import re

from tools import annotator

import importlib
sutime_mod = importlib.import_module("python-sutime.sutime")

def to_list(data):
    element_list = [] # Make an empty list

    for element in re.split('[.\n]', data):
        stripped_element = element.strip()
        if stripped_element != '':	    
            element_list.append(stripped_element) #Append to list the striped element
    
    return element_list

def annotate_transner(sentence_list):
    model = Transner(pretrained_model='bert_uncased_base_easyrights_v0.1', use_cuda=False, cuda_device=2, language_detection=True, threshold=0.8)
    return model.ner(sentence_list, apply_regex=True), model

def annotate_sutime(ner_dict):
    for item in ner_dict:
        text = item['sentence']
        jar_files = os.path.join(os.path.dirname(__file__) + 'python-sutime/', 'jars')
        sutime = sutime_mod.SUTime(jars=jar_files, mark_time_ranges=True)

        json = sutime.parse(text)
        
        for item_sutime in json:
            item['entities'].append({'type': 'TIME', 'value': item_sutime['text'], 'confidence': 0.8, 'offset': item_sutime['start']})

    return ner_dict

def main(path=None):   
    sentence_list = to_list(open(path, 'r').read())

    ner_dict, model = annotate_transner(sentence_list)
    #ner_dict = annotate_sutime(ner_dict)
    ner_dict = model.find_dates(ner_dict)

    ner_dict = annotator.aggregate_dict(ner_dict)

    #ner_dict = resolve_uri_entities(ner_dict, path)

    annotator.export_to_json(ner_dict, os.path.splitext(path)[0])
    annotator.export_to_doccano(ner_dict, os.path.splitext(path)[0])

if __name__ == '__main__':
    """Input example:

        $python annotate.py --file \
            filename.txt
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f',
        '--file',
        help='List of files to be converted before transner',
        required=False
    )

    args = parser.parse_args()

    main(path=args.file)