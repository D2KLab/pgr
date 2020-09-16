import pdb

def aggregate_entities(ner_dict):
    """
    Arguments:
        result_dict {dict} -- dictionary of predictions

    Returns:
        dict -- format: 
        {'text': ..., 
        'entities' :{
            'type':  [{'value': , 'offset': }],
            ...
            }
        }
    """
    aggregated_dict = {
        'text': '',
        'entities': {
            'PERSON': [],
            'LOCATION': [],
            'ORGANIZATION': [],
            'MISCELLANEOUS': [],
            'TIME': [],
            'DOCUMENT': [],
            'PROCEDURE': []
        }
    }

    aggregated_dict['text'] = ner_dict['text']

    for entity in ner_dict['entities']:
        entity_type = entity.pop('type')          
        aggregated_dict['entities'][entity_type].append(entity) 
                
    return aggregated_dict