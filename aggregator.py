import pdb

def aggregate_ner_dict(result_dict):
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
            'EU_PHONE_NUMBER': [],
            'EMAIL_ADDRESS': []
        }
    }
    offset = 0

    for element in result_dict:
        for entity in element['entities']:          
            aggregated_dict['entities'][entity['type']].append({
                'value': entity['value'],
                'confidence': entity['confidence'],
                'start_offset': offset + entity['offset'],
                'end_offset': offset + entity['offset'] + len(entity['value'])
            })

        offset = offset + len(element['sentence'])
        aggregated_dict['text'] = aggregated_dict['text'] + element['sentence']
    
    #print(aggregated_dict)

    return aggregated_dict