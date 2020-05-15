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
        cms_ip = str(request.environ['HTTP_X_FORWARDED_FOR']) #забираем IP

        if type (cdr_dict['records']['record']) is list:
            print("CMS_RECEIVER " + cms_ip + ": We get record list")
            record_list = cdr_dict['records']['record']
        else:
            print("CMS_RECEIVER " + cms_ip + ": We get not record list")
            record_list = [cdr_dict['records']['record']]

        print("CMS_RECEIVER " + cms_ip + ": Number of records in list: " + str(len(record_list)))

        for record_item in record_list:
            print("CMS_RECEIVER " + cms_ip + ": record_item")
            pprint(record_item)
            if record_item['@type'] == 'callLegStart':  #проверяем что, это новый коллег
                print("CMS_RECEIVER " + cms_ip + ": We get callLegStart")
                callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID
                sipcall_id = str(record_item['callLeg']['sipCallId'])  # забираем sipcall_id
                remoteAddress = str(record_item['callLeg']['remoteAddress'])  # забираем  remoteAddress
                localAddress = str(record_item['callLeg']['localAddress'])  # забираем  localAddress
                displayName = str(record_item['callLeg']['displayName'])  # забираем  displayName
                callLegStartTime = str(record_item['@time']) #забираем время лега
                timenow = str(datetime.datetime.now())

                ### добавляем идентификаторы в базу
                cms_sql_request(
                    "INSERT INTO cms_cdr_records SET date='" + timenow + "', startTime='" + callLegStartTime + "',cms_ip='" + cms_ip + "',callleg_id='" + callleg_id + "',sipcall_id='" + sipcall_id + "',displayName='" + displayName + "',localAddress='" + localAddress + "',remoteAddress='" + remoteAddress + "';")
                print("CMS_RECEIVER " + cms_ip + ":     SIP ID: " + sipcall_id + " and " + callleg_id + " inserted to database")
                #собираем статистику по данному вызову
                #callleginfo(callleg_id,cms_ip)
                print("CMS_RECEIVER " + cms_ip + ": requests to CMS " + cms_ip + " for "+ callleg_id + " is stop")

            if record_item['@type'] == 'callLegUpdate':
                print("CMS_RECEIVER " + cms_ip + ": we get callLegUpdate")
                callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID для обновления базы данных
                if "call" in record_item['callLeg']:
                    call_id = str(record_item['callLeg']['call'])  # забираем  reason
                    cm_sqlupdate(call_id, 'cms_cdr_records', 'call_id', 'callleg_id',callleg_id)  # дополняем информацию о вызове
                    cms_sql_request(
                        "UPDATE cms_cdr_records,cms_cdr_calls SET coSpace_name=cms_cdr_calls.name WHERE cms_cdr_calls.id='" + call_id + "';") # берем Имя спэйса из другой таблицы.

            if record_item['@type'] == 'callLegEnd':
                print("CMS_RECEIVER " + cms_ip + ": we get callLegEnd")
                callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID для обновления базы данных
                durationSeconds = str(record_item['callLeg']['durationSeconds'])  # забираем  durationSeconds
                reason = str(record_item['callLeg']['reason'])  # забираем  reason
                callLegEndTime = str(record_item['@time'])  # забираем время лега

                #проверяем наличие информации о Аудио
                if "rxAudio" in record_item['callLeg']:
                    if "codec" in record_item['callLeg']['rxAudio']:
                        acodecrx = str(record_item['callLeg']['rxAudio']['codec']) # забираем тип кодека аудио RX
                    else:
                        acodecrx = "none"
                    # собираем статистику вызова
                    if "packetStatistics" in record_item['callLeg']['rxAudio']:
                        if "packetGap" in record_item['callLeg']['rxAudio']['packetStatistics']:
                            if "density" in record_item['callLeg']['rxAudio']['packetStatistics']['packetGap']:
                                rxAudio_packetGap_density = str(record_item['callLeg']['rxAudio']['packetStatistics']['packetGap']['density'])
                            else:
                                rxAudio_packetGap_density = "none"
                            if "duration" in record_item['callLeg']['rxAudio']['packetStatistics']['packetGap']:
                                rxAudio_packetGap_duration = str(record_item['callLeg']['rxAudio']['packetStatistics']['packetGap']['duration'])
                            else:
                                rxAudio_packetGap_duration = "none"
                        else:
                            rxAudio_packetGap_density = "none"
                            rxAudio_packetGap_duration = "none"
                        if "packetLossBursts" in record_item['callLeg']['rxAudio']['packetStatistics']:
                            if "density" in record_item['callLeg']['rxAudio']['packetStatistics']['packetLossBursts']:
                                rxAudio_packetLossBurst_density = str(record_item['callLeg']['rxAudio']['packetStatistics']['packetLossBursts']['density'])
                            else:
                                rxAudio_packetLossBurst_density = "none"
                            if "duration" in record_item['callLeg']['rxAudio']['packetStatistics']['packetLossBursts']:
                                rxAudio_packetLossBurst_duration = str(record_item['callLeg']['rxAudio']['packetStatistics']['packetLossBursts']['duration'])
                            else:
                                rxAudio_packetLossBurst_duration = "none"
                        else:
                            rxAudio_packetLossBurst_density = "none"
                            rxAudio_packetLossBurst_duration = "none"
                    else:
                        rxAudio_packetGap_density = "none"
                        rxAudio_packetGap_duration = "none"
                        rxAudio_packetLossBurst_density = "none"
                        rxAudio_packetLossBurst_duration = "none"
                else:
                    acodecrx = "none"
                    rxAudio_packetGap_density = "none"
                    rxAudio_packetGap_duration = "none"
                    rxAudio_packetLossBurst_density = "none"
                    rxAudio_packetLossBurst_duration = "none"

                if "txAudio" in record_item['callLeg']:
                    if "codec" in record_item['callLeg']['txAudio']:
                        acodectx = str(record_item['callLeg']['txAudio']['codec']) # забираем тип кодека аудио TX
                    else:
                        acodectx = "none"
                else:
                    acodectx = "none"

                #проверяем наличие информации о Видео
                if "rxVideo" in record_item['callLeg']:
                    if "codec" in record_item['callLeg']['rxVideo']:
                        vcodecrx = str(record_item['callLeg']['rxVideo']['codec']) # забираем тип кодека аудио RX
                    else:
                        vcodecrx = "none"

                    # собираем статистику вызова
                    if "packetStatistics" in record_item['callLeg']['rxVideo']:
                        if "packetGap" in record_item['callLeg']['rxVideo']['packetStatistics']:
                            if "density" in record_item['callLeg']['rxVideo']['packetStatistics']['packetGap']:
                                rxVideo_packetGap_density = str(record_item['callLeg']['rxVideo']['packetStatistics']['packetGap']['density'])
                            else:
                                rxVideo_packetGap_density = "none"
                            if "duration" in record_item['callLeg']['rxVideo']['packetStatistics']['packetGap']:
                                rxVideo_packetGap_duration = str(record_item['callLeg']['rxVideo']['packetStatistics']['packetGap']['duration'])
                            else:
                                rxVideo_packetGap_duration = "none"
                        else:
                            rxVideo_packetGap_density = "none"
                            rxVideo_packetGap_duration = "none"
                        if "packetLossBursts" in record_item['callLeg']['rxVideo']['packetStatistics']:
                            if "density" in record_item['callLeg']['rxVideo']['packetStatistics']['packetLossBursts']:
                                rxVideo_packetLossBurst_density = str(record_item['callLeg']['rxVideo']['packetStatistics']['packetLossBursts']['density'])
                            else:
                                rxVideo_packetLossBurst_density = "none"
                            if "duration" in record_item['callLeg']['rxVideo']['packetStatistics']['packetLossBursts']:
                                rxVideo_packetLossBurst_duration = str(record_item['callLeg']['rxVideo']['packetStatistics']['packetLossBursts']['duration'])
                            else:
                                rxVideo_packetLossBurst_duration = "none"
                        else:
                            rxVideo_packetLossBurst_density = "none"
                            rxVideo_packetLossBurst_duration = "none"
                    else:
                        rxVideo_packetGap_density = "none"
                        rxVideo_packetGap_duration = "none"
                        rxVideo_packetLossBurst_density = "none"
                        rxVideo_packetLossBurst_duration = "none"
                else:
                    vcodecrx = "none"
                    rxVideo_packetGap_density = "none"
                    rxVideo_packetGap_duration = "none"
                    rxVideo_packetLossBurst_density = "none"
                    rxVideo_packetLossBurst_duration = "none"

                if "txVideo" in record_item['callLeg']:
                    if "codec" in record_item['callLeg']['txVideo']:
                        vcodectx = str(record_item['callLeg']['txVideo']['codec']) # забираем тип кодека видео TX
                    else:
                        vcodectx = "none"
                    if "maxSizeHeight" in record_item['callLeg']['txVideo']:
                        maxSizeHeight_videoTX = str(record_item['callLeg']['txVideo']['maxSizeHeight']) # забираем максимальную высоту видео TX
                    else:
                        maxSizeHeight_videoTX = "none"
                    if "maxSizeWidth" in record_item['callLeg']['txVideo']:
                        maxSizeWidth_videoTX = str(record_item['callLeg']['txVideo']['maxSizeWidth']) # забираем максимальную ширину видео TX
                    else:
                        maxSizeWidth_videoTX = "none"
                else:
                    vcodectx = "none"
                    maxSizeHeight_videoTX = "none"
                    maxSizeWidth_videoTX = "none"

                # проверяем наличие информации об аларме
                if "alarm" in record_item['callLeg']:
                    # проверяем наличие информации о типе аларме
                    if "@type" in record_item['callLeg']['alarm']:
                        alarm_type = str(record_item['callLeg']['alarm']['@type'])  # забираем тип аларма
                    else:
                        alarm_type = "none"
                    # проверяем наличие информации о продолжительности аларма
                    if "@durationPercentage" in record_item['callLeg']['alarm']:
                        alarm_value = str(record_item['callLeg']['alarm']['@durationPercentage'])  # забираем тип аларма
                    else:
                        alarm_value = "none"
                else:
                    alarm_type = "none"
                    alarm_value = "none"

                ### обновляем информацию о вызове
                print("CMS_RECEIVER " + cms_ip + ": insert CallLegEnd data to database")
                cms_sql_request("UPDATE cms_cdr_records SET txAudio_codec='" + acodectx
                                + "',endTime='" + callLegEndTime
                                + "',durationSeconds='" + durationSeconds
                                + "',reason='" + reason
                                + "',txVideo_codec='" + vcodectx
                                + "',txVideo_maxHeight='" + maxSizeHeight_videoTX
                                + "',txVideo_maxWidth='" + maxSizeWidth_videoTX
                                + "',rxVideo_codec='" + vcodecrx
                                + "',rxVideo_packetGap_density='" + rxVideo_packetGap_density
                                + "',rxVideo_packetGap_duration='" + rxVideo_packetGap_duration
                                + "',rxVideo_packetLossBurst_density='" + rxVideo_packetLossBurst_density
                                + "',rxVideo_packetLossBurst_duration='" + rxVideo_packetLossBurst_duration
                                + "',rxAudio_codec='" + acodecrx
                                + "',rxAudio_packetGap_density='" + rxAudio_packetGap_density
                                + "',rxAudio_packetGap_duration='" + rxAudio_packetGap_duration
                                + "',rxAudio_packetLossBurst_density='" + rxAudio_packetLossBurst_density
                                + "',rxAudio_packetLossBurst_duration='" + rxAudio_packetLossBurst_duration
                                + "',alarm_type='" + alarm_type
                                + "',alarm_value='" + alarm_value
                                + "' WHERE callleg_id='" + callleg_id + "';")

                print("CMS_RECEIVER " + cms_ip + ":  call detail updated from callLegEnd")
                #pprint(cdr_dict)

            if record_item['@type'] == 'callStart':
                print("CMS_RECEIVER " + cms_ip + ": we get callStart")
                call_id = str(record_item['call']['@id'])
                coSpace = str(record_item['call']['coSpace'])
                name = str(record_item['call']['name'])
                starttime = str(record_item['@time'])

                print("CMS_RECEIVER " + cms_ip + ": cospace: " + coSpace + " time: " + starttime)
                if not cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                    print("CMS_RECEIVER " + cms_ip + ": insert CALL to database")
                    # insert IDs to database
                    cms_sql_request(
                        "INSERT INTO cms_cdr_calls SET id='" + call_id
                        + "',StartTime='" + starttime
                        + "',coSpace='" + coSpace
                        + "',cms_ip='" + cms_ip
                        + "',name='" + name + "';")
                else:
                    print("CMS_RECEIVER " + cms_ip + ": Space ID data already presence")
                #pprint(cdr_dict)

            if record_item['@type'] == 'callEnd':
                print("CMS_RECEIVER " + cms_ip + ": we get callEnd")
                call_id = str(record_item['call']['@id'])
                call_callLegsMaxActive = str(record_item['call']['callLegsMaxActive'])
                call_durationSeconds = str(record_item['call']['durationSeconds'])
                call_endtime = str(record_item['@time'])

                if cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                    print("CMS_RECEIVER " + cms_ip + ": update CALL to database")
                    # insert IDs to database
                    cms_sql_request(
                        "UPDATE cms_cdr_calls SET EndTime='" + call_endtime
                        + "',callLegsMaxActive='" + call_callLegsMaxActive
                        + "',durationSeconds='" + call_durationSeconds
                        + "' WHERE cms_cdr_calls.id='" + call_id + "';")
                else:
                    print("CMS_RECEIVER " + cms_ip + ": Call " + call_id + " is not found in DB")
                #pprint(cdr_dict)


        return('', 204)

    except:
        print('CMS_RECEIVER: Parser failure!')
        pprint(cdr_dict)
        return('', 204)

