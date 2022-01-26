import argparse
import json
import os
from pgr import PathwayGenerator

def main(path, pilot, service):   
    pgr = PathwayGenerator(file_path=path, pilot=pilot, service=service, use_cuda=True, cuda_device=4, annotation_model='en')
    ner_dict = pgr.do_annotate(pgr.to_list())
    doccano_dict, ner_path = pgr.export_annotation_to_doccano()
    response = input('Do you want to export the ner_dict object into a .json file? y/n:\t')
    if response == 'y':
        file_out = open(os.path.splitext(pgr.path)[0] +'_ner.json', 'w', encoding='utf-8')
        file_out.write(json.dumps(ner_dict))
        file_out.write('\n')
    print('Annotation process ended. You can find the jsonl at the following path: {}'.format(ner_path))

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
        required=True
    )

    parser.add_argument(
        '-p',
        '--pilot',
        help='Specify pilot.',
        required=True
    )

    parser.add_argument(
        '-s',
        '--service',
        help='Specify service.',
        required=True
    )

    args = parser.parse_args()

    main(path=args.file, pilot=args.pilot, service=args.service)