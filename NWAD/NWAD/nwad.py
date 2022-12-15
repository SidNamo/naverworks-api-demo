import requests
import json
import re
from common.utils import util
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from urllib import parse

from django.views.decorators.csrf import csrf_exempt

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
            return render(request, 'NWAD/login.html')
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
            context["pw"] = util.sha256encode(request.POST["password"])
            memberSearchData = member.objects.filter(
                id=context["id"], password=context["pw"], status="1").first()
            if memberSearchData is None:
                memberSearchData = member.objects.filter(
                    id=context["id"], password=context["pw"]).first()
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
                util.insertLog(request, msg + "    " +
                               util.jsonToStr(request.POST.dict()))
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
        util.insertLog(request, msg + "    " +
                       util.jsonToStr(request.POST.dict()))
    return redirect('/')


def join(request):
    if 'memberInfo' in request.session:
        return render(request, 'NWAD/main.html')
    if (request.method == "GET"):
        return render(request, 'NWAD/join.html')
    elif (request.method == "POST"):
        memeberInfo = {}
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        checkList = ['id', 'password', 'name', 'email']
        replaceList = ['아이디를', '비밀번호를', '이름을', '이메일을']

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
                    password=util.sha256encode(request.POST["password"]),
                    name=request.POST["name"],
                    email=request.POST["email"],
                )
            except Exception as err:
                context["flag"] = "9"
                context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)
# endregion

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


def apiReg(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "GET":
        return render(request, 'NWAD/API/apiReg.html')
    elif request.method == "POST":
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
                        client_secret=request.POST["client_secret"],
                        service_account=request.POST["service_account"],
                        private_key=request.POST["private_key"],
                        scope=request.POST["scope"],
                        rmk="",
                        member_no=member.objects.get(
                            member_no=request.session["memberInfo"]["member_no"])
                    )
                    util.tokenReg(result)

                else:
                    context["flag"] = "2"
                    context["result_msg"] = result["description"]
            except Exception as err:
                context["flag"] = "2"
                context["result_msg"] = err
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
            apidata["access_token"] = util.getAccessToken(request.POST["api_no"])
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
                        bot_secret=request.POST["bot_secret"],
                        bot_name=result["botName"],
                        rmk="",
                        member_no=member.objects.get(
                            member_no=request.session["memberInfo"]["member_no"])
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


def botRm(request):
    if 'memberInfo' not in request.session:
        return redirect('login')

    if request.method == "POST":
        context = {}
        context["flag"] = "0"
        context["result_msg"] = "success"
        try:
            bot.objects.filter(
                bot_no=request.POST["bot_no"], member_no=request.session["memberInfo"]["member_no"]).delete()
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
                        api_no = apiData,
                        bot_no = botData,
                        domain = request.POST["domain_id"],
                        channel = channelId,
                        members = members,
                        member_no = member.objects.filter(member_no=request.session["memberInfo"]["member_no"]).first()
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
                context["result_msg"] = err
        util.insertLog(
            request, context["result_msg"] + "    " + util.jsonToStr(request.POST.dict()))
        return JsonResponse(context, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=200)


@csrf_exempt
def botResponse(request):
    try:
        util.insertLog(request, "시작/" + request.method)
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
                                        btn.append({"text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}"})
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
                                        btn.append({"text":"대화 취소","data":"{'action':'cancleChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}"})

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
                                        btn.append({"text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}"})

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

                                        content = util.strToJson(util.simpleTemplate(""))
                                        content["contents"]["contents"].pop()

                                        for connData in connDatas:
                                            res = getUserInfo(api_no=scenData.api_no.api_no, bot_no=scenData.bot_no.bot_no, user_id=connData.reporter)
                                            result = util.strToJson(res.text)  # 인증 완료 후 응답 값
                                            if res.status_code != 200 and res.status_code != 201:
                                                raise Exception(result["description"])
                                            name = result["userName"]["lastName"] + result["userName"]["firstName"]
                                            text = name + "님으로부터 메시지가 도착하였습니다.\n선택해주세요.\n요청일자: "+str(connData.reg_date.strftime("%Y-%m-%d %H:%M:%S"))
                                            btn = []
                                            btn.append({"text":"대화 시작", "data":"{'action':'startChat','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}"})
                                            btn.append({"text":"전달된 메시지 보기", "data":"{'action':'showMessage','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}"})
                                            btn.append({"text":"대기 메시지 전송", "data":"{'action':'sendWait','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}"})
                                            btn.append({"text":"대화 취소", "data":"{'action':'cancleChat','conn':'"+str(connData.conn_no)+"','scen':'"+str(connData.scen_no.scen_no)+"'}"})
                                            content = util.strToJson(util.simpleTemplate(text, button=btn))
                                            content["contents"]["contents"].append(content["contents"]["contents"][0])
                                            if content["altText"] == "":
                                                content["altText"] = content["altText"]

                                        content = util.jsonToStr(content)

                                        # 메시지 전송
                                        res = sendMessage(
                                            api_no=scenData.api_no.api_no, 
                                            bot_no=scenData.bot_no.bot_no, 
                                            content=util.simpleTemplate(text, button=btn), 
                                            channel_id=scenData.channel
                                        )

                                        #보고자에게 메시지 전송
                                        text = "담당자에게 메시지 전달 하였습니다.\n수락 할 때까지 기다려 주세요."
                                        btn = []
                                        btn.append({"text":"대화 취소", "data":"{'action':'cancleChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}"})

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
                                    btn.append({"text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}"})
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
                                    btn.append({"text":"대화 종료","data":"{'action':'finishChat','conn':'"+str(scenConnData.conn_no)+"','scen':'"+str(scenConnData.scen_no.scen_no)+"'}"})

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











@csrf_exempt
def callback(request):
    jsonString = log.objects.filter(reg_user='callback').last().msg
    jsonObj = util.strToJson(jsonString)
    requests.post(request._current_scheme_host +
        "/botResponse", headers={"Content-Type":"application/json"}, json=jsonObj)
    return ""
    
    # apiData = api.objects.filter(api_no = 18).first()
    # botData = bot.objects.filter(bot_no = 20).first()
    # reqData = {}
    # reqData["channel_id"] = "021a677c-b709-3a6a-9a9f-a43094420ea9"
    # reqData["api_no"] = apiData.api_no
    # reqData["bot_no"] = botData.bot_no
    # client = requests.session()
    # csrftoken = client.get(
    #     request._current_scheme_host + "/login").cookies['csrftoken']
    # headers = {'X-CSRFToken': csrftoken}
    # res = client.post(request._current_scheme_host +
    #                 "/api/getChannelMembers", headers=headers, data=reqData)
    # response = util.strToJson(res.text)
    # if res.status_code != 200 and res.status_code != 201:
    #     raise Exception(response["description"])
    # return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=res.status_code) 

    # connData = scen_conn.objects.order_by('-conn_no').all()

    # # for conn in connData:
    # contents = util.templateText(text="테스트")
    # apiData = api.objects.filter(api_no = 18).first()
    # botData = bot.objects.filter(bot_no = 20).first()
    # reqData = {}
    # reqData["user_id"] = "821c4e72-f022-44f3-1767-039a66c98a20"
    # reqData["api_no"] = apiData.api_no
    # reqData["bot_no"] = botData.bot_no
    # reqData["content"] = util.jsonToStr(contents)
    # res = sendMessage(request, reqData)
    # response = util.strToJson(res.text)
    # if res.status_code != 200 and res.status_code != 201:
    #     raise Exception(response["description"])
    # return JsonResponse(response, content_type="application/json", json_dumps_params={'ensure_ascii': False}, status=res.status_code) 

