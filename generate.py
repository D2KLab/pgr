import argparse
import json
import os
from pgr import PathwayGenerator

def main(path, pilot, service):   
    pgr = PathwayGenerator(path=path, pilot=pilot, service=service, use_cuda=True, cuda_device=4, model='en')
    pathway = pgr.do_generate()
    pathway_dict, pathway_path = pgr.export_generation_to_doccano()

    print('Generation process ended. You can find the jsonl at the following path: {}'.format(pathway_path))

if __name__ == '__main__':
    """Input example:

        $python generate.py --file \
            filename.json
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