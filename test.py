import pandas as pd
import numpy as np
import random
import os
import warnings
warnings.filterwarnings('ignore')
import en_core_web_lg
nlp = en_core_web_lg.load()
df=pd.read_excel('wordlist.xlsx',sheet_name=None,header=None)
overall=np.array([[0,0,0]])
for sheet in df:
    print(sheet)
if os.path.exists('error.npy'):
    error=np.load('error.npy',allow_pickle=True)
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
overall=overall[1:,0]
profound_idx=np.random.permutation(overall.shape[0])[:200]
overall=np.unique(np.concatenate((overall[profound_idx],test[:,0]),axis=0))
test_idx=np.random.permutation(test.shape[0])
score=0
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
        if error is None:
            error=test[[test_idx[i]],:]
        else:
            error=np.concatenate((error,test[[test_idx[i]],:]),axis=0)
print('Your score:',float(score)/test.shape[0]*100)
if error is not None:
    np.save('error.npy',error)
os.system("pause")

    
