import base64
import json
import hashlib
import time
import datetime
from NWAD.models import api, log, token, member


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
    return json.loads(str.encode('utf-8'))

def jsonTostr(obj):
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
Token 정보 저장
"""
def tokenReg(request, tokenData):
    tokenType=["access_token","refresh_token"]
    for type in tokenType:
        if tokenData.keys().__contains__(type):
            token.objects.create(
                member_no=member.objects.filter(member_no=request.session["memberInfo"]["member_no"]).first(),
                api_no=tokenData["api"],
                type=type,
                token=tokenData[type],
                scope=tokenData["scope"]
            )
    

"""
Token 오래된 토큰 제거
호출시간 기준 저장된 시간보다 오래된 토큰 제거
"""
# def tokenRm():
#     tokenInfo = []
#     # tokenInfo.append({'type':'authorization_code','exp':'600'})
#     tokenInfo.append({'type':'access_token','exp':86400})
#     tokenInfo.append({'type':'refresh_token','exp':7776000})
#     now = datetime.datetime.now()

#     for ti in tokenInfo:
#         last = add_datetime(now, -1*ti["exp"])
#         token.objects.filter().all()