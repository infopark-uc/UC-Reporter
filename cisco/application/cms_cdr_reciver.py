from flask import Flask, request
import xmltodict
import json
import datetime
from pprint import pprint
from pprint import pformat
import uuid
import logging.handlers
import logging
from application.ucreporter_logs import logger_init
from application.sqlrequests import cms_sql_request,cm_sqlselect_dict,cm_sqlupdate,sql_request_dict,sql_execute

def cdr_receiver():

    # Настройка логирования
    logger = logger_init('CMS_RECEIVER', logging.DEBUG)

    try:
        cdr = xmltodict.parse(request.data) #get OrderedDict
        cdr_dict = json.loads(json.dumps(cdr)) #trasfrorm OrderedDict to Dict
        if "HTTP_X_FORWARDED_FOR" in request.environ:
            cms_ip = str(request.environ['HTTP_X_FORWARDED_FOR'])  # забираем IP
        elif "REMOTE_ADDR" in request.environ:
            cms_ip = str(request.environ['REMOTE_ADDR'])  # забираем IP
        else:
            cms_ip = "UNKNOWN"

        if type (cdr_dict['records']['record']) is list:
            console_output = cms_ip + ": We get record list"
            logger.debug(console_output)
            record_list = cdr_dict['records']['record']
        else:
            console_output =  cms_ip + ": We get not record list"
            logger.debug(console_output)
            record_list = [cdr_dict['records']['record']]

        console_output = cms_ip + ": Number of records in list: " + str(len(record_list))
        logger.debug(console_output)

        for record_item in record_list:
            console_output = "CMS_RECEIVER " + cms_ip + ": record_item"
            logger.debug(console_output)
            logger.debug("\n" + pformat(record_item))

            if record_item['@type'] == 'callLegStart':  #проверяем что, это новый коллег
                console_output =  cms_ip + ": We get callLegStart"
                logger.debug(console_output)
                console_output =  cms_ip + ": Start to process callLegStart"
                logger.debug(console_output)

                if "@id" in record_item['callLeg']:
                    callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID
                    console_output =  cms_ip + ": We get callLegID from callLegStart"
                    logger.debug(console_output)

                    # забираем sipcall_id
                    if "sipCallId" in record_item['callLeg']:
                        sipcall_id = str(record_item['callLeg']['sipCallId'])
                        console_output =  cms_ip + ": We get sipCallID from callLegStart"
                        logger.debug(console_output)
                    else:
                        sipcall_id = "none"

                    # забираем call_id
                    if "call" in record_item['callLeg']:
                        call_id = str(record_item['callLeg']['call'])
                        console_output =  cms_ip + ": We get callID from callLegStart"
                        logger.debug(console_output)
                    else:
                        call_id = "none"

                    # забираем  remoteAddress
                    if "remoteAddress" in record_item['callLeg']:
                        remoteAddress = str(record_item['callLeg']['remoteAddress'])
                        console_output =  cms_ip + ": We get remoteAddress from callLegStart"
                        logger.debug(console_output)
                    else:
                        remoteAddress = "none"

                    # забираем  remoteParty
                    if "remoteParty" in record_item['callLeg']:
                        remoteParty = str(record_item['callLeg']['remoteParty'])
                        console_output =  cms_ip + ": We get remoteParty from callLegStart"
                        logger.debug(console_output)
                    else:
                        remoteParty = "none"

                    # забираем  localAddress
                    if "localAddress" in record_item['callLeg']:
                        localAddress = str(record_item['callLeg']['localAddress'])
                        console_output =  cms_ip + ": We get localAddress from callLegStart"
                        logger.debug(console_output)
                    else:
                        localAddress = "none"

                    # забираем  displayName
                    if "displayName" in record_item['callLeg']:
                        displayName = str(record_item['callLeg']['displayName'])
                        console_output =  cms_ip + ": We get displayName from callLegStart"
                        logger.debug(console_output)
                    else:
                        displayName = "none"

                    # забираем время лега
                    if "@time" in record_item:
                        callLegStartTime = str(record_item['@time'])
                        callLegStartTimeMSK = str(datetime.datetime.strptime(callLegStartTime, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=3))
                        console_output =  cms_ip + ": We get callLegTime from callLegStart"
                        logger.debug(console_output)
                    else:
                        callLegStartTime = "none"
                        callLegStartTimeMSK = "none"

                    timenow = str(datetime.datetime.now())

                    # забираем GuestConnection
                    if "guestConnection" in record_item['callLeg']:
                        guestConnection = str(record_item['callLeg']['guestConnection'])
                        console_output =  cms_ip + ": We get guestConnection from callLegStart"
                        logger.debug(console_output)
                    else:
                         guestConnection = "none"

                    # забираем  recording
                    if "recording" in record_item['callLeg']:
                        recording = str(record_item['callLeg']['recording'])
                        console_output =  cms_ip + ": We get recording from callLegStart"
                        logger.debug(console_output)
                    else:
                         recording = "none"

                    # забираем CallLeg type
                    if "type" in record_item['callLeg']:
                        callLeg_type = str(record_item['callLeg']['type'])
                        console_output =  cms_ip + ": We get type from callLegStart"
                        logger.debug(console_output)
                    else:
                        callLeg_type = "none"

                    # забираем CallLeg subtype
                    if "subType" in record_item['callLeg']:
                        callLeg_subtype = str(record_item['callLeg']['subType'])
                        console_output =  cms_ip + ": We get subType from callLegStart"
                        logger.debug(console_output)
                    else:
                        callLeg_subtype = "none"

                    ### добавляем идентификаторы в базу
                    cms_sql_request(
                        "INSERT INTO cms_cdr_records SET date='" + timenow
                        + "',startTime='" + callLegStartTimeMSK
                        + "',cms_ip='" + cms_ip
                        + "',callleg_id='" + callleg_id
                        + "',sipcall_id='" + sipcall_id
                        + "',call_id='" + call_id
                        + "',displayName='" + displayName
                        + "',localAddress='" + localAddress
                        + "',remoteParty='" + remoteParty
                        + "',guestConnection='" + guestConnection
                        + "',recording='" + recording
                        + "',callLeg_type='" + callLeg_type
                        + "',callLeg_subtype='" + callLeg_subtype
                        + "',remoteAddress='" + remoteAddress + "';")

                    console_output =  cms_ip + ":     SIP ID: " + sipcall_id + " and " + callleg_id + " inserted to database"
                    logger.debug(console_output)
                else:
                    console_output =  cms_ip + ": CallLeg Id not found in callLegStart - nothing was inserted in DB"
                    logger.debug(console_output)

            if record_item['@type'] == 'callLegUpdate':
                console_output =  cms_ip + ": we get callLegUpdate"
                logger.debug(console_output)
                callleg_id = str(record_item['callLeg']['@id'])  # забираем callleg ID для обновления базы данных
                if "call" in record_item['callLeg']:
                    call_id = str(record_item['callLeg']['call'])  # забираем  reason
                    cm_sqlupdate(call_id, 'cms_cdr_records', 'call_id', 'callleg_id',callleg_id)  # дополняем информацию о вызове
                    #cms_sql_request(
                    #    "UPDATE cms_cdr_records,cms_cdr_calls SET coSpace_name=cms_cdr_calls.name WHERE cms_cdr_calls.id='" + call_id + "';") # берем Имя спэйса из другой таблицы.

            if record_item['@type'] == 'callLegEnd':
                console_output =  cms_ip + ": we get callLegEnd"
                logger.debug(console_output)

                # забираем callleg ID для обновления базы данных
                if "@id" in record_item['callLeg']:
                    callleg_id = str(record_item['callLeg']['@id'])
                    console_output =  cms_ip + ": We get callLegID from callLegEnd"
                    logger.debug(console_output)

                    # забираем  durationSeconds
                    if "durationSeconds" in record_item['callLeg']:
                        durationSeconds = str(record_item['callLeg']['durationSeconds'])  # забираем  durationSeconds
                        console_output =  cms_ip + ": We get durationSeconds from callLegEnd"
                        logger.debug(console_output)
                    else:
                        durationSeconds = "none"

                    # забираем  reason
                    if "reason" in record_item['callLeg']:
                        reason = str(record_item['callLeg']['reason'])
                        console_output =  cms_ip + ": We get reason from callLegEnd"
                        logger.debug(console_output)
                    else:
                        reason = "none"

                    # забираем remoteTeardown
                    if "remoteTeardown" in record_item['callLeg']:
                        remoteTeardown = str(record_item['callLeg']['remoteTeardown'])
                        console_output =  cms_ip + ": We get remoteTeardown from callLegEnd"
                        logger.debug(console_output)
                    else:
                        remoteTeardown = "none"

                    # забираем время лега
                    if "@time" in record_item:
                        callLegEndTime = str(record_item['@time'])
                        callLegEndTimeMSK = str(datetime.datetime.strptime(callLegEndTime, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=3))
                        console_output =  cms_ip + ": We get callLegEndTime from callLegEnd"
                        logger.debug(console_output)
                    else:
                        callLegEndTime = "none"
                        callLegEndTimeMSK = "none"

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
                    console_output =  cms_ip + ": insert CallLegEnd data to database"
                    #print("CMS_RECEIVER " + console_output)
                    logger.debug(console_output)
                    cms_sql_request("UPDATE cms_cdr_records SET txAudio_codec='" + acodectx
                                    + "',endTime='" + callLegEndTimeMSK
                                    + "',durationSeconds='" + durationSeconds
                                    + "',reason='" + reason
                                    + "',remoteTeardown='" + remoteTeardown
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

                    console_output =  cms_ip + ":  call detail updated from callLegEnd"
                    logger.debug(console_output)
                else:
                    console_output =  cms_ip + ": CallLeg Id not found in callLegEnd - nothing was inserted in DB"
                    logger.debug(console_output)

            if record_item['@type'] == 'callStart':
                console_output =  cms_ip + ": we get callStart"
                logger.debug(console_output)

                if "@id" in record_item['call']:
                    call_id = str(record_item['call']['@id'])  # забираем call ID
                    console_output =  cms_ip + ": We get callID from callStart"
                    logger.debug(console_output)

                    # забираем coSpace
                    if "coSpace" in record_item['call']:
                        coSpace = str(record_item['call']['coSpace'])
                        console_output =  cms_ip + ": We get coSpace from callStart"
                        logger.debug(console_output)
                    else:
                        coSpace = "none"

                    # забираем name
                    if "name" in record_item['call']:
                        name = str(record_item['call']['name'])
                        console_output =  cms_ip + ": We get name from callStart"
                        logger.debug(console_output)
                    else:
                        name = "none"

                    # забираем callCorrelator
                    if "callCorrelator" in record_item['call']:
                        call_correlator = str(record_item['call']['callCorrelator'])
                        console_output =  cms_ip + ": We get callCorrelator from callStart"
                        logger.debug(console_output)
                    else:
                        call_correlator = "none"

                    # забираем время
                    if "@time" in record_item:
                        starttime = str(record_item['@time'])
                        starttimeMSK = str(datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=3))
                        console_output =  cms_ip + ": We get start time from callStart"
                        logger.debug(console_output)
                        console_output = cms_ip + ": Call start time:" + starttimeMSK
                        logger.debug(console_output)
                    else:
                        starttime = "none"
                        starttimeMSK = "none"

                    console_output = cms_ip + ": cospace: " + coSpace + " time: " + starttime
                    logger.debug(console_output)

                    # Добавление активного вызова - начало
                    console_output = cms_ip + ": Request meeting_id_list form DB: " + "SELECT meeting_id FROM cms_cdr_active_calls WHERE callCorrelator_id='" + call_correlator + "'"
                    logger.debug(console_output)
                    meeting_id_list = sql_request_dict("SELECT meeting_id FROM cms_cdr_active_calls WHERE callCorrelator_id='" + str(call_correlator) + "'")
                    if not meeting_id_list:
                        meeting_id = str(uuid.uuid1())
                        console_output = cms_ip + ": insert new active CALL to database with new meeting_id: " + meeting_id
                        logger.debug(console_output)
                        # insert new active call IDs to database
                        sql_execute(
                            "INSERT INTO cms_cdr_active_calls SET meeting_id='" + meeting_id
                            + "',coSpace_id='" + coSpace
                            + "',callCorrelator_id='" + call_correlator
                            + "',call_id='" + call_id + "';")
                    else:
                        console_output =  cms_ip + ": active call already exists in database with call_correlator: " + call_correlator
                        logger.debug(console_output)
                        if meeting_id_list[0]["meeting_id"]:
                            meeting_id = str(meeting_id_list[0]["meeting_id"])
                            console_output = cms_ip + ": insert existing active call in database with meeting_id: " + meeting_id
                            logger.debug(console_output)
                            sql_execute(
                                "INSERT INTO cms_cdr_active_calls SET meeting_id='" + meeting_id
                                + "',coSpace_id='" + coSpace
                                + "',callCorrelator_id='" + call_correlator
                                + "',call_id='" + call_id + "';")
                        else:
                            console_output = cms_ip + ": meeting_id not found for callCorrelator: " + call_correlator
                            meeting_id = "UNKNOWN"
                            logger.debug(console_output)
                    # Добавление активного вызова - конец

                    if not cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                        console_output = cms_ip + ": insert CALL to database"
                        logger.debug(console_output)
                        # insert IDs to database
                        cms_sql_request(
                            "INSERT INTO cms_cdr_calls SET id='" + call_id
                            + "',StartTime='" + starttimeMSK
                            + "',coSpace='" + coSpace
                            + "',cms_ip='" + cms_ip
                            + "',callCorrelator='" + call_correlator
                            + "',meeting_id='" + meeting_id
                            + "',name='" + name + "';")
                    else:
                        console_output =  cms_ip + ": Space ID data already presence"
                        logger.debug(console_output)


            if record_item['@type'] == 'callEnd':
                console_output =  cms_ip + ": we get callEnd"
                logger.debug(console_output)
                if "@id" in record_item['call']:
                    call_id = str(record_item['call']['@id'])
                    console_output = cms_ip + ": We get callID from callEnd"
                    logger.debug(console_output)

                    # забираем call_callLegsMaxActive
                    if "callLegsMaxActive" in record_item['call']:
                        call_callLegsMaxActive = str(record_item['call']['callLegsMaxActive'])
                        console_output = cms_ip + ": We get call_callLegsMaxActive from callEnd"
                        logger.debug(console_output)
                    else:
                        call_callLegsMaxActive = "none"

                    # забираем call_durationSeconds
                    if "durationSeconds" in record_item['call']:
                        call_durationSeconds = str(record_item['call']['durationSeconds'])
                        console_output = cms_ip + ": We get call_durationSeconds from callEnd"
                        logger.debug(console_output)
                    else:
                        call_durationSeconds = "none"

                    # забираем время
                    if "@time" in record_item:
                        call_endtime = str(record_item['@time'])
                        call_endtimeMSK = str(datetime.datetime.strptime(call_endtime, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=3))
                        console_output = cms_ip + ": Call end time: " + call_endtimeMSK
                        logger.debug(console_output)
                    else:
                        call_endtime = "none"
                        call_endtimeMSK = "none"

                    if cm_sqlselect_dict('id', 'cms_cdr_calls', 'id', call_id):
                        console_output =  cms_ip + ": update CALL to database"
                        logger.debug(console_output)
                        # insert IDs to database
                        cms_sql_request(
                            "UPDATE cms_cdr_calls SET EndTime='" + call_endtimeMSK
                            + "',callLegsMaxActive='" + call_callLegsMaxActive
                            + "',durationSeconds='" + call_durationSeconds
                            + "' WHERE cms_cdr_calls.id='" + call_id + "';")
                    else:
                        console_output =  cms_ip + ": Call " + call_id + " is not found in DB"
                        logger.debug(console_output)

                    # Удаление активного вызова - начало
                    console_output = cms_ip + ": Start to delete active call: " + "DELETE FROM cms_cdr_active_calls WHERE call_id='" + call_id + "'"
                    logger.debug(console_output)
                    sql_execute("DELETE FROM cms_cdr_active_calls WHERE call_id='" + str(call_id) + "'")
                    console_output = cms_ip + ": End to delete active call"
                    logger.debug(console_output)
                    # Удаление активного вызова - конец

                else:
                    console_output = cms_ip + ": callEnd does not contain CallID"
                    logger.debug(console_output)


            if record_item['@type'] == 'recordingStart':
                console_output =  cms_ip + ": we get recordingStart"
                logger.debug(console_output)

                if "@id" in record_item['recording']:
                    recording_id = str(record_item['recording']['@id'])
                    console_output = cms_ip + ": We get RecordingID from recordingStart"
                    logger.debug(console_output)

                    # забираем path
                    if "path" in record_item['recording']:
                        recording_path = str(record_item['recording']['path'])
                        console_output = cms_ip + ": We get path from recordingStart"
                        logger.debug(console_output)
                    else:
                        recording_path = "none"

                    # забираем call_id
                    if "call" in record_item['recording']:
                        recording_call_id = str(record_item['recording']['call'])
                        console_output = cms_ip + ": We get call_id from recordingStart"
                        logger.debug(console_output)
                    else:
                        recording_call_id = "none"

                    # забираем callLeg_id
                    if "callLeg" in record_item['recording']:
                        recording_callLeg_id = str(record_item['recording']['callLeg'])
                        console_output = cms_ip + ": We get callLeg_id from recordingStart"
                        logger.debug(console_output)
                    else:
                        recording_callLeg_id = "none"

                    ### добавляем информацию о записи в базу
                    cms_sql_request(
                        "INSERT INTO cms_cdr_recordings SET recording_id='" + recording_id
                        + "',path='" + recording_path
                        + "',call_id='" + recording_call_id
                        + "',callLeg_id='" + recording_callLeg_id + "';")

                    console_output = cms_ip + ":  RecordingID: " + recording_id + " inserted to database"
                    logger.debug(console_output)

        return('', 204)

    except:
        console_output = cms_ip + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!<<<Parser failure>>!"
        print("CMS_RECEIVER " + console_output)
        logger.error(console_output)
        pprint(cdr_dict)
        logger.error("\n" + pformat(record_item))
        return('', 204)

