import pandas as pd
import numpy as np
import random
import os
import warnings
import requests
import pyttsx3
warnings.filterwarnings('ignore')
import en_core_web_lg
engine=pyttsx3.init()
voices=engine.getProperty('voices')
voice_capa=0
for voice in voices:
    if '_en' in voice.id.lower().split('\\')[-1]:
        engine.setProperty('voice',voice.id)
        voice_capa=1
        break
if voice_capa==0:
    print('Warning: cannot load the English voice library. Please download at https://www.microsoft.com/en-us/download/details.aspx?id=27224')
nlp = en_core_web_lg.load()
df=pd.read_excel('wordlist.xlsx',sheet_name=None,header=None)
overall=np.array([[0,0,0]])
for sheet in df:
    print(sheet)
if os.path.exists('error.csv'):
    error=pd.read_csv('error.csv',encoding='ansi',header=None).values
    print('Errors')
else:
    error=None
id=input('Input sheet id to test:')
if id not in df:
    if id=='Errors' and error is not None:
        test=error
    else:
        print('Invalid id')
        os.system("pause")
        exit()
if id!='Errors':
    test=df[id].values
    test=test[1:,1:]
for sheet in df:
    if sheet==id:
        continue
    tmp=df[sheet].values
    tmp=tmp[1:,1:]
    overall=np.concatenate((overall,tmp),axis=0)
overall=overall[1:,:]
profound_idx=np.random.permutation(overall.shape[0])[:100]
test_idx=np.random.permutation(test.shape[0])
score=0
dictation=input('Dictation?(y/n)')
if dictation!='y' and dictation!='Y':
    overall=overall[:,0]
    overall=np.unique(np.concatenate((overall[profound_idx],test[:,0]),axis=0))
    for i in range(len(test_idx)):
        print(str(i+1)+'.',test[test_idx[i]][2])
        similarities=[]
        for word in overall:
            similarity = nlp(test[test_idx[i]][0]).similarity(nlp(word))
            similarities.append((word, similarity))
        similarities = sorted(similarities, key=lambda item: -item[1])
        choices=[similarities[0][0],similarities[1][0],similarities[2][0],similarities[3][0]]
        random.shuffle(choices)
        for j in range(len(choices)):
            print(chr(ord('A')+j)+'.',choices[j])
        choice=ord(input().upper())-ord('A')
        if choices[choice]==test[test_idx[i]][0]:
            score+=1
            print('Correct!')
        else:
            print('The right answer is',test[test_idx[i]][0])
            to_append=test[[test_idx[i]],:]
            to_append[0][1]='Confounder:'+choices[choice]
            if error is not None and test[test_idx[i]][0] in error[:,0]:
                for ind in range(error.shape[0]):
                    if error[ind][0]==test[test_idx[i]][0]:
                        if isinstance(error[ind][1],str):
                            error[ind][1]+='\nConfounder:'+choices[choice]
                        else:
                            error[ind][1]='\nConfounder:'+choices[choice]
                        break
            else:
                if error is None:
                    error=to_append
                else:
                    error=np.concatenate((error,to_append),axis=0)
else:
    if voice_capa==0:
        print('You cannot use the dictation mode! Make sure your English voice library in regedit')
        os.system('pause')
        exit()
    answers=overall[:,2]
    answers=np.concatenate((answers[profound_idx],test[:,2]),axis=0)
    overall=overall[:,0]
    overall=np.concatenate((overall[profound_idx],test[:,0]),axis=0)
    for i in range(len(test_idx)):
        print(str(i+1)+'.')
        engine.say(test[test_idx[i]][0])
        engine.runAndWait()
        similarities=[]
        for j in range(len(overall)):
            similarity = nlp(test[test_idx[i]][0]).similarity(nlp(overall[j]))
            similarities.append((answers[j], similarity))
        similarities = sorted(similarities, key=lambda item: -item[1])
        choices=[]
        j=0
        while(len(np.unique(np.array(choices)))<4):
            choices.append(similarities[j][0])
            j+=1
        choices=np.unique(np.array(choices)).tolist()
        random.shuffle(choices)
        for j in range(len(choices)):
            print(chr(ord('A')+j)+'.',choices[j])
        choice=ord(input().upper())-ord('A')
        if choices[choice]==test[test_idx[i]][2]:
            score+=1
            print('Correct!')
        else:
            print('The right answer is',test[test_idx[i]][2])
            to_append=test[[test_idx[i]],:]
            to_append[0][1]='Confounder:'+choices[choice]
            if error is not None and test[test_idx[i]][0] in error[:,0]:
                for ind in range(error.shape[0]):
                    if error[ind][0]==test[test_idx[i]][0]:
                        if isinstance(error[ind][1],str):
                            error[ind][1]+='\nConfounder:'+choices[choice]
                        else:
                            error[ind][1]='\nConfounder:'+choices[choice]
                        break
            else:
                if error is None:
                    error=to_append
                else:
                    error=np.concatenate((error,to_append),axis=0)
print('Your score:',float(score)/test.shape[0]*100)
if error is not None:
    error=pd.DataFrame(error)
    error.to_csv('error.csv',index=False,header=None,encoding='ansi')
os.system("pause")
