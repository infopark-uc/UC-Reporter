from flask import Flask, request, redirect, jsonify
import xmltodict
import json
from pprint import pprint
from collections import OrderedDict
from application.sqlrequests import cms_sql_request,cm_sqlselect_dict
def cdr_receiver():
    try:
        cdr = xmltodict.parse(request.data) #get OrderedDict
        cdr_dict = json.loads(json.dumps(cdr)) #trasfrorm OrderedDict to Dict

        session_id = str(cdr_dict['records']["@session"])   # забираем Session ID
        print("Session ID:  " +session_id)

        callleg_id = str(cdr_dict['records']['record']['callLeg']['@id']) # забираем callleg ID
        print ("CallLeg ID:  " + callleg_id)

        sipcall_id = str(cdr_dict['records']['record']['callLeg']['sipCallId']) #забираем sipcall_id
        print("SipCall ID:  " + sipcall_id)

        sqlcheck = cm_sqlselect_dict('callleg_id','ms_cdr_records','callleg_id',callleg_id)
        pprint(sqlcheck)
        if not sqlcheck:
            print("If check")
            cms_sql_request("INSERT INTO cms_cdr_records SET session_id='" + session_id + "',callleg_id='" + callleg_id + "';")
        else:
            print("Else check")

        if "displayName" in cdr_dict['records']['record']['callLeg']:
              displayName = str(cdr_dict['records']['record']['callLeg']['displayName'])  # забираем  displayName
              print("displayName:  " + displayName)
        if "remoteAddress" in cdr_dict['records']['record']['callLeg']:
              remoteAddress = str(cdr_dict['records']['record']['callLeg']['remoteAddress'])  # забираем  remoteAddress
              print("remoteAddress:  " + remoteAddress)

        if "durationSeconds" in cdr_dict['records']['record']['callLeg']:
              durationSeconds = str(cdr_dict['records']['record']['callLeg']['durationSeconds'])  # забираем  durationSeconds
              print("durationSeconds:  " + durationSeconds)
        if "reason" in cdr_dict['records']['record']['callLeg']:
              reason = str(cdr_dict['records']['record']['callLeg']['reason'])  # забираем  reason
              print("reason:  " + reason)

        return('', 204)

    except:
        print('Parser failure!')
        #pprint (cdr_dict)
        return('', 204)

