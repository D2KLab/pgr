import argparse

from pgr import PathwayGenerator

def main(path, pilot, service):   
    pgr = PathwayGenerator(path=path, pilot=pilot, service=service, use_cuda=True, cuda_device=4, model='en')
    ner_dict = pgr.do_annotate()
    doccano_dict, ner_path = pgr.export_annotation_to_doccano()

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