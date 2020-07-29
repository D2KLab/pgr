import pdb
import argparse
from transner import Transner
import doc2txt, aggregator, generator
import json

import spacy
from spacy import displacy

import pandas as pd
import os

def text_to_doccano(ner_dict, filename):
    labels = []

    label = {}
    label['text'] = ner_dict['text']
    label['labels'] = []
    label['meta'] = filename
    for entity in ner_dict['entities']:
        for token in ner_dict['entities'][entity]:
            label_add = []
            label_add.append(token['start_offset'])
            label_add.append(token['end_offset'])
            label_add.append(entity)
            label['labels'].append(label_add)

        labels.append(label)
    
    file_out = open('./doccano_annotated.json', 'w', encoding='utf-8')
    file_out.write(str(json.dumps(labels[0], ensure_ascii=False)))
    file_out.write('\n')

def main(strings=None, files=None):
    model = Transner(pretrained_model='multilang_uncased', use_cuda=True, cuda_device=1)

    file = doc2txt.convert_to_txt(files)

    ner_dict = model.ner(doc2txt.text2str(file), apply_regex=False)
    print('ner finished, traslating to dict...')
    ner_dict = model.find_from_gazetteers(ner_dict)
    
    aggregated_ner_dict = aggregator.aggregate_ner_dict(ner_dict)
    text_to_doccano(aggregated_ner_dict, os.path.splitext(os.path.basename(files))[0])

    pathway = generator.generate(aggregated_ner_dict)

    json_pathway = pathway.to_json(orient='records')

if __name__ == '__main__':
    """Input example:

        $python usage.py --strings \
            "Mario è nato a Milano" \
            "The war of Orleans"
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s',
        '--strings', 
        nargs='+', 
        help='List of strings for the NER', 
        required=False)

    parser.add_argument(
        '-f',
        '--files',
        help='List of files to be converted before transner',
        required=False
    )

    parser.add_argument(
        '-e',
        '--encoding',
        help='Specify encoding. Default is UTF-8.',
        required=False
    )
    args = parser.parse_args()


    main(files=args.files)

    
    
