import generator
import argparse

import json
import os

def pathway_to_doccano(json_pathway, filename):
    pathway_jsonl = []
    where_dict = {"text": "where", "labels": [], "meta": filename}
    how_dict = {"text": "how", "labels": [], "meta": filename}
    when_dict = {"text": "when", "labels": [], "meta": filename}

    for entity in json_pathway:
        if len(entity["entity"].strip()) > 0:
            if entity["step"] == "where":
                if entity["entity"].strip() not in where_dict["labels"]:
                    where_dict["labels"].append(entity["entity"].strip())
            elif entity["step"] == "how":
                if entity["entity"].strip() not in how_dict["labels"]:
                    how_dict["labels"].append(entity["entity"].strip())
            elif entity["step"] == "when":
                if entity["entity"].strip() not in when_dict["labels"]:
                    when_dict["labels"].append(entity["entity"].strip())
    
    pathway_jsonl.append(where_dict)
    pathway_jsonl.append(when_dict)
    pathway_jsonl.append(how_dict)
    file_out = open(filename +'_pathway.jsonl', 'w', encoding='utf-8')
    for element in pathway_jsonl:
        file_out.write(str(json.dumps(element, ensure_ascii=False)))
        file_out.write('\n')

def main(files=None):
    json_file = open(files, 'r')
    aggregated_ner_dict = json.load(json_file)

    pathway = generator.generate(aggregated_ner_dict)
    json_pathway = pathway.to_json(orient='records')

    pathway_to_doccano(json.loads(json_pathway), os.path.splitext(files)[0])

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