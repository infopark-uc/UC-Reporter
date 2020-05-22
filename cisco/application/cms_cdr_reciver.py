from flask import Flask, request
import xmltodict
import json
import datetime
from pprint import pprint
from application.sqlrequests import cms_sql_request,cm_sqlselect_dict,cm_sqlupdate

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
                print("CMS_RECEIVER " + cms_ip + ": Start to process callLegStart")

                if "@id" in record_item['callLeg']:
                    callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID
                    print("CMS_RECEIVER " + cms_ip + ": We get callLegID from callLegStart")

                    # забираем sipcall_id
                    if "sipCallId" in record_item['callLeg']:
                        sipcall_id = str(record_item['callLeg']['sipCallId'])
                        print("CMS_RECEIVER " + cms_ip + ": We get sipCallID from callLegStart")
                    else:
                        sipcall_id = "none"

                    # забираем call_id
                    if "call" in record_item['callLeg']:
                        call_id = str(record_item['callLeg']['call'])
                        print("CMS_RECEIVER " + cms_ip + ": We get callID from callLegStart")
                    else:
                        call_id = "none"

                    # забираем  remoteAddress
                    if "remoteAddress" in record_item['callLeg']:
                        remoteAddress = str(record_item['callLeg']['remoteAddress'])
                        print("CMS_RECEIVER " + cms_ip + ": We get remoteAddress from callLegStart")
                    else:
                        remoteAddress = "none"

                    # забираем  remoteParty
                    if "remoteParty" in record_item['callLeg']:
                        remoteParty = str(record_item['callLeg']['remoteParty'])
                        print("CMS_RECEIVER " + cms_ip + ": We get remoteParty from callLegStart")
                    else:
                        remoteParty = "none"

                    # забираем  localAddress
                    if "localAddress" in record_item['callLeg']:
                        localAddress = str(record_item['callLeg']['localAddress'])
                        print("CMS_RECEIVER " + cms_ip + ": We get localAddress from callLegStart")
                    else:
                        localAddress = "none"

                    # забираем  displayName
                    if "displayName" in record_item['callLeg']:
                        displayName = str(record_item['callLeg']['displayName'])
                        print("CMS_RECEIVER " + cms_ip + ": We get displayName from callLegStart")
                    else:
                        displayName = "none"

                    # забираем время лега
                    if "@time" in record_item:
                        callLegStartTime = str(record_item['@time'])
                        print("CMS_RECEIVER " + cms_ip + ": We get callLegTime from callLegStart")
                    else:
                        callLegStartTime = "none"

                    timenow = str(datetime.datetime.now())

                    ### добавляем идентификаторы в базу
                    cms_sql_request(
                        "INSERT INTO cms_cdr_records SET date='" + timenow
                        + "', startTime='" + callLegStartTime
                        + "',cms_ip='" + cms_ip
                        + "',callleg_id='" + callleg_id
                        + "',sipcall_id='" + sipcall_id
                        + "',call_id='" + call_id
                        + "',displayName='" + displayName
                        + "',localAddress='" + localAddress
                        + "',remoteParty='" + remoteParty
                        + "',remoteAddress='" + remoteAddress + "';")

                    print("CMS_RECEIVER " + cms_ip + ":     SIP ID: " + sipcall_id + " and " + callleg_id + " inserted to database")
                else:
                    print("CMS_RECEIVER " + cms_ip + ": CallLeg Id not found in callLegStart - nothing was inserted in DB")

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

                # забираем callleg ID для обновления базы данных
                if "@id" in record_item['callLeg']:
                    callleg_id = str(record_item['callLeg']['@id'])
                    print("CMS_RECEIVER " + cms_ip + ": We get callLegID from callLegEnd")

                    # забираем  durationSeconds
                    if "durationSeconds" in record_item['callLeg']:
                        durationSeconds = str(record_item['callLeg']['durationSeconds'])  # забираем  durationSeconds
                        print("CMS_RECEIVER " + cms_ip + ": We get durationSeconds from callLegEnd")
                    else:
                        durationSeconds = "none"

                    # забираем  reason
                    if "reason" in record_item['callLeg']:
                        reason = str(record_item['callLeg']['reason'])
                        print("CMS_RECEIVER " + cms_ip + ": We get reason from callLegEnd")
                    else:
                        reason = "none"

                    # забираем время лега
                    if "@time" in record_item:
                        callLegEndTime = str(record_item['@time'])
                        print("CMS_RECEIVER " + cms_ip + ": We get callLegEndTime from callLegEnd")
                    else:
                        callLegEndTime = "none"

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
                else:
                    print("CMS_RECEIVER " + cms_ip + ": CallLeg Id not found in callLegEnd - nothing was inserted in DB")

            if record_item['@type'] == 'callStart':
                print("CMS_RECEIVER " + cms_ip + ": we get callStart")

                if "@id" in record_item['call']:
                    call_id = str(record_item['call']['@id'])  # забираем call ID
                    print("CMS_RECEIVER " + cms_ip + ": We get callID from callStart")

                    # забираем coSpace
                    if "coSpace" in record_item['call']:
                        coSpace = str(record_item['call']['coSpace'])
                        print("CMS_RECEIVER " + cms_ip + ": We get coSpace from callStart")
                    else:
                        coSpace = "none"

                    # забираем name
                    if "name" in record_item['call']:
                        name = str(record_item['call']['name'])
                        print("CMS_RECEIVER " + cms_ip + ": We get name from callStart")
                    else:
                        name = "none"

 
                    # забираем время
                    if "@time" in record_item:
                        starttime = str(record_item['@time'])
                        starttimeMSK = str(datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=3))
                        print("CMS_RECEIVER " + cms_ip + ": We get start time from callStart")
                        print("CMS_RECEIVER " + cms_ip + ": Call start time: " + starttimeMSK)
                    else:
                        starttime = "none"
                        starttimeMSK = "none"


                    print("CMS_RECEIVER " + cms_ip + ": cospace: " + coSpace + " time: " + starttime)
                    if not cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                        print("CMS_RECEIVER " + cms_ip + ": insert CALL to database")
                        # insert IDs to database
                        cms_sql_request(
                            "INSERT INTO cms_cdr_calls SET id='" + call_id
                            + "',StartTime='" + starttimeMSK
                            + "',coSpace='" + coSpace
                            + "',cms_ip='" + cms_ip
                            + "',name='" + name + "';")
                    else:
                        print("CMS_RECEIVER " + cms_ip + ": Space ID data already presence")


            if record_item['@type'] == 'callEnd':
                print("CMS_RECEIVER " + cms_ip + ": we get callEnd")
                call_id = str(record_item['call']['@id'])
                call_callLegsMaxActive = str(record_item['call']['callLegsMaxActive'])
                call_durationSeconds = str(record_item['call']['durationSeconds'])
                call_endtime = str(record_item['@time'])
                call_endtimeMSK = str(datetime.datetime.strptime(call_endtime, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=3))
                print("CMS_RECEIVER " + cms_ip + ": Call end time: " + call_endtimeMSK)

                if cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                    print("CMS_RECEIVER " + cms_ip + ": update CALL to database")
                    # insert IDs to database
                    cms_sql_request(
                        "UPDATE cms_cdr_calls SET EndTime='" + call_endtimeMSK
                        + "',callLegsMaxActive='" + call_callLegsMaxActive
                        + "',durationSeconds='" + call_durationSeconds
                        + "' WHERE cms_cdr_calls.id='" + call_id + "';")
                else:
                    print("CMS_RECEIVER " + cms_ip + ": Call " + call_id + " is not found in DB")
                #pprint(cdr_dict)


        return('', 204)

    except:
        print("CMS_RECEIVER: " + cms_ip + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!<<<Parser failure>>!")
        pprint(cdr_dict)
        return('', 204)

