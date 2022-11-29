from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from urllib import parse
from common.utils import util
from jwt import encode

def authJwt(request):
    result = {}
    status = 300
    try:
        client_id = parse.unquote(request.POST["client_id"])
        client_secret = parse.unquote(request.POST["client_secret"])
        service_account = parse.unquote(request.POST["service_account"])
        private_key = parse.unquote(request.POST["private_key"])

        header = {}
        header["alg"] = "RS256"
        header["typ"] = "JWT"
        headerStr = util.base64encode(header)

        payload = {}
        # payload["iss"] = client_id
        # payload["sub"] = service_account
        # now = datetime.datetime.now()
        # payload["iat"] = convert_unixtime(now)
        # payload["exp"] = convert_unixtime(add_datetime(now,3600)) #1시간 = 3600초
        payload["iss"] = "abcd"
        payload["sub"] = "46c4f281f81148c9b846c59262ae5888@example.com"
        payload["iat"] = 1634711358
        payload["exp"] = 1634714958
        payloadStr = util.base64encode(payload)
        
        signature = "{" + headerStr + "}.{" + payloadStr + "}"
        # signatureStr = util.sha256encode(signature)
        signatureStr = encode(payload=payload, key=private_key, algorithm="RS256", headers=header)

    except Exception as err:
        status = 500

    return JsonResponse(result, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=status) 