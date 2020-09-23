from tools import doc2txt
import argparse

def main(files=None):
    file = doc2txt.convert_to_txt(files)

if __name__ == '__main__':
    """Input example:

        $python convert.py --file \
            filename
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