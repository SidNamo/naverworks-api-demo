
import requests
import json
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from hashlib import sha256
from urllib import parse

from django.views.decorators.csrf import csrf_exempt

from .models import log, member

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
            context["pw"] = sha256encode(request.POST["password"])
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
                insertLog(request, msg)
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
        insertLog(request, msg)
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
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break
        if(context["flag"] == "0"):
            try:
                member.objects.create(
                    id=request.POST["id"],
                    password=sha256encode(request.POST["password"]),
                    name=request.POST["name"],
                    email=request.POST["email"],
                )
            except Exception as err:
                context["flag"] = "9"
                context["result_msg"] = err
        insertLog(request, context["result_msg"])
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        
    
def apiList(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        return render(request, 'NWAD/API/apiList.html')
    elif request.method == "":
        return 

# def getApiList(request):
#     if request.method == "POST":


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
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break
            else: 
                apidata[val] = parse.quote(request.POST[val])
        if(context["flag"] == "0"):
            try:
                client = requests.session()
                csrftoken = client.get(request._current_scheme_host + "/login").cookies['csrftoken']
                headers = {'X-CSRFToken':csrftoken}
                res = client.post(request._current_scheme_host + "/auth/jwt", headers=headers, data=apidata)
                if res.status_code != 200:
                    context["flag"] = "2"
                    context["result_msg"] = "JWT 인증 API 호출 실패"
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err
        insertLog(request, context["result_msg"])
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)











def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def insertLog(request, msg):
    msg = request.path + "    " + msg
    msg += "    IP(" + getClientIp(request) + ")"
    log.objects.create(
        msg=msg,
        reg_user="system"
    )

def sha256encode(text):
    return sha256(text.encode()).hexdigest()