import requests
import base64
import json
import re
# import hashlib
# import time
import datetime
from urllib import parse
from NWAD.models import *
from AUTH.authApi import *
from django.conf import settings

host = settings.DEFAULT_DOMAIN


"""
공용으로 사용되는 Util 함수 모음
"""

"""
각종 string 인코딩
"""
def base64encode(jsonString):
    jsonString = json.dumps(jsonString, separators=(",", ":"))
    jsonString = base64.b64encode(jsonString.encode('utf-8'))
    result = jsonString.decode('utf-8')
    return result

def sha256encode(jsonString):
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
    res["max"] = 1 if count == 0 else data.count() // count + 1
    res["count"] = count
    dataList = []
    for idx, val in enumerate(data):
        if idx >= count*(now-1) and (True if count == 0 else idx < count*now):
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
                    token=tokenData[type["type"]],
                    exp_date=getTime(type["exp"])
                )
            else:
                token.objects.create(
                    api_no=tokenData["api"],
                    type=type["type"],
                    scope=tokenData["scope"],
                    reg_date=getTime(),
                    token=tokenData[type["type"]],
                    exp_date=getTime(type["exp"])
                )
    

    
"""
AccessToken 조회
1. DB에 AccessToken 있는지 조회
2. DB에 RefreshToken 있는지 조회
3. JWT 인증
"""
def getAccessToken(request, apiNo):
    tokenInfo = []
    # tokenInfo.append({'type':'authorization_code','exp':'600'})
    tokenInfo.append({'type':'access_token','exp':86400}) # 1일 = 86,400초
    tokenInfo.append({'type':'refresh_token','exp':7776000}) # 90일 = 7,776,000초
    accessToken = ""
    # AccessToken 조회
    type = "access_token"
    tokenData = token.objects.filter(
        member_no=member.objects.filter(member_no=request.session["memberInfo"]["member_no"]).first(),
        api_no=apiNo,
        type=type,
        exp_date__gt=getTime()
    ).first()
    if tokenData is not None:
        accessToken = tokenData.token
    else:
        type = "refresh_token"
        tokenData = token.objects.filter(
            member_no=member.objects.filter(member_no=request.session["memberInfo"]["member_no"]).first(),
            api_no=apiNo,
            type=type,
        exp_date__gt=getTime()
        ).first()

        apidata=api.objects.filter(
            member_no=member.objects.filter(member_no=request.session["memberInfo"]["member_no"]).first(),
            api_no=apiNo
        ).first()
        apidata = objectToDict(apidata)

        if tokenData is not None:
            apidata["refresh_token"] = tokenData.token
            # JWT Auth Api 호출
            client = requests.session()
            csrftoken = client.get(request._current_scheme_host + "/login").cookies['csrftoken']
            headers = {'X-CSRFToken':csrftoken}
            res = client.post(request._current_scheme_host + "/auth/authRefreshToken", headers=headers, data=apidata)
            result = strToJson(res.text) # 인증 완료 후 응답 값
            if res.status_code == 200:
                result["api"] = api.objects.filter(
                    member_no=member.objects.filter(member_no=request.session["memberInfo"]["member_no"]).first(),
                    api_no=apiNo
                ).first()
                tokenReg(request, result)
                accessToken = result["access_token"]
        else:
            # JWT Auth Api 호출
            client = requests.session()
            csrftoken = client.get(request._current_scheme_host + "/login").cookies['csrftoken']
            headers = {'X-CSRFToken':csrftoken}
            res = client.post(request._current_scheme_host + "/auth/jwt", headers=headers, data=apidata)
            result = strToJson(res.text) # 인증 완료 후 응답 값
            if res.status_code == 200:
                result["api"] = api.objects.filter(
                    member_no=member.objects.filter(member_no=request.session["memberInfo"]["member_no"]).first(),
                    api_no=apiNo
                ).first()
                tokenReg(request, result)
                accessToken = result["access_token"]

    return accessToken


    
"""
AccessToken 조회
1. DB에 AccessToken 있는지 조회
2. DB에 RefreshToken 있는지 조회
3. JWT 인증
"""
def getAccessTokenForApi(request, apiNo, type="access_token"):
        
    insertLog(request, "AccessToken 조회 시작")

    host = request._current_scheme_host
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
            accessToken = tokenData.token
    elif type == "refresh_token":
        # RefreshToken 조회
        tokenData = token.objects.filter(
            api_no=apiNo,
            scope=apiData.scope,
            type=type,
        exp_date__gt=getTime()
        ).first()
        if tokenData is not None:
            apidata["refresh_token"] = tokenData.token

            res = authRefreshToken(
                client_id=apiData.client_id,
                client_secret=apiData.client_secret,
                refresh_token=tokenData.token
            )

            # # JWT Auth Api 호출
            # client = requests.session()
            # csrftoken = client.get(host + "/login").cookies['csrftoken']
            # headers = {'X-CSRFToken':csrftoken}
            # res = client.post(host + "/auth/authRefreshToken", headers=headers, data=apidata)

            result = strToJson(res.text) # 인증 완료 후 응답 값
            if res.status_code == 200:
                result["api"] = api.objects.filter(
                    api_no=apiNo
                ).first()
                tokenReg(result)
                accessToken = result["access_token"]
    elif type == "jwt":

        res = authJwt(
            client_id=apiData.client_id,
            client_secret=apiData.client_secret,
            service_account=apiData.service_account,
            private_key=apiData.private_key,
            scope=apiData.scope
        )
            
        # # JWT Auth Api 호출
        # client = requests.session()
        # csrftoken = client.get(host + "/login").cookies['csrftoken']
        # headers = {'X-CSRFToken':csrftoken}
        # res = client.post(host + "/auth/jwt", headers=headers, data=apidata)

        result = strToJson(res.text) # 인증 완료 후 응답 값
        if res.status_code == 200:
            result["api"] = api.objects.filter(
                api_no=apiNo
            ).first()
            tokenReg(result)
            accessToken = result["access_token"]

    return accessToken

def messageObjToJson(type, content="", contents=[], text="", data="", header="", body="", footer=""):
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
            "paddingAll": "0px",
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
            footerContent.append(messageObjToJson(type="separator"))
            footerContent.append(messageObjToJson(type="button", text=fc["text"], data=fc["data"]))
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