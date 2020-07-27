import pdb
import argparse
from transner import Transner
import doc2txt, aggregator, generator

import spacy
from spacy import displacy

import pandas as pd


def main(strings=None, files=None):
    model = Transner(pretrained_model='multilang_uncased', use_cuda=True, cuda_device=1)

    file = doc2txt.convert_to_txt(files)
    #strings = text2str(file)

    ner_dict = model.ner(doc2txt.text2str(file), apply_regex=False)
    print('ner finished, traslating to dict...')
    ner_dict = model.find_from_gazetteers(ner_dict)

    '''#SPACY INTEGRATION
    ner_dict.append({'ents': ['PERSON', 'LOCATION', 'ORGANIZATION', 'MISCELLANEOUS', 'EU_PHONE_NUMBER', 'EMAIL_ADDRESS']})
    #nlp = spacy.load("en_core_web_sm")
    #doc = nlp(strings)
    displacy.serve(ner_dict, style="ent", manual=True)
    options = {'ents': ['PERSON', 'LOCATION', 'ORGANIZATION', 'MISCELLANEOUS', 'EU_PHONE_NUMBER', 'EMAIL_ADDRESS']}
    displacy.serve(ner_dict, style='ent', options=options)'''

    
    aggregated_ner_dict = aggregator.aggregate_ner_dict(ner_dict)
    
    pathway = generator.generate(aggregated_ner_dict)

    pathway.to_json('./output_values.txt', orient='records')

    pdb.set_trace()
    
    
    # output a file with all the annotations
    '''
    file_out = open('out.txt', 'w')
    for ner in ner_dict:
        file_out.write(ner['sentence'])
        for ent in ner['entities']:
            file_out.write(ent['type'])
            file_out.write(ent['value'])
            file_out.write('\n')
    file_out.close()'''

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

    
    