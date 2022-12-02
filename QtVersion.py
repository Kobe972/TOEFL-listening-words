# -*- coding: gbk -*-
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
from PyQt5 import QtCore
import pandas as pd
import numpy as np
import random
import os
import warnings
import requests
import pickle
import json
from pydub import AudioSegment
from pydub.playback import play
import io
import time
warnings.filterwarnings('ignore')
import en_core_web_lg
import sys
import pyttsx3

id=None
df=None
error=None
dictation=None
nlp=None
test=None
overall=np.array([[0,0,0]])
score=0
test_idx=None
answers=None
isRetest=False
def pronounce(phrase):
    url='https://dict.youdao.com/dictvoice?audio='+phrase.replace(' ','+')
    try:
        req=requests.get(url)
    except:
        msg_box = QMessageBox(QMessageBox.Warning, "Error", "Internet Error!")
        msg_box.exec_()
        QCoreApplication.instance().quit()
        sys.exit()
    if req.status_code!=200:
        msg_box = QMessageBox(QMessageBox.Warning, "Error", "Internet Error!")
        msg_box.exec_()
        QCoreApplication.instance().quit()
        sys.exit()
    sound_bytes=req.content
    sound_bytes = AudioSegment.from_file(io.BytesIO(sound_bytes), format="mp3")
    play(sound_bytes)
class MainPanel(QWidget):
    def __init__(self):
        super(MainPanel,self).__init__()
        self.resize(640,480)
        self.setWindowTitle("单词测试")
        mainPanel_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()
        self.qls = QStackedLayout()
        startPanel=StartPanel()
        self.qls.addWidget(startPanel)
        mainPanel_layout.addLayout(self.qls)
        mainPanel_layout.addLayout(self.button_layout)
        self.setLayout(mainPanel_layout)
        self.progress=0
        self.stage=0 #ChoiceSheetPanel
    def loaded(self):
        self.choiceSheetPanel=ChoiceSheetPanel()
        self.qls.addWidget(self.choiceSheetPanel)
        confirm=QPushButton('确认')
        confirm.clicked.connect(lambda:self.confirm())
        retest=QPushButton('返回主菜单')
        retest.clicked.connect(lambda:self.retest())
        self.button_layout.addWidget(confirm)
        self.button_layout.addWidget(retest)
        index = self.qls.currentIndex()
        self.qls.setCurrentIndex(index + 1)
    def retest(self):
        global isRetest
        reply = QMessageBox.question(self, 'Notify', 'You sure to retest?',QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply==QMessageBox.Yes:
            isRetest=True
            self.close()
    def NextTextQuestion(self):
        global test_idx
        global overall
        global nlp
        if self.progress==len(test_idx):
            pass
        else:
            similarities=[]
            for word in overall:
                similarity = nlp(test[test_idx[self.progress]][0]).similarity(nlp(word))
                similarities.append((word, similarity))
            similarities = sorted(similarities, key=lambda item: -item[1])
            choices=[similarities[0][0],similarities[1][0],similarities[2][0],similarities[3][0]]
            random.shuffle(choices)
            self.answer=test[[test_idx[self.progress]],0]
            self.textQuizPanel=TextQuizPanel(self.progress,choices)
            self.qls.addWidget(self.textQuizPanel)
            index = self.qls.currentIndex()
            self.qls.setCurrentIndex(index + 1)
    def NextDictationQuestion(self):
        global test_idx
        global overall
        global nlp
        global answers
        try:
            pronounce(test[test_idx[self.progress],0])
        except:
            pronounce(test[test_idx[self.progress],0]+' ')
        if self.progress==len(test_idx):
            pass
        else:
            similarities=[]
            for j in range(len(overall)):
                similarity = nlp(test[test_idx[self.progress]][0]).similarity(nlp(overall[j]))
                similarities.append((answers[j], similarity))
            similarities = sorted(similarities, key=lambda item: -item[1])
            choices=[]
            j=0
            while(len(np.unique(np.array(choices)))<4):
                choices.append(similarities[j][0])
                j+=1
            choices=np.unique(np.array(choices)).tolist()
            random.shuffle(choices)
            self.answer=test[[test_idx[self.progress]],2]
            self.dictationQuizPanel=DictationQuizPanel(self.progress,choices)
            self.qls.addWidget(self.dictationQuizPanel)
            index = self.qls.currentIndex()
            self.qls.setCurrentIndex(index + 1)
    def confirm(self):
        if(self.stage==0):
            global df
            global test
            global error
            global score
            global test_idx
            global overall
            global answers
            id=self.choiceSheetPanel.Sheets.currentText()
            self.dictation=self.choiceSheetPanel.dictation.isChecked()
            if id=='Errors':
                test=error
            else:
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
            self.stage=1
            if self.dictation:
                answers=overall[:,2]
                answers=np.concatenate((answers[profound_idx],test[:,2]),axis=0)
                overall=overall[:,0]
                overall=np.concatenate((overall[profound_idx],test[:,0]),axis=0)
                self.NextDictationQuestion()
            else:
                overall=overall[:,0]
                overall=np.unique(np.concatenate((overall[profound_idx],test[:,0]),axis=0))
                self.NextTextQuestion()
        elif self.dictation:
            choice=self.dictationQuizPanel.selected_text
            if choice!=self.answer:
                self.dictationQuizPanel.setBold(self.answer)
                msg_box = QMessageBox(QMessageBox.Warning, "Wrong Answer", "The right answer is \""+test[test_idx[self.progress]][2]+"\"")
                msg_box.exec_()
                to_append=test[[test_idx[self.progress]],:]
                to_append[0][1]='Confounder:'+choice
                if error is not None and test[test_idx[self.progress]][0] in error[:,0]:
                    for ind in range(error.shape[0]):
                        if error[ind][0]==test[test_idx[self.progress]][0]:
                            if isinstance(error[ind][1],str):
                                error[ind][1]+='\nConfounder:'+choice
                            else:
                                error[ind][1]='\nConfounder:'+choice
                            break
                else:
                    if error is None:
                        error=to_append
                    else:
                        error=np.concatenate((error,to_append),axis=0)
                pd.DataFrame(error).to_csv('error.csv',index=False,header=None,encoding='ansi')
            else:
                score+=1
            self.progress+=1
            if self.progress==len(test_idx):
                msg_box = QMessageBox(QMessageBox.Warning, "Completed", "Your score is"+str(float(score)/test.shape[0]*100))
                msg_box.exec_()
                if error is not None:
                    error=pd.DataFrame(error)
                    error.to_csv('error.csv',index=False,header=None,encoding='ansi')
                QCoreApplication.instance().quit()
                return
            self.NextDictationQuestion()
        else:
            choice=self.textQuizPanel.selected_text
            if choice!=self.answer:
                self.textQuizPanel.setBold(self.answer)
                msg_box = QMessageBox(QMessageBox.Warning, "Wrong Answer", "The right answer is \""+test[test_idx[self.progress]][0]+"\"")
                msg_box.exec_()
                to_append=test[[test_idx[self.progress]],:]
                to_append[0][1]='Confounder:'+choice
                if error is not None and test[test_idx[self.progress]][0] in error[:,0]:
                    for ind in range(error.shape[0]):
                        if error[ind][0]==test[test_idx[self.progress]][0]:
                            if isinstance(error[ind][1],str):
                                error[ind][1]+='\nConfounder:'+choice
                            else:
                                error[ind][1]='\nConfounder:'+choice
                            break
                else:
                    if error is None:
                        error=to_append
                    else:
                        error=np.concatenate((error,to_append),axis=0)
                pd.DataFrame(error).to_csv('error.csv',index=False,header=None,encoding='ansi')
            else:
                score+=1
            self.progress+=1
            if self.progress==len(test_idx):
                msg_box = QMessageBox(QMessageBox.Warning, "Completed", "Your score is "+str(float(score)/test.shape[0]*100))
                msg_box.exec_()
                isRetest=True
                self.close()
                return
            self.NextTextQuestion()
class StartPanel(QWidget):
    def __init__(self):
        super(StartPanel,self).__init__()
        StartPanel_layout = QHBoxLayout()
        StartPanel_layout.addWidget(QLabel('正在读取excel...'))
        self.setLayout(StartPanel_layout)
class Banner(QWidget):
    def __init__(self):
        super(Banner,self).__init__()
        self.index=0
        self.urls=[]
        self.links=[]
        grid=QHBoxLayout()
        left=QPushButton('<')
        right=QPushButton('>')
        self.banner=QPushButton()
        self.banner_update_timer=QTimer(self)
        left.setFixedSize(int(480*0.05),150)
        right.setFixedSize(int(480*0.05),150)
        self.banner.setFixedSize(int(480),150)
        left.clicked.connect(lambda:self.decrease())
        right.clicked.connect(lambda:self.increase())
        self.banner.clicked.connect(lambda:self.openURL())
        grid.addWidget(left)
        grid.addWidget(self.banner)
        grid.addWidget(right)
        self.setLayout(grid)
        self.banner_update_timer.timeout.connect(self.increase)
        self.banner_update_timer.start(3000)
        self.load()
        self.setIndex(0)
    def load(self):
        try:
            config=requests.get('http://home.ustc.edu.cn/~xuyichang/mywork/config.json')
        except:
            msg_box = QMessageBox(QMessageBox.Warning, "Error", "Internet Error!")
            msg_box.exec_()
            QCoreApplication.instance().quit()
            sys.exit()
        if config.status_code!=200:
            msg_box = QMessageBox(QMessageBox.Warning, "Error", "Internet Error!")
            msg_box.exec_()
            QCoreApplication.instance().quit()
            sys.exit()
        config=json.loads(config.text)
        for item in config:
            self.urls.append(item['banner'])
            self.links.append(item['link'])
    def openURL(self):
        QDesktopServices.openUrl(QtCore.QUrl(self.links[self.index]))
    def setIndex(self,index):
        self.index=index
        try:
            data=requests.get(self.urls[index]).content
        except:
            msg_box = QMessageBox(QMessageBox.Warning, "Error", "Unable to download the banner!")
            msg_box.exec_()
            return
        pixmap=QPixmap()
        pixmap.loadFromData(data)
        self.banner.setIcon(QIcon(pixmap))
        self.banner.setIconSize(self.banner.size())
    def increase(self):
        self.setIndex((self.index+1)%len(self.urls))
    def decrease(self):
        self.setIndex((self.index-1)%len(self.urls))
class ChoiceSheetPanel(QWidget):
    def __init__(self):
        super(ChoiceSheetPanel,self).__init__()
        global df
        global error
        layout = QVBoxLayout()
        self.Sheets=QComboBox()
        self.Sheets.addItems(df)
        banner=Banner()
        if os.path.exists('error.csv'):
            error=pd.read_csv('error.csv',encoding='ansi',header=None).values
            self.Sheets.addItem('Errors')
        else:
            error=None
        self.dictation=QCheckBox('听题模式')
        layout.addWidget(banner)
        layout.addWidget(QLabel('请选择测试单元'))
        layout.addWidget(self.Sheets)
        layout.addWidget(self.dictation)
        self.setLayout(layout)
class TextQuizPanel(QWidget):
    def __init__(self,progress,choices):
        super(TextQuizPanel,self).__init__()
        global test
        global test_idx
        layout = QVBoxLayout(self)
        self.btngroup=QButtonGroup()
        layout.addWidget(QLabel(str(progress+1)+'. '+test[test_idx[progress]][2]))
        for choice in choices:
            radio=QRadioButton(choice)
            self.btngroup.addButton(radio)
            layout.addWidget(radio)
        def handle_button_idclicked(id_):
            self.selected_text=self.btngroup.button(id_).text()
        self.btngroup.idClicked.connect(handle_button_idclicked)
        self.setLayout(layout)
    def setBold(self,choice):
        for button in self.btngroup.buttons():
            if button.text()==choice:
                font = QFont()
                font.setBold(True)
                button.setFont(font)
class DictationQuizPanel(QWidget):
    def __init__(self,progress,choices):
        super(DictationQuizPanel,self).__init__()
        global test
        global test_idx
        layout = QVBoxLayout()
        self.btngroup=QButtonGroup()
        layout.addWidget(QLabel(str(progress+1)+'. '))
        for choice in choices:
            radio=QRadioButton(choice)
            self.btngroup.addButton(radio)
            layout.addWidget(radio)
        def handle_button_idclicked(id_):
            self.selected_text=self.btngroup.button(id_).text()
        self.btngroup.idClicked.connect(handle_button_idclicked)
        self.setLayout(layout)
    def setBold(self,choice):
        for button in self.btngroup.buttons():
            if button.text()==choice:
                font = QFont()
                font.setBold(True)
                button.setFont(font)
        
if __name__ == '__main__':
    appctxt = QApplication([])       # 1. Instantiate ApplicationContext
    firstLoad=True
    while True:
        main=MainPanel()
        main.show()
        if firstLoad:
            pyttsx3.init()
            nlp = en_core_web_lg.load()
            if not os.path.exists('cache/cached_sheet.dat'):
                df=pd.read_excel('wordlist.xlsx',sheet_name=None,header=None)
                if not os.path.exists('cache/'):
                    os.mkdir('cache')
                with open('cache/cached_sheet.dat','wb') as fp:
                    pickle.dump(df, fp)
            else:
                with open('cache/cached_sheet.dat','rb') as fp:
                    df=pickle.load(fp)
            firstLoad=False
        main.loaded()
        exit_code = appctxt.exec()
        if not isRetest:
            break
        isRetest=False
        id=None
        error=None
        dictation=None
        test=None
        overall=np.array([[0,0,0]])
        score=0
        test_idx=None
        answers=None
    sys.exit(exit_code)
