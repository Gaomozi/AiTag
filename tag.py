from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
import urllib.request
import urllib.parse
import json
import os
import sys
from functools import partial

def transYoudao(content : str)->str:
    if content == '':
        return ''
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

class CurTags(object):

    def __init__(self, pg:Page, allfiles: list[str]):
        self.__txtPath = allfiles[pg.Current()].replace('.png', '.txt')
        self.engtags = []
        self.cntags = []
        self.buttons = []
    
    def LoadTags(self)->list[str]:
        if(os.path.exists(self.__txtPath)):
                with open(self.__txtPath) as file:
                    self.engtags =file.read().split(', ')
        self.LoadCnTags()
        
    def LoadCnTags(self)->list[str]: 
        for entag in self.engtags:
            cn = transYoudao(entag)
            self.cntags.append(cn)
            self.buttons.append(entag + '('+ cn +')  X')
    
    def DelTag(self, index :int):
        self.cntags.pop(index)
        self.engtags.pop(index)
        self.buttons.pop(index)
    
    def WriteTags(self):
        st = ''
        if len(self.engtags) > 0:
            st = self.engtags[0]
            for i in range(1, len(self.engtags)):
                st += ', '+self.engtags[i]

        with open(self.__txtPath, 'w') as f:
            f.write(st)
            with use_scope('txt' , clear=True):
                put_text(self.__txtPath, "保存成功") 
    def Clear(self):
        self.cntags.clear()
        self.engtags.clear()
        self.buttons.clear()

class StrTags(object):
    def __init__(self, En, Cn):
        self.entags=En
        self.cntags=Cn

def Trans(a:str, tg:CurTags):
    tg.Clear()
    a =a.split('，')
    strtmp = ''
    for tmp in a:
        tg.cntags.append(tmp)
        en = transYoudao(tmp)
        tg.engtags.append(en)
        tg.buttons.append(en+ '('+ tmp +')  X')
        strtmp += (' '+en + ',')

    with use_scope('image'):
        with use_scope('trans', clear=True):
            put_text("有道翻译结果:", strtmp)

def ReloadImage(a :Page):
    with use_scope('image' , clear=True):
            put_image(open(pngfiles[a.Current()], 'rb').read())
            put_text(pngfiles[a.Current()], "  当前：", a.Current()+1, "/ 总共：", len(pngfiles))


def ReloadTags(pg :Page):
    with use_scope('tags' , clear=True):
        Tag = CurTags(pg, pngfiles)
        Tag.LoadTags()
        if Tag.engtags != ['']:
            buttons = []
            for i in range(0, len(Tag.engtags)):
                buttons.append(dict(label=Tag.buttons[i], value=i, color='dark'))
            put_buttons(buttons, onclick=partial(DeletTag, Tag))
                
def DeletTag(Tag: CurTags, index: int):

    Tag.DelTag(index)
    Save(Tag, page)
          
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

def Save(tg:CurTags, pg:Page):
    tags = CurTags(pg, pngfiles)
    tags.engtags = tg.engtags
    tags.cntags = tg.cntags
    tags.buttons = tg.buttons
    
    tags.WriteTags()
    ReloadTags(pg)

def AddSave(tg, pg):
    tags = CurTags(pg, pngfiles)
    tags.LoadTags()
    tags.engtags += tg.engtags
    tags.cntags += tg.cntags
    tags.buttons += tg.buttons
    tags.WriteTags()  
    ReloadTags(pg)


if getattr(sys, 'frozen', False):
    path = sys._MEIPASS
else:
    path = os.path.split(os.path.realpath(__file__))[0]
path = os.getcwd()
pngfiles = [name for name in os.listdir('./')
        if name.endswith('.png')]
if len(pngfiles) == 0:
    put_text("  当前路径没有png图片，请将本程序放置在图片所在目录")
    sys.exit()

pngfiles = sorted(pngfiles, key=lambda x: int(x.replace('.png', '')), reverse=False)

page=Page(len(pngfiles))

with use_scope('image'):
    ReloadImage(page)
put_buttons(['上一张','下一张'] , onclick=[lambda: PrePage(page), lambda: NextPage(page)])

put_input('CnTags', label='请输入该图片Tag，使用 , (中文逗号)分割')
tmptags = CurTags(page, pngfiles)
put_buttons(['翻译','覆盖保存','追加保存'], onclick=[lambda: Trans(pin.CnTags, tmptags), lambda: Save(tmptags, page), lambda: AddSave(tmptags, page)])


with use_scope('tags'):
    ReloadTags(page)
put_input('Jump', label='输入需要跳转的图像编号（数字）')
put_button('跳转', onclick=lambda: Jump(pin.Jump, page))



