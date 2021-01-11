from transner import Transner
from datetime import datetime

#sections = [
#            ['To refugees in Spain, namely those with a well-founded fear of being persecuted in their country for reasons of race, religion, nationality, political opinions, belonging to a particular social group, gender or sexual orientation', 'If you find yourself in any of the aforementioned situations and you need protection from the Spanish authorities, you must submit a request for international protection'],
#            ['You will have to attend an interview in which you must answer a series of questions regarding your personal data, and in which you must explain all the reasons for which you are applying for international protection at Office of Asylum Refugees and how you arrived in Spain'],
#            ['All applications, regardless of who submits them, are examined by the Office of Asylum and Refuge', 'Decisions are made by the Ministry of the Interior', 'For decisions on applications admitted for processing, the Ministry of the Interior decides at the proposal of the lnterministerial Commission for Asylum and Refuge']
#        ]

sections = [['You will have to attend an interview in which you must answer a series of questions regarding your personal data, and in which you must explain all the reasons for which you are applying for international protection at Office of Asylum Refugees and how you arrived in Spain']] * 100

model = Transner(pretrained_model='bert_uncased_en', use_cuda=True, cuda_device=4, language_detection=True, threshold=0.85, args={"use_multiprocessing": False})
start_t = datetime.now()
for section in sections:
    ner_dict = model.ner(section, apply_regex=True)
    print(ner_dict)

end_t = datetime.now()
print('total time: {}'.format(str(end_t-start_t).split('.')[0]))

#total time: 0:00:53 multiprocessing on
#total time: 0:00:02 multiprocessing off