import requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse
from common.utils import util
from jwt import encode

def authJwt(request):
    result = {}
    status = 418
    try:
        client_id = parse.unquote(request.POST["client_id"])
        client_secret = parse.unquote(request.POST["client_secret"])
        service_account = parse.unquote(request.POST["service_account"])
        private_key = parse.unquote(request.POST["private_key"])
        scope = parse.unquote(request.POST["scope"])

        # 고정값
        header = {}
        header["alg"] = "RS256"
        header["typ"] = "JWT"
        headerStr = util.base64encode(header)

        payload = {}
        payload["iss"] = client_id
        payload["sub"] = service_account
        now = util.datetime.datetime.now()
        payload["iat"] = util.convert_unixtime(now)
        payload["exp"] = util.convert_unixtime(util.add_datetime(now,600)) #1시간 = 3600초 , 10분 = 600초
        
        signature = encode(payload=payload, key=private_key, algorithm="RS256", headers=header)

        # NaverWorks API 호출
        nwa_url = 'https://auth.worksmobile.com/oauth2/v2.0/token'
        nwa_header = {'content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
        nwa_data = {}
        nwa_data["assertion"] = signature # 생성한 JWT
        nwa_data["grant_type"] = "urn:ietf:params:oauth:grant-type:jwt-bearer" # 고정값
        nwa_data["client_id"] = client_id
        nwa_data["client_secret"] = client_secret
        nwa_data["scope"] = scope
        res = requests.post(url=nwa_url, headers=nwa_header, data=nwa_data)
        status = res.status_code
        result = util.strToJson(res.text)

    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 

def authRefreshToken(request):
    result = {}
    status = 418
    try:
        client_id = parse.unquote(request.POST["client_id"])
        client_secret = parse.unquote(request.POST["client_secret"])
        refresh_token = parse.unquote(request.POST["refresh_token"])

        # 고정값
        grant_type = "refresh_token"

        # NaverWorks API 호출
        nwa_url = 'https://auth.worksmobile.com/oauth2/v2.0/token'
        nwa_header = {'content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
        nwa_data = {}
        nwa_data["grant_type"] = grant_type
        nwa_data["client_id"] = client_id
        nwa_data["client_secret"] = client_secret
        nwa_data["refresh_token"] = refresh_token
        res = requests.post(url=nwa_url, headers=nwa_header, data=nwa_data)
        status = res.status_code
        result = util.strToJson(res.text)

    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 


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