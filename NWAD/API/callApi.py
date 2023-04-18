import requests
import json
import re
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse
from common.utils import util
from NWAD.models import *
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

# Revaliate Token
def revalidate_token(api_no, token_type="access_token"):
    apiData = api.objects.filter(api_no=api_no).first()
    access_token = util.getAccessToken(apiData.api_no, token_type)

    if token_type != "jwt":
        if token_type == "access_token":
            token.objects.filter(api_no=apiData.api_no, type="access_token").delete()
            token_type="refresh_token"
        elif token_type == "refresh_token":
            token.objects.filter(api_no=apiData.api_no).delete()
            token_type = "jwt"

        return revalidate_token(api_no, token_type)
    else:
        return access_token


def getBotInfo(bot_id, access_token):
    nwa_url = 'https://www.worksapis.com/v1.0/bots/' + bot_id
    nwa_header = {'content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Authorization':authorization(access_token)}
    res = requests.get(url=nwa_url, headers=nwa_header)
    return res

@csrf_exempt
def sendMessage(api_no, bot_no, content, user_id="", channel_id=""):
    type = "users"
    channel = ""
    if user_id != "":
        channel = user_id
    else:
        type = "channels"
        channel = channel_id

    if isinstance(content, str):
        content = util.strToJson(content)

    res = sendMessageProc(api_no, bot_no, type, channel, content)
    return res

def sendMessageProc(api_no, bot_no, type, channel, content, token_type="access_token"):
    apiData = api.objects.filter(api_no=api_no).first()
    botData = bot.objects.filter(bot_no=bot_no).first()
    accessToken = util.getAccessToken(apiData.api_no, token_type)
    if accessToken != "":
        Authorization = authorization(accessToken)

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + botData.bot_id + "/" + type + "/" + channel + "/messages"
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        nwa_data = {}

        if (("content" in content) or ("contents" in content)):
            nwa_data["content"] = content
        else:
            nwa_data = content

        res = requests.post(url=nwa_url, headers=nwa_header, json=nwa_data)

        status = res.status_code
        if status != 201 and status != 200 and util.strToJson(res.text)["code"] == "UNAUTHORIZED":
            re = True
        else:
            re = False
    else:
        re = True
    if re:
        if token_type != "jwt":
            if token_type == "access_token":
                token.objects.filter(api_no=apiData.api_no, type="access_token").delete()
                token_type="refresh_token"
            elif token_type == "refresh_token":
                token.objects.filter(api_no=apiData.api_no).delete()
                token_type = "jwt"
            res = sendMessageProc(api_no, bot_no, type, channel, content, token_type)
    return res



def createChannel(api_no, bot_no, members, title):
    res = createChannelProc(api_no, bot_no, members, title)
    return res

def createChannelProc(api_no, bot_no, members, title, token_type="access_token"):
    apiData = api.objects.filter(api_no=api_no).first()
    botData = bot.objects.filter(bot_no=bot_no).first()
    accessToken = util.getAccessToken(apiData.api_no, token_type)
    if accessToken != "":
        Authorization = authorization(accessToken)

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + botData.bot_id + "/channels"
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        nwa_data = {}
        nwa_data["title"] = title
        nwa_data["members"] = members.split(",")
        res = requests.post(url=nwa_url, headers=nwa_header, json=nwa_data)
        status = res.status_code
        if status != 201 and status != 200 and util.strToJson(res.text)["code"] == "UNAUTHORIZED":
            re = True
        elif status == 201 or status == 200:
            re = False
        else:
            raise Exception(util.strToJson(res.text)["description"])
    else:
        re = True
    if re:
        if token_type != "jwt":
            if token_type == "access_token":
                token.objects.filter(api_no=apiData.api_no, type="access_token").delete()
                token_type="refresh_token"
            elif token_type == "refresh_token":
                token.objects.filter(api_no=apiData.api_no).delete()
                token_type = "jwt"
            res = createChannelProc(api_no, bot_no, members, title, token_type)
    return res


def getChannelMembers(api_no, bot_no, channel_id):
    apiData = api.objects.filter(api_no=api_no).first()
    botData = bot.objects.filter(bot_no=bot_no).first()
    res = getChannelMembersProc(api_no, botData.bot_id, channel_id)
    return res

def getChannelMembersProc(api_no, bot_id, channel_id, token_type="access_token", cursor=""):
    accessToken = util.getAccessToken(api_no, token_type)
    if accessToken != "":
        Authorization = authorization(accessToken)

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + bot_id + "/channels/" + channel_id +"/members"
        nwa_header = {'Authorization':Authorization}
        nwa_data = {}
        nwa_data["count"] = 100
        if cursor != "":
            nwa_data["cursor"] = cursor
        # nwa_url += "?" + nwa_data
        res = requests.get(url=nwa_url, headers=nwa_header, params=nwa_data)
        status = res.status_code
        if status != 201 and status != 200 and util.strToJson(res.text)["code"] == "UNAUTHORIZED":
            re = True
        else:
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
            res = getChannelMembersProc(api_no, bot_id, channel_id, token_type, cursor)
    return res


def getUserInfo(api_no, bot_no, user_id):
    res = getUserInfoProc(api_no, bot_no, user_id)
    return res

def getUserInfoProc(api_no, bot_no, user_id, token_type="access_token"):
    accessToken = util.getAccessToken(api_no, token_type)
    if accessToken != "":
        Authorization = authorization(accessToken)

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/users/' + user_id
        nwa_header = {'Authorization':Authorization}
        nwa_data = {}
        res = requests.get(url=nwa_url, headers=nwa_header, json=nwa_data)
        status = res.status_code
        if status != 201 and status != 200 and util.strToJson(res.text)["code"] == "UNAUTHORIZED":
            re = True
        else:
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
            res = getUserInfoProc(api_no, bot_no, user_id, token_type)
    return res


def authorization(accessToken):
    return "Bearer " + accessToken


# region 외부에서 호출 가능한 API

"""
인트라넷에서 사용하는 네이버웍스 봇 알람 기능
"""
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        api_no = data['api_no']
        bot_no = data['bot_no']
        target = data['target']
        content = data['content']

        json_content = setup_message_content(content)

        # For response - return
        res = False

        #Decide whether its channel Id or email(Account Id)
        if '@' in target:
            res = sendMessage(api_no, bot_no, json_content, user_id = target)
        else:
            res = sendMessage(api_no, bot_no, json_content, channel_id = target)

        response_data = {}

        if res:
            response_data['result'] = 'OK'
            response_data['message'] = 'Message Successfully Sent'
        else:
            response_data['result'] = 'Failed'
            response_data['message'] = res.text

        # Write Log
        util.insertLog(request, response_data['message'])

        return HttpResponse(json.dumps(response_data), content_type="application/json")


def setup_message_content(content):
    nw = util.Object()
    nw.content = util.Object()
    nw.content.type = content["type"]
    message_type = content["type"]

    if message_type == "text":
        nw.content.text = content["text"][:2000] # Naverworks Bot Message 는 2000자까지 지원
    elif message_type == "link":
        nw.content.contentText = content["contentText"][:1000] # 1000자까지 지원
        nw.content.linkText = content["linkText"][:1000]
        nw.content.link = content["link"][:1000]
    else:
        raise Exception("unsupported message type")

    json_content = nw.toJSON()

    return json_content

@csrf_exempt
def get_events_list(request, token_type="access_token"):
    if request.method == "POST":
        data = json.loads(request.body)
        api_no = data['api_no']
        user_id = data['user_id']
        calendar_id = data['calendar_id']
        # event_id = data['event_id'] if 'event_id' in data else ''
        
        start_date = data['start_date'].replace('.', '-') + "T00:00:00" + "%2B09:00"
        until_date = data['until_date'].replace('.', '-') + "T23:59:59" + "%2B09:00"
    else:
        raise Exception("unsupported request method")

    # d = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
    response_data = {}
    access_token = revalidate_token(api_no)

    if access_token != "":
        Authorization = authorization(access_token)

        url = 'https://www.worksapis.com/v1.0/users/{0}/calendars/{1}/events'.format(user_id, calendar_id)
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        params = { "fromDateTime" : start_date, "untilDateTime" : until_date}
        res = requests.get(url=url, headers=nwa_header, params=params)

        if res.status_code == 200:
            response_data['result'] = 'OK'
            response_data['content'] = res.text
        else:
            response_data['result'] = 'Failed'
            response_data['message'] = res.text
    else:
        response_data['result'] = 'Failed'
        response_data['message'] = 'Failed validating access token'

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def get_event(request, token_type="access_token"):
    if request.method == "POST":
        data = json.loads(request.body)
        api_no = data['api_no']
        user_id = data['user_id']
        calendar_id = data['calendar_id']
        event_id = data['event_id']
    else:
        raise Exception("unsupported request method")

    # d = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
    response_data = {}
    access_token = revalidate_token(api_no)

    if access_token != "":
        Authorization = authorization(access_token)

        url = 'https://www.worksapis.com/v1.0/users/{0}/calendars/{1}/events/{2}'.format(user_id, calendar_id, event_id)
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        res = requests.get(url=url, headers=nwa_header)

        if res.status_code == 200:
            response_data['result'] = 'OK'
            response_data['content'] = res.text
        else:
            response_data['result'] = 'Failed'
            response_data['message'] = res.text
    else:
        response_data['result'] = 'Failed'
        response_data['message'] = 'Failed validating access token'

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def create_event(request):
    if request.method == "POST":
        data = json.loads(request.body)
        api_no = data['authComponents']['api_no']
        user_id = data['authComponents']['user_id']
        calendar_id = data['authComponents']['calendar_id']
        event_components = data['eventComponents']
    else:
        raise Exception("unsupported request method")
        
    nwa_data = {}
    nwa_data['eventComponents'] = event_components
    response_data = {}
    access_token = revalidate_token(api_no)

    if access_token != "":
        Authorization = authorization(access_token)

        url = 'https://www.worksapis.com/v1.0/users/{0}/calendars/{1}/events'.format(user_id, calendar_id)
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        json_data = json.dumps(nwa_data, ensure_ascii=False)
        res = requests.post(url=url, headers=nwa_header, data=json_data.encode('utf-8'))

        if res.status_code in (200, 201):
            response_data['result'] = 'OK'
            response_data['content'] = res.text
        else:
            response_data['result'] = 'Failed'
            response_data['message'] = res.text
    else:
        response_data['result'] = 'Failed'
        response_data['message'] = 'Failed validating access token'

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def update_event(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        api_no = data['authComponents']['api_no']
        user_id = data['authComponents']['user_id']
        calendar_id = data['authComponents']['calendar_id']
        event_id = data['eventComponents'][0]['event_id']
        event_components = data['eventComponents']
    else:
        raise Exception("unsupported request method")
        
    nwa_data = {}
    nwa_data['eventComponents'] = event_components
    response_data = {}
    access_token = revalidate_token(api_no)

    if access_token != "":
        Authorization = authorization(access_token)

        url = 'https://www.worksapis.com/v1.0/users/{0}/calendars/{1}/events/{2}'.format(user_id, calendar_id, event_id)
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        json_data = json.dumps(nwa_data, ensure_ascii=False)
        res = requests.put(url=url, headers=nwa_header, data=json_data.encode('utf-8'))

        if res.status_code == 200:
            response_data['result'] = 'OK'
            response_data['content'] = res.text
        else:
            response_data['result'] = 'Failed'
            response_data['message'] = res.text
    else:
        response_data['result'] = 'Failed'
        response_data['message'] = 'Failed validating access token'

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def delete_event(request):
    if request.method == "DELETE":
        data = json.loads(request.body)
        api_no = data['authComponents']['api_no']
        user_id = data['authComponents']['user_id']
        calendar_id = data['authComponents']['calendar_id']
        event_id = data['eventComponents'][0]['event_id']
    else:
        raise Exception("unsupported request method")
        
    response_data = {}
    access_token = revalidate_token(api_no)

    if access_token != "":
        Authorization = authorization(access_token)

        url = 'https://www.worksapis.com/v1.0/users/{0}/calendars/{1}/events/{2}'.format(user_id, calendar_id, event_id)
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        res = requests.delete(url=url, headers=nwa_header)

        if res.status_code == 200:
            response_data['result'] = 'OK'
            response_data['content'] = res.text
        else:
            response_data['result'] = 'Failed'
            response_data['message'] = res.text
    else:
        response_data['result'] = 'Failed'
        response_data['message'] = 'Failed validating access token'

    return HttpResponse(json.dumps(response_data), content_type="application/json")

def getTargetIds(jsonData):
    data = json.loads(jsonData)
    if 'to' not in data:
        raise ValueError("No target in given data")
    if 'data' not in data['to']:
        raise ValueError("No data for target")

    for dest in data['to']['data']:
        if 'id' not in dest:
            continue
        targetId = dest['id']
        print("to_id:", targetId)
# endregion