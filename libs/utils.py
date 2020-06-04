from datetime import datetime, timedelta
import uuid
import base64
from flask import request
import os
from  libs import logs, variables
from flask import make_response, request, jsonify
import json
import traceback
from sqlalchemy import or_, and_
import sqlalchemy



    
def returnResponse(data, code):
    resp = make_response(data, code )
    return resp, code

def getArgs(default, request, argName):
    if ((request.args.get(argName) != None) & (request.args.get(argName) !='')):
        return request.args.get(argName)
    return default

def getForm(default, request, argName):
    if ((request.form.get(argName) != None) & (request.form.get(argName) !='')):
        return request.form.get(argName)
    return default

def get_debug_all(request):
    str_debug = '* url: {}\n* method:{}\n'.format(request.url, request.method)
    
    str_debug += '* Args:\n'
    for entry in request.args:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.args[entry])
    str_debug += '* Headers:\n'
    for entry in request.headers:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry[0], entry[1])
    str_debug += '* Form:\n'
    for entry in request.form:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.form[entry])        
    str_debug += '* Files:\n'        
    for entry in request.files :
        str_debug = str_debug +  '\t* {} = {}\n'.format(entry, request.files[entry])       
    str_debug += '* JSON:\n'                
    if (request.json!= None):
        str_debug = str_debug +  '\t* Json = {}\n'.format(request.json)       
    return str_debug    

def checkAuthorization(request):
    if ("Authorization" not in request.headers):
        logs.logger.error("Authorization code is not in headers")
        return  False, None
    else:
        authorizationCode = request.headers['Authorization']
        #base decode
        authorizationCodeB64 = authorizationCode.split(" ")[1]
        logs.logger.info("Authorization Code in B64={}".format(authorizationCodeB64))
        decoded = base64.b64decode(authorizationCodeB64)
        logs.logger.info("Authorization Code decoded={}".format(decoded))

        return  True, decoded       

def getDayFromStr(date):
    today = datetime.strptime((datetime.now()).strftime(variables.DATE_PATTERN), variables.DATE_PATTERN)
    return today

def getCurrentDay():
    today = datetime.strptime((datetime.now()).strftime(variables.DATE_PATTERN), variables.DATE_PATTERN)
    return today

def getTomorrowDT():
    tomorrow = datetime.strptime((datetime.now() + timedelta(days=1)).strftime(variables.DATE_PATTERN), variables.DATE_PATTERN)
    return tomorrow

def getDateFromStr(str, pattern):
    return datetime.strptime(str, pattern)

def dateToStr(date, pattern):
    return date.strftime(pattern)