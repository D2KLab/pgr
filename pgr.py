import argparse
import os 
import re
import json
import pdb

from transner import Transner
from doc2txt import doc2txt

from tools import annotator, aggregator, generator

from sentence_transformers.cross_encoder import CrossEncoder

import importlib
sutime_mod = importlib.import_module("python-sutime.sutime")

class PathwayGenerator():
    def __init__(self, 
                file_path, 
                pilot, 
                service, 
                use_cuda=False, 
                cuda_device=-1, 
                annotation_model='en', 
                section_split_model='section_split/models/training_unfolding_structure-2020-12-22_11-07-07_distilroberta-base/pytorch_model.bin'):

        ''' PathwayGenerator object constructor

        Args:
            path (str): path of the file from which the pathway is generated.
            pilot (str): name of the pilot.
            service (str): name of the service considered.
            use_cuda (bool): flag to use gpu model.
            cuda_device (int, optional): Id of the gpu device to use. Defaults to -1.
            annotation_model (str, optional): The name of the annotation model
            section_split_model (str, optional): The name of the section splitter model
        '''

        assert file_path is not None, "A file path is required"

        languages = {
            'Larissa': 'el',
            'Birmingham': 'en',
            'Malaga': 'es',
            'Palermo': 'it'
        }

        self.path = file_path
        if os.path.splitext(self.path)[-1] == '.txt':
            self.converted_file = doc2txt.purge_urls(open(self.path, 'r').read(), os.path.splitext(self.path)[0])
        self.use_cuda = use_cuda
        self.cuda_device = cuda_device
        self.language = languages[pilot]
        # TODO: language detection param?
        if annotation_model is None:
            self.annotation_model = Transner(pretrained_model='bert_uncased_base_easyrights_v0.1', use_cuda=use_cuda, cuda_device=cuda_device, language_detection=True, threshold=0.85, args={"use_multiprocessing": False})
        else:
            self.annotation_model = Transner(pretrained_model='bert_uncased_'+annotation_model, use_cuda=use_cuda, cuda_device=cuda_device, language_detection=True, threshold=0.85, args={"use_multiprocessing": False})

        self.section_split_model = CrossEncoder(section_split_model, num_labels=1)

        self.annotation_metadata = metadata = pilot + ' - ' + service + ' - ' + os.path.basename(self.path)

        self.generation_metadata = pilot + ' - ' + service + ' - ' + os.path.basename(self.path) + ' - '

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

    def do_split(self, threshold=0.5):
        sentence_list = self.to_list()

        scores = []
        for i in range(0, len(sentence_list)-1):
            current_sentence = sentence_list[i]
            next_sentence = sentence_list[i+1]

            score = self.section_split_model.predict([current_sentence, next_sentence])
            scores.append(score)
        
        sections = []
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
        self.ner_dict = self.annotation_model.ner(sentence_list, apply_regex=True)
        if self.language in ['es', 'en']:
            self.ner_dict = self.annotate_sutime(self.ner_dict)
        else:
            self.ner_dict = self.annotation_model.find_dates(self.ner_dict)

        self.ner_dict = annotator.aggregate_dict(self.ner_dict)

        self.ner_dict['entities'] = sorted(self.ner_dict['entities'], key=lambda ner: ner['start_offset'])

        self.ner_dict = annotator.resolve_uri_entities(self.ner_dict, self.path)

        return self.ner_dict

    def do_generate(self):
        if os.path.splitext(self.path)[-1] == '.json':
            self.ner_dict = json.load(open(self.path, 'r'))
        aggregated_ner_dict = aggregator.aggregate_entities(self.ner_dict)

        json_pathway = generator.generate(aggregated_ner_dict)
        mapped_entities = json.loads(json_pathway)

        dict_pathway = json.load(open("tools/dict_pathway.json", 'r'))

        self.pathway = {}

        for key, sub_types in dict_pathway.items():
            self.pathway[key] = {}
            for sub_type in sub_types:
                self.pathway[key][sub_type] = []

        for entity in mapped_entities:
            self.pathway[self.keys_of_value(dict_pathway, entity['step'])][entity['step']].append(entity)  

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
                tmp_dict["meta"] = self.generation_metadata + key
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
            
            time_type = self.annotation_model.check_opening_time(item['entities'])

            for item_sutime in json:
                if not self.annotation_model.find_overlap(item['entities'], item_sutime['start'], item_sutime['end']):
                    item['entities'].append({'type': time_type, 'value': item_sutime['text'], 'confidence': 0.85, 'offset': item_sutime['start']})

        return ner_dict

    def sections_to_doccano(self, sections):
        count, step = 0, 1 
        doccano_dict = {'text': '', 'labels': []}

        for section in sections:
            initial_count, final_count = count, 0

            for sentence in section:
                doccano_dict['text'] = doccano_dict['text'] + sentence + '.\n'
                final_count = final_count + len(sentence) + 2

            doccano_dict['labels'].append([initial_count, initial_count+final_count-1, 'Step'+str(step)])
            step = step + 1
            count = initial_count+final_count

        return doccano_dict

def main(path=None, empty=False, convert=True, pilot='', service=''):
    pgr = PathwayGenerator(file_path=path, pilot=pilot, service=service, use_cuda=False, cuda_device=0, annotation_model='el', section_split_model='section_split/models/training_unfolding_structure-2020-12-22_11-07-07_distilroberta-base')
    converted_file = pgr.do_convert()
    sections = pgr.do_split()
    file_out = open('section_log.jsonl', 'w', encoding='utf-8')
    test_section = pgr.sections_to_doccano(sections)
    file_out.write(json.dumps(test_section))
    full_ner_dict = {}
    count = 1
    for section in sections:
        pgr.annotation_model.reset_preprocesser()
        ner_dict = pgr.do_annotate(section)
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
        required=True
    )

    parser.add_argument(
        '-s',
        '--service',
        help='Specify service.',
        required=True
    )
    args = parser.parse_args()


    main(path=args.path, empty=args.empty, convert=args.convert, pilot=args.pilot, service=args.service)