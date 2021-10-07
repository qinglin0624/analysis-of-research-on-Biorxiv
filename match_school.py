import pandas as pd
import os
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime

school = pd.read_csv('../input/schoool/A-Z list of World Universities.csv')
school_list = school['University'].tolist()
school.set_index('University',inplace = True)

QS = pd.read_csv('../input/schoool/QS.csv')
QS_list = QS['institution'].tolist()
QS.set_index('institution',inplace = True)

for file in os.listdir('../input/match-school-smaller-than300'):
    match = pd.read_csv(os.path.join('../input/match-school-smaller-than300',file))
    num = 0
    match['matched'] = None
    match['country'] = None
    for i in match.index:
        num+=1
        start_time_ref = datetime.datetime.now()
        if type(match.loc[i,'institution']) == float:
            continue
        schools = []
        line = []
        country = []
        for inst in match.loc[i,'institution'].split(";"):
            for univ in inst.split(","):
                if re.search("[Uu]niv",univ) or re.search("[In]stit",univ):
                    line.append(univ.strip())
        line = set(line)
        try:
            for univ in line:
                a = process.extractOne(univ,QS_list,score_cutoff = 89)
                if a is None:
                    b = process.extractOne(univ,school_list,score_cutoff = 89)
                    if b is None:
                        continue
                    else:
                        schools.append(b[0])
                        try:
                            na = QS.loc[QS['country code']==school.loc[b[0],'Country'].strip().upper(),'country'][0]
                            country.append(na)
                        except:
                            country.append(school.loc[b[0],'Country'].strip().upper())
                else:
                    schools.append(a[0])
                    country.append(QS.loc[a[0],'country'])
        except:
            print('wrong',i)
        match.loc[i,'matched'] = ';'.join(set(schools))
        match.loc[i,'country'] = ';'.join(set(country))
#         matching = matching.append({'original':match.loc[i,'institution'],'matched':';'.join(set(schools)),'country':';'.join(set(country))}, ignore_index=True)
        end_time_ref = datetime.datetime.now()
        print(num,';'.join(set(schools)),';'.join(set(country)),end_time_ref-start_time_ref)
    match.to_csv(file,index = False)
