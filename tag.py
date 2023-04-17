from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
import urllib.request
import urllib.parse
import json
import os
import sys
from functools import partial

from tencentcloud.common import credential#这里需要安装腾讯翻译sdk
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models   

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

def transTencentYun(content : str)->str:
    import binascii
import hashlib
import hmac
import sys
import urllib.parse
import urllib.request
import time
import random

def sign(secretKey, signStr, signMethod):
    '''
    该方法主要是实现腾讯云的签名功能
    :param secretKey: 用户的secretKey
    :param signStr: 传递进来字符串，加密时需要使用
    :param signMethod: 加密方法
    :return:
    '''
    if sys.version_info[0] > 2:
        signStr = signStr.encode("utf-8")
        secretKey = secretKey.encode("utf-8")

    # 根据参数中的signMethod来选择加密方式
    if signMethod == 'HmacSHA256':
        digestmod = hashlib.sha256
    elif signMethod == 'HmacSHA1':
        digestmod = hashlib.sha1

    # 完成加密，生成加密后的数据
    hashed = hmac.new(secretKey, signStr, digestmod)
    base64 = binascii.b2a_base64(hashed.digest())[:-1]

    if sys.version_info[0] > 2:
        base64 = base64.decode()

    return base64

    def dictToStr(dictData):
        '''
        本方法主要是将Dict转为List并且拼接成字符串
        :param dictData:
        :return: 拼接好的字符串
        '''
        tempList = []
        for eveKey, eveValue in dictData.items():
            tempList.append(str(eveKey) + "=" + str(eveValue))
        return "&".join(tempList)


# 用户必须准备好的secretId和secretKey
# 可以在 https://console.cloud.tencent.com/capi 获取
    secretId = "你的secretId"
    secretKey = "你的secretKey"

    # 在此处定义一些必须的内容
    timeData = str(int(time.time())) # 时间戳
    nonceData = int(random.random()*10000) # Nonce，官网给的信息：随机正整数，与 Timestamp 联合起来， 用于防止重放攻击
    actionData = "TextTranslate" # Action一般是操作名称
    uriData = "tmt.tencentcloudapi.com" # uri，请参考官网
    signMethod="HmacSHA256" # 加密方法
    requestMethod = "GET" # 请求方法，在签名时会遇到，如果签名时使用的是GET，那么在请求时也请使用GET
    regionData = "ap-hongkong" # 区域选择
    versionData = '2018-03-21' # 版本选择

    # 签名时需要的字典
    # 首先对所有请求参数按参数名做字典序升序排列，所谓字典序升序排列，
    # 直观上就如同在字典中排列单词一样排序，按照字母表或数字表里递增
    # 顺序的排列次序，即先考虑第一个“字母”，在相同的情况下考虑第二
    # 个“字母”，依此类推。
    signDictData = {
        'Action' : actionData,
        'Nonce' : nonceData,
        'ProjectId':0,
        'Region' : regionData,
        'SecretId' : secretId,
        'SignatureMethod':signMethod,
        'Source': "en",
        'SourceText': "hello world",
        'Target': "zh",
        'Timestamp' : int(timeData),
        'Version':versionData ,
    }

#
requestStr = "%s%s%s%s%s"%(requestMethod,uriData,"/","?",dictToStr(signDictData))

# 调用签名方法，同时将结果进行url编码，官方文档描述如下：
# 生成的签名串并不能直接作为请求参数，需要对其进行 URL 编码。 注意：如果用户的请求方法是GET，则对所有请求参
# 数值均需要做URL编码。 如上一步生成的签名串为 EliP9YW3pW28FpsEdkXt/+WcGeI= ，最终得到的签名串请求参数(Signature)
# 为： EliP9YW3pW28FpsEdkXt%2f%2bWcGeI%3d ，它将用于生成最终的请求URL。
signData = urllib.parse.quote(sign(secretKey,requestStr,signMethod))

# 上述操作是实现签名，下面即进行请求
# 先建立请求参数, 此处参数只在签名时多了一个Signature
actionArgs = signDictData
actionArgs["Signature"] = signData

# 根据uri构建请求的url
requestUrl = "https://%s/?"%(uriData)
# 将请求的url和参数进行拼接
requestUrlWithArgs = requestUrl + dictToStr(actionArgs)

# 获得response
responseData = urllib.request.urlopen(requestUrlWithArgs).read().decode("utf-8")

print(responseData)

# 获得到的结果形式：
#  {"Response":{"RequestId":"0fd2e5b4-0beb-4e01-906f-e63dd7dd33af","Source":"en","Target":"zh","TargetText":"\u4f60\u597d\u4e16\u754c"}}

# 对Json字符串处理
import json
print(json.loads(responseData)["Response"]["TargetText"])

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
        self.__EnPath = allfiles[pg.Current()].replace('.png', '.txt')
        self.__CnPath = "./cntags/" + self.__EnPath
        self.engtags = []
        self.cntags = []
        self.buttons = []
    
    def LoadTags(self)->list[str]:
        if(os.path.exists(self.__EnPath)):
            with open(self.__EnPath) as file:
                enfile = file.read()
                if(enfile!=''):
                    self.engtags =enfile.split(', ')
        self.LoadCnTags()
        
    def LoadCnTags(self)->list[str]: 
        if(os.path.exists(self.__CnPath)):
            with open(self.__CnPath) as file:
                cnfile = file.read()
                if(cnfile!=''):
                    self.cntags =cnfile.split('，')
        for i in range(len(self.cntags)):
            self.buttons.append(self.cntags[i] + '('+ self.engtags[i] +')  X')
        #for a,b in self.cntags, self.engtags:
            #self.buttons.append(a + '('+ b +')  X')
    
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

        with open(self.__EnPath, 'w') as f:
            f.write(st)
            with use_scope('txt' , clear=True):
                put_text(self.__EnPath, "保存成功") 
        
        if len(self.cntags) > 0:
            st = self.cntags[0]
            for i in range(1, len(self.cntags)):
                st += '，'+self.cntags[i]

        with open(self.__CnPath, 'w') as f:
            f.write(st)
            with use_scope('txt' , clear=True):
                put_text(self.__CnPath, "保存成功") 
        
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
        en = transTencentYun(tmp)
        tg.engtags.append(en)
        tg.buttons.append(en+ '('+ tmp +')  X')
        strtmp += (' '+en + ',')

    with use_scope('image'):
        with use_scope('trans', clear=True):
            put_text("有道翻译结果:", strtmp[:-1])

def ReloadImage(a :Page):
    with use_scope('image' , clear=True):
            put_image(open(pngfiles[a.Current()], 'rb').read())
            put_text(pngfiles[a.Current()], "  当前：", a.Current()+1, "/ 总共：", len(pngfiles))


def ReloadTagsButton(pg :Page):
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
        ReloadTagsButton(a)

    
def NextPage(a : Page):
    if a.NextPage():  
        ReloadImage(a)
        ReloadTagsButton(a)

def Jump(a, b: Page):
    num = int(a) - int(pngfiles[b.Current()].replace('.png', ''))
    if(b.Jump(num) == 1):
        ReloadImage(b)
        ReloadTagsButton(b)

def Save(tg:CurTags, pg:Page):
    tags = CurTags(pg, pngfiles)
    tags.engtags = tg.engtags
    tags.cntags = tg.cntags
    tags.buttons = tg.buttons
    
    tags.WriteTags()
    ReloadTagsButton(pg)

def AddSave(tg, pg):
    tags = CurTags(pg, pngfiles)
    tags.LoadTags()
    if(len(tags.engtags) == 0):
        Save(tg, pg)
        return
    tags.engtags += tg.engtags
    tags.cntags += tg.cntags
    tags.buttons += tg.buttons
    tags.WriteTags()  
    ReloadTagsButton(pg)


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

page=Page(len(pngfiles))

with use_scope('image'):
    ReloadImage(page)
put_buttons(['上一张','下一张'] , onclick=[lambda: PrePage(page), lambda: NextPage(page)])

put_input('CnTags', label='请输入该图片Tag，使用 , (中文逗号)分割')
tmptags = CurTags(page, pngfiles)
put_buttons(['翻译','覆盖保存','追加保存'], onclick=[lambda: Trans(pin.CnTags, tmptags), lambda: Save(tmptags, page), lambda: AddSave(tmptags, page)])


with use_scope('tags'):
    ReloadTagsButton(page)
put_input('Jump', label='输入需要跳转的图像编号（数字）')
put_button('跳转', onclick=lambda: Jump(pin.Jump, page))



