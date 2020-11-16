import json
import os 
import re

def export_to_json(ner_dict, path):
    json_file = json.dumps(ner_dict, indent=4)
    f = open(path +'_ner.json', 'w')
    f.write(json_file)
    f.close()

def aggregate_dict(ner_dict):
    aggregated_dict = {
        'text': '', 
        'entities': []
    }
    offset = 0

    for element in ner_dict:
        aggregated_dict['text'] = aggregated_dict['text'] + element['sentence'] +'.\n'
        for entity in element['entities']:       
            start_offset = offset + entity['offset']
            end_offset = offset + entity['offset'] + len(entity['value'])
            
            aggregated_dict['entities'].append({
                    'value': entity['value'],
                    'confidence': entity['confidence'],
                    'start_offset': start_offset,
                    'end_offset': end_offset,
                    'type': entity['type'] 
                })
        
        # +1 for the newline
        offset = offset + len(element['sentence'] + '.\n')     

    return aggregated_dict

def export_to_doccano(ner_dict, path, pilot='', service='', add_confidence=False):

    metadata = os.path.basename(path) if pilot == '' else pilot + ' - ' + service + ' - ' + os.path.basename(path)

    doccano_dict = {}
    doccano_dict['text'] = ner_dict['text']
    doccano_dict['labels'] = []

    doccano_dict['meta'] = metadata

    for item in ner_dict['entities']:
        if add_confidence:
            doccano_dict['labels'].append([item['start_offset'], item['end_offset'], item['type'], item['confidence']])
        else:
            doccano_dict['labels'].append([item['start_offset'], item['end_offset'], item['type']])

    file_out = open(path +'_ner.jsonl', 'w', encoding='utf-8')
    file_out.write(json.dumps(doccano_dict))
    file_out.write('\n')

    return doccano_dict, path +'_ner.jsonl'

def replacer(s, newstring, index, length, nofail=False):
    # raise an error if index is outside of the string
    if not nofail and index not in range(len(s)):
        raise ValueError("index outside given string")

    # if not erroring, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return newstring + s
    if index > len(s):  # add it to the end
        return s + newstring

    # insert the new string between "slices" of the original
    return s[:index] + newstring + s[index + length:]

def update_offsets(ner_dict, index, offset):

    for entity in ner_dict["entities"][index+1:]:
        entity['start_offset'] = entity['start_offset'] + offset
        entity['end_offset'] = entity['end_offset'] + offset
        #print("aggiunto offset di %d" % (offset))
        #print(entity)
        #input()
    return ner_dict

def resolve_uri_entities(ner_dict, path):
    uri_file = open(os.path.splitext(path)[0] + "_urls.json", 'r')
    uri = json.load(uri_file)

    try:
        for entity in ner_dict["entities"]:
            if entity["type"] == "URI":
                span = len(entity["value"])
                url = uri[entity["value"]]
                
                #ner_dict["text"] = re.sub(entity['value'], url, ner_dict['text'], 1)
                ner_dict["text"] = ner_dict['text'].replace(entity['value'], url, 1)
                entity["value"] = url
                entity['end_offset'] = entity['start_offset'] + len(url)



                ner_dict = update_offsets(ner_dict, ner_dict['entities'].index(entity), len(url)-span)
    except KeyError as e:
        print(e)

    return ner_dict