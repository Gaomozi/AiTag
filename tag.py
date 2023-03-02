from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
import urllib.request
import urllib.parse
import json
import os

def transYoudao(content : str)->str:
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule' #选择要爬取的网页，上面找过了
    #加上一个帽子，减少被发现的概率（下面head列表的内容就是上面找的）
    head = {}
    head['User - Agent'] = '请替换'

    #伪装计算机提交翻译申请（下面的内容也在在上面有过，最好根据自己的进行修改）
    data = {}
    data['type'] = 'AUTO'
    data['i'] = content
    data['doctype'] = 'json'
    data['version'] = '2.1'
    data['keyfrom:'] = 'fanyi.web'
    data['ue'] = 'UTF-8'
    data['typoResult'] = 'true'
    data = urllib.parse.urlencode(data).encode('utf-8')

    response = urllib.request.urlopen(url, data)
    #解码
    html = response.read().decode('utf-8')

    paper = json.loads(html)
    return  paper['translateResult'][0][0]['tgt']

def Trans(a, b):
    b.entags = a
    b.entags = transYoudao(a)
    with use_scope('image'):
        with use_scope('trans', clear=True):
            put_text("有道翻译结果:", b.entags)

class Page(object):
    def __init__(self, MaxPage):
        self.__currentpage=0
        self.__maxpage=MaxPage
        
    def NextPage(self):
        if self.__currentpage<self.__maxpage-1:
            self.__currentpage = self.__currentpage +1
            return 1
        else:
            return 0
            
    def PrePage(self):
        if self.__currentpage>0:
            self.__currentpage =self.__currentpage-1
            return 1
        else:
            return 0
        
    def Jump(self, num):
        if self.__currentpage+num>0 and self.__currentpage+num<self.__maxpage:
            self.__currentpage =self.__currentpage+num
            print(self.__currentpage, self.__maxpage)
            return 1
        else:
            return 0
        print(self.__currentpage, self.__maxpage)
            
    def Current(self):
        return self.__currentpage

class Tags(object):
    def __init__(self, En, Cn):
        self.entags=En
        self.cntags=Cn

def ReloadImage(a :Page):
    with use_scope('image' , clear=True):
            put_image(open(pngfiles[a.Current()], 'rb').read())
            put_text(pngfiles[a.Current()], "  当前：", a.Current()+1, "/ 总共：", len(pngfiles))


def ReloadTags(a :Page):
    with use_scope('trags' , clear=True):
            if(os.path.exists(pngfiles[a.Current()].replace('.png', '.txt'))):
                with open(pngfiles[a.Current()].replace('.png', '.txt')) as file:
                    txt = file.read()
                put_text("当前已有tags:", txt)
                put_text("已有tags翻译:", transYoudao(txt))
            
def PrePage (a : Page):
    if a.PrePage():
        ReloadImage(a)
        ReloadTags(a)

    
def NextPage(a : Page):
    if a.NextPage():  
        ReloadImage(a)
        ReloadTags(a)

def Jump(a, b: Page):
    num = int(a) - int(pngfiles[b.Current()].replace('.png', ''))
    if(b.Jump(num) == 1):
        ReloadImage(b)
        ReloadTags(b)

def Save(tg, pg):
    filename = pngfiles[pg.Current()].replace('.png' , '.txt')
    print(filename)    
    with open(filename, 'w') as f:
        f.write(tg.entags)
        with use_scope('txt' , clear=True):
            put_text(filename, "保存成功")
            


path = os.getcwd()
pngfiles = [name for name in os.listdir('./')
        if name.endswith('.png')]

pngfiles = sorted(pngfiles, key=lambda x: int(x.replace('.png', '')), reverse=False)

page=Page(len(pngfiles))

with use_scope('image'):
    ReloadImage(page)
put_buttons(['上一张','下一张'] , onclick=[lambda: PrePage(page), lambda: NextPage(page)])

put_input('CnTags', label='请输入该图片Tag，使用 , (中英文都行)分割')
tags = Tags("", "")
put_buttons(['翻译','保存翻译的tags'], onclick=[lambda: Trans(pin.CnTags, tags), lambda: Save(tags, page)])

with use_scope('tags'):
    ReloadTags(page)
put_input('Jump', label='输入需要跳转的图像编号（数字）')
put_button('跳转', onclick=lambda: Jump(pin.Jump, page))



