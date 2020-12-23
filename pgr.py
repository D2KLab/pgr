import argparse
import os 
import re
import json
import pdb

from transner import Transner
from doc2txt import doc2txt

from tools import annotator, aggregator, generator

import importlib
sutime_mod = importlib.import_module("python-sutime.sutime")

class PathwayGenerator():
    def __init__(self, path, pilot, service, use_cuda=False, cuda_device=-1, model=None):
        ''' PathwayGenerator object constructor

        Args:
            path (str): path of the file from which the pathway is generated.
            pilot (str): name of the pilot.
            service (str): name of the service considered.
            use_cuda (bool): flag to use gpu model.
            cuda_device (int, optional): Id of the gpu device to use. Defaults to -1.
        '''

        assert path is not None, "A file path is required"

        languages = {
            'Larissa': 'el',
            'Birmingham': 'en',
            'Malaga': 'es',
            'Palermo': 'it'
        }

        self.path = path
        if os.path.splitext(path)[-1] == '.txt':
            self.converted_file = doc2txt.purge_urls(open(path, 'r').read(), os.path.splitext(path)[0])
        self.use_cuda = use_cuda
        self.cuda_device = cuda_device
        self.language = languages[pilot]
        # TODO: language detection param?
        if model is None:
            self.model = Transner(pretrained_model='bert_uncased_base_easyrights_v0.1', use_cuda=use_cuda, cuda_device=cuda_device, language_detection=True, threshold=0.85)
        else:
            self.model = Transner(pretrained_model='bert_uncased_'+model, use_cuda=use_cuda, cuda_device=cuda_device, language_detection=True, threshold=0.85)

        self.annotation_metadata = metadata = pilot + ' - ' + service + ' - ' + os.path.basename(path)
        self.generation_metadata = {
            'where': pilot + ' - ' + service + ' - ' + 'Where - ' + os.path.basename(path) + ' - ',
            'when': pilot + ' - ' + service + ' - ' + 'When - ' + os.path.basename(path) + ' - ',
            'how': pilot + ' - ' + service + ' - ' + 'How - ' + os.path.basename(path) + ' - '
        }

    def to_list(self):
        element_list = [] # Make an empty list

        for element in re.split('[.\n]', self.converted_file):
            stripped_element = element.strip()
            if stripped_element != '':	    
                element_list.append(stripped_element) #Append to list the striped element
        
        return element_list

    def do_convert(self):
        self.converted_file = doc2txt.convert_to_txt(self.path)
        return self.converted_file

    def do_split(self):
        '''return [['test 1 of the section 1', 'test 2 of the section 1', 'test 3 of the section 1']#,
                #['test 1 of the section 2', 'test 2 of the section 2'],
                #['test 1 of the section 3']
        ]'''
        sentence_list = self.to_list()

        model = CrossEncoder('MODEL_PATH', num_labels=1)
        scores = []
        for i in range(0, len(sentence_list)-1):
            current_sentence = sentence_list[i]
            next_sentence = sentence_list[i+1]

            score = model.predict([current_sentence, next_sentence])
            scores.append(score)
        
        sections = [] # sections = [['section1'], ['section2'], ... , ['sectionN']]
        section_text = []
        section_text.append(sentence_list[0])
        for i in range(0, len(scores)):
            if scores[i] >= threshold:
                section_text.append(sentence_list[i+1])              
            else:
                sections.append(section_text)
                section_text = []
                section_text.append(sentence_list[i+1])
        sections.append(section_text)

        return sections

    def do_annotate(self, sentence_list):
        self.ner_dict = self.model.ner(sentence_list, apply_regex=True)
        if self.language in ['es', 'en']:
            self.ner_dict = self.annotate_sutime(self.ner_dict)
        else:
            self.ner_dict = self.model.find_dates(self.ner_dict)

        self.ner_dict = annotator.aggregate_dict(self.ner_dict)

        self.ner_dict['entities'] = sorted(self.ner_dict['entities'], key=lambda ner: ner['start_offset'])

        self.ner_dict = annotator.resolve_uri_entities(self.ner_dict, self.path)

        return self.ner_dict

    def do_generate(self):
        if os.path.splitext(self.path)[-1] == '.json':
            self.ner_dict = json.load(open(self.path, 'r'))
        aggregated_ner_dict = aggregator.aggregate_entities(self.ner_dict)
        #aggregated_ner_dict = self.ner_dict = {'text': 'test 1 of the section 1.\ntest 2 of the section 1.\ntest 3 of the section 1.\n', 'entities': {'LOCATION': [{'value': 'test', 'confidence': 0.9737, 'start_offset': 0, 'end_offset': 4}], 'ORGANIZATION': [{'value': 'test', 'confidence': 0.9676, 'start_offset': 25, 'end_offset': 29}], 'TIME': [{'value': 'test', 'confidence': 0.9573, 'start_offset': 50, 'end_offset': 54}]}}
        json_pathway = generator.generate(aggregated_ner_dict)
        mapped_entities = json.loads(json_pathway)

        dict_pathway = json.load(open("tools/dict_pathway.json", 'r'))

        self.pathway = {}

        #{'physical_office': [{'start', 'end'}...]}
        for key, sub_types in dict_pathway.items():
            self.pathway[key] = {}
            for sub_type in sub_types:
                self.pathway[key][sub_type] = []

        for entity in mapped_entities:
            self.pathway[self.keys_of_value(dict_pathway, entity['step'])][entity['step']].append(entity)  
        
        # {'dove': [], 'come': [], 'quando': []}

        #todo: remove return because we can read the value in the pgr object
        return self.pathway

    def export_annotation_to_doccano(self, add_confidence=False):
        filename = os.path.splitext(self.path)[0]

        doccano_dict = {}
        doccano_dict['text'] = self.ner_dict['text']
        doccano_dict['labels'] = []

        doccano_dict['meta'] = self.annotation_metadata

        for item in self.ner_dict['entities']:
            if add_confidence:
                doccano_dict['labels'].append([item['start_offset'], item['end_offset'], item['type'], item['confidence']])
            else:
                doccano_dict['labels'].append([item['start_offset'], item['end_offset'], item['type']])

        file_out = open(filename +'_ner.jsonl', 'w', encoding='utf-8')
        file_out.write(json.dumps(doccano_dict))
        file_out.write('\n')

        return doccano_dict, filename +'_ner.jsonl'

    def export_generation_to_doccano(self, pathway=None):
        dict_translations = json.load(open("tools/dict_translations.json", 'r'))

        filename = os.path.splitext(self.path)[0]
        pathway_jsonl = []

        for key in pathway:
            tmp_dict = {"text": '', "labels": [], "meta": ''}
            tmp_dict["text"] = key
            

            for step, step_dict in pathway[key].items():
                tmp_dict["meta"] = self.generation_metadata[step] + key
                for sub_type, entities in step_dict.items():
                    label = dict_translations[self.language][step] + ' - ' + dict_translations[self.language][sub_type] + ': '
                    if len(entities) == 0:
                        label = label + '-'
                        tmp_dict['labels'].append(label)
                    else:
                        for entity in entities:
                            label = label + entity['entity'].strip() + ' , '

                        tmp_dict['labels'].append(label[:-2].strip())                  
            
            pathway_jsonl.append(tmp_dict)

        file_out = open(filename + '_pathway.jsonl', 'w', encoding='utf-8')

        return_string = ''

        for element in pathway_jsonl:
            string_element = str(json.dumps(element, ensure_ascii=False))
            file_out.write(string_element)
            file_out.write('\n')

            return_string = return_string + string_element + '\n'

        return return_string, filename + '_pathway.jsonl'

    def keys_of_value(self, dct, value):
        for k in dct:
            if isinstance(dct[k], list):
                if value in dct[k]:
                    return k
            else:
                if value == dct[k]:
                    return k

    def annotate_sutime(self, ner_dict):
        for item in ner_dict:
            text = item['sentence']
            jar_files = os.path.join('python-sutime/', 'jars')
            sutime = sutime_mod.SUTime(jars=jar_files, mark_time_ranges=True)

            json = sutime.parse(text)
            
            time_type = self.model.check_opening_time(item['entities'])

            for item_sutime in json:
                if not self.model.find_overlap(item['entities'], item_sutime['start'], item_sutime['end']):
                    item['entities'].append({'type': time_type, 'value': item_sutime['text'], 'confidence': 0.85, 'offset': item_sutime['start']})

        return ner_dict

def main(path=None, empty=False, convert=True, pilot='', service=''):
    pgr = PathwayGenerator(path=path, pilot=pilot, service=service, use_cuda=False, cuda_device=0, model='en')
    converted_file = pgr.do_convert()
    sentence_list = pgr.do_split()
    full_ner_dict = {}
    count = 1
    for sentence in sentence_list:
        pgr.model.reset_preprocesser()
        ner_dict = pgr.do_annotate(sentence)
        pathway = pgr.do_generate()
        label = 'Step'+str(count)
        full_ner_dict[label] = pathway
        count = count + 1
    pathway_dict, pathway_path = pgr.export_generation_to_doccano(full_ner_dict)
    print(pathway_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f',
        '--path',
        help='List of files to be converted before transner',
        required=True
    )

    parser.add_argument(
        '-e',
        '--empty',
        help='Specify if the jsonl output for doccano needs to be empty. Default is false.',
        required=False
    )
    parser.add_argument(
        '-c',
        '--convert',
        help='Specify if you need the file conversion. Default is true.',
        required=False
    )

    parser.add_argument(
        '-p',
        '--pilot',
        help='Specify pilot.',
        required=False
    )

    parser.add_argument(
        '-s',
        '--service',
        help='Specify service.',
        required=False
    )
    args = parser.parse_args()


    main(path=args.path, empty=args.empty, convert=args.convert, pilot=args.pilot, service=args.service)