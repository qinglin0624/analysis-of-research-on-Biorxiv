import json
import copy
import itertools
import pandas as pd
import numpy as np

dataset = pd.read_csv('school_matched_country.csv')

index_to_delete = list(dataset[dataset['matched'] != dataset['matched']].index)
dataset.drop(labels=index_to_delete, inplace=True)
index_to_delete = list(dataset[dataset['Country_match'] != dataset['Country_match']].index)
dataset.drop(labels=index_to_delete, inplace=True)
dataset = dataset.reset_index(drop=True)

# find collaboration
ones = []
twos = []
country_dic = {}

for i in range(len(dataset)):
    institutes = dataset['matched'][i]
    countries = dataset['Country_match'][i]
    institutes = institutes.split(';')
    countries = countries.split(';')
    
    # fill country_dic
    for i in range(len(institutes)):
        country_dic[institutes[i]] = countries[i]
    
    for pair in list(itertools.combinations(np.arange(len(institutes)),2)):
        ones.append(institutes[pair[0]])
        twos.append(institutes[pair[1]])

dataset = pd.DataFrame({'ins1':ones, 'ins2':twos, 'times':twos})
dataset['processed_ins1'] = dataset.apply(lambda dataset: min(dataset['ins1'], dataset['ins2']), axis=1)
dataset['processed_ins2'] = dataset.apply(lambda dataset: max(dataset['ins1'], dataset['ins2']), axis=1)
dataset_group = dataset.groupby(['processed_ins1','processed_ins2'])['times'].count().reset_index()

dataset_group = dataset_group[dataset_group['times']>20] # collabration for > 20 paper
dataset_group = dataset_group.reset_index(drop=True)

dic = {}
for i in range(len(dataset_group['processed_ins1'])):
    ins1 = dataset_group['processed_ins1'][i]
    ins2 = dataset_group['processed_ins2'][i]
    dic[ins1] = dic.get(ins1,0) + 1
    dic[ins2] = dic.get(ins2,0) + 1

degree1 = []
for p in dataset_group['processed_ins1']:
    degree1.append(dic[p])

degree2 = []
for p in dataset_group['processed_ins2']:
    degree2.append(dic[p])

country1 = []
for p in dataset_group['processed_ins1']:
    country1.append(country_dic[p])

country2 = []
for p in dataset_group['processed_ins2']:
    country2.append(country_dic[p])
    
dataset_group['degree1'] = degree1
dataset_group['degree2'] = degree2
dataset_group['country1'] = country1
dataset_group['country2'] = country2

print(len(dataset_group))
dataset_group.to_excel('collaboration_relation_group.xlsx',index=False)
