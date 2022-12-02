# 托福听力学科词测试软件
## 使用方法
* `pip install -r requirements.txt`安装依赖
* 安装en-core-web-lg
* 输入`python QtVersion.py`，按回车运行程序
* 测试种遇到的错题会保存在目录下的error.csv内，可以自行删除或修改。
* 单词表缓存到安装目录或工作目录下的cache文件夹，这样可以减少后续读取excel的时间。如果修改wordlist.xlsx，需要手动删除缓存以重新加载。

Release版本可以直接双击exe文件运行。
## 100元有偿：打包为Mac版本或安卓版本。
Windows下用pyinstaller打包后(需用hook把en-core-web-lg打包进去，再在--hidden-import中添加PyQt5.QtGui)，需要把python Qt包下的imageformats/, platforms/目录以及ffmpeg.exe, ffprobe.exe还有wordlist.xlsx全部放入打包后程序的根目录下(参考Release版本)。