import requests
import json
import re
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse
from common.utils import util

def getBotInfo(request):
    result = {}
    status = 418
    try:
        bot_id = parse.unquote(request.POST["bot_id"])
        # bot_secret = parse.unquote(request.POST["bot_secret"])
        Authorization = authrization(parse.unquote(request.POST["access_token"]))

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
            bot_id: ~
            access_token: ~
            user_id: ~ # 받는 사람
            channel_id: ~ # 받는 채널
            content: ~
        }
    """
    result = {}
    status = 418
    try:
        bot_id = parse.unquote(request.POST["bot_id"])
        type = "users"
        channel = ""
        try:
            channel = parse.unquote(request.POST["user_id"])
        except:
            type = "channels"
            channel = parse.unquote(request.POST["channel_id"])

        Authorization = authrization(parse.unquote(request.POST["access_token"]))

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + bot_id + "/" + type + "/" + channel + "/messages"
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        nwa_data = {}
        nwa_data["content"] = util.strToJson(request.POST["content"])
        res = requests.post(url=nwa_url, headers=nwa_header, json=nwa_data)
        status = res.status_code
        if status != 201:
            result = util.strToJson(res.text)

    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 


def createChannel(request):
    """
        {
            bot_id: ~
            access_token: ~
            members: ~ 대화방 생성에 포함될 멤버 (문자열 , 기준 공백 제거)
            title: ~ 대화방 제목
        }
    """
    result = {}
    status = 418
    try:
        bot_id = parse.unquote(request.POST["bot_id"])
        members = re.sub(r"\s", "", parse.unquote(request.POST["members"]))
        title = parse.unquote(request.POST["title"])
        Authorization = authrization(parse.unquote(request.POST["access_token"]))

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + bot_id + "/channels"
        nwa_header = {'content-Type':'application/json', 'Authorization':Authorization}
        nwa_data = {}
        nwa_data["title"] = title
        nwa_data["members"] = members.split(",")
        res = requests.post(url=nwa_url, headers=nwa_header, json=nwa_data)
        status = res.status_code
        result = util.strToJson(res.text)

    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 


def authrization(accessToken):
    return "Bearer " + accessToken