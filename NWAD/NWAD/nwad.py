from itertools import chain
import random
import string
import requests
import json
import re
from common.utils import util
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from urllib import parse
from django.template import loader
from django.core import serializers
from django.core.mail import send_mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import *
from API.callApi import *
from AUTH.authApi import *

# region Main 관련

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
            context = {}
            user_ip = request.META.get('REMOTE_ADDR', '')  # 요청 객체의 IP 주소를 가져옵니다.

            if user_ip in (settings.INTRANET_IP, '127.0.0.1'):  # IP 주소가 로컬일 경우
                isAllowedIP = True
            else:
                isAllowedIP = False

            context['isAllowedIP'] = isAllowedIP

            return render(request, 'NWAD/login.html', context)
    elif request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['id', 'password']
        replaceList = ['아이디를', '비밀번호를']
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break

        if (context["flag"] == "0"):
            context["id"] = request.POST["id"]
            context["pw"] = util.sha512encrypt(request.POST["password"])
            memberSearchData = member.objects.filter(
                id=context["id"], password=context["pw"], status="1").first()
            if memberSearchData is None:
                context["flag"] = "2"
                memberSearchData = member.objects.filter(
                    id=context["id"], password=context["pw"], status="2").first()
                if memberSearchData is not None:
                    context["result_msg"] = "가입 승인 후 사용 가능합니다."
                else:
                    memberSearchData = member.objects.filter(
                        id=context["id"]).first()
                    if memberSearchData is not None:
                        context["result_msg"] = "비밀번호가 일치하지 않습니다."
                    else:
                        context["result_msg"] = "일치하는 회원이 없습니다."
            else:
                memberInfo = {}
                memberInfo["member_no"] = memberSearchData.member_no
                memberInfo["name"] = memberSearchData.name
                memberInfo["email"] = util.aes256decrypt(memberSearchData.email)
                memberInfo["id"] = memberSearchData.id
                memberInfo["corp_name"] = memberSearchData.corp_name
                request.session["memberInfo"] = memberInfo
                msg = ""
                msg += "유저 로그인(" + request.POST["id"] + ")"
                util.insertLog(request, msg + "    " +
                               util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def logout(request):
    if request.method == "GET":
        request.session.clear()
    return redirect('/')


def join(request):
    if 'memberInfo' in request.session:
        return render(request, 'NWAD/main.html')
    if (request.method == "GET"):
        return render(request, 'NWAD/join.html')
    elif (request.method == "POST"):
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['id', 'password', 'name', 'email', 'corp_name']
        replaceList = ['아이디를', '비밀번호를', '이름을', '이메일을', '업체명을']

        # 파라미터 검사
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break

        # 중복 검사
        if (context["flag"] == "0"):
            memberData = member.objects.filter(id=request.POST["id"]).first()
            if memberData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 id 입니다."

        # 등록
        if (context["flag"] == "0"):
            try:
                member.objects.create(
                    id=request.POST["id"],
                    password=util.sha512encrypt(request.POST["password"]),
                    name=request.POST["name"],
                    email=util.aes256encrypt(request.POST["email"]),
                    corp_name=request.POST["corp_name"],
                    status="1"
                )
            except Exception as err:
                context["flag"] = "9"
                context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def withdrawal(request):
    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"

        # 파라미터 검사
        if (request.POST["current_password"] == None or request.POST["current_password"] == ""):
            context["flag"] = "2"
            context["result_msg"] = "비밀번호를 입력하세요"
        else:
            memberSearchData = member.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                password=util.sha512encrypt(request.POST["current_password"])
            ).first()
            if memberSearchData is None:
                context["flag"] = "3"
                context["result_msg"] = "비밀번호가 잘못되었습니다."
            else:
                memberSearchData.delete()
                request.session.clear()
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

        
        
        # request.session.clear()
        


def loginFind(request):
    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['name', 'email', 'id']
        replaceList = ['이름을', '이메일을', '아이디를']
        for idx, val in enumerate(checkList):
            if (val == 'id' and request.POST['type'] == 'id'):
                continue
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break

        if (context["flag"] == "0"):
            if (request.POST["type"] == "id"):
                memberSearchData = member.objects.filter(
                    name=request.POST["name"], email=util.aes256encrypt(request.POST["email"]), status="1").first()
            elif (request.POST["type"] == "pw"):
                memberSearchData = member.objects.filter(
                    name=request.POST["name"], email=util.aes256encrypt(request.POST["email"]), id=request.POST["id"], status="1").first()

            if memberSearchData is None:
                context["flag"] = "2"
                if (request.POST["type"] == "id"):
                    memberSearchData = member.objects.filter(
                        name=request.POST["name"], email=util.aes256encrypt(request.POST["email"]), status="2").first()
                elif (request.POST["type"] == "pw"):
                    memberSearchData = member.objects.filter(
                        name=request.POST["name"], email=util.aes256encrypt(request.POST["email"]), id=request.POST["id"], status="2").first()
                if memberSearchData is None:
                    context["result_msg"] = "일치하는 회원이 없습니다."
                else:
                    context["result_msg"] = "가입 승인 후 사용 가능합니다."
            else:
                context["val"] = ""
                if (request.POST["type"] == "id"):
                    # context["id"] = memberSearchData.id[0:(len(memberSearchData.id) - len(memberSearchData.id)//2)] + ('*' * (len(memberSearchData.id)//2))
                    context["id"] = memberSearchData.id[0:3] + ('*' * 6)
                if (request.POST["type"] == "pw"):
                    new_pw = ""
                    for i in range(20):
                        new_pw += str(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*()"))
                    memberSearchData.password = util.sha512encrypt(new_pw)
                    memberSearchData.save()
                    context["pw"] = new_pw
                msg = ""
                msg += "아이디/비밀번호 찾기 (" + str(memberSearchData.member_no) + ")"
                util.insertLog(request, msg + "    " +
                               util.jsonToStr(request.POST.dict()))

                send_simple_mail(request.POST["email"], '임시 비밀번호 발급 안내', '임시비밀번호', new_pw)
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def joinIdCheck(request):
    if (request.method == "POST"):
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"

        # 중복 검사
        if (context["flag"] == "0"):
            memberData = member.objects.filter(id=request.POST["id"]).first()
            if memberData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 id 입니다."
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def mypage(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        context = {
            'id': request.session["memberInfo"]["id"],
            'name': request.session["memberInfo"]["name"],
            'email': request.session["memberInfo"]["email"],
            'corp_name': request.session["memberInfo"]["corp_name"],
        }
        return render(request, 'NWAD/mypage.html', context)
    elif request.method == "POST":
        if request.POST["type"] == "saveInfo":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            checkList = ['id', 'corp_name', 'name', 'email']
            replaceList = ['아이디를', '업체명을', '관리자 이름을' ,'이메일을']
            for idx, val in enumerate(checkList):
                if (request.POST[val] == None or request.POST[val] == ""):
                    context["flag"] = "2"
                    context["result_msg"] = replaceList[idx] + " 입력하세요"
                    break

            if (context["flag"] == "0"):
                memberSearchData = member.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"],
                    status="1"
                ).first()
                if memberSearchData is not None:
                    memberSearchData.id = request.POST["id"]
                    memberSearchData.corp_name = request.POST["corp_name"]
                    memberSearchData.name = request.POST["name"]
                    memberSearchData.email = util.aes256encrypt(request.POST["email"])
                    memberSearchData.save()

                    memberInfo = request.session["memberInfo"]
                    memberInfo["id"] = memberSearchData.id
                    memberInfo["corp_name"] = memberSearchData.corp_name
                    memberInfo["name"] = memberSearchData.name
                    memberInfo["email"] = util.aes256decrypt(memberSearchData.email)
                    request.session["memberInfo"] = memberInfo
                    msg = ""
                    msg += "유저 정보수정( 회원번호 : " + str(request.session["memberInfo"]["member_no"]) + " )"
                    util.insertLog(request, msg + "    " +
                                util.jsonToStr(request.POST.dict()))
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        elif request.POST["type"] == "checkPw":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            memberSearchData = member.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                password=util.sha512encrypt(request.POST["password"]),
                status="1"
            ).all()
            context["count"] = str(len(memberSearchData))
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        elif request.POST["type"] == "savePw":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            checkList = ['current_password', 'new_password', 'new_password_check']
            replaceList = ['기존 비밀번호를', '새 비밀번호를', '새 비밀번호 확인을']
            for idx, val in enumerate(checkList):
                if (request.POST[val] == None or request.POST[val] == ""):
                    context["flag"] = "2"
                    context["result_msg"] = replaceList[idx] + " 입력하세요"
                    break

            if (context["flag"] == "0"):
                memberSearchData = member.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"],
                    password=util.sha512encrypt(request.POST["current_password"]),
                    status="1"
                ).all()
                if len(memberSearchData) == 0:
                    context["flag"] = "2"
                    context["result_msg"] = "기존 비밀번호가 다릅니다"

            if (context["flag"] == "0"):
                if request.POST["new_password"] != request.POST["new_password_check"]:
                    context["flag"] = "2"
                    context["result_msg"] = "비밀번호가 일치하지 않습니다"

            if (context["flag"] == "0"):
                memberSearchData = member.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"],
                    status="1"
                ).first()
                if memberSearchData is not None:
                    memberSearchData.password = util.sha512encrypt(request.POST["new_password"])
                    memberSearchData.save()
                    msg = ""
                    msg += "유저 비밀번호 수정( 회원번호 : " + str(request.session["memberInfo"]["member_no"]) + " )"
                    util.insertLog(request, msg + "    " +
                                util.jsonToStr(request.POST.dict()))
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
# endregion

@csrf_exempt
def botMessage(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        context = {
            'name': request.session["memberInfo"]["name"],
            'api_no': request.GET.get('api_no'),
            'bot_no': request.GET.get('bot_no')
        }
        return render(request, 'NWAD/bot-message.html', context)
    elif request.method == "POST":
        if request.POST["type"] == "getDefaultData":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            try:
                apiData = api.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"]).all()
                context["api_data"] = util.objectToPaging(apiData, 1, 0)
                botData = bot.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"]).all()
                context["bot_data"] = util.objectToPaging(botData, 1, 0)
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        if request.POST["type"] == "sendMessage":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            # 파라미터 유효성 검사
            apiData = api.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                api_no=request.POST["api_no"]
            ).first()
            if apiData is None:
                context["flag"] = "4"
                context["result_msg"] = "잘못된 API NO 입니다."
            
            if context["flag"] == "0":
                botData = bot.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"],
                    bot_no=request.POST["bot_no"]
                ).first()
                if botData is None:
                    context["flag"] = "4"
                    context["result_msg"] = "잘못된 BOT NO 입니다."
            
            if context["flag"] == "0":
                if(request.POST["message_type"] == "textUrl" and not request.POST["url"].startswith('http')):
                    context["flag"] = "4"
                    context["result_msg"] = "프로토콜을 입력해주세요."


            if (context["flag"] == "0"):
                try:
                    # 멤버 확인 모든 멤버가 정상적인 멤버인지
                    members = request.POST["member"].replace(" " , "").split(',')
                    sTo = []
                    for member in members:
                        res = getUserInfo(apiData.api_no, botData.bot_no, member)
                        result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                        if res.status_code != 200 and res.status_code != 201:
                            res = getChannelMembers(apiData.api_no, botData.bot_no, member)
                            result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                            if res.status_code != 200 and res.status_code != 201:
                                context["flag"] = "2"
                                context["result_msg"] = "Member Id 가 존재하지 않습니다."
                                break
                            else:
                                sTo.append({"id":member, "type":"channel"})
                        else:
                            sTo.append({"id":member, "type":"member"})
                    if context["flag"] == "0":
                        # 컨텐츠 제작
                        btn = []
                        if(request.POST["message_type"] == "textUrl"):
                            btn.append({"type":"boxButtonLinkCustom","color":request.POST["btn_color"],"text":request.POST["btn_text"],"uri":request.POST["url"],"padding":"10px"})
                        content = util.simpleTemplate(request.POST["message"], button=btn)

                        for member in sTo:
                            # 메시지 전송
                            if member["type"] == "member":
                                res = sendMessage(
                                    api_no=apiData.api_no, 
                                    bot_no=botData.bot_no, 
                                    content=content, 
                                    user_id=member["id"]
                                )
                            else:
                                res = sendMessage(
                                    api_no=apiData.api_no, 
                                    bot_no=botData.bot_no, 
                                    content=content, 
                                    channel_id=member["id"]
                                )
                            result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                            if res.status_code != 200 and res.status_code != 201:
                                context["flag"] = "2"
                                context["result_msg"] = result["description"]
                                break

                except Exception as err:
                    context["flag"] = "2"
                    context["result_msg"] = err.args[0]
            util.insertLog(
                request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def scenarioList(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        context = {
            'name': request.session["memberInfo"]["name"],
        }
        return render(request, 'NWAD/scenario-list.html', context)
    elif request.method == "POST":
        if request.POST["type"] == "getList":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            try:
                scenSearchData = scen.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"],
                    status=1
                ).values('scen_no', 'scen_name', 'scen_type__title')
                context["data"] = util.objectToPaging(scenSearchData, int(request.POST["page"]), int(request.POST["count"]))
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        elif request.POST["type"] == "rmScen":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            try:
                scenSearchData = scen.objects.filter(
                    scen_no=request.POST["scen_no"],
                    member_no=request.session["memberInfo"]["member_no"],
                    status=1
                ).first()
                scenSearchData.status=9
                scenSearchData.save()
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        elif request.POST["type"] == "getInfo":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            try:
                if request.POST["scen_no"] != "":
                    scenData = scen.objects.filter(
                        scen_no=request.POST["scen_no"],
                        member_no=request.session["memberInfo"]["member_no"],
                        status=1
                    ).first()
                    context["scen_data"] = util.objectToDict(scenData)
                apiData = api.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"]).all()
                context["api_data"] = util.objectToPaging(apiData, 1, 0)
                botData = bot.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"]).all()
                context["bot_data"] = util.objectToPaging(botData, 1, 0)
                scenTypeData = scen_type.objects.all()
                context["scen_type_data"] = util.objectToPaging(scenTypeData, 1, 0)
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        elif request.POST["type"] == "updScen":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            try:
                checkList = ['scen_type', 'scen_name', 'domain', 'api_no', 'bot_no', 'members']
                replaceList = ['Scenario Template 를 선택하세요', 'Scenario Name 을 입력하세요', 'Domain Id 를 입력하세요', 'API 를 선택하세요' ,'Bot 을 선택하세요', 'Member 를 입력하세요']
                for idx, val in enumerate(checkList):
                    if (val == 'id' and request.POST['type'] == 'id'):
                        continue
                    if (request.POST[val] == None or request.POST[val] == ""):
                        raise Exception(replaceList[idx])

                # 파라미터 유효성 검사
                apiData = api.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"],
                    api_no=request.POST["api_no"]
                ).first()
                if apiData is None:
                    context["flag"] = "4"
                    context["result_msg"] = "잘못된 API NO 입니다."
                
                if context["flag"] == "0":
                    botData = bot.objects.filter(
                        member_no=request.session["memberInfo"]["member_no"],
                        bot_no=request.POST["bot_no"]
                    ).first()
                    if botData is None:
                        context["flag"] = "4"
                        context["result_msg"] = "잘못된 BOT NO 입니다."
                
                # 중복 데이터 조회
                if context["flag"] == "0":
                    scenData = scen.objects.filter(
                        member_no=request.session["memberInfo"]["member_no"],
                        domain=request.POST["domain"],
                        status=1
                    ).exclude(scen_no=request.POST["scen_no"]).first()
                    if scenData is not None:
                        context["flag"] = "3"
                        context["result_msg"] = "중복된 Domain Id 입니다."
                if (context["flag"] == "0"):
                    res = createChannel(
                        api_no=apiData.api_no, 
                        bot_no=botData.bot_no,
                        members=re.sub(r"\s", "", request.POST["members"]),
                        title="익명 보고 시나리오 결재자",
                    )
                    result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                    if res.status_code != 200 and res.status_code != 201:
                        context["flag"] = "2"
                        context["result_msg"] = result["description"]
                    else:
                        channelId = result["channelId"]
                        res = getChannelMembers(
                            api_no=apiData.api_no, 
                            bot_no=botData.bot_no, 
                            channel_id=channelId
                        )
                        result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                        if res.status_code != 200 and res.status_code != 201:
                            raise Exception(result["description"])
                        else:
                            members = ",".join(result["members"])
                        # DB 저장
                        scenData = scen.objects.filter(
                            member_no = request.session["memberInfo"]["member_no"],
                            scen_no = request.POST["scen_no"]
                        ).first()

                        scenData.scen_type = scen_type.objects.filter(scen_type=request.POST["scen_type"]).first()
                        scenData.scen_name = request.POST["scen_name"]
                        scenData.api_no = apiData
                        scenData.bot_no = botData
                        scenData.domain = request.POST["domain"]
                        scenData.channel = channelId
                        scenData.members = request.POST["members"]
                        scenData.save()

                        text = "익명 보고 시나리오 결재자 단톡방입니다."
                        # 메시지 전송
                        res = sendMessage(
                            api_no=scenData.api_no.api_no, 
                            bot_no=scenData.bot_no.bot_no, 
                            content=util.simpleTemplate(text), 
                            channel_id=scenData.channel
                        )
                        result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                    
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
            util.insertLog(
                request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def scenarioAdd(request):
    if 'memberInfo' not in request.session:
        return redirect('login')
    
    if request.method == "GET":
        context = {
            'name': request.session["memberInfo"]["name"],
        }
        return render(request, 'NWAD/scenario-add.html', context)
    elif request.method == "POST":
        if request.POST["type"] == "getApiBot":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            try:
                apiData = api.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"]
                )
                context["api_data"] = util.objectToPaging(apiData, 1, 0)
                botData = bot.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"]
                )
                context["bot_data"] = util.objectToPaging(botData, 1, 0)
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        elif request.POST["type"] == "regScen":
            context = {}
            context["flag"] = "0"
            context["result_msg"] = "success"
            try:
                checkList = ['scen_type', 'scen_name', 'domain', 'api_no', 'bot_no', 'members']
                replaceList = ['Scenario Template 를 선택하세요', 'Scenario Name 을 입력하세요', 'Domain Id 를 입력하세요', 'API 를 선택하세요' ,'Bot 을 선택하세요', 'Member 를 입력하세요']
                for idx, val in enumerate(checkList):
                    if (val == 'id' and request.POST['type'] == 'id'):
                        continue
                    if (request.POST[val] == None or request.POST[val] == ""):
                        raise Exception(replaceList[idx])

                # 파라미터 유효성 검사
                apiData = api.objects.filter(
                    member_no=request.session["memberInfo"]["member_no"],
                    api_no=request.POST["api_no"]
                ).first()
                if apiData is None:
                    context["flag"] = "4"
                    context["result_msg"] = "잘못된 API NO 입니다."
                
                if context["flag"] == "0":
                    botData = bot.objects.filter(
                        member_no=request.session["memberInfo"]["member_no"],
                        bot_no=request.POST["bot_no"]
                    ).first()
                    if botData is None:
                        context["flag"] = "4"
                        context["result_msg"] = "잘못된 BOT NO 입니다."
                
                # 중복 데이터 조회
                if context["flag"] == "0":
                    scenData = scen.objects.filter(
                        domain=request.POST["domain"],
                        status=1
                    ).first()
                    if scenData is not None:
                        context["flag"] = "3"
                        context["result_msg"] = "중복된 Domain Id 입니다."


                if (context["flag"] == "0"):
                    res = createChannel(
                        api_no=apiData.api_no, 
                        bot_no=botData.bot_no,
                        members=re.sub(r"\s", "", request.POST["members"]),
                        title="익명 보고 시나리오 결재자",
                    )
                    result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                    if res.status_code != 200 and res.status_code != 201:
                        context["flag"] = "2"
                        context["result_msg"] = result["description"]
                    else:
                        channelId = result["channelId"]
                        res = getChannelMembers(
                            api_no=apiData.api_no, 
                            bot_no=botData.bot_no, 
                            channel_id=channelId
                        )
                        result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                        if res.status_code != 200 and res.status_code != 201:
                            raise Exception(result["description"])
                        else:
                            members = ",".join(result["members"])
                        # DB 저장
                        scenData = scen.objects.create(
                            scen_type = scen_type.objects.filter(scen_type=request.POST["scen_type"]).first(),
                            scen_name = request.POST["scen_name"],
                            api_no = apiData,
                            bot_no = botData,
                            domain = request.POST["domain"],
                            channel = channelId,
                            members = members,
                            member_no = member.objects.filter(member_no=request.session["memberInfo"]["member_no"],status="1").first()
                        )
                        text = "익명 보고 시나리오 결재자 단톡방입니다."
                        # 메시지 전송
                        res = sendMessage(
                            api_no=scenData.api_no.api_no, 
                            bot_no=scenData.bot_no.bot_no, 
                            content=util.simpleTemplate(text), 
                            channel_id=scenData.channel
                        )
                        result = util.strToJson(res.text)  # 인증 완료 후 응답 값
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
            util.insertLog(
                request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
            return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def apiBotList(request):
    if 'memberInfo' in request.session:
        context = {
            'name': request.session["memberInfo"]["name"],
        }
        return render(request, 'NWAD/api-bot-list.html', context)
    else:
        return redirect('login')



# region Api 관련


def apiList(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "GET":
        return render(request, 'NWAD/API/apiList.html')
    elif request.method == "":
        return


def getApiList(request):
    if request.method == "POST":
        apiData = api.objects.filter(
            member_no=request.session["memberInfo"]["member_no"]).all()
        res = util.objectToPaging(apiData, 1, 0)
        return JsonResponse(res, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def getApi(request):
    context = {}
    context["flag"] = "0"
    context["result_msg"] = "success"
    if request.method == "POST":
        try:
            apiData = api.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                api_no=request.POST["api_no"]
            ).first()

            apiData.client_secret = util.aes256decrypt(apiData.client_secret)
            apiData.service_account = util.aes256decrypt(apiData.service_account)
            apiData.private_key = util.aes256decrypt(apiData.private_key)

            context["data"] = util.objectToDict(apiData)
        except Exception as err:
            context["flag"] = "2"
            context["result_msg"] = err.args[0]
    return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def apiReg(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['api_name', 'client_id', 'client_secret',
                     'service_account', 'private_key', 'scope']
        replaceList = ['api 이름을', 'client id를', 'client secret을',
                       'service account를', 'private_key를', 'scope를',]
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
        if (context["flag"] == "0"):
            apiData = api.objects.filter(
                client_id=request.POST["client_id"], 
                member_no=request.session["memberInfo"]["member_no"]
            ).first()
            if apiData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 client_id 입니다."

        if (context["flag"] == "0"):
            try:
                res = authJwt(
                    client_id=request.POST["client_id"],
                    client_secret=request.POST["client_secret"],
                    service_account=request.POST["service_account"],
                    private_key=request.POST["private_key"],
                    scope=request.POST["scope"]
                )
                result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                if res.status_code == 200 or res.status_code == 201:

                    # API 테이블에 값 저장
                    result["api"] = api.objects.create(
                        api_name=request.POST["api_name"],
                        client_id=request.POST["client_id"],
                        client_secret=util.aes256encrypt(request.POST["client_secret"]),
                        service_account=util.aes256encrypt(request.POST["service_account"]),
                        private_key=util.aes256encrypt(request.POST["private_key"]),
                        scope=request.POST["scope"],
                        rmk="",
                        member_no=member.objects.get(
                            member_no=request.session["memberInfo"]["member_no"]),
                            status="1"
                    )
                    util.tokenReg(result)

                else:
                    context["flag"] = "2"
                    context["result_msg"] = result["description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def apiUpd(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['api_no','api_name', 'client_id', 'client_secret',
                     'service_account', 'private_key', 'scope']
        replaceList = ['api 번호를', 'api 이름을', 'client id를', 'client secret을',
                       'service account를', 'private_key를', 'scope를',]
        apidata = {}

        # 파라미터 검사
        for idx, val in enumerate(checkList):
            if (request.POST[val] == None or request.POST[val] == ""):
                context["flag"] = "2"
                context["result_msg"] = replaceList[idx] + " 입력하세요"
                break
            else:
                apidata[val] = parse.quote(request.POST[val])

        if (context["flag"] == "0"):
            apiData = api.objects.filter(
                api_no=request.POST["api_no"], 
                member_no=request.session["memberInfo"]["member_no"]
            ).first()
            if apiData is None:
                context["flag"] = "3"
                context["result_msg"] = "잘못된 API 입니다."

        # 중복 검사
        if (context["flag"] == "0"):
            apiData2 = api.objects.filter(
                client_id=request.POST["client_id"], 
                member_no=request.session["memberInfo"]["member_no"],
            ).exclude(
                api_no=request.POST["api_no"]
            ).first()
            if apiData2 is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 client_id 입니다."

        if (context["flag"] == "0"):
            try:
                res = authJwt(
                    client_id=request.POST["client_id"],
                    client_secret=request.POST["client_secret"],
                    service_account=request.POST["service_account"],
                    private_key=request.POST["private_key"],
                    scope=request.POST["scope"]
                )
                result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                if res.status_code == 200 or res.status_code == 201:

                    # API 테이블에 값 저장
                    apiData.api_name=request.POST["api_name"]
                    apiData.client_id=request.POST["client_id"]
                    apiData.client_secret=util.aes256encrypt(request.POST["client_secret"])
                    apiData.service_account=util.aes256encrypt(request.POST["service_account"])
                    apiData.private_key=util.aes256encrypt(request.POST["private_key"])
                    apiData.scope=request.POST["scope"]
                    apiData.rmk=""
                    apiData.save()
                    result["api"] = apiData
                    util.tokenReg(result)

                else:
                    context["flag"] = "2"
                    context["result_msg"] = result["description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def apiRm(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        try:
            api.objects.filter(
                api_no=request.POST["api_no"], member_no=request.session["memberInfo"]["member_no"]).delete()
        except Exception as err:
            context["flag"] = "2"
            context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

# endregion

# region Bot 관련


def botList(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "GET":
        return render(request, 'NWAD/BOT/botList.html')
    elif request.method == "":
        return


def getBotList(request):
    if request.method == "POST":
        apiData = bot.objects.filter(
            member_no=request.session["memberInfo"]["member_no"]).all()
        res = util.objectToPaging(apiData, 1, 0)
        return JsonResponse(res, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def getBot(request):
    context = {}
    context["flag"] = "0"
    context["result_msg"] = "success"
    if request.method == "POST":
        try:
            botData = bot.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                bot_no=request.POST["bot_no"]
            ).first()
            botData.bot_secret = util.aes256decrypt(botData.bot_secret)
            res = util.objectToDict(botData)
            context["data"] = res
            
            apiData = api.objects.filter(
                member_no=request.session["memberInfo"]["member_no"]
            ).all()
            context["apis"] = util.objectToPaging(apiData, 1, 0)
        except Exception as err:
            context["flag"] = "2"
            context["result_msg"] = err.args[0]
    return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def botReg(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "GET":
        apiData = api.objects.filter(
            member_no=request.session["memberInfo"]["member_no"]).all()
        return render(request, 'NWAD/BOT/botReg.html', {'apiData': apiData})
    elif request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['api_no', 'bot_id', 'bot_secret']
        replaceList = ['api no를', 'bot id를', 'bot secret을']
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
        apiData = api.objects.filter(
            api_no=request.POST["api_no"], member_no=request.session["memberInfo"]["member_no"]).first()
        if apiData is None:
            context["flag"] = "4"
            context["result_msg"] = "잘못된 API NO 입니다."

        # 중복 검사
        if (context["flag"] == "0"):
            botData = bot.objects.filter(
                bot_id=request.POST["bot_id"], member_no=request.session["memberInfo"]["member_no"]).first()
            if botData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 bot id 입니다."

        if (context["flag"] == "0"):
            # AccessToken 조회
            apidata["access_token"] = util.getAccessTokenRe(request.POST["api_no"])
            if apidata["access_token"] == "":
                context["flag"] = "5"
                context["result_msg"] = "access_token을 조회 할 수 없습니다."

        if (context["flag"] == "0"):
            try:
                res = getBotInfo(request.POST["bot_id"], apidata["access_token"])
                result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                if res.status_code == 200 or res.status_code == 201:
                    # BOT 테이블에 값 저장
                    bot.objects.create(
                        bot_id=request.POST["bot_id"],
                        bot_secret=util.aes256encrypt(request.POST["bot_secret"]),
                        bot_name=result["botName"],
                        rmk="",
                        member_no=member.objects.get(
                            member_no=request.session["memberInfo"]["member_no"]),
                            status=1
                    )

                else:
                    context["flag"] = "2"
                    context["result_msg"] = result["description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def botUpd(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['bot_no', 'bot_name', 'api_no', 'bot_id', 'bot_secret']
        replaceList = ['bot no를', 'bot 이름을', 'api no를', 'bot id를', 'bot secret을']
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
        apiData = api.objects.filter(
            api_no=request.POST["api_no"], member_no=request.session["memberInfo"]["member_no"]).first()
        if apiData is None:
            context["flag"] = "4"
            context["result_msg"] = "잘못된 API NO 입니다."

        # 중복 검사
        if (context["flag"] == "0"):
            botData = bot.objects.filter(
                bot_id=request.POST["bot_id"], member_no=request.session["memberInfo"]["member_no"]
            ).exclude(
                bot_no=request.POST["bot_no"]
            ).first()
            if botData is not None:
                context["flag"] = "3"
                context["result_msg"] = "이미 등록된 bot id 입니다."

        if (context["flag"] == "0"):
            # AccessToken 조회
            apidata["access_token"] = util.getAccessTokenRe(request.POST["api_no"])
            if apidata["access_token"] == "" or apidata["access_token"] is None:
                context["flag"] = "5"
                context["result_msg"] = "access_token을 조회 할 수 없습니다."

        if (context["flag"] == "0"):
            try:
                res = getBotInfo(request.POST["bot_id"], apidata["access_token"])
                result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                if res.status_code == 200 or res.status_code == 201:
                    # BOT 테이블에 값 저장
                    botData = bot.objects.filter(
                        bot_no=request.POST["bot_no"], 
                        member_no=request.session["memberInfo"]["member_no"]
                    ).first()
                    
                    botData.bot_id=request.POST["bot_id"]
                    botData.bot_secret=util.aes256encrypt(request.POST["bot_secret"])
                    botData.bot_name=request.POST["bot_name"]
                    botData.rmk=""
                    botData.save()
                else:
                    context["flag"] = "2"
                    context["result_msg"] = result["description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err.args[0]
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

def botRm(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        try:
            bot.objects.filter(
                bot_no=request.POST["bot_no"], 
                member_no=request.session["memberInfo"]["member_no"]
            ).delete()
        except Exception as err:
            context["flag"] = "2"
            context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)

# endregion

def textMessage(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "GET":
        apiData = api.objects.filter(
            member_no=request.session["memberInfo"]["member_no"]).all()
        botData = bot.objects.filter(
            member_no=request.session["memberInfo"]["member_no"]).all()
        return render(request, 'NWAD/Message/textMessage.html', {'apiData': apiData, 'botData': botData})
    elif request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        # 파라미터 유효성 검사
        apiData = api.objects.filter(
            member_no=request.session["memberInfo"]["member_no"],
            api_no=request.POST["api_no"]
        ).first()
        if apiData is None:
            context["flag"] = "4"
            context["result_msg"] = "잘못된 API NO 입니다."
        
        if context["flag"] == "0":
            botData = bot.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                bot_no=request.POST["bot_no"]
            ).first()
            if botData is None:
                context["flag"] = "4"
                context["result_msg"] = "잘못된 BOT NO 입니다."

        if (context["flag"] == "0"):
            try:
                # 메시지 전송
                res = sendMessage(
                    api_no=apiData.api_no, 
                    bot_no=botData.bot_no, 
                    content=util.simpleTemplate(request.POST["text"]), 
                    user_id="didim365@didimnow.net"
                )
                result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                if res.status_code != 200 and res.status_code != 201:
                    context["flag"] = "2"
                    context["result_msg"] = result["description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
        


def scenarioReg(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "GET":
        apiData = api.objects.filter(
            member_no=request.session["memberInfo"]["member_no"]).all()
        botData = bot.objects.filter(
            member_no=request.session["memberInfo"]["member_no"]).all()
        scenTypeData = scen_type.objects.all()
        return render(request, 'NWAD/Scenario/scenarioReg.html', {'apiData': apiData, 'botData': botData, 'scenTypeData': scenTypeData})
    elif request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"

        # 파라미터 유효성 검사
        apiData = api.objects.filter(
            member_no=request.session["memberInfo"]["member_no"],
            api_no=request.POST["api_no"]
        ).first()
        if apiData is None:
            context["flag"] = "4"
            context["result_msg"] = "잘못된 API NO 입니다."
        
        if context["flag"] == "0":
            botData = bot.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                bot_no=request.POST["bot_no"]
            ).first()
            if botData is None:
                context["flag"] = "4"
                context["result_msg"] = "잘못된 BOT NO 입니다."
        
        # 중복 데이터 조회
        if context["flag"] == "0":
            scenData = scen.objects.filter(
                member_no=request.session["memberInfo"]["member_no"],
                domain=request.POST["domain_id"]
            ).first()
            if scenData is not None:
                context["flag"] = "3"
                context["result_msg"] = "중복된 Domain Id 입니다."


        if (context["flag"] == "0"):
            try:
                res = createChannel(
                    api_no=apiData.api_no, 
                    bot_no=botData.bot_no,
                    members=re.sub(r"\s", "", request.POST["members"]),
                    title="1:N 보고 BOT 시나리오",
                )
                result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                if res.status_code != 200 and res.status_code != 201:
                    context["flag"] = "2"
                    context["result_msg"] = result["description"]
                else:
                    channelId = result["channelId"]
                    res = getChannelMembers(
                        api_no=apiData.api_no, 
                        bot_no=botData.bot_no, 
                        channel_id=channelId
                    )
                    result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                    if res.status_code != 200 and res.status_code != 201:
                        raise Exception(result["description"])
                    else:
                        members = ",".join(result["members"])
                    # DB 저장
                    scenData = scen.objects.create(
                        scen_type = scen_type.objects.filter(scen_type=request.POST["scen_type"]).first(),
                        api_no = apiData,
                        bot_no = botData,
                        domain = request.POST["domain_id"],
                        channel = channelId,
                        members = members,
                        member_no = member.objects.filter(member_no=request.session["memberInfo"]["member_no"], status="1").first()
                    )
                    text = "1:N 보고 BOT 시나리오 방이 생성되었습니다."
                    # 메시지 전송
                    res = sendMessage(
                        api_no=scenData.api_no.api_no, 
                        bot_no=scenData.bot_no.bot_no, 
                        content=util.simpleTemplate(text), 
                        channel_id=scenData.channel
                    )
                    result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


def termsService(request):
    return render(request, 'NWAD/terms-service.html')

def privacyPoilcy(request):
    return render(request, 'NWAD/privacy-poilcy.html')



@csrf_exempt
def callback(request):
    try:
        if request.method == "POST":
            req = util.strToJson(request.body.decode('utf-8'))
            log.objects.create(
                msg=request.body.decode('utf-8'),
                reg_user="callback",
            )
            scenData = scen.objects.filter(domain=req["source"]["domainId"],status=1).first()
            if scenData is not None:
                # 익명 보고 시나리오
                if scenData.scen_type.scen_type == 1:
                    res = getUserInfo(api_no=scenData.api_no.api_no, bot_no=scenData.bot_no.bot_no, user_id=req["source"]["userId"])

                    result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                    if res.status_code != 200 and res.status_code != 201:
                        raise Exception(result["description"])
                    sender = {}
                    sender["name"] = result["userName"]["lastName"] + result["userName"]["firstName"]
                    sender["id"] = result["userId"]
                    try:
                        if req["type"] == "message":
                            # message postback "start" 감지
                            postback = ""
                            try:
                                postback = req["content"]["postback"]
                            except:
                                postback = ""
                            if postback == "start":
                                return

                            # 채팅쓴게 1:1 메시지 인지 확인
                            channelId = ""
                            try:
                                channelId = req["source"]["channelId"]
                            except:
                                channelId = ""

                            if channelId == "":
                                sender["message"] = req["content"]["text"]
                                util.insertLog(request, "받은 메시지: " + sender["message"])
                                # 연결중 인지 체크
                                scenConnData = scen_conn.objects.filter(reporter = sender["id"]).exclude(status = 9).first()
                                if scenConnData is not None:
                                    # 상태가 대화중인지 확인
                                    if scenConnData.status == "1": # 대화중
                                        # 결재자에게 메시지 전송
                                        text = sender["name"]+"님으로부터 전달된 메시지 \n\n"
                                        text += "\"" + sender["message"] + "\""
                                        btn = []
                                        btn.append({"type":"button","text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}","separator":""})
                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text, button=btn), 
                                            user_id=scenConnData.approver
                                        )
                                    elif scenConnData.status == "2" or scenConnData.status == "3": # 요청중, 대기중

                                        text = "요청중인 대화가 있습니다.\n취소 후 진행해주세요."
                                        btn = []
                                        btn.append({"type":"button","text":"대화 취소","data":"{'action':'cancleChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}","separator":""})

                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text, button=btn), 
                                            user_id=sender["id"]
                                        )
                                else:
                                    scenConnData = scen_conn.objects.filter(approver = sender["id"]).exclude(status = 9).first()
                                    if scenConnData is not None:
                                        # 보고자에게 메시지 전송
                                        text = "담당자로부터 전달된 메시지 \n\n"
                                        text += "\"" + sender["message"] + "\""
                                        btn = []
                                        btn.append({"type":"button","text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}","separator":""})

                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text, button=btn), 
                                            user_id=scenConnData.reporter
                                        )
                                    else:
                                        # 신규 대화
                                        # db에 저장
                                        scenConnData = scen_conn.objects.create(
                                            reporter=sender["id"],
                                            scen_no=scenData,
                                            message=sender["message"]
                                        )

                                        # 결재자에게 메시지 전송
                                        connDatas = scen_conn.objects.filter(scen_no=scenConnData.scen_no.scen_no).exclude(status=1).exclude(status=9).order_by('-conn_no')[:5]

                                        contents = util.strToJson(util.simpleTemplate(""))
                                        contents["contents"]["contents"].pop()

                                        for connData in connDatas:
                                            res = getUserInfo(api_no=scenData.api_no.api_no, bot_no=scenData.bot_no.bot_no, user_id=connData.reporter)
                                            result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                                            if res.status_code != 200 and res.status_code != 201:
                                                raise Exception(result["description"])
                                            name = result["userName"]["lastName"] + result["userName"]["firstName"]
                                            text = name + "님으로부터 메시지가 도착하였습니다.\n선택해주세요.\n요청일자: "+str(connData.reg_date.strftime("%Y-%m-%d %H:%M:%S"))
                                            btn = []
                                            btn.append({"type":"button","text":"대화 시작", "data":"{'action':'startChat','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}","separator":""})
                                            btn.append({"type":"button","text":"전달된 메시지 보기", "data":"{'action':'showMessage','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}","separator":""})
                                            btn.append({"type":"button","text":"대기 메시지 전송", "data":"{'action':'sendWait','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}","separator":""})
                                            btn.append({"type":"button","text":"대화 취소", "data":"{'action':'cancleChat','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}","separator":""})
                                            content = util.strToJson(util.simpleTemplate(text, button=btn))
                                            contents["contents"]["contents"].append(content["contents"]["contents"][0])
                                            if contents["altText"] == "":
                                                contents["altText"] = content["altText"]

                                        contents = util.jsonToStr(contents)

                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=contents, 
                                            channel_id=scenData.channel
                                        )

                                        #보고자에게 메시지 전송
                                        text = "담당자에게 메시지를 전달 하였습니다.\n잠시만 기다려 주세요."
                                        btn = []
                                        btn.append({"type":"button","text":"대화 취소", "data":"{'action':'cancleChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}","separator":""})

                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text, button=btn),
                                            user_id=sender["id"]
                                        )
                        elif req["type"] == "postback":
                            postbackData = util.strToJson(util.unicodeAddSlash(req["data"]).replace('\'','\"'))

                            scenConnData = scen_conn.objects.filter(conn_no=postbackData["conn"]).exclude(status='9').first()
                            if postbackData["action"] == "startChat":
                                if scenConnData is not None:
                                    # 상태 변경
                                    scen_conn.objects.filter(conn_no=postbackData["conn"]).update(status='1',approver=sender["id"])

                                    # # 보고자 정보 조회
                                    res = getUserInfo(scenData.api_no.api_no, scenData.bot_no.bot_no, scenConnData.reporter)

                                    result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                                    if res.status_code != 200 and res.status_code != 201:
                                        raise Exception(result["description"])
                                    reporter = {}
                                    reporter["name"] = result["userName"]["lastName"] + result["userName"]["firstName"]
                                    reporter["id"] = result["userId"]

                                    # 대화 시작 메시지 전송
                                    # 보고자에게 메시지 전송
                                    text = "담당자와 대화를 시작합니다.\n전달할 메시지를 입력해주세요."
                                    btn = []
                                    btn.append({"type":"button","text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}","separator":""})
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text, button=btn), 
                                        user_id=scenConnData.reporter
                                    )
                                    # 결재자에게 메시지 전송
                                    text = reporter["name"] + "님과 대화를 시작합니다.\n전달할 메시지를 입력해주세요."
                                    btn = []
                                    btn.append({"type":"button","text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}","separator":""})

                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text, button=btn), 
                                        user_id=sender["id"]
                                    )
                                else:
                                    scenConnData = scen_conn.objects.filter(conn_no=postbackData["conn"]).first()
                                    scenData = scen.objects.filter(scen_no=postbackData["scen"]).first()
                                    if scenData is not None:
                                        if scenConnData is not None:
                                            text = "대화가 종료된 메시지 입니다."
                                        else:
                                            text = "해당 메시지 조회에 실패하였습니다."
                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text), 
                                            channel_id=scenData.channel
                                        )
                            elif postbackData["action"] == "showMessage":
                                scenConnData = scen_conn.objects.filter(conn_no=postbackData["conn"]).first()
                                if scenConnData is not None:
                                    text = sender["name"] + "님으로부터 전달된 메시지\n\n"
                                    text += "\"" + scenConnData.message + "\""
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text), 
                                        channel_id=scenData.channel
                                    )
                                else:
                                    scenConnData = scen_conn.objects.filter(conn_no=postbackData["conn"]).first()
                                    scenData = scen.objects.filter(scen_no=postbackData["scen"]).first()
                                    if scenData is not None:
                                        if scenConnData is not None:
                                            text = "대화가 종료된 메시지 입니다."
                                        else:
                                            text = "해당 메시지 조회에 실패하였습니다."
                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text), 
                                            channel_id=scenData.channel
                                        )
                            elif postbackData["action"] == "sendWait":
                                # 상태 변경
                                scen_conn.objects.filter(conn_no=postbackData["conn"]).update(status='3')
                                if scenConnData is not None:
                                    #보고자에게 메시지 전송
                                    text = "담당자로부터 전달된 메시지 \n\n"
                                    text += "\"잠시만 기다려 주세요.\""
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text), 
                                        user_id=scenConnData.reporter
                                    )
                                else:
                                    scenConnData = scen_conn.objects.filter(conn_no=postbackData["conn"]).first()
                                    scenData = scen.objects.filter(scen_no=postbackData["scen"]).first()
                                    if scenData is not None:
                                        if scenConnData is not None:
                                            text = "대화가 종료된 메시지 입니다."
                                        else:
                                            text = "해당 메시지 조회에 실패하였습니다."
                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text), 
                                            channel_id=scenData.channel
                                        )
                            elif postbackData["action"] == "finishChat":
                                if scenConnData is not None:
                                    # 상태 변경
                                    scen_conn.objects.filter(conn_no=postbackData["conn"]).update(status='9')

                                    # # 보고자 정보 조회
                                    res = getUserInfo(scenData.api_no.api_no, scenData.bot_no.bot_no, scenConnData.reporter)

                                    result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                                    if res.status_code != 200 and res.status_code != 201:
                                        raise Exception(result["description"])
                                    reporter = {}
                                    reporter["name"] = result["userName"]["lastName"] + result["userName"]["firstName"]
                                    reporter["id"] = result["userId"]

                                    # 결재자에게 메시지 전송
                                    text = reporter["name"] + "님과의 대화가 종료되었습니다."
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text), 
                                        user_id=scenConnData.approver
                                    )

                                    # 보고자에게 메시지 전송
                                    text = "담당자와의 대화가 종료되었습니다."
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text), 
                                        user_id=scenConnData.reporter
                                    )
                                else:
                                    scenConnData = scen_conn.objects.filter(conn_no=postbackData["conn"]).first()
                                    if scenConnData is not None:
                                        text = "대화가 종료된 메시지 입니다."
                                    else:
                                        text = "해당 메시지 조회에 실패하였습니다."
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text), 
                                        user_id=sender["id"]
                                    )
                            elif postbackData["action"] == "cancleChat":
                                if scenConnData is not None:
                                    # 상태 변경
                                    scen_conn.objects.filter(conn_no=postbackData["conn"]).update(status='9')
                                    # 결재자 채널과 보고자 에게 모두 전송 
                                    # 결재자 채널에게 메시지 전송
                                    if sender["id"] == scenConnData.reporter:
                                        text = sender["name"] + "님의 대화 요청이 취소되었습니다."
                                    else:
                                        text = sender["name"] + " 담당자가 대화 요청을 취소하였습니다."
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text), 
                                        channel_id=scenData.channel
                                    )

                                    # 보고자에게 메시지 전송
                                    if sender["id"] == scenConnData.reporter:
                                        text = "대화 요청이 취소되었습니다."
                                    else:
                                        text = "담당자가 대화 요청을 취소하였습니다."
                                    # 메시지 전송
                                    res = sendMessage(
                                        api_no=scenData.api_no.api_no, 
                                        bot_no=scenData.bot_no.bot_no, 
                                        content=util.simpleTemplate(text), 
                                        user_id=scenConnData.reporter
                                    )
                                else:
                                    scenConnData = scen_conn.objects.filter(conn_no=postbackData["conn"]).first()

                                    if scenConnData is not None:
                                        text = "대화가 종료된 메시지 입니다."
                                        if sender["id"] == scenConnData.reporter:
                                            # 메시지 전송
                                            res = sendMessage(
                                                api_no=scenData.api_no.api_no, 
                                                bot_no=scenData.bot_no.bot_no, 
                                                content=util.simpleTemplate(text), 
                                                user_id=sender["id"]
                                            )
                                        else:
                                            # 메시지 전송
                                            res = sendMessage(
                                                api_no=scenData.api_no.api_no, 
                                                bot_no=scenData.bot_no.bot_no, 
                                                content=util.simpleTemplate(text), 
                                                channel_id=scenData.channel
                                            )
                                    else:
                                        text = "해당 메시지 조회에 실패하였습니다."
                                        if sender["id"] in scenData.members:
                                            # 메시지 전송
                                            res = sendMessage(
                                                api_no=scenData.api_no.api_no, 
                                                bot_no=scenData.bot_no.bot_no, 
                                                content=util.simpleTemplate(text, header="에러 발생"),
                                                channel_id=scenData.channel
                                            )
                                        else:
                                            # 메시지 전송
                                            res = sendMessage(
                                                api_no=scenData.api_no.api_no, 
                                                bot_no=scenData.bot_no.bot_no, 
                                                content=util.simpleTemplate(text, header="에러 발생"),
                                                user_id=sender["id"]
                                            )
                    except Exception as err:
                        # 전송 실패 메시지 전달
                        # 메시지 전송
                        res = sendMessage(
                            api_no=scenData.api_no.api_no, 
                            bot_no=scenData.bot_no.bot_no, 
                            content=util.simpleTemplate(err.args[0], "에러발생"),
                            user_id=sender["id"]
                        )
    except Exception as err:
        util.insertLog(request, err.args[0])
    util.insertLog(request, util.jsonToStr(req))
    return


# @csrf_exempt
# def testCallback(request):
#     jsonString = log.objects.filter(reg_user='callback').last().msg
#     jsonObj = util.strToJson(jsonString)
#     requests.post(request._current_scheme_host +
#         "/botResponse", headers={"Content-Type":"application/json"}, json=jsonObj)
#     return ""
    
#     # apiData = api.objects.filter(api_no = 18).first()
#     # botData = bot.objects.filter(bot_no = 20).first()
#     # reqData = {}
#     # reqData["channel_id"] = "021a677c-b709-3a6a-9a9f-a43094420ea9"
#     # reqData["api_no"] = apiData.api_no
#     # reqData["bot_no"] = botData.bot_no
#     # client = requests.session()
#     # csrftoken = client.get(
#     #     request._current_scheme_host + "/login").cookies['csrftoken']
#     # headers = {'X-CSRFToken': csrftoken}
#     # res = client.post(request._current_scheme_host +
#     #                 "/api/getChannelMembers", headers=headers, data=reqData)
#     # response = util.strToJson(res.text)
#     # if res.status_code != 200 and res.status_code != 201:
#     #     raise Exception(response["description"])
#     # return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=res.status_code) 

#     # connData = scen_conn.objects.order_by('-conn_no').all()

#     # # for conn in connData:
#     # contents = util.templateText(text="테스트")
#     # apiData = api.objects.filter(api_no = 18).first()
#     # botData = bot.objects.filter(bot_no = 20).first()
#     # reqData = {}
#     # reqData["user_id"] = "821c4e72-f022-44f3-1767-039a66c98a20"
#     # reqData["api_no"] = apiData.api_no
#     # reqData["bot_no"] = botData.bot_no
#     # reqData["content"] = util.jsonToStr(contents)
#     # res = sendMessage(request, reqData)
#     # response = util.strToJson(res.text)
#     # if res.status_code != 200 and res.status_code != 201:
#     #     raise Exception(response["description"])
#     # return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=res.status_code) 



def testPage(request):
    if request.method == "GET":
        return render(request, 'NWAD/testPage.html')
    elif request.method == "POST":
        reqData = {}
        reqData["text1"] = request.POST["text"]
        try:
            if(request.POST["type"]=="enc"):
                reqData["text2"] = util.aes256encrypt(request.POST["text"])
            elif(request.POST["type"]=="dec"):
                reqData["text2"] = util.aes256decrypt(request.POST["text"])
            elif(request.POST["type"]=="sha"):
                reqData["text2"] = util.sha512encrypt(request.POST["text"])
        except Exception as err:
            reqData["text2"] = err.args[0]
        return JsonResponse(reqData, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200) 



def testIp(request):
    msg = ""
    msg += "테스트 IP"
    util.insertLog(request, msg + "    " + util.jsonToStr(request.POST.dict()))
    return HttpResponse("192.168.60.9\n192.168.60.6", content_type="text/plain")


def load_mail_template(template_name, password):
    return render_to_string('NWAD/DidimAPI Sampler mail/' + template_name + '.html').format(password)

def send_simple_mail(mail_to, subject, template_name, password):
    mail_from = 'noreply@didim365.com'

    msg = MIMEMultipart()
    msg['From'] = mail_from
    msg['To'] = mail_to
    msg['Subject'] = subject
    mail_body = load_mail_template(template_name, password)
    msg.attach(MIMEText(mail_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.sendgrid.net', 587)
        server.ehlo()
        server.login('apikey', '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')
        server.sendmail(mail_from, mail_to, msg.as_string())
        server.close()
        return "OK"
    except Exception as err:
        return "Failed : " + err

    