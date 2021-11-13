#!/usr/bin/env python
# coding: utf-8

# In[663]:


from randomtimestamp import randomtimestamp, random_date, random_time 
import pandas as pd
import numpy as np
import random
from random import choices,seed,randrange
from codicefiscale import codicefiscale
import datetime
import time
from random_italian_person import RandomItalianPerson

person = RandomItalianPerson()


# In[664]:


df = pd.DataFrame([
    RandomItalianPerson().data
    for _ in range(300)
])


# In[665]:


df.head()


# In[877]:


home_addr = df[['address','house_number','cap']]
home_addr = home_addr.head(101)


# In[667]:


df_filtered=df[['surname','name','sex','birthdate']]


# In[669]:


def cf(df):
    '''compute codice fiscale'''
    
    cf_ex= codicefiscale.encode(surname    = df['surname'], 
                                name       = df['name'], 
                                sex        = df['sex'],
                                birthdate  = df['birthdate'],
                                birthplace = 'Milano')

    return cf_ex 


# In[670]:


df_filtered['codice_fiscale']=df_filtered.apply(cf,axis=1)


# In[671]:


def homeID(df_filtered):
    df_filtered['ID_home'] = random.randint(0,100)
    return df_filtered


# In[672]:


df_filtered=df_filtered.apply(homeID,axis=1)


# In[674]:


df_final=df_filtered[['surname','name','birthdate','codice_fiscale','ID_home']]


# In[880]:


home_addr.insert(0,'id',range(0,0+len(home_addr)))


# In[882]:


path='/Users/lea/Desktop/' 
home_addr.to_csv(path +'homes.csv',sep=',',index=False)


# In[678]:


path='/Users/lea/Desktop/' 
df_final.to_csv(path +'persone.csv',sep=',',index=False)


# In[769]:


#CREAZIONE TABELLA GOES TO che collega i posti pubblici alle persone


# In[770]:


goes_to1 = df_final.copy(deep=True)[['codice_fiscale']] #tutti vanno in 2 posti pubblici
goes_to2 = df_final.copy(deep=True)[['codice_fiscale']]
goes_to = goes_to1.append(goes_to2, ignore_index=True, verify_integrity=False, sort=False)


# In[772]:


def randPlace(df):
    df['id_place'] = random.randint(1,20)
    return df


# In[773]:


goes_to=goes_to.apply(randPlace,axis=1)


# In[803]:


#considero l'ultimo mese con un picco in un giorno per ottenere più risultati dalle query
pplaces_orari = []
for i in range(5):
    pplaces_orari.append(randomtimestamp(start=datetime.datetime(2021, 10, 15,8,0), end=datetime.datetime(2021, 11, 15,18,0)))
for i in range(5):
    pplaces_orari.append(randomtimestamp(start=datetime.datetime(2021, 10, 31,8,0), end=datetime.datetime(2021, 10, 31,21,0)))


# In[804]:


def randomDate(df):
    df['dateIn']=random.choice(pplaces_orari)
    df['dateOut']=df['dateIn']+datetime.timedelta(hours=3)
    return df


# In[805]:


goes_to=goes_to.apply(randomDate,axis=1)


# In[806]:


path='/Users/lea/Desktop/' 
goes_to.to_csv(path +'public_visits.csv',sep=',',index=False)


# In[743]:


#TABELLA MEETS TRA PERSONE


# In[852]:


#20 luoghi
luoghi_df=pd.DataFrame({'geopoint'   :[str(np.round(random.uniform(45.4375,45.5191),4))+" "+str(np.round(random.uniform(9.1242,9.2286),4)) for x in range(20)],
                         'fake_key'      :1
          })

#10 orari
orari_df=pd.DataFrame({'timestamp'   :[randomtimestamp(start=datetime.datetime(2021, 10, 15,8,0), end=datetime.datetime(2021, 11, 15,18,0)) for x in range(5)], 
         'fake_key'      :1
          })
orari_df2=pd.DataFrame({'timestamp'   :[randomtimestamp(start=datetime.datetime(2021, 10, 31,8,0), end=datetime.datetime(2021, 10, 31,18,0)) for x in range(5)], 
         'fake_key'      :1
          })
orari_df = orari_df.append(orari_df2)
 
df_filtered['fake_key']=1


# In[855]:


# cross join: tutte le ore per ogni posto
place_luoghi=luoghi_df.merge(orari_df,on ='fake_key')
place_luoghi


# In[856]:


# cross join: tutte le ore per ogni posto
people_place_time=df_filtered.merge(place_luoghi,on ='fake_key').drop(columns='fake_key')
people_place_time


# In[857]:


# campiono persone raggruppando per luoghi e orari
size=5
np.random.seed(0)
random_place_time        = lambda x: x.loc[np.random.choice(x.index, size, replace=False),:]
sample_people_time_place = people_place_time.groupby(['geopoint','timestamp']).apply(random_place_time).reset_index(drop=True)


# In[858]:


sample_people_time_place.shape


# In[860]:


# rimuovo persone che stanno in luoghi diversi in tempi uguali
sample_people_time_place_no_dup=sample_people_time_place.drop_duplicates(subset=['codice_fiscale','timestamp'])


# In[861]:


sample_people_time_place_no_dup.shape


# In[863]:


# ne prendo una frazione casuale
sample_people_time_place_no_dup=sample_people_time_place_no_dup.sample(n=600, random_state=1).reset_index(drop=True).sort_values(by=['geopoint','timestamp'])


# In[864]:


save_columns=sample_people_time_place_no_dup.columns
save_columns_1 =[x + '_1' for x in save_columns]
save_columns_2 =[x + '_2' for x in save_columns]
save_columns_1


# In[865]:


from itertools import combinations

comb_df = sample_people_time_place_no_dup.groupby(['geopoint','timestamp']).apply(lambda x : list(combinations(x.values,2))).apply(pd.Series)                                                 .stack().reset_index().drop(columns='level_2')


# In[867]:


split_df   = pd.DataFrame(comb_df[0].to_list(), columns=['persona_1','persona_2'])
split_df_1 = pd.DataFrame(split_df['persona_1'].to_list(),columns=save_columns_1)
split_df_2 = pd.DataFrame(split_df['persona_2'].to_list(),columns=save_columns_2)


# In[868]:


final_df=pd.concat([split_df_1,split_df_2],axis=1)


# In[869]:


final_df=final_df.drop(columns=['timestamp_2','geopoint_2'])


# In[870]:


reorder_columns=['geopoint_1', 'timestamp_1',
                 'codice_fiscale_1','codice_fiscale_2',
                 ]


# In[871]:


final_df=final_df[reorder_columns]


# In[873]:


path='/Users/lea/Desktop/' 
final_df.to_csv(path +'meetings.csv',sep=',',index=False)


# In[709]:


#CREAZIONE VACCINI 


# In[710]:


vaccDict = {
  0: "AstraZeneca",
  1: "Pfizer-BioNTech",
  2: "Moderna",
  3: "Johnson & Johnson" 
}


# In[711]:


vacc = df_final.copy(deep=True)[['codice_fiscale']].iloc[:250,:] #prendo le prime 250 persone


# In[712]:


def whichVacc(df):
    df['type']= vaccDict[random.randint(0,3)]
    return df   


# In[713]:


vacc = vacc.apply(whichVacc,axis=1)


# In[714]:


def randDate(df):
    df["datetime"]=randomtimestamp(start_year=2021, end_year=2021)
    return df


# In[831]:


def randTestDate(df):
    df["datetime"]=randomtimestamp(start=datetime.datetime(2021, 10, 15,8,0), end=datetime.datetime(2021, 11, 15,18,0))
    return df


# In[832]:


vacc = vacc.apply(randDate,axis=1)


# In[833]:


scnd_dose =  vacc.copy(deep=True).iloc[:180,:] #persone che hanno fatto la seconda dose


# In[834]:


def next_dose(df):
    df['datetime'] = df['datetime'] + datetime.timedelta(days=28)
    return df


# In[835]:


scnd_dose = scnd_dose.apply(next_dose,axis=1)
scnd_dose = scnd_dose.drop(scnd_dose[scnd_dose.type=='Johnson & Johnson'].index) #non ha la seconda dose


# In[836]:


vacc = vacc.append(scnd_dose)


# In[837]:


path='/Users/lea/Desktop/' 
vacc.to_csv(path +'vaccines.csv',sep=',',index=False)


# In[838]:


#CREAZIONE TEST


# In[839]:


testDict = {
  0: "Antigen",
  1: "Molecular",
}


# In[840]:


resultDict = {
  0: "Negative",
  1: "Positive",
}


# In[841]:


test = df_final.copy(deep=True)[['codice_fiscale']].tail(200) #prendo le ultime 200 persone
test2 = df_final.copy(deep=True)[['codice_fiscale']].tail(100)
test3 = df_final.copy(deep=True)[['codice_fiscale']].tail(150)


# In[842]:


def whichTest(df):
    df['type']= testDict[random.randint(0,1)]
    return df  


# In[843]:


def whichRes(df):
    df['result']= resultDict[random.randint(0,1)]
    return df  


# In[844]:


test = test.apply(whichTest,axis=1)
test2 = test2.apply(whichTest,axis=1)
test3 = test3.apply(whichTest,axis=1)
test = test.apply(whichRes,axis=1)
test2 = test2.apply(whichRes,axis=1)
test3 = test3.apply(whichRes,axis=1)


# In[845]:


test = test.apply(randTestDate,axis=1)
test2 = test2.apply(randTestDate,axis=1)
test3 = test3.apply(randTestDate,axis=1)


# In[846]:


test = test.append(test2)


# In[847]:


test = test.append(test3)


# In[848]:


path='/Users/lea/Desktop/' 
test.to_csv(path +'tests.csv',sep=',',index=False)

