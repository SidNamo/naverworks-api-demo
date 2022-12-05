import requests
import json
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
        user_id = parse.unquote(request.POST["user_id"])
        Authorization = authrization(parse.unquote(request.POST["access_token"]))

        # NaverWorks API 호출
        nwa_url = 'https://www.worksapis.com/v1.0/bots/' + bot_id + "/users/" + user_id + "/messages"
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


def authrization(accessToken):
    return "Bearer " + accessToken