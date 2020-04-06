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
        if cdr_dict['records']['record']['@type'] == 'callLegStart':  #проверяем что, это новый коллег
            # print("We get callLegStart")
            cms_ip = str(request.environ['REMOTE_ADDR'])
            session_id = str(cdr_dict['records']["@session"])  # забираем Session ID
            callleg_id = str(cdr_dict['records']['record']['callLeg']['@id'])  # забираем callleg ID
            sipcall_id = str(cdr_dict['records']['record']['callLeg']['sipCallId'])  # забираем sipcall_id
            remoteAddress = str(cdr_dict['records']['record']['callLeg']['remoteAddress'])  # забираем  remoteAddress
            localAddress = str(cdr_dict['records']['record']['callLeg']['localAddress'])  # забираем  localAddress
            displayName = str(cdr_dict['records']['record']['callLeg']['displayName'])  # забираем  displayName

            ### добавляем идентификаторы в базу
            cms_sql_request(
                "INSERT INTO cms_cdr_records SET session_id='" + session_id + "',cms_ip='" + cms_ip + "',callleg_id='" + callleg_id + "',sipcall_id='" + sipcall_id + "';")
            print("SIP ID: " + sipcall_id + " and " + callleg_id + " inserted to database")
            ### обновляем информацию о вызове
            cms_sql_request(
                "UPDATE cms_cdr_records SET remoteAddress='" + remoteAddress + "',localAddress='" + localAddress + "' WHERE callleg_id='" + callleg_id + "';")

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

            #проверяем наличие информации о аудио
            if "codec" in cdr_dict['records']['record']['callLeg']['rxAudio']:
                acodecrx = str(cdr_dict['records']['record']['callLeg']['rxAudio']['codec']) # забираем тип кодека аудио RX
            else:
                acodecrx = "none"
            if "codec" in cdr_dict['records']['record']['callLeg']['txAudio']:
                acodectx = str(cdr_dict['records']['record']['callLeg']['txAudio']['codec']) # забираем тип кодека аудио TX
            else:
                acodecrx = "none"

            #проверяем наличие информации о Видео
            if "codec" in cdr_dict['records']['record']['callLeg']['rxVideo']:
                vcodecrx = str(cdr_dict['records']['record']['callLeg']['rxVideo']['codec']) # забираем тип кодека аудио RX
                print("video codec RX: " + vcodecrx)
            else:
                vcodecrx = "none"
            if "codec" in cdr_dict['records']['record']['callLeg']['txVideo']:
                vcodectx = str(cdr_dict['records']['record']['callLeg']['txVideo']['codec']) # забираем тип кодека аудио TX
                print("video codec TX: " + vcodectx)
            else:
                vcodectx = "none"

            ### обновляем информацию о вызове
            cms_sql_request(
                "UPDATE cms_cdr_records SET txAudio_codec='" + acodectx + "',durationSeconds='" + durationSeconds + "',reason='" + reason + "',txVideo_codec='" + vcodectx + "',rxVideo_codec='" + vcodecrx + "',rxAudio_codec='" + acodecrx + "' WHERE callleg_id='" + callleg_id + "';")
            print("call detail updated from callLegEnd")
            pprint(cdr_dict)





        if cdr_dict['records']['record']['@type'] == 'callStart':
            #print("this is callStart")
            call_id = str(cdr_dict['records']['record']['call']['@id'])
            coSpace = str(cdr_dict['records']['record']['call']['coSpace'])
            name = str(cdr_dict['records']['record']['call']['name'])
            print("cospace: " + coSpace)
            print("space name: " + name )
            if not cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                print("insert CALL to database")
                # insert IDs to database
                cms_sql_request(
                    "INSERT INTO cms_cdr_calls SET id='" + call_id + "',coSpace='" + coSpace + "',name='" + name + "';")
            else:
                print("Space ID data already presence")

        return('', 204)

    except:
        print('Parser failure!')
        pprint(cdr_dict)
        return('', 204)

