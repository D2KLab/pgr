import doc2txt
import argparse
from transner import Transner
import json
import os

import pdb

from python_sutime.sutime import SUTime

def annotate_transner(sentence_list):
    model = Transner(pretrained_model='multilang_uncased', use_cuda=True, cuda_device=4)
    return model.ner(sentence_list, apply_regex=True)

def annotate_sutime(ner_dict):
    for item in ner_dict:
        text = item['sentence']
        jar_files = os.path.join(os.path.dirname(__file__) + 'python_sutime/', 'jars')
        sutime = SUTime(jars=jar_files, mark_time_ranges=True)

        json = sutime.parse(text)
        
        for item_sutime in json:
            item['entities'].append({'type': 'TIME', 'value': item_sutime['text'], 'confidence': 0.8, 'offset': item_sutime['start']})

    return ner_dict

def export_to_json(ner_dict, path):
    json_file = json.dumps(ner_dict, indent=4)
    f = open(path +'_ner.json', 'w')
    f.write(json_file)
    f.close()

def aggregate_dict(ner_dict):
    aggregated_dict = {
        'text': '', 
        'entities': []
    }
    offset = 0

    for element in ner_dict:
        for entity in element['entities']:          
            start_offset = offset + entity['offset']
            end_offset = offset + entity['offset'] + len(entity['value'])
            
            aggregated_dict['entities'].append({
                    'value': entity['value'],
                    'confidence': entity['confidence'],
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                    'type': entity['type'] 
                })
        
        offset = offset + len(element['sentence'])
        aggregated_dict['text'] = aggregated_dict['text'] + element['sentence']

    return aggregated_dict

def export_to_doccano(ner_dict, path):

    doccano_dict = {}
    doccano_dict['text'] = ner_dict['text']
    doccano_dict['labels'] = []

    doccano_dict['meta'] = os.path.basename(path)

    for item in ner_dict['entities']:
        doccano_dict['labels'].append([item['start_offset'], item['end_offset'], item['type']])

    file_out = open(path +'_ner.jsonl', 'w', encoding='utf-8')
    file_out.write(json.dumps(doccano_dict))
    file_out.write('\n')

def main(path=None):   
    sentence_list = doc2txt.to_list(open(path, 'r').read())

    ner_dict = annotate_transner(sentence_list)
    ner_dict = annotate_sutime(ner_dict)
   
    ner_dict = aggregate_dict(ner_dict)
    export_to_json(ner_dict, os.path.splitext(path)[0])
    export_to_doccano(ner_dict, os.path.splitext(path)[0])

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