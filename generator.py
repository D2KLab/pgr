import pandas as pd 
import pdb

def generate(ner_dict):
    pathway_aggregated = generate_pathway(ner_dict)
    pathway_df = compute_pertinence(pathway_aggregated)
    pathway = filter_pathway(pathway_df)
    return pathway

def generate_pathway(ner_dict):
    pathway = {'when': [], 'where': [], 'how': []}

    try:
        pathway['when'] = pathway['when'] + ner_dict['entities']['TIME']
    except KeyError:
        pass
    pathway['where'] = pathway['where'] + ner_dict['entities']['LOCATION'] + ner_dict['entities']['ORGANIZATION']
    pathway['how'] = pathway['how'] + ner_dict['entities']['MISCELLANEOUS']

    return pathway

def filter_pathway(pathway):    
    #return pathway.loc[(pathway['confidence'] >= 0) & (pathway['pertinence'] >= 0)]
    return pathway.loc[pathway['confidence'] >= 0]

def compute_pertinence(pathway):
    p_df = pd.DataFrame(columns=['step', 'start_offset', 'end_offset', 'confidence', 'pertinence'])
    #p_df = pd.DataFrame()
    for e_type, e_values in pathway.items():        
        for e_value in e_values:
            element = {}
            element['step'] = e_type
            for k, v in e_value.items():
                element[k] = v
            p_df = p_df.append(element, ignore_index=True)
            
    p_df.rename(columns={'value': 'entity'}, inplace=True)
    return p_df