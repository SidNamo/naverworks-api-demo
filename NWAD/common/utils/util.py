import base64
import json
import hashlib

import time
import datetime


"""
공용으로 사용되는 Util 함수 모음
"""

'''
string 인코딩
'''
def base64encode(jsonString):
    jsonString = json.dumps(jsonString, separators=(",", ":"))
    jsonString = base64.b64encode(jsonString.encode('ascii'))
    result = jsonString.decode('utf-8')
    
    return result

def sha256encode(jsonString):
    jsonString = json.dumps(jsonString, separators=(",", ":"))
    jsonString = base64.b64encode(jsonString.encode('ascii'))
    result = jsonString.decode('utf-8')

    return result


'''
시간 / 날짜 관련
'''
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