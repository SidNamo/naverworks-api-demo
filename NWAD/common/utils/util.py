import requests
import base64
import json
import re
# import time
import datetime
from urllib import parse
from NWAD.models import *
from AUTH.authApi import *
from django.conf import settings
from django.contrib.auth.hashers import make_password
from Crypto.Cipher import AES
from hashlib import sha512

host = settings.DEFAULT_DOMAIN
aes256key = b'didim365didim365'
aes256iv = b'563midid563midid'

"""
공용으로 사용되는 Util 함수 모음
"""

"""
각종 string 인코딩
"""
def aes256encrypt(plaintext):
    # 패딩을 적용
    padding_length = AES.block_size - len(plaintext) % AES.block_size
    padding = chr(padding_length) * padding_length
    padded_text = plaintext + padding

    # 암호화
    cipher = AES.new(aes256key, AES.MODE_CBC, aes256iv)
    encrypted_text = cipher.encrypt(padded_text.encode('utf-8'))

    # 암호화된 값을 base64로 인코딩하여 반환
    encoded_encrypted_text = base64.b64encode(encrypted_text).decode('utf-8')
    return encoded_encrypted_text

def aes256decrypt(encoded_encrypted_text):
    # 저장된 값을 디코딩하고, 복호화
    decoded_encrypted_text = base64.b64decode(encoded_encrypted_text)
    cipher = AES.new(aes256key, AES.MODE_CBC, aes256iv)
    decrypted_text = cipher.decrypt(decoded_encrypted_text).decode('utf-8')

    # 복호화된 값에서 패딩 제거 후 반환
    padding_length = ord(decrypted_text[-1])
    decrypted_text = decrypted_text[:-padding_length]
    return decrypted_text

def sha512encrypt(string):
    # 문자열을 byte 형태로 인코딩
    string_bytes = string.encode('utf-8')
    
    # SHA-512 암호화 수행
    sha512_hash = sha512(string_bytes)
    hashed_string = sha512_hash.hexdigest()
    
    # 암호화된 문자열 리턴
    return hashed_string

def base64encode(jsonString):
    jsonString = json.dumps(jsonString, separators=(",", ":"))
    jsonString = base64.b64encode(jsonString.encode('utf-8'))
    result = jsonString.decode('utf-8')
    return result

def strToJson(str):
    if str != "":   
        return json.loads(str.encode('utf-8'))
    else: 
        return {}

def jsonToStr(obj):
    return json.dumps(obj, separators=(",", ":"))

def unicodeAddSlash(str):
    return re.sub('(u[0-9A-F]{4})',r'\\'+r'\1',str).encode('utf-8').decode('unicode_escape')

'''
시간 / 날짜 관련
'''
def convert_datetime(unixtime):
    """Convert unixtime to datetime"""
    date = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    return date # format : str

def convert_unixtime(date_time):
    """Convert datetime to unixtime"""
    try:
        unixtime = date_time.timestamp()
    except:
        unixtime = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').timestamp()
    return unixtime

def add_datetime(date_time, seconds):
    """
    :return: add 1 minute datetime
    """
    try:
        date_time += datetime.timedelta(seconds=seconds)
    except:
        date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        date_time += datetime.timedelta(seconds=seconds)
    return date_time

def getTime(seconds=0):
    now = datetime.datetime.now()
    return add_datetime(now, seconds)


"""
Client Ip 획득
"""
def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


"""
로그 기능
"""
def insertLog(request, msg):
    msg = request.path + "    " + msg
    msg += "    IP(" + getClientIp(request) + ")"
    
    log.objects.create(
        msg=msg,
        reg_user="system"
    )

"""
db objects 를 페이징 처리하여 object 형태로 변경
{
    now : 현재 페이지
    max : 최대 페이지
    count : 한 페이지에 노출되는 수
    data : 자료
}
"""
def objectToPaging(data, now=1, count=10):
    res = {}
    res["now"] = now
    res["max"] = 1 if count == 0 else (data.count() - 1) // count + 1
    res["count"] = count
    dataList = []
    for idx, val in enumerate(data):
        if idx >= count*(now-1) and (True if count == 0 else idx < count*now):
            if type(val) == type(dict()):
                val["idx"] = idx
                dataList.append(val)
            else:
                val.__dict__.pop('_state')
                val.__dict__['idx'] = idx
                dataList.append(val.__dict__)
    res["data"] = dataList
    return res

"""
db objects 를 dict 형태로 변경
"""
def objectToDict(data):
    res = data.__dict__
    res.pop('_state')
    return res


    
"""
Token 정보 저장
이전 기록이 있으면 UPDATE
"""
def tokenReg(tokenData):
    tokenInfo = []
    # tokenInfo.append({'type':'authorization_code','exp':'600'})
    tokenInfo.append({'type':'access_token','exp':86400}) # 1일 = 86,400초
    tokenInfo.append({'type':'refresh_token','exp':7776000}) # 90일 = 7,776,000초
    for type in tokenInfo:
        if tokenData.keys().__contains__(type["type"]):
            # 토큰정보 저장 (없으면 Insert 있으면 Update)
            item = token.objects.filter(
                api_no=tokenData["api"],
                type=type["type"],
                scope=tokenData["scope"]
            )
            if item.first() is not None:
                item.update(
                    token=aes256encrypt(tokenData[type["type"]]),
                    exp_date=getTime(type["exp"])
                )
            else:
                token.objects.create(
                    api_no=tokenData["api"],
                    type=type["type"],
                    scope=tokenData["scope"],
                    reg_date=getTime(),
                    token=aes256encrypt(tokenData[type["type"]]),
                    exp_date=getTime(type["exp"])
                )
    


def getAccessTokenRe(api_no, token_type="access_token"):
    res = util.getAccessToken(api_no, token_type)
    if res != "":
        re = False
    else:
        re = True
    if re:
        if token_type != "jwt":
            if token_type == "access_token":
                token.objects.filter(api_no=api_no, type="access_token").delete()
                token_type="refresh_token"
            elif token_type == "refresh_token":
                token.objects.filter(api_no=api_no).delete()
                token_type = "jwt"
            res = getAccessTokenRe(api_no, token_type)
    return res


"""
AccessToken 조회
1. DB에 AccessToken 있는지 조회
2. DB에 RefreshToken 있는지 조회
3. JWT 인증
"""
def getAccessToken(apiNo, type="access_token"):
        
    tokenInfo = []
    # tokenInfo.append({'type':'authorization_code','exp':'600'})
    tokenInfo.append({'type':'access_token','exp':86400}) # 1일 = 86,400초
    tokenInfo.append({'type':'refresh_token','exp':7776000}) # 90일 = 7,776,000초
    accessToken = ""
    apiData=api.objects.filter(
        api_no=apiNo
    ).first()
    apidata = objectToDict(apiData)
    if type == "access_token":
        # AccessToken 조회
        tokenData = token.objects.filter(
            api_no=apiNo,
            scope=apiData.scope,
            type=type,
            exp_date__gt=getTime()
        ).first()
        if tokenData is not None:
            accessToken = aes256decrypt(tokenData.token)
    elif type == "refresh_token":
        # RefreshToken 조회
        tokenData = token.objects.filter(
            api_no=apiNo,
            scope=apiData.scope,
            type=type,
        exp_date__gt=getTime()
        ).first()
        if tokenData is not None:
            apidata["refresh_token"] = aes256decrypt(tokenData.token)

            res = authRefreshToken(
                client_id=apiData.client_id,
                client_secret=apiData.client_secret,
                refresh_token=aes256decrypt(tokenData.token)
            )
            result = strToJson(res.text) # 인증 완료 후 응답 값
            if res.status_code == 200 or res.status_code == 201:
                result["api"] = api.objects.filter(
                    api_no=apiNo
                ).first()
                tokenReg(result)
                accessToken = result["access_token"]
    elif type == "jwt":

        res = authJwt(
            client_id=apiData.client_id,
            client_secret=aes256decrypt(apiData.client_secret),
            service_account=aes256decrypt(apiData.service_account),
            private_key=aes256decrypt(apiData.private_key),
            scope=apiData.scope
        )
        result = strToJson(res.text) # 인증 완료 후 응답 값
        if res.status_code == 200 or res.status_code == 201:
            result["api"] = api.objects.filter(
                api_no=apiNo
            ).first()
            tokenReg(result)
            accessToken = result["access_token"]
        else:
            raise Exception(result["error_description"])

    return accessToken

def messageObjToJson(type, content="", contents=[], text="", data="", header="", body="", footer="", color="#ffffff", uri="", padding="0px"):
    if type == "flex":
        res = {
            "type": "flex",
            "altText": text,
            "contents": content
        }
    elif type =="carousel":
        res = {
            "type": "carousel",
            "contents": contents
        }
    elif type =="bubble":
        res = {
            "type": "bubble",
        }
        if header != "":
            res["header"] = header
        if header != "":
            res["body"] = body
        if header != "":
            res["footer"] = footer
    elif type == "box":
        res = {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "paddingAll": padding,
        }
    elif type == "text":
        res = {
            "type": "text",
            "text": text,
            "wrap": True
        }
    elif type == "button":
        res = {
            "type": "button",
            "style": "link",
            "color": "#157efb",
            "height": "sm",
            "action": {
                "type": "postback",
                "label": text,
                "data": data
            }
        }
    elif type == "boxButtonLinkCustom":
        res = messageObjToJson(type="box", contents=[messageObjToJson(type="buttonLinkCustom", color=color, text=text, uri=uri)], padding=padding)
    elif type == "buttonLinkCustom":
        res = {
            "type": "button",
            "style": "primary",
            "color": color,
            "height": "sm",
            "paddingAll": "20px",
            "action": {
                "type": "uri",
                "label": text[0:20],
                "uri": uri
            }
        }
    elif type == "separator":
        res = {
            "type": "separator",
            "color": "#c9c9c9"
        } 
    return res

def makeMessageBtnTemplate(contents):
    """
        {
            altText: ~,
            contents: [
                {
                    header: [
                        {
                            text: ~,
                        },
                    ],
                    body: [
                        {
                            text: ~,
                        },
                    ],
                    footer: [
                        {
                            text: ~,
                            data: ~
                        },
                    ]
                },
            ]
        }
    """
    flex = messageObjToJson(type="flex")
    flex["altText"] = contents["altText"]
    carousel = messageObjToJson(type="carousel")
    bubbles = []
    for content in contents["contents"]:
        bubble = messageObjToJson(type="bubble")

        if len(content["header"]) > 0:
            header = messageObjToJson(type="box")
            header["paddingAll"] = "10px"
            header["paddingStart"] = "15px"
            headerContent = []
            for hc in content["header"]:
                headerText = messageObjToJson(type="text", text=hc["text"])
                headerText["color"] = "#000000"
                headerText["size"] = "sm"
                headerText["weight"] = "bold"
                headerContent.append(headerText)
            header["contents"] = headerContent
            bubble["header"] = header

        if len(content["body"]) > 0:
            body = messageObjToJson(type="box")
            body["paddingAll"] = "10px"
            body["paddingStart"] = "15px"
            if len(content["header"]) > 0:
                body["paddingTop"] = "0px"
            bodyContent = []
            for bc in content["body"]:
                if bc["text"] == "":
                    continue
                bodyText = messageObjToJson(type="text", text=bc["text"])
                bodyText["size"] = "sm"
                if len(content["header"]) != "":
                    bodyText["color"] = "#000000"
                bodyContent.append(bodyText)
            body["contents"] = bodyContent
            bubble["body"] = body

        footer = messageObjToJson(type="box")
        footerContent = []
        for fc in content["footer"]:
            if(fc.get('separator') != None):
                footerContent.append(messageObjToJson(type="separator"))
            footerContent.append(messageObjToJson(
                type = fc.get('type') if fc.get('type') != None else 'button',
                text = fc.get('text') if fc.get('text') != None else '',
                data = fc.get('data') if fc.get('data') != None else '',
                color = fc.get('color') if fc.get('color') != None else '',
                uri = fc.get('uri') if fc.get('uri') != None else '',
                padding = fc.get('padding') if fc.get('padding') != None else '',
            ))
        footer["contents"] = footerContent
        bubble["footer"] = footer

        bubbles.append(bubble)
    carousel["contents"] = bubbles
    flex["contents"] = carousel

    return jsonToStr(flex)

def messageTemplateSample():
    return {
        "altText": "",
        "contents": [
            {
                "header": [
                ],
                "body": [
                ],
                "footerBtn": [
                ]
            },
        ]
    }

def simpleTemplate(text, header="", button=[]):
    body = text
    if header != "":
        text = header
    content = {
        "altText": (text if len(text) < 30 else text[0:30]),
        "contents": [
            {
                "header": [
                ],
                "body": [
                ],
                "footer": [
                ]
            },
        ]
    }
    if header != "":
        content["contents"][0]["header"].append({"text":header, "data":""})
    if body != "":
        content["contents"][0]["body"].append({"text":body, "data":""})
    for btn in button:
        content["contents"][0]["footer"].append(btn)
    
    return makeMessageBtnTemplate(content)

"""
JSON SERIALIZE 대신 사용할 수 있는 Object
https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
"""
class Object():
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)