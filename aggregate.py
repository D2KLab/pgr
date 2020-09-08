import aggregator
import argparse

import json
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
    
    file_out = open(filename +'_ner.json', 'w', encoding='utf-8')
    file_out.write(str(json.dumps(labels[0], ensure_ascii=False)))
    file_out.write('\n')

def main(files=None):
    json_file = open(files, 'r')
    ner_dict = json.load(json_file)

    aggregated_ner_dict = aggregator.aggregate_ner_dict(ner_dict)
    text_to_doccano(aggregated_ner_dict, os.path.splitext(files)[0])

    json_out = json.dumps(aggregated_ner_dict)
    f = open(os.path.splitext(files)[0] +'.json', 'w')
    f.write(json_out)
    f.close()

if __name__ == '__main__':
    """Input example:

        $python convert.py --file \
            filename.json
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f',
        '--file',
        help='List of files to be converted before transner',
        required=False
    )

    args = parser.parse_args()

    main(files=args.file)