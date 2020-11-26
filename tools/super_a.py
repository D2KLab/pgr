import json
import os
import argparse
import inflection as inf
from itertools import chain

def manual_annotation(tokens, file_out, statistics_file):
    words = [tok.split(' ')[0] for tok in tokens]
    tags = [tok.split(' ')[1].strip() for tok in tokens]

    while True:
        # print the sentence with tags
        count = 0
        for word, tag in zip(words, tags):
            count = count + 1
            print('{' + str(count) + '}' +word + '[' + tag + '] ', end='')
        print('\n')

        #TODO: insert statistics
        #deleting_elements = 

        elements = input('Write here the word/words that have to be annotated: ')
        sentence_indexes = []

        # exit from loop if there are no more annotations to do
        if elements == '':
            break
        for element in elements.split(' '):
            if int(element) < 0 or int(element) > len(words):
                print('The element is not present in the sentence.\n')
                continue
            else:
                sentence_indexes.append(int(element)-1)

        annotations = ['PROC', 'DOC']
        annotation_sym = input('Which type of annotation? Value accepted are PROC[0], DOC[1]: ')
        if annotation_sym not in ['0', '1']:
            print('The element is not present in the accepted values.\n')
            continue

        # default: substitute the annotation
        substitute = True

        # check if there are elements with some other tag
        for idx in sentence_indexes:
            if tags[idx] != 'O':
                response = input('The element ' + words[idx] + ' has already the tag ' + tags[idx] + ', do you want to overwrite it? y/n : ')
                if response == 'n':
                    substitute = False

        if substitute:
            # first element begins with B-
            tags[sentence_indexes[0]] = 'B-'+annotations[int(annotation_sym)]
            for idx in sentence_indexes[1:]:
                # other elements has I-
                tags[idx] = 'I-'+annotations[int(annotation_sym)]
        
        break

    # write to file the new elements modified
    for word, tag in zip(words, tags):
        file_out.write(word + ' ' + tag + '\n')
    file_out.write('\n')

def substitute_hits(tokens, path, classes):
    # open up taxonomy for documents and procedures and put them into a list
    file_classes = json.load(open(classes, 'r'))
    elements = list(chain.from_iterable(file_classes.values()))
    
    # open the final modified conll file: name is as the input with _refactored
    file_out = open(os.path.splitext(path)[0] + '_refactored.conll', 'w')
    statistics_file = open('statistics.txt', 'w')

    # sentence collect all the elements of a sentence
    sentence = []
    found_hit = False

    for token in tokens:
        # if at the end of the sentence (row with '\n' only) we don't have hits, we continue the loop
        if token == '\n':
            if found_hit is True:
                manual_annotation(sentence, file_out, statistics_file)
            else:
                for token in sentence:
                    file_out.write(token)
                file_out.write('\n')

            found_hit = False  
            sentence = []
            continue

        tok = token.split(' ')[0]
        sentence.append(token)

        # use singularize to hit also the plural nouns
        if inf.singularize(tok).lower() in elements:
            found_hit = True

def main(path, classes):
    # open file data to collect the tokens
    file_data = open(path, 'r')
    tokens = file_data.readlines()
    file_data.close()

    substitute_hits(tokens, path, classes)

# python3 tools/super_a.py -f datasets/wikiner/wikiner_conll/it/wikinerIT.conll.test -c tools/entity_classes_it.json
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f',
        '--file',
        help='CONLL file location.',
        required=True
    )
    parser.add_argument(
        '-c', 
        '--classes', 
        help='filters of class labels', 
        required=True)

    args = parser.parse_args()

    main(path=args.file, classes=args.classes)
    