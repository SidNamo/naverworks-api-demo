import requests
import json
import re
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse
from common.utils import util
from NWAD.models import *


def getBotInfo(bot_id, access_token):
    nwa_url = 'https://www.worksapis.com/v1.0/bots/' + bot_id
    nwa_header = {'content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Authorization':authorization(access_token)}
    res = requests.get(url=nwa_url, headers=nwa_header)
    return res
    
def sendMessage(api_no, bot_no, content, user_id="", channel_id=""):
    type = "users"
    channel = ""
    if user_id != "":
        channel = user_id
    else:
        type = "channels"
        channel = channel_id

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
        nwa_data["content"] = content
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
    else:
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
    else:
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
    else:
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
    else:
        return res




def authorization(accessToken):
    return "Bearer " + accessToken
