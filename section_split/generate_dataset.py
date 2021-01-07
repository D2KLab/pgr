import pandas as pd
import sys 

df = pd.read_csv('dataset.csv')

#file_out = open('refactored_dataset.csv')
df_out = pd.DataFrame(columns=["split", "dataset", "sentence_1", "section_1_title", "sentence_2", "section_2_title", "article_link", "class"])

full_size = df.shape[0]
train_size_index = full_size*0.8
val_size_index = train_size_index + full_size*0.1

for idx, row in df.iterrows():
    sys.stdout.write("\rcomputing sentence at index %i" % idx)
    sys.stdout.flush()
    #dict_tmp = {"sentence_1": '', "section_1_title": '', "sentence_2": '', "section_2_title": '', "article_link": '', "class": 0}
    dict_tmp = {}
    dict_tmp['sentence_1'] = row['Sentence']
    dict_tmp['section_1_title'] = row['SectionTitle']
    dict_tmp['article_link'] = row['Article Link']
    dict_tmp['dataset'] = 'IBM_Debater_ACL_2018'

    if idx <= train_size_index:
        dict_tmp['split'] = 'train'
    elif idx > train_size_index and idx <= val_size_index:
        dict_tmp['split'] = 'val'
    else:
        dict_tmp['split'] = 'test'

    if idx+1 == df.shape[0]:
        df_pos = df[(df["SectionTitle"] != dict_tmp['section_1_title']) & (df['Article Link'] == dict_tmp['article_link'])]
        df_neg = df[(df["SectionTitle"] == dict_tmp['section_1_title']) & (df['Article Link'] == dict_tmp['article_link'])]
        dict_tmp['article_link'] = row['Article Link']
        random_pos = df_pos.sample().to_dict('records')[-1]
        random_neg = df_neg.sample().to_dict('records')[-1]
        dict_tmp['sentence_2'] = random_pos['Sentence']
        dict_tmp['section_2_title'] = random_pos['SectionTitle']
        dict_tmp['class'] = 1

        df_out = df_out.append(dict_tmp, ignore_index=True)
        dict_tmp['sentence_2'] = random_neg['Sentence']
        dict_tmp['section_2_title'] = random_neg['SectionTitle']
        dict_tmp['class'] = 0

        df_out = df_out.append(dict_tmp, ignore_index=True)
        continue

    next_row = df.loc[idx+1] 

    dict_tmp['sentence_2'] = next_row['Sentence']
    dict_tmp['section_2_title'] = next_row['SectionTitle']

    dict_tmp['class'] = 1 if dict_tmp['section_2_title'] == dict_tmp['section_1_title'] else 0
    df_out = df_out.append(dict_tmp, ignore_index=True)

    if dict_tmp['class'] == 1:
        #find negative
        df_subset = df[(df["SectionTitle"] != dict_tmp['section_1_title']) & (df['Article Link'] == dict_tmp['article_link'])]
        random_row = df_subset.sample().to_dict('records')[-1]
        dict_tmp['sentence_2'] = random_row['Sentence']
        dict_tmp['section_2_title'] = random_row['SectionTitle']
        dict_tmp['class'] = 0
        df_out = df_out.append(dict_tmp, ignore_index=True)
    else:
        #find class
        df_subset = df[(df["SectionTitle"] != dict_tmp['section_1_title']) & (df['Article Link'] == dict_tmp['article_link'])]
        random_row = df_subset.sample()
        sentence_list = pd.Series(list(df_out['sentence_1']))
        while not sentence_list[sentence_list.isin([random_row['Sentence']])].empty:           
            random_row = df_subset.sample()
        random_row = random_row.to_dict('records')[-1]
        dict_tmp['sentence_2'] = random_row['Sentence']
        dict_tmp['section_2_title'] = random_row['SectionTitle']
        dict_tmp['class'] = 1
        df_out = df_out.append(dict_tmp, ignore_index=True)

df_out.to_csv('dataset_extended.csv', index=False)