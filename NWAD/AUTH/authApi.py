from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse
from common.utils import util

def authJwt(request):
    result = {}
    status = 300
    try:
        header = {}
        header["alg"] = "RS256"
        header["typ"] = "JWT"
        headerStr = util.base64encode(header)


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
        jsonClaimStr = util.base64encode(jsonClaim)
        
        signature = "{" + headerStr + "}.{" + jsonClaimStr + "}"
        signatureStr = util.sha256encode(signature)

        
    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status)