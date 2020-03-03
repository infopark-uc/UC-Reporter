from flask import Flask, request, redirect, jsonify
import xmltodict
import json
from pprint import pprint
from collections import OrderedDict
from application.sqlrequests import cms_sql_request,cm_sqlselect_dict,cm_sqlupdate
def cdr_receiver():
    try:
        cdr = xmltodict.parse(request.data) #get OrderedDict
        cdr_dict = json.loads(json.dumps(cdr)) #trasfrorm OrderedDict to Dict

        session_id = str(cdr_dict['records']["@session"])   # забираем Session ID
        #print("Session ID:  " +session_id)

        callleg_id = str(cdr_dict['records']['record']['callLeg']['@id']) # забираем callleg ID
        #print ("CallLeg ID:  " + callleg_id)

        sipcall_id = str(cdr_dict['records']['record']['callLeg']['sipCallId']) #забираем sipcall_id
        #print("SipCall ID:  " + sipcall_id)


        if not cm_sqlselect_dict('callleg_id','cms_cdr_records','callleg_id',callleg_id):
            print("insert data to database")
            #insert IDs to database
            cms_sql_request("INSERT INTO cms_cdr_records SET session_id='" + session_id + "',callleg_id='" + callleg_id + "',sipcall_id='" + sipcall_id + "';")
        else:
            print("ID data already presence")

        if "displayName" in cdr_dict['records']['record']['callLeg']:
              displayName = str(cdr_dict['records']['record']['callLeg']['displayName'])  # забираем  displayName
              print("displayName:  " + displayName)

        if "remoteAddress" in cdr_dict['records']['record']['callLeg']:
              remoteAddress = str(cdr_dict['records']['record']['callLeg']['remoteAddress'])  # забираем  remoteAddress
              cm_sqlupdate(remoteAddress, 'cms_cdr_records', 'remoteAddress', 'callleg_id',callleg_id)  # дополняем информацию о вызове
              print("remoteAddress: " + remoteAddress + " inserted to database")

        if "durationSeconds" in cdr_dict['records']['record']['callLeg']:
              durationSeconds = str(cdr_dict['records']['record']['callLeg']['durationSeconds'])  # забираем  durationSeconds
              cm_sqlupdate(durationSeconds, 'cms_cdr_records', 'durationSeconds', 'callleg_id',callleg_id)  # дополняем информацию о вызове
              print("durationSeconds: " + durationSeconds + " inserted to database")

        if "reason" in cdr_dict['records']['record']['callLeg']:
              reason = str(cdr_dict['records']['record']['callLeg']['reason'])  # забираем  reason
              cm_sqlupdate(reason, 'cms_cdr_records', 'reason', 'callleg_id',callleg_id)  # дополняем информацию о вызове
              print("reason: " + reason + " inserted to database")

        if "codec" in cdr_dict['records']['record']['callLeg']['rxAudio']:
              codecrx = str(cdr_dict['records']['record']['callLeg']['rxAudio']['codec'])
              cm_sqlupdate(codecrx, 'cms_cdr_records', 'rxAudio_codec', 'callleg_id',callleg_id)  # дополняем информацию о вызове
              print("rxAudio_codec: " + codecrx + " inserted to database")

        if "codec" in cdr_dict['records']['record']['callLeg']['txAudio']:
              codectx = str(cdr_dict['records']['record']['callLeg']['txAudio']['codec'])
              cm_sqlupdate(codectx, 'cms_cdr_records', 'txAudio_codec', 'callleg_id',callleg_id)  # дополняем информацию о вызове
              print("txAudio_codec: " + codectx + " inserted to database")
        if "coSpace" in cdr_dict['records']['record']['call']:
            coSpace = str(cdr_dict['records']['record']['call']['coSpace'])
            cm_sqlupdate(coSpace, 'cms_cdr_records', 'coSpace_id', 'callleg_id',callleg_id)  # дополняем информацию о вызове
            print("coSpace_id: " + coSpace + " inserted to database")

            coSpace_name = str(cdr_dict['records']['record']['call']['name'])
            cm_sqlupdate(coSpace_name, 'cms_cdr_records', 'coSpace_name', 'callleg_id',callleg_id)  # дополняем информацию о вызове
            print("coSpace_name: " + coSpace_name + " inserted to database")





        return('', 204)

    except:
        print('Parser failure!')
        pprint(cdr_dict)
        return('', 204)

