from flask import Flask, request, redirect, jsonify
import xmltodict
import json
from pprint import pprint
from collections import OrderedDict
from application.sqlrequests import cms_sql_request,cm_sqlselect_dict,cm_sqlupdate
from application.cms_cdr_requester import callleginfo
def cdr_receiver():
    try:
        cdr = xmltodict.parse(request.data) #get OrderedDict
        cdr_dict = json.loads(json.dumps(cdr)) #trasfrorm OrderedDict to Dict
        if cdr_dict['records']['record']['@type'] == 'callLegStart':  #проверяем что, это новый коллег
            # print("We get callLegStart")
            cms_ip = str(request.environ['REMOTE_ADDR'])
            session_id = str(cdr_dict['records']["@session"])  # забираем Session ID
            callleg_id = str(cdr_dict['records']['record']['callLeg']['@id'])  # забираем callleg ID
            sipcall_id = str(cdr_dict['records']['record']['callLeg']['sipCallId'])  # забираем sipcall_id
            remoteAddress = str(cdr_dict['records']['record']['callLeg']['remoteAddress'])  # забираем  remoteAddress
            localAddress = str(cdr_dict['records']['record']['callLeg']['localAddress'])  # забираем  localAddress
            #displayName = str(cdr_dict['records']['record']['callLeg']['displayName'])  # забираем  displayName
            callLegStartTime = str(cdr_dict['records']['record']['@time']) #забираем время лега
            timenow = str(datetime.datetime.now())

            ### добавляем идентификаторы в базу
            cms_sql_request(
                "INSERT INTO cms_cdr_records SET session_id='" + session_id + "', date='" + timenow + "', startTime='" + callLegStartTime + "',cms_ip='" + cms_ip + "',callleg_id='" + callleg_id + "',sipcall_id='" + sipcall_id + "';")
            print("CMS_CDR:     SIP ID: " + sipcall_id + " and " + callleg_id + " inserted to database")
            ### обновляем информацию о вызове
            cms_sql_request(
                "UPDATE cms_cdr_records SET remoteAddress='" + remoteAddress + "',localAddress='" + localAddress + "' WHERE callleg_id='" + callleg_id + "';")
            #собираем статистику по данному легу
            callleginfo(callleg_id,cms_ip)

        if cdr_dict['records']['record']['@type'] == 'callLegUpdate':
            #print("this is callLegUpdate")
            callleg_id = str(cdr_dict['records']['record']['callLeg']['@id'])  # забираем callleg ID для обновления базы данных
            if "call" in cdr_dict['records']['record']['callLeg']:
                call_id = str(cdr_dict['records']['record']['callLeg']['call'])  # забираем  reason
                cm_sqlupdate(call_id, 'cms_cdr_records', 'call_id', 'callleg_id',callleg_id)  # дополняем информацию о вызове
                cms_sql_request(
                    "UPDATE cms_cdr_records,cms_cdr_calls SET coSpace_name=cms_cdr_calls.name WHERE cms_cdr_calls.id='" + call_id + "';") # берем Имя спэйса из другой таблицы.

        if cdr_dict['records']['record']['@type'] == 'callLegEnd':
            #print("this is callLegEnd")
            callleg_id = str(cdr_dict['records']['record']['callLeg']['@id'])  # забираем callleg ID для обновления базы данных
            durationSeconds = str(cdr_dict['records']['record']['callLeg']['durationSeconds'])  # забираем  durationSeconds
            reason = str(cdr_dict['records']['record']['callLeg']['reason'])  # забираем  reason
            callLegEndTime = str(cdr_dict['records']['record']['@time'])  # забираем время лега

            #проверяем наличие информации о Аудио
            if "codec" in cdr_dict['records']['record']['callLeg']['rxAudio']:
                acodecrx = str(cdr_dict['records']['record']['callLeg']['rxAudio']['codec']) # забираем тип кодека аудио RX
            else:
                acodecrx = "none"
            #print ("audio codec RX: " + acodecrx)
            if "codec" in cdr_dict['records']['record']['callLeg']['txAudio']:
                acodectx = str(cdr_dict['records']['record']['callLeg']['txAudio']['codec']) # забираем тип кодека аудио TX
            else:
                acodectx = "none"
            #print("audio codec TX: " + acodectx)
            #проверяем наличие информации о Видео
            if "rxVideo" in cdr_dict['records']['record']['callLeg']:
                if "codec" in cdr_dict['records']['record']['callLeg']['rxVideo']:
                    vcodecrx = str(cdr_dict['records']['record']['callLeg']['rxVideo']['codec']) # забираем тип кодека аудио RX
            else:
                vcodecrx = "none"
            #print("video codec RX: " + vcodecrx)
            if "txVideo" in cdr_dict['records']['record']['callLeg']:
                if "codec" in cdr_dict['records']['record']['callLeg']['txVideo']:
                    vcodectx = str(cdr_dict['records']['record']['callLeg']['txVideo']['codec']) # забираем тип кодека аудио TX
            else:
                vcodectx = "none"

            #print("video codec TX: " + vcodectx)
            ### обновляем информацию о вызове
            print("CMS_CDR: insert CallLegEnd data to database")
            cms_sql_request(
                "UPDATE cms_cdr_records SET txAudio_codec='" + acodectx + "',endTime='" + callLegEndTime + "',durationSeconds='" + durationSeconds + "',reason='" + reason + "',txVideo_codec='" + vcodectx + "',rxVideo_codec='" + vcodecrx + "',rxAudio_codec='" + acodecrx + "' WHERE callleg_id='" + callleg_id + "';")
            print("CMS_CDR:  call detail updated from callLegEnd")
            #pprint(cdr_dict)

        if cdr_dict['records']['record']['@type'] == 'callStart':
            #print("this is callStart")
            call_id = str(cdr_dict['records']['record']['call']['@id'])
            coSpace = str(cdr_dict['records']['record']['call']['coSpace'])
            name = str(cdr_dict['records']['record']['call']['name'])
            starttime = str(cdr_dict['records']['record']['@time'])

            print("cospace: " + coSpace + " time: " + starttime)
            print("space name: " + name )
            if not cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                print("insert CALL to database")
                # insert IDs to database
                cms_sql_request(
                    "INSERT INTO cms_cdr_calls SET id='" + call_id + "',StartTime='" + starttime + "',coSpace='" + coSpace + "',name='" + name + "';")
            else:
                print("Space ID data already presence")
            #pprint(cdr_dict)
        return('', 204)

    except:
        print('CMS_CDR: Parser failure!')
        #pprint(cdr_dict)
        return('', 204)

