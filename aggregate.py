import aggregator
import argparse
import re
import pdb

import json
import os

def export_to_json(ner_dict, path):
    json_file = json.dumps(ner_dict, indent=4)
    filename = re.sub('_ner.json', '_cluster.json', path)
    f = open(filename, 'w')
    f.write(json_file)
    f.close()

def main(path=None):
    json_file = open(path, 'r')
    ner_dict = json.load(json_file)

    aggregated_ner_dict = aggregator.aggregate_entities(ner_dict)

    export_to_json(aggregated_ner_dict, path)
   

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

    main(path=args.file)