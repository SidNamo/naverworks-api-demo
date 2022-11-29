import base64
import json
import time
import datetime
import hashlib
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse

def authJwt(request):
    result = {}
    status = 300
    try:
        header = {}
        header["alg"] = "RS256"
        header["typ"] = "JWT"
        headerStr = base64.b64encode(json.dumps(header).encode('ascii')).decode('utf-8')


        jsonClaim = {}
        # jsonClaim["iss"] = parse.unquote(request.POST["client_id"])
        # jsonClaim["sub"] = parse.unquote(request.POST["service_account"])
        # now = datetime.datetime.now()
        # jsonClaim["iat"] = convert_unixtime(now)
        # jsonClaim["exp"] = convert_unixtime(add_datetime(now,3600)) #1시간 = 3600초
        jsonClaim["iss"] = "abcd"
        jsonClaim["sub"] = "46c4f281f81148c9b846c59262ae5888@example.com"
        jsonClaim["iat"] = 1634711358
        jsonClaim["exp"] = 1634714958
        jsonClaimStr = base64.b64encode(json.dumps(jsonClaim).encode('ascii')).decode('utf-8')
        
        signature = "{" + headerStr + "}.{" + jsonClaimStr + "}"
        signatureStr = hashlib.sha256()

        
    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status)



def convert_datetime(unixtime):
    """Convert unixtime to datetime"""
    date = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    return date # format : str

def convert_unixtime(date_time):
    """Convert datetime to unixtime"""
    unixtime = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').timestamp()
    return unixtime

def add_datetime(date_time, seconds):
    """
    :return: add 1 minute datetime
    """
    import datetime
    date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    date_time += datetime.timedelta(seconds=seconds)
    return date_time