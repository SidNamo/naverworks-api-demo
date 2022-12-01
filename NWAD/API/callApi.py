import requests
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

def authrization(token):
    return "Bearer " + token