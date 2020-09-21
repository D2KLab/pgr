import pandas as pd 
import pdb

def generate(ner_dict):
    pathway_aggregated = generate_pathway(ner_dict)
    pathway_df = compute_pertinence(pathway_aggregated)
    pathway = filter_pathway(pathway_df)
    pathway = remove_duplicates(pathway)
    return pathway

def generate_pathway(ner_dict):
    pathway = {'when': [], 'where': [], 'how': []}

    try:
        pathway['when'] = pathway['when'] + ner_dict['entities']['TIME']
        pathway['where'] = pathway['where'] + ner_dict['entities']['LOCATION'] + ner_dict['entities']['ORGANIZATION']
        pathway['how'] = pathway['how'] + ner_dict['entities']['MISCELLANEOUS'] + ner_dict['entities']['PROCEDURE'] + ner_dict['entities']['DOCUMENT']
    except KeyError as e:
        print(e)

    return pathway

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
    pathway['pivot_column'] = pathway['entity'].str.strip()
    pathway['pivot_column'] = pathway['pivot_column'].str.lower()
    pathway = pathway.drop_duplicates(subset=['pivot_column'], keep="first")
    pathway = pathway.drop(columns = 'pivot_column')
    pathway = pathway.reset_index(drop = True)

    return pathway