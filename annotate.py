import doc2txt
import argparse
from transner import Transner
import json
import os

def main(files=None):
    model = Transner(pretrained_model='multilang_uncased', use_cuda=True, cuda_device=4)
    file = open(files, 'r')
    text_list = doc2txt.text2str(file.read())

    ner_dict = model.ner(text_list)

    json_file = json.dumps(ner_dict)
    f = open(os.path.splitext(files)[0] +'.json', 'w')
    f.write(json_file)
    f.close()

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

    main(files=args.file)