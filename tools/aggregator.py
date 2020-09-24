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

        }
    }

    aggregated_dict['text'] = ner_dict['text']

    for entity in ner_dict['entities']:
        entity_type = entity.pop('type')

        if entity_type in aggregated_dict['entities']:
            aggregated_dict['entities'][entity_type].append(entity)
        else: 
            aggregated_dict['entities'].update({entity_type: [entity]})
                
    return aggregated_dict