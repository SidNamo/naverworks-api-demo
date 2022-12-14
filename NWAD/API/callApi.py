import requests
import json
import re
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse
from common.utils import util
from NWAD.models import *

def getBotInfo(request):
    result = {}
    status = 418
    try:
        bot_id = parse.unquote(request.POST["bot_id"])
        # bot_secret = parse.unquote(request.POST["bot_secret"])
        Authorization = authorization(parse.unquote(request.POST["access_token"]))

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + bot_id
        nwa_header = {'content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Authorization':Authorization}
        res = requests.get(url=nwa_url, headers=nwa_header)
        status = res.status_code
        result = util.strToJson(res.text)

    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 





def sendMessage(request):
    """
        {
            api_no: ~
            bot_no: ~
            user_id: ~ # 받는 사람
            channel_id: ~ # 받는 채널
            content: ~
        }
    """
    try:
        api_no = parse.unquote(request.POST["api_no"])
        bot_no = parse.unquote(request.POST["bot_no"])
        type = "users"
        channel = ""
        try:
            channel = parse.unquote(request.POST["user_id"])
        except:
            type = "channels"
            channel = parse.unquote(request.POST["channel_id"])

        content = util.strToJson(request.POST["content"])
        res = sendMessageProc(request, api_no, bot_no, type, channel, content)
        response = util.strToJson(res.text)
        status = res.status_code
    except Exception as err:
        status = 500
    return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 

def sendMessage2(request, api_no, bot_no, content, user_id="", channel_id=""):
    """
        {
            api_no: ~
            bot_no: ~
            user_id: ~ # 받는 사람
            channel_id: ~ # 받는 채널
            content: ~
        }
    """
    try:
        type = "users"
        channel = ""
        if user_id != "":
            channel = user_id
        else:
            type = "channels"
            channel = channel_id

        content = util.strToJson(content)
        res = sendMessageProc(request, api_no, bot_no, type, channel, content)
        response = util.strToJson(res.text)
        status = res.status_code
    except Exception as err:
        status = 500
    return res

def sendMessageProc(request, api_no, bot_no, type, channel, content, token_type="access_token"):
    apiData = api.objects.filter(api_no=api_no).first()
    botData = bot.objects.filter(bot_no=bot_no).first()
    accessToken = util.getAccessTokenForApi(request, apiData.api_no, token_type)
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
            res = sendMessageProc(request, api_no, bot_no, type, channel, content, token_type)
    else:
        return res



def createChannel(request):
    """
        {
            bot_id: ~
            access_token: ~
            members: ~ 대화방 생성에 포함될 멤버 (문자열 , 기준 공백 제거)
            title: ~ 대화방 제목
        }
    """
    try:
        api_no = parse.unquote(request.POST["api_no"])
        bot_no = parse.unquote(request.POST["bot_no"])
        members = parse.unquote(request.POST["members"])
        title = parse.unquote(request.POST["title"])
        res = createChannelProc(request, api_no, bot_no, members, title)
        response = util.strToJson(res.text)
        status = res.status_code
    except Exception as err:
        status = 500
    return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 

def createChannelProc(request, api_no, bot_no, members, title, token_type="access_token"):
    apiData = api.objects.filter(api_no=api_no).first()
    botData = bot.objects.filter(bot_no=bot_no).first()
    accessToken = util.getAccessTokenForApi(request, apiData.api_no, token_type)
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
            res = createChannelProc(request, api_no, bot_no, members, title, token_type)
    else:
        return res




def getUserInfo(request):
    """
        {
            api_no: ~
            bot_no: ~
            user_id: ~
        }
    """
    try:
        api_no = parse.unquote(request.POST["api_no"])
        bot_no = parse.unquote(request.POST["bot_no"])
        user_id = parse.unquote(request.POST["user_id"])
        res = getUserInfoProc(request,api_no, bot_no, user_id)
        response = util.strToJson(res.text)
        status = res.status_code
    except Exception as err:
        status = 500
    return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 

def getUserInfoProc(request, api_no, bot_no, user_id, token_type="access_token"):
    apiData = api.objects.filter(api_no=api_no).first()
    botData = bot.objects.filter(bot_no=bot_no).first()
    accessToken = util.getAccessTokenForApi(request, apiData.api_no, token_type)
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
                token.objects.filter(api_no=apiData.api_no, type="access_token").delete()
                token_type="refresh_token"
            elif token_type == "refresh_token":
                token.objects.filter(api_no=apiData.api_no).delete()
                token_type = "jwt"
            res = getUserInfoProc(request, api_no, bot_no, user_id, token_type)
    else:
        return res




def getChannelMembers(request):
    """
        {
            api_no: ~
            bot_no: ~
            channel_id: ~
        }
    """
    try:
        api_no = parse.unquote(request.POST["api_no"])
        bot_no = parse.unquote(request.POST["bot_no"])
        channel_id = parse.unquote(request.POST["channel_id"])
        res = getChannelMembersProc(request,api_no, bot_no, channel_id)
        response = util.strToJson(res.text)
        status = res.status_code
    except Exception as err:
        status = 500
    return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 

def getChannelMembersProc(request, api_no, bot_no, channel_id, token_type="access_token", cursor=""):
    apiData = api.objects.filter(api_no=api_no).first()
    botData = bot.objects.filter(bot_no=bot_no).first()
    accessToken = util.getAccessTokenForApi(request, apiData.api_no, token_type)
    if accessToken != "":
        Authorization = authorization(accessToken)

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + botData.bot_id + "/channels/" + channel_id +"/members"
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
            response = util.strToJson(res.text)
            if response["responseMetaData"]["nextCursor"] is not None:
                resp = getChannelMembersProc(request, api_no, bot_no, channel_id, cursor=response["responseMetaData"]["nextCursor"])
                response["members"].extend(util.strToJson(resp.text)["members"])
                response["responseMetaData"]["nextCursor"] = None
                type(res).text = util.jsonToStr(response)
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
            res = getChannelMembersProc(request, api_no, bot_no, channel_id, token_type, cursor)
    else:
        return res





def authorization(accessToken):
    return "Bearer " + accessToken
