import pdb
import argparse
from transner import Transner
from doc2txt import convert_to_txt, text2str

import spacy
from spacy import displacy


def main(strings=None, files=None):
    model = Transner(pretrained_model='multilang_uncased', use_cuda=False)
    file = convert_to_txt(files)
    strings = text2str(file)

    ner_dict = model.ner(strings, apply_regex=True)

    ner_dict = model.find_from_gazetteers(ner_dict)
    #ner_dict.append({'ents': ['PERSON', 'LOCATION', 'ORGANIZATION', 'MISCELLANEOUS', 'IT_FISCAL_CODE', 'EU_IBAN', 'NL_CITIZEN_SERVICE_NUMBER', 'UK_NATIONAL_ID_NUMBER', 'EU_PHONE_NUMBER', 'EMAIL_ADDRESS', 'IPV4_ADDRESS']})
    #nlp = spacy.load("en_core_web_sm")
    #doc = nlp(strings)
    #displacy.serve(ner_dict, style="ent", manual=True)
    #options = {'ents': ['PERSON', 'LOCATION', 'ORGANIZATION', 'MISCELLANEOUS', 'IT_FISCAL_CODE', 'EU_IBAN', 'NL_CITIZEN_SERVICE_NUMBER', 'UK_NATIONAL_ID_NUMBER', 'EU_PHONE_NUMBER', 'EMAIL_ADDRESS', 'IPV4_ADDRESS']}
    #displacy.serve(ner_dict, style='ent', options=options)
    #print(ner_dict)
    file_out = open('out.txt', 'w')
    for ner in ner_dict:
        file_out.write(ner['sentence'])
        for ent in ner['entities']:
            file_out.write(ent['type'])
            file_out.write(ent['value'])
            file_out.write('\n')
    file_out.close()


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
    args = parser.parse_args()

    main(files=args.files)
    
    