import requests
import json
from common.utils import util
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from urllib import parse

from django.views.decorators.csrf import csrf_exempt

from .models import member, api, bot, token

def index(request):
    if 'memberInfo' in request.session:
        return render(request, 'NWAD/main.html')
    else:
        return redirect('login')


def login(request):
    if request.method == "GET":
        if 'memberInfo' in request.session:
            return redirect('/')
        else:
            return render(request, 'NWAD/login.html')
    elif request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['id','password']
        replaceList = ['아이디를','비밀번호를']
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break

        if(context["flag"] == "0"):
            context["id"] = request.POST["id"]
            context["pw"] = util.sha256encode(request.POST["password"])
            memberSearchData = member.objects.filter(id=context["id"], password=context["pw"], status="1").first()
            if memberSearchData is None:
                memberSearchData = member.objects.filter(id=context["id"], password=context["pw"]).first()
                context["flag"] = "2"
                if memberSearchData is None:
                    context["result_msg"] = "일치하는 회원이 없습니다."
                else:
                    context["result_msg"] = "가입 승인 후 사용 가능합니다."
            else:
                memberInfo = {}
                memberInfo["member_no"] = memberSearchData.member_no
                memberInfo["name"] = memberSearchData.name
                memberInfo["email"] = memberSearchData.email
                memberInfo["id"] = memberSearchData.id
                request.session["memberInfo"] = memberInfo
                msg = ""
                msg += "유저 로그인(" + request.POST["id"] + ")"
                util.insertLog(request, msg + "    " + util.jsonTostr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def logout(request):
    if request.method == "GET":
        request.session.clear()
    return redirect('/')


def testLogin(request):
    if request.method == "GET":
        apiInfo = {}
        apiInfo["client_id"] = "dDX9hTgohiMOVOiG8XAC"
        apiInfo["client_secret"] = "ouyUJ8511q"
        apiInfo["service_account"] = "vyka1.serviceaccount@didim365.kr"
        apiInfo["private_key"] = ""
        apiInfo["scope"] = "bot"
        apiInfo["bot_id"] = "3481407"
        apiInfo["bot_secret"] = "IOmaUQa+ucJkcrXojZMs0fNxD9PnQl"
        request.session["apiInfo"] = apiInfo
        request.session["id"] = "test"
        msg = ""
        msg += "테스트 사이트 로그인(" + request.POST["id"] + ")"
        util.insertLog(request, msg + "    " + util.jsonTostr(request.POST.dict()))
    return redirect('/')


def join(request):
    if 'memberInfo' in request.session:
        return render(request, 'NWAD/main.html')
    if(request.method == "GET"):
        return render(request, 'NWAD/join.html')
    elif(request.method == "POST"):
        memeberInfo = {}
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['id','password','name','email']
        replaceList = ['아이디를','비밀번호를','이름을','이메일을']

        # 파라미터 검사
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break
            
        # 중복 검사    
        if(context["flag"] == "0"):
            memberData = member.objects.filter(id=request.POST["id"]).first()
            if memberData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 id 입니다."

        # 등록
        if(context["flag"] == "0"):
            try:
                member.objects.create(
                    id=request.POST["id"],
                    password=util.sha256encode(request.POST["password"]),
                    name=request.POST["name"],
                    email=request.POST["email"],
                )
            except Exception as err:
                context["flag"] = "9"
                context["result_msg"] = err
        util.insertLog(request, context["result_msg"] + "    " + util.jsonTostr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        
    
def apiList(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        return render(request, 'NWAD/API/apiList.html')
    elif request.method == "":
        return 

def getApiList(request):
    if request.method == "POST":
        apiData = api.objects.filter(member_no=request.session["memberInfo"]["member_no"]).all()
        res = util.objectToPaging(apiData, 1, 0)
        return JsonResponse(res, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def apiReg(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        return render(request, 'NWAD/API/apiReg.html')
    elif request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['api_name','client_id','client_secret','service_account','private_key','scope']
        replaceList = ['api 이름을','client id를','client secret을','service account를','private_key를','scope를',]
        apidata = {}

        # 파라미터 검사
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break
            else: 
                apidata[val] = parse.quote(request.POST[val])
                
        # 중복 검사    
        if(context["flag"] == "0"):
            apiData = api.objects.filter(client_id=request.POST["client_id"],member_no=request.session["memberInfo"]["member_no"]).first()
            if apiData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 client_id 입니다."

        if(context["flag"] == "0"):
            try:
                # JWT Auth Api 호출
                client = requests.session()
                csrftoken = client.get(request._current_scheme_host + "/login").cookies['csrftoken']
                headers = {'X-CSRFToken':csrftoken}
                res = client.post(request._current_scheme_host + "/auth/jwt", headers=headers, data=apidata)
                result = util.strToJson(res.text) # 인증 완료 후 응답 값
                if res.status_code == 200:

                    # API 테이블에 값 저장
                    result["api"] = api.objects.create(
                        api_name=request.POST["api_name"],
                        client_id=request.POST["client_id"],
                        client_secret=request.POST["client_secret"],
                        service_account=request.POST["service_account"],
                        private_key=request.POST["private_key"],
                        scope=request.POST["scope"],
                        rmk="",
                        member_no=member.objects.get(member_no=request.session["memberInfo"]["member_no"])
                    )
                    util.tokenReg(request, result)

                else:
                    context["flag"] = "2"
                    context["result_msg"] = result["error_description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err
        util.insertLog(request, context["result_msg"] + "    " + util.jsonTostr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def apiRm(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        try:
            api.objects.filter(api_no=request.POST["api_no"], member_no=request.session["memberInfo"]["member_no"]).delete()
        except Exception as err:
            context["flag"] = "2"
            context["result_msg"] = err
        util.insertLog(request, context["result_msg"] + "    " + util.jsonTostr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        


def botList(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        return render(request, 'NWAD/BOT/botList.html')
    elif request.method == "":
        return 

def getBotList(request):
    if request.method == "POST":
        apiData = bot.objects.filter(member_no=request.session["memberInfo"]["member_no"]).all()
        res = util.objectToPaging(apiData, 1, 0)
        return JsonResponse(res, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def botReg(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        apiData = api.objects.filter(member_no=request.session["memberInfo"]["member_no"]).all()
        return render(request, 'NWAD/BOT/botReg.html', {'apiData': apiData})
    elif request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['api_no','bot_id','bot_secret']
        replaceList = ['api no를','bot id를','bot secret을']
        apidata = {}
        
        # 파라미터 검사
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break
            else: 
                apidata[val] = parse.quote(request.POST[val])

        # API NO 유효성 검사
        apiData = api.objects.filter(api_no=request.POST["api_no"], member_no=request.session["memberInfo"]["member_no"]).first()
        if apiData is None:
            context["flag"] = "4"
            context["result_msg"] = "잘못된 API NO 입니다."
                
        # 중복 검사    
        if(context["flag"] == "0"):
            botData = bot.objects.filter(bot_id=request.POST["bot_id"],member_no=request.session["memberInfo"]["member_no"]).first()
            if botData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 bot id 입니다."

        if(context["flag"] == "0"):
            # AccessToken 조회
            apidata["access_token"] = util.getAccessToken(request, request.POST["api_no"])
            if apidata["access_token"] == "":
                context["flag"] = "5"
                context["result_msg"] = "access_token을 조회 할 수 없습니다."


        if(context["flag"] == "0"):
            try:
                # JWT Auth Api 호출
                client = requests.session()
                csrftoken = client.get(request._current_scheme_host + "/login").cookies['csrftoken']
                headers = {'X-CSRFToken':csrftoken}
                res = client.post(request._current_scheme_host + "/api/getBotInfo", headers=headers, data=apidata)
                result = util.strToJson(res.text) # 인증 완료 후 응답 값
                if res.status_code == 200:
                    # BOT 테이블에 값 저장
                    bot.objects.create(
                        bot_id=request.POST["bot_id"],
                        bot_secret=request.POST["bot_secret"],
                        bot_name=result["botName"],
                        rmk="",
                        member_no=member.objects.get(member_no=request.session["memberInfo"]["member_no"])
                    )

                else:
                    context["flag"] = "2"
                    context["result_msg"] = result["error_description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err
        util.insertLog(request, context["result_msg"] + "    " + util.jsonTostr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def botRm(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        try:
            bot.objects.filter(bot_no=request.POST["bot_no"], member_no=request.session["memberInfo"]["member_no"]).delete()
        except Exception as err:
            context["flag"] = "2"
            context["result_msg"] = err
        util.insertLog(request, context["result_msg"] + "    " + util.jsonTostr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        