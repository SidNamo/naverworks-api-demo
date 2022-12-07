import requests
import base64
import json
# import hashlib
# import time
import datetime
from urllib import parse
from NWAD.models import *
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
    host = request._current_scheme_host
    tokenInfo = []
    # tokenInfo.append({'type':'authorization_code','exp':'600'})
    tokenInfo.append({'type':'access_token','exp':86400}) # 1일 = 86,400초
    tokenInfo.append({'type':'refresh_token','exp':7776000}) # 90일 = 7,776,000초
    accessToken = ""
    if type == "access_token":
        # AccessToken 조회
        tokenData = token.objects.filter(
            api_no=apiNo,
            type=type,
            exp_date__gt=getTime()
        ).first()
        if tokenData is not None:
            accessToken = tokenData.token
    elif type == "refresh_token":
        # RefreshToken 조회
        tokenData = token.objects.filter(
            api_no=apiNo,
            type=type,
        exp_date__gt=getTime()
        ).first()
        apidata=api.objects.filter(
            api_no=apiNo
        ).first()
        apidata = objectToDict(apidata)
        if tokenData is not None:
            apidata["refresh_token"] = tokenData.token
            # JWT Auth Api 호출
            client = requests.session()
            csrftoken = client.get(host + "/login").cookies['csrftoken']
            headers = {'X-CSRFToken':csrftoken}
            res = client.post(host + "/auth/authRefreshToken", headers=headers, data=apidata)
            result = strToJson(res.text) # 인증 완료 후 응답 값
            if res.status_code == 200:
                result["api"] = api.objects.filter(
                    api_no=apiNo
                ).first()
                tokenReg(result)
                accessToken = result["access_token"]
    elif type == "jwt":
        # JWT Auth Api 호출
        apidata=api.objects.filter(
            api_no=apiNo
        ).first()
        apidata = objectToDict(apidata)
        client = requests.session()
        csrftoken = client.get(host + "/login").cookies['csrftoken']
        headers = {'X-CSRFToken':csrftoken}
        res = client.post(host + "/auth/jwt", headers=headers, data=apidata)
        result = strToJson(res.text) # 인증 완료 후 응답 값
        if res.status_code == 200:
            result["api"] = api.objects.filter(
                api_no=apiNo
            ).first()
            tokenReg(result)
            accessToken = result["access_token"]

    return accessToken
