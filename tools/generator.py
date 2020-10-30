import pandas as pd 
import pdb
import json

dict_types = json.loads("tools/dict_types.json")
steps = list(dict_types.keys())

def generate(ner_dict):
    pathway_aggregated = generate_pathway(ner_dict)
    pathway_df = compute_pertinence(pathway_aggregated)
    pathway = filter_pathway(pathway_df)

    result_pathway = pd.DataFrame(columns=pathway.columns)

    for step in steps:
        result_pathway = result_pathway.append(remove_duplicates(pathway.loc[pathway['step'] == step, :]))
    
    return result_pathway

def generate_pathway(ner_dict):
    #pathway = {'when': [], 'where': [], 'how': []}

    #dict_types = json.loads("tools/dict_types.json")

    info_subtypes = {}
    for dtype in dict_types:
        info_subtypes[dtype] = []

    '''
    try:
        info_subtypes['when'] = info_subtypes['when'] + ner_dict['entities']['TIME']
    except KeyError as e:
        print('Key not found: '+ str(e))
    #try:
    #    info_subtypes['where'] = info_subtypes['where'] + ner_dict['entities']['LOCATION']
    #except KeyError as e:
    #    print('Key not found: '+ str(e))
    try:
        info_subtypes['where'] = info_subtypes['where'] + ner_dict['entities']['ORGANIZATION']
    except KeyError as e:
        print('Key not found: '+ str(e))
    try:
        info_subtypes['how'] = info_subtypes['how'] + ner_dict['entities']['MISCELLANEOUS'] 
    except KeyError as e:
        print('Key not found: '+ str(e))
    try:
        info_subtypes['how'] = info_subtypes['how'] + ner_dict['entities']['PROCEDURE']
    except KeyError as e:
        print('Key not found: '+ str(e))
    try:
        info_subtypes['how'] = info_subtypes['how'] + ner_dict['entities']['DOCUMENT']
    except KeyError as e:
        print('Key not found: '+ str(e))'''

    for key, sub_types in dict_types.items():
        for sub_type in sub_types:
            try:
                info_subtypes[key] = info_subtypes[key] + ner_dict['entities'][sub_type]
            except KeyError as e:
                print('Key not found: '+ str(e))

    print(info_subtypes)
    input()

    return info_subtypes

def filter_pathway(pathway):    
    #return pathway.loc[(pathway['confidence'] >= 0) and (pathway['pertinence'] >= 0)]
    return pathway.loc[pathway['confidence'] >= 0.8]

def compute_pertinence(pathway):
    p_df = pd.DataFrame(columns=['step', 'start_offset', 'end_offset', 'confidence', 'pertinence'])
    for e_type, e_values in pathway.items():        
        for e_value in e_values:
            element = {}
            element['step'] = e_type
            for k, v in e_value.items():
                element[k] = v
            p_df = p_df.append(element, ignore_index=True)
            
    p_df.rename(columns={'value': 'entity'}, inplace=True)
    return p_df

def remove_duplicates(pathway):
    tmp_pathway = pathway.copy()
    tmp_pathway['pivot_column'] = tmp_pathway['entity'].str.strip()
    tmp_pathway['pivot_column'] = tmp_pathway['pivot_column'].str.lower()
    tmp_pathway = tmp_pathway.drop_duplicates(subset=['pivot_column'], keep="first")
    tmp_pathway = tmp_pathway.drop(columns = 'pivot_column')
    tmp_pathway = tmp_pathway.reset_index(drop = True)

    return tmp_pathway