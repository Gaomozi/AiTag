from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
import urllib.request
import urllib.parse
import json
import os
import sys
from functools import partial

class StrSaver(object):
    def __init__(self, en:str, cn: str): 
        self.en = en
        self.cn = cn

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

# def transTencentYun(content : str)->str:
#     if content == '':
#         with use_scope('trans', clear=True):
#             put_text("请输入翻译内容")
#     cred = credential.Credential("AKIDEGILDvX2Okx791qcEexeAVeYDl7F8ZyA", "5gCZrssfDVhgSDoESSYmokU6TbdHm481")#"xxxx"改为SecretId，"yyyyy"改为SecretKey
#     httpProfile = HttpProfile()
#     httpProfile.endpoint = "tmt.tencentcloudapi.com"

#     clientProfile = ClientProfile()
#     clientProfile.httpProfile = httpProfile
#     client = tmt_client.TmtClient(cred, "ap-guangzhou", clientProfile)

#     req = models.TextTranslateRequest()
#     req.SourceText = content
#     req.Source ='ch'#源语言类型
#     req.Target ='en'#目标语言类型
#     req.ProjectId = 0

#     resp = client.TextTranslate(req)
#     data = json.loads(resp.to_json_string())
#     return data['TargetText']

class TagManager(object):

    def __init__(self, i:int, allfiles: list[str]):
        self.index = i
        self.__EnPath = allfiles[i].replace('.png', '.txt')
        self.__CnPath = "./cntags/" + self.__EnPath
        self.engtags = []
        self.cntags = []
        self.buttons = []
    
    def LoadTags(self):
        self.LoadCnTags()
        self.LoadEnTags()
        self.LoadButtons()
        
    def LoadCnTags(self): 
        if(os.path.exists(self.__CnPath)):
            with open(self.__CnPath) as file:
                cnfile = file.read()
                self.cntags =cnfile.split('，')
    def LoadEnTags(self):
        if len(self.cntags) == 0:
            return
        if(os.path.exists(self.__EnPath)):
            with open(self.__EnPath) as file:
                enfile = file.read()
                if(enfile!=''):
                    self.engtags =enfile.split(', ')
        if len(self.engtags)>len(self.cntags):
            self.engtags = self.engtags[:len(self.cntags)]
        elif len(self.engtags)<len(self.cntags):
            self.engtags = self.engtags+['(null)']*(len(self.cntags)-len(self.engtags))
    def LoadButtons(self):
        if len(self.cntags) == 0:
            return
        for i in range(len(self.cntags)):
            self.buttons.append(self.cntags[i] + '('+ self.engtags[i] +')  X')

    
    def DelTag(self, index :int):
        self.cntags.pop(index)
        self.engtags.pop(index)
        self.buttons.pop(index)
    
    def WriteTags(self):
        st = ''
        if len(self.engtags) > 0:
            st = self.engtags[0]
            for i in range(1, len(self.engtags)):
                st = st+', '+self.engtags[i]

        with open(self.__EnPath, 'w') as f:
            f.write(st)
        
        if len(self.cntags) > 0:
            st = self.cntags[0]
            for i in range(1, len(self.cntags)):
                st = st+'，'+self.cntags[i]

        with open(self.__CnPath, 'w') as f:
            f.write(st)
        
    def Clear(self):
        self.cntags.clear()
        self.engtags.clear()
        self.buttons.clear()

def Trans(cnstr:str, transStr:StrSaver):
    transStr.cn = cnstr
    cnstr =cnstr.split('，')

    if len(cnstr) ==0:
        with use_scope('trans', clear=True):
            put_text("输入内容为空!")
            transStr.cn = ''
        return
    if len(cnstr)>0:
        transStr.en = transYoudao(cnstr[0])
    for i in range(1, len(cnstr)):
        transStr.en = transStr.en+(', '+transYoudao(cnstr[i]))
    with use_scope('trans', clear=True):
        put_text("有道翻译结果:", transStr.en)

def GetTagButtonDic(Tag: TagManager):
    buttons = []
    for i in range(0, len(Tag.engtags)):
        buttons.append(dict(label=Tag.buttons[i], value=i, color='dark'))
    return buttons

def ReloadTagsButton(i:int):
    with use_scope('tags'+str(i) , clear=True):
        #alltags[i].LoadTags()
        if alltags[i].engtags != ['']:
            return put_buttons(GetTagButtonDic(alltags[i]), onclick=partial(DeletTag, alltags[i]))
            #put_row([None, put_buttons(GetTagButtonDic(Tag), onclick=partial(DeletTag, tmptags))], size='40% 60%')
                               
def DeletTag(Tag: TagManager, index: int):

    Tag.DelTag(index)
    Tag.WriteTags() 
    Reloadtable(Tag.index)
              
def Save(s:StrSaver, chosen:set, alltgs:list):
    if len(s.cn)==0 or len(s.en)==0:
        print("no input")
        return
    engtags = s.en.split(', ')
    cntags = s.cn.split('，')
    buttons = []
    if len(engtags)!=len(cntags):
        print("input cn\en nums not equ")
        return
    for i in range(len(engtags)):
        buttons.append(engtags[i]+ '('+ cntags[i] +')  X')

    for i in chosen:
        alltgs[i].engtags = engtags
        alltgs[i].cntags = cntags
        alltgs[i].buttons = buttons
        alltgs[i].WriteTags()    
        Reloadtable(i)

def AddSave(s:StrSaver, chosen:set, alltgs:list):
    if len(s.cn)==0 or len(s.en)==0:
        print("no input")
        return
    engtags = s.en.split(', ')
    cntags = s.cn.split('，')
    buttons = []
    if len(engtags)!=len(cntags):
        print("input cn\en nums not equ")
        return
    for i in range(len(engtags)):
        buttons.append(cntags[i]+ '('+ engtags[i] +')  X')

    for i in chosen:
        if(len(alltgs[i].engtags) == 0):
            alltgs[i].engtags = engtags
            alltgs[i].cntags = cntags
            alltgs[i].buttons = buttons
        else:
            alltgs[i].engtags = alltgs[i].engtags + engtags
            alltgs[i].cntags = alltgs[i].cntags + cntags
            alltgs[i].buttons = alltgs[i].buttons + buttons
        alltgs[i].WriteTags()  
        Reloadtable(i)

def ClickChoose(i:int):
    if i in chosenSet:
        chosenSet.remove(i)
    else:
        chosenSet.add(i)
    Reloadtable(i)
    ReloadSelectTool()

def Select(i:int):
    with use_scope('select'+str(i), clear=True):
        if i in chosenSet:
            return put_button('☑：点击取消选择', onclick=lambda: ClickChoose(i), color='danger',scope='select'+str(i))
        else:
            return put_button('☐：点击选择图片', onclick=lambda: ClickChoose(i), color='secondary',scope='select'+str(i))

def Reloadtable(i:int):
    with use_scope('table'+str(i), clear=True):
        # put_table([
        #     [Select(i),span(put_image(open(pngfiles[i], 'rb').read(), width = '150'), row=4),span(ReloadTagsButton(i), row=4),put_text("sadasdasdasd")],
        #     #[ReloadTagsButton(i)],                
        # ])
        #put_row([put_text('------NO:', i ,'----------------------', pngfiles[i] ,'---------------------------------')])
        put_row([Select(i),put_text(' NO:',i,'\n ',pngfiles[i]), put_image(open(pngfiles[i], 'rb').read(), width = '150'),ReloadTagsButton(i)], size='60px 60px 150px')
        put_row([put_text('------------------------------------------------------------------------------')])

def ReloadChoosen():
    return put_text('已选数量：'+str(len(chosenSet)) + ' :' +str(chosenSet))

def ClearSelect():
    clearlist=[]
    for i in chosenSet:
        clearlist.append(i)
    for i in clearlist:
        ClickChoose(i)

def ReloadSelectTool():
    with use_scope('selectNum', clear=True):
        put_row([put_button('清除选择', onclick= lambda: ClearSelect()),ReloadChoosen()],size='100px')

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
if not os.path.exists('./cntags'):
    os.mkdir('./cntags')
pngfiles = sorted(pngfiles, key=lambda x: int(x.replace('.png', '')), reverse=False)
totalNum =len(pngfiles)
chosenSet = set()
alltags = []
transStr = StrSaver('', '')

pageNum = int(totalNum/50)
remainNum = totalNum-pageNum
imageBegin =0
imageEnd =min(50 + imageBegin, pageNum)

def last():
    if imageBegin > 49:
        imageBegin -= 50
        imageEnd -= 50
    LoadPage()

def next():
    if imageBegin < pageNum-remainNum:
        imageBegin += 50
        imageEnd += 50
        if imageEnd>totalNum:
            imageEnd = totalNum
    LoadPage()


def LoadPage():
    with use_scope('page', clear=True):
        put_scrollable(put_scope('scrollable'), height=750, keep_bottom=False, border = True)
        with use_scope('scrollable'):
            alltags.clear()
            for i in range(imageBegin, imageEnd):
                alltags.append(TagManager(i, pngfiles))
                alltags[i].LoadTags()
                Reloadtable(i)

put_buttons(['last','next'], onclick=[lambda: last(),lambda: next()])
LoadPage()
[[put_buttons(['翻译','覆盖保存','追加保存'], onclick=[lambda: Trans(pin.CnTags, transStr), lambda: Save(transStr, chosenSet, alltags), lambda: AddSave(transStr, chosenSet, alltags)])], put_input(name = 'CnTags', label='请输入该图片Tag，使用 , (中文逗号)分割')]
with use_scope('trans', clear=True):
    put_text('翻译结果：')
ReloadSelectTool()

