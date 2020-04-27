from flask import Flask, request
import xmltodict
import json
import datetime
from pprint import pprint
from application.sqlrequests import cms_sql_request,cm_sqlselect_dict,cm_sqlupdate
from application.cms_cdr_requester import callleginfo

def cdr_receiver():
    try:
        cdr = xmltodict.parse(request.data) #get OrderedDict
        cdr_dict = json.loads(json.dumps(cdr)) #trasfrorm OrderedDict to Dict
        cms_ip = str(request.environ['REMOTE_ADDR']) #забираем IP

        if type (cdr_dict['records']['record']) is list:
            print("CMS_RECEIVER: We get record list")
            record_list = cdr_dict['records']['record']
        else:
            print("CMS_RECEIVER: We get not record list")
            record_list = [cdr_dict['records']['record']]

        print("CMS_RECEIVER: Number of records in list: " + record_list.count())

        for record_item in record_list:
            print("CMS_RECEIVER: record_item")
            pprint(record_item)
            if record_item['@type'] == 'callLegStart':  #проверяем что, это новый коллег
                print("CMS_RECEIVER: We get callLegStart")
                callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID
                sipcall_id = str(record_item['callLeg']['sipCallId'])  # забираем sipcall_id
                remoteAddress = str(record_item['callLeg']['remoteAddress'])  # забираем  remoteAddress
                localAddress = str(record_item['callLeg']['localAddress'])  # забираем  localAddress
                #displayName = str(record_item['callLeg']['displayName'])  # забираем  displayName
                callLegStartTime = str(record_item['@time']) #забираем время лега
                timenow = str(datetime.datetime.now())

                ### добавляем идентификаторы в базу
                cms_sql_request(
                    "INSERT INTO cms_cdr_records SET date='" + timenow + "', startTime='" + callLegStartTime + "',cms_ip='" + cms_ip + "',callleg_id='" + callleg_id + "',sipcall_id='" + sipcall_id + "',localAddress='" + localAddress + "',remoteAddress='" + remoteAddress + "';")
                print("CMS_RECEIVER:     SIP ID: " + sipcall_id + " and " + callleg_id + " inserted to database")
                #собираем статистику по данному вызову
                callleginfo(callleg_id,cms_ip)
                print("CMS_RECEIVER: requests to CMS " + cms_ip + " for "+ callleg_id + " is stop")

            if record_item['@type'] == 'callLegUpdate':
                print("CMS_RECEIVER: we get callLegUpdate")
                callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID для обновления базы данных
                if "call" in record_item['callLeg']:
                    call_id = str(record_item['callLeg']['call'])  # забираем  reason
                    cm_sqlupdate(call_id, 'cms_cdr_records', 'call_id', 'callleg_id',callleg_id)  # дополняем информацию о вызове
                    cms_sql_request(
                        "UPDATE cms_cdr_records,cms_cdr_calls SET coSpace_name=cms_cdr_calls.name WHERE cms_cdr_calls.id='" + call_id + "';") # берем Имя спэйса из другой таблицы.

            if record_item['@type'] == 'callLegEnd':
                print("CMS_RECEIVER: we get callLegEnd")
                callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID для обновления базы данных
                durationSeconds = str(record_item['callLeg']['durationSeconds'])  # забираем  durationSeconds
                reason = str(record_item['callLeg']['reason'])  # забираем  reason
                callLegEndTime = str(record_item['@time'])  # забираем время лега

                #проверяем наличие информации о Аудио
                if "codec" in record_item['callLeg']['rxAudio']:
                    acodecrx = str(record_item['callLeg']['rxAudio']['codec']) # забираем тип кодека аудио RX
                else:
                    acodecrx = "none"
                #print ("audio codec RX: " + acodecrx)
                if "codec" in record_item['callLeg']['txAudio']:
                    acodectx = str(record_item['callLeg']['txAudio']['codec']) # забираем тип кодека аудио TX
                else:
                    acodectx = "none"
                #print("audio codec TX: " + acodectx)
                #проверяем наличие информации о Видео
                if "rxVideo" in record_item['callLeg']:
                    if "codec" in record_item['callLeg']['rxVideo']:
                        vcodecrx = str(record_item['callLeg']['rxVideo']['codec']) # забираем тип кодека аудио RX
                else:
                    vcodecrx = "none"
                #print("video codec RX: " + vcodecrx)
                if "txVideo" in record_item['callLeg']:
                    if "codec" in record_item['callLeg']['txVideo']:
                        vcodectx = str(record_item['callLeg']['txVideo']['codec']) # забираем тип кодека аудио TX
                else:
                    vcodectx = "none"

                #print("video codec TX: " + vcodectx)
                ### обновляем информацию о вызове
                print("CMS_RECEIVER: insert CallLegEnd data to database")
                cms_sql_request(
                    "UPDATE cms_cdr_records SET txAudio_codec='" + acodectx + "',endTime='" + callLegEndTime + "',durationSeconds='" + durationSeconds + "',reason='" + reason + "',txVideo_codec='" + vcodectx + "',rxVideo_codec='" + vcodecrx + "',rxAudio_codec='" + acodecrx + "' WHERE callleg_id='" + callleg_id + "';")
                print("CMS_RECEIVER:  call detail updated from callLegEnd")
                #pprint(cdr_dict)

            if record_item['@type'] == 'callStart':
                print("CMS_RECEIVER: we get callStart")
                call_id = str(record_item['call']['@id'])
                coSpace = str(record_item['call']['coSpace'])
                name = str(record_item['call']['name'])
                starttime = str(record_item['@time'])

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
        print('CMS_RECEIVER: Parser failure!')
        pprint(cdr_dict)
        return('', 204)

