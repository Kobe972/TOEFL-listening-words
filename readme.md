# 托福听力学科词测试软件
## Requirements
* Python3
* Spacy with eng_core_web_lg
* Pandas&numpy
* pyttsx3
* openpyxl
In Qt version, also need: 
* PyQt5
* requests
* pydub
* PyAudio
## Instructions
* `python test.py`或者`python QtVersion.py`运行程序
* 等待程序启动，会有界面要求选择测试范围，最后的Errors代表之前的错题
* 测试种遇到的错题会保存在目录下的error.csv内，如果想清除将其删掉即可
