import xmltodict
import pymysql
import time
import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict
import getopt
import sys
from sys import platform
import threading
import logging.handlers
import logging
from multiprocessing import Process

def logger_init(logger_name, logging_level):
    # Настройка логирования для логирования в файл
    LOG_FILE_NAME = "../logs/" + logger_name + ".log"
    LOG_FILE_SIZE = 2048000
    LOG_FILE_COUNT = 5

    # Создаем диспетчер логов
    logger = logging.getLogger(logger_name)
    # Устанавливаем уровень логирования для диспетчера логов
    logger.setLevel(logging_level)

    # Проверяем наличие обработчика логов в диспетчере логов
    if logger.hasHandlers():
        console_output = "Handlers are already exists in Logger " + logger_name + str([(type(handler)) for handler in logger.handlers])
        logger.debug(console_output)
        console_output = logger_name + ": logging level: " + logging.getLevelName(logging_level)
        logger.debug(console_output)
        return logger
    else:
        console_output = "No any handlers in Logger " + logger_name + " - create new one"
        # Проверяем платформу
        if platform == "linux":
            # Создаем обработчик логов отправляющий их на SocketServer логов для Linux
            socketHandler = logging.handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
            logger.addHandler(socketHandler)

        elif platform == "win32":
            # Создаем обработчик логов отправляющий файл логов для Windows
            auth_rotate_file_handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME,
                                                                            maxBytes=LOG_FILE_SIZE,
                                                                            backupCount=LOG_FILE_COUNT)

            auth_rotate_file_handler.setLevel(logging_level)
            formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
            auth_rotate_file_handler.setFormatter(formatter)
            logger.addHandler(auth_rotate_file_handler)

        logger.info(console_output)
        console_output = "New handler was created in Logger " + logger_name + " logging level: " + logging.getLevelName(
            logging_level)
        logger.info(console_output)
        return logger

def insert_data_to_cdr(callleg_data, cms_ip, logger):


    console_output = cms_ip + " Start parsing callleg info for distribution link"
    logger.debug(console_output)

    try:
        #данные о CallLeg
        timenow = str(datetime.datetime.now())
        #парсим ID
        if "@id" in callleg_data:
            callleg_id = str(callleg_data["@id"])

        #парсим Name
        if "name" in callleg_data:
            displayName = str(callleg_data["name"])
            remoteAddress = displayName
        else:
            displayName = "none"
            remoteAddress = "none"

        if "call" in callleg_data:
            call_id = str(callleg_data['call'])
        else:
            call_id = "none"

        # забираем  remoteParty
        if "remoteParty" in callleg_data:
            remoteParty = str(callleg_data['remoteParty'])
        else:
            remoteParty = "none"


        if "subType" in callleg_data:
            callLeg_subtype = str(callleg_data['subType'])
        else:
            callLeg_subtype = "none"


        #данные о соединении
        if "durationSeconds" in callleg_data['status']:
            durationSeconds = str(callleg_data['status']['durationSeconds'])  # забираем  durationSeconds
        else:
            durationSeconds = "none"
            # проверяем наличие информации о Аудио
        if "rxAudio" in callleg_data['status']:
            if "codec" in callleg_data['status']['rxAudio']:
                acodecrx = str(callleg_data['status']['rxAudio']['codec'])  # забираем тип кодека аудио RX
            else:
                acodecrx = "none"
            # собираем статистику вызова
            if "packetStatistics" in callleg_data['status']['rxAudio']:
                if "packetGap" in callleg_data['status']['rxAudio']['packetStatistics']:
                    if "density" in callleg_data['status']['rxAudio']['packetStatistics']['packetGap']:
                        rxAudio_packetGap_density = str(
                            callleg_data['status']['rxAudio']['packetStatistics']['packetGap']['density'])
                    else:
                        rxAudio_packetGap_density = "none"
                    if "duration" in callleg_data['status']['rxAudio']['packetStatistics']['packetGap']:
                        rxAudio_packetGap_duration = str(
                            callleg_data['status']['rxAudio']['packetStatistics']['packetGap']['duration'])
                    else:
                        rxAudio_packetGap_duration = "none"
                else:
                    rxAudio_packetGap_density = "none"
                    rxAudio_packetGap_duration = "none"
                if "packetLossBursts" in callleg_data['status']['rxAudio']['packetStatistics']:
                    if "density" in callleg_data['status']['rxAudio']['packetStatistics']['packetLossBursts']:
                        rxAudio_packetLossBurst_density = str(
                            callleg_data['status']['rxAudio']['packetStatistics']['packetLossBursts']['density'])
                    else:
                        rxAudio_packetLossBurst_density = "none"
                    if "duration" in callleg_data['status']['rxAudio']['packetStatistics']['packetLossBursts']:
                        rxAudio_packetLossBurst_duration = str(
                            callleg_data['status']['rxAudio']['packetStatistics']['packetLossBursts']['duration'])
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

        if "txAudio" in callleg_data['status']:
            if "codec" in callleg_data['status']['txAudio']:
                acodectx = str(callleg_data['status']['txAudio']['codec'])  # забираем тип кодека аудио TX
            else:
                acodectx = "none"
        else:
            acodectx = "none"

        # проверяем наличие информации о Видео
        if "rxVideo" in callleg_data['status']:
            if "codec" in callleg_data['status']['rxVideo']:
                vcodecrx = str(callleg_data['status']['rxVideo']['codec'])  # забираем тип кодека аудио RX
            else:
                vcodecrx = "none"

            # собираем статистику вызова
            if "packetStatistics" in callleg_data['status']['rxVideo']:
                if "packetGap" in callleg_data['status']['rxVideo']['packetStatistics']:
                    if "density" in callleg_data['status']['rxVideo']['packetStatistics']['packetGap']:
                        rxVideo_packetGap_density = str(
                            callleg_data['status']['rxVideo']['packetStatistics']['packetGap']['density'])
                    else:
                        rxVideo_packetGap_density = "none"
                    if "duration" in callleg_data['status']['rxVideo']['packetStatistics']['packetGap']:
                        rxVideo_packetGap_duration = str(
                            callleg_data['status']['rxVideo']['packetStatistics']['packetGap']['duration'])
                    else:
                        rxVideo_packetGap_duration = "none"
                else:
                    rxVideo_packetGap_density = "none"
                    rxVideo_packetGap_duration = "none"
                if "packetLossBursts" in callleg_data['status']['rxVideo']['packetStatistics']:
                    if "density" in callleg_data['status']['rxVideo']['packetStatistics']['packetLossBursts']:
                        rxVideo_packetLossBurst_density = str(
                            callleg_data['status']['rxVideo']['packetStatistics']['packetLossBursts'][
                                'density'])
                    else:
                        rxVideo_packetLossBurst_density = "none"
                    if "duration" in callleg_data['status']['rxVideo']['packetStatistics']['packetLossBursts']:
                        rxVideo_packetLossBurst_duration = str(
                            callleg_data['status']['rxVideo']['packetStatistics']['packetLossBursts'][
                                'duration'])
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

        if "txVideo" in callleg_data['status']:
            if "codec" in callleg_data['status']['txVideo']:
                vcodectx = str(callleg_data['status']['txVideo']['codec'])  # забираем тип кодека видео TX
            else:
                vcodectx = "none"
            if "maxSizeHeight" in callleg_data['status']['txVideo']:
                maxSizeHeight_videoTX = str(
                    callleg_data['status']['txVideo']['maxSizeHeight'])  # забираем максимальную высоту видео TX
            else:
                maxSizeHeight_videoTX = "none"
            if "maxSizeWidth" in callleg_data['status']['txVideo']:
                maxSizeWidth_videoTX = str(
                    callleg_data['status']['txVideo']['maxSizeWidth'])  # забираем максимальную ширину видео TX
            else:
                maxSizeWidth_videoTX = "none"
        else:
            vcodectx = "none"
            maxSizeHeight_videoTX = "none"
            maxSizeWidth_videoTX = "none"

        console_output = cms_ip + " Insert distribution link info in DB"
        logger.debug(console_output)
        #заносим инфу базу данных
        if not sqlselect_dict("SELECT callleg_id FROM cms_cdr_records WHERE callleg_id='" + callleg_id + "'",logger):
            sqlrequest("INSERT INTO cms_cdr_records SET date='" + timenow
                           + "',call_id='" + call_id
                           + "',remoteParty='" + remoteParty
                           + "',remoteAddress='" + remoteAddress
                           + "',callleg_id='" + callleg_id
                           + "',displayName='" + displayName
                           + "',cms_ip='" + cms_ip
                           + "',callLeg_subtype='" + callLeg_subtype  + "';",logger)
        else: #если уже данны есть, обновляем
            sqlrequest("UPDATE cms_cdr_records SET durationSeconds='" + durationSeconds
                           + "',txVideo_maxHeight='" + maxSizeHeight_videoTX
                           + "',txVideo_maxWidth='" + maxSizeWidth_videoTX
                           + "',remoteAddress='" + remoteAddress
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
                           + "',txVideo_codec='" + vcodectx
                           + "',txAudio_codec='" + acodectx
                           + "',txVideo_maxHeight='" + maxSizeHeight_videoTX
                           + "',txVideo_maxWidth='" + maxSizeWidth_videoTX
                           + "' WHERE callleg_id='" + callleg_id + "';",logger)
    except:
        console_output = cms_ip + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! distributionLink !!!!!!!!<<<Parser failure>>!"
        logger.error(console_output)

def sqlselect_dict(sqlrequest, logger):

    try:
         con = pymysql.connect('172.20.5.19', 'sqladmin', 'Qwerty123', 'ucreporter', cursorclass=pymysql.cursors.DictCursor)
    except:
        console_output = "sqlselect_dict: MySQL DB access error"
        logger.info(console_output)
        return None
    with con:
        cur = con.cursor()
        cur.execute(sqlrequest)
        result = cur.fetchall()
        cur.close()  # закрываем курсор
    con.close() # закрываем соединение
    return result

def sqlrequest(sqlrequest, logger):

    try:
        con = pymysql.connect('172.20.5.19', 'sqladmin', 'Qwerty123', 'ucreporter')
    except:
        console_output = "sqlrequest: MySQL DB access error"
        print(console_output) #info
        logger.info(console_output)
        return None
    with con:
        cur = con.cursor()
        cur.execute(sqlrequest)
        cur.close()  # закрываем курсор
    con.close() # закрываем соединение
    return "Request to database done"


def callleginfo(callleg_id,cms_ip,cms_login,cms_password,cms_port,logger):

    console_output = cms_ip + ": Start get CallLegInfo procedure for callLeg: " + callleg_id
    logger.debug(console_output)

    # URL
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/callLegs/" + callleg_id
    console_output =  cms_ip + ": URL: "+ http_url
    logger.debug(console_output)

    http_headers = {'Content-Type': 'text/xml'}

    timenow = str(datetime.datetime.now())
    try:
       get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
    except requests.exceptions.ConnectionError:
        console_output =  cms_ip + ":  Server connection error " + cms_ip
        logger.error(console_output)
        get.close()
        return
    except requests.exceptions.RequestException as err:
        console_output = cms_ip + ":Error Something Else" + err
        logger.error(console_output)
        get.close()
        return
    except BaseException as e:
        console_output = ('{!r}; callleginfo get exception '.format(e) + ' ' + cms_ip)
        logger.error(console_output)
        return


    if get.status_code == 401:
        console_output = cms_ip + ": User " + cms_login + " deny by " + cms_ip
        logger.error(console_output)
        get.close()
        return

    if get.status_code != 200:
        console_output = cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
        logger.error(console_output)
        get.close()
        return

    console_output = cms_ip + ": we got dict with callLeg Information"
    logger.debug(console_output)
    get.encoding = 'utf-8'
    xml_dict = xmltodict.parse(get.text)
    get.close()  # закрываем web сессию
    callLeg = xml_dict['callLeg']

    # забираем call ID
    if "call" in callLeg:
        call_id = callLeg['call']
    else:
        call_id="none"
    console_output = cms_ip + ": we got callLeg for call: " + call_id
    logger.debug(console_output)

    # забираем Имя
    if "name" in callLeg:
        call_id_name = str(callLeg['name'])
    else:
        call_id_name = "None"
    console_output = cms_ip + ": we got callLeg: " + call_id_name
    logger.debug(console_output)

    #вносим информацию о distributionLink в таблицу CDR
    if "subType" in callLeg:
        if callLeg['subType'] == "distributionLink":
            console_output = cms_ip + ": callLeg subtype is distribution link"
            logger.debug(console_output)
            insert_data_to_cdr(callLeg,cms_ip,logger)

    # забираем Remote Party
    if "remoteParty" in callLeg:
        call_id_remote_party = str(callLeg['remoteParty'])
    else:
        call_id_remote_party = "None"
    console_output = cms_ip + ": we got remoteparty: " + call_id_name
    logger.debug(console_output)

    if call_id_name == "None":
        current_user = call_id_remote_party
    else:
        current_user = call_id_name

    # забираем информацию по Аудио
    if "rxAudio" in callLeg['status']:
       if "packetLossPercentage" in callLeg['status']['rxAudio']:
            AudioPacketLossPercentageRX = callLeg['status']['rxAudio']['packetLossPercentage']
       else:
            AudioPacketLossPercentageRX = "0.0"
    else:
        AudioPacketLossPercentageRX = "0.0"
    if "txAudio" in callLeg['status']:
       if "packetLossPercentage" in callLeg['status']['txAudio']:
            AudioPacketLossPercentageTX = callLeg['status']['txAudio']['packetLossPercentage']
       else:
            AudioPacketLossPercentageTX = "0.0"
       if "roundTripTime" in callLeg['status']['txAudio']:
            AudioRoundTripTimeTX = callLeg['status']['txAudio']['roundTripTime']
       else:
            AudioRoundTripTimeTX = "0"
    else:
       AudioPacketLossPercentageTX = "0.0"
       AudioRoundTripTimeTX = "0"
    console_output = cms_ip + ": we got audio information for callLeg: " + call_id_name
    logger.debug(console_output)

    # забираем информацию по Видео
    if "rxVideo" in callLeg['status']:
       if "packetLossPercentage" in callLeg['status']['rxVideo']:
            VideoPacketLossPercentageRX = callLeg['status']['rxVideo']['packetLossPercentage']
       else:
            VideoPacketLossPercentageRX = "0.0"
    else:
         VideoPacketLossPercentageRX = "0.0"

    if "txVideo" in callLeg['status']:
       if "packetLossPercentage" in callLeg['status']['txVideo']:
            VideoPacketLossPercentageTX = callLeg['status']['txVideo']['packetLossPercentage']
       else:
            VideoPacketLossPercentageTX = "0.0"
       if "roundTripTime" in callLeg['status']['txVideo']:
            VideoRoundTripTimeTX = callLeg['status']['txVideo']['roundTripTime']
       else:
            VideoRoundTripTimeTX = "0"
    else:
       VideoPacketLossPercentageTX = "0.0"
       VideoRoundTripTimeTX = "0"
    console_output = cms_ip + ": we got video information for callLeg: " + call_id_name
    logger.debug(console_output)

    sqlrequest("INSERT INTO cms_cdr_calllegs SET callleg_id='" + callleg_id
                    + "',cms_node='" + cms_ip
                    + "',date='" + timenow
                    + "',call_id='" + call_id
                    + "',VideoRoundTripTimeTX='" + VideoRoundTripTimeTX
                    + "',VideoPacketLossPercentageTX='" + VideoPacketLossPercentageTX
                    + "',VideoPacketLossPercentageRX='" + VideoPacketLossPercentageRX
                    + "',AudioPacketLossPercentageRX='" + AudioPacketLossPercentageRX
                    + "',AudioPacketLossPercentageTX='" + AudioPacketLossPercentageTX
                    + "',AudioRoundTripTimeTX='" + AudioRoundTripTimeTX + "';",logger)
    console_output = cms_ip + " CallLeg for user " + current_user + " ID:" + callleg_id + " is inserted to database"
    logger.info(console_output)

def getCallLegs(cms_login,cms_password,cms_ip,cms_port,repeat_check):

    # Настройка логирования
    logger = logger_init('UC-REQUESTER', logging.DEBUG)

    console_output = cms_ip + ": Start get CallLegs procedure"
    logger.debug(console_output)

    if (cms_login is None) or (cms_password is None) or (cms_port is None):
        console_output = cms_ip + ": Login, password and port not received"
        logger.error(console_output)
        return

    # URL
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    http_headers = {'Content-Type': 'text/xml'}

    # запускаем цикл

    while True:
        timenow = str(datetime.datetime.now())
        page_offset = 0
        page_limit = 10
        callLeg_list = []
        tasks = {}

        endOfCycle = False
        while not endOfCycle:
            http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/callLegs?limit=" + str(page_limit) + "&offset=" + str(page_offset)
            #console_output =  cms_ip + ": URL: " + http_url
            #logger.debug(console_output)

            try:
                get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
            except requests.exceptions.ConnectionError:
                console_output = cms_ip + ":  Server connection error " + cms_ip
                logger.error(console_output)
                get.close()
                break
            except requests.exceptions.RequestException as err:
                console_output = cms_ip + ": Error Something Else: " + str(err)
                logger.error(console_output)
                get.close()
                return #закрываем функцию т.к. мы не знаем что это такое, если бы мы знали, что это такое, но мы не знаем, что это такое.
            except BaseException as e:
                console_output = ('{!r}; getCallLegs get exception '.format(e)  + ' ' + cms_ip)
                logger.error(console_output)
                return

            if get.status_code == 401:
                console_output = cms_ip + ": User " + cms_login + " deny by " + cms_ip
                logger.error(console_output)
                get.close()
                return #закрываем функцию, т.к. можно заблочить пользователя на длительный срок.

            if get.status_code != 200:
                console_output =cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
                logger.error(console_output)
                get.close()
                break

            #console_output = cms_ip + ": we got dict with calls"
            #logger.debug(console_output)

            xml_dict = xmltodict.parse(get.text)
            get.close() #закрываем web сессию
            totalCallLegs = xml_dict["callLegs"]["@total"]

            # проверям что есть активные CallLeg
            if "callLeg" in xml_dict["callLegs"]:

                console_output = cms_ip + ": Total number of CallLegs: " + totalCallLegs
                logger.debug(console_output)

                # Проверяем тип list или OrderedDict для выбора корректного способа добавления в общий список
                if type(xml_dict["callLegs"]["callLeg"]) is OrderedDict:
                    callLeg_list.append(xml_dict["callLegs"]["callLeg"])
                    console_output =  cms_ip + ": Number of CallLegs from current request: 1"
                    logger.debug(console_output)
                    console_output = cms_ip + ": Number of collected CallLegs: " + str(len(callLeg_list))
                    logger.debug(console_output)
                elif type(xml_dict["callLegs"]["callLeg"]) is list:
                    callLeg_list.extend(xml_dict["callLegs"]["callLeg"])
                    console_output =  cms_ip + ": Number of CallLegs from current request: " + str(len(xml_dict["callLegs"]["callLeg"]))
                    logger.debug(console_output)
                    console_output = cms_ip + ": Number of collected CallLegs: " + str(len(callLeg_list))
                    logger.debug(console_output)

            if int(totalCallLegs) > len(callLeg_list):
                page_offset = len(callLeg_list)
                endOfCycle = False
            else:
                endOfCycle = True
                if len(callLeg_list) > 0:
                    console_output = cms_ip + ": Total number of collected CallLegs: " + str(len(callLeg_list))
                    logger.info(console_output)

        # перебираем все активные callLeg
        for callLeg in callLeg_list:
            # забираем callLeg ID
            if "@id" in callLeg:
                callLeg_id = callLeg["@id"]
                # Record the task, and then launch it
                tasks[callLeg_id] = threading.Thread(target=callleginfo, args=(callLeg_id,cms_ip,cms_login,cms_password,cms_port,logger))
                tasks[callLeg_id].start()

            while threading.active_count() > 1: #засыпаем пока работают потоки
                time.sleep(repeat_check) #уменьшаем переодичность запросов callLeg



def main(argv):

    # Настройка логирования
    logger = logger_init('UC-REQUESTER', logging.DEBUG)

    cms_ip_address = ""
    try:
        opts, args = getopt.getopt(argv, 's:d')
        for opt,val in opts:
            if opt=='-s':
                cms_ip_address = val
            elif opt=='-d':
                console_output = "start database mode"
                print("UC-REQUESTER: " + console_output)  # info
                logger.info(console_output)

    except:
        console_output = "usage: ucrequester.py -s <CMS ip address>"
        print(console_output) #info
        logger.info(console_output)
        sys.exit(2)

    if cms_ip_address:  #если указан IP
        print("start for " + (str(cms_ip_address)))
        request_configuration_dict = sqlselect_dict(
            "SELECT DISTINCT cms_servers.ip,cms_servers.login,cms_servers.password,cms_servers.api_port, cms_requester_config.repeat_check FROM cms_requester_config INNER JOIN cms_servers ON cms_servers.cluster=cms_requester_config.cluster WHERE cms_servers.ip='" + cms_ip_address + "'")  # получаем лист словарей
        cluster_data = request_configuration_dict[0]  # делаем из листа словарь
        console_output = "we get config for: " + cms_ip_address
        print(console_output)  # info
        getCallLegs(cluster_data['login'],cluster_data['password'],cluster_data['ip'],cluster_data['api_port'],cluster_data['repeat_check'])

    else:
        process_dict = {} #объявляем словарь для работы с потоками


        request_configuration_dict = sqlselect_dict(
            "SELECT cms_servers.ip,cms_servers.login,cms_servers.password,cms_servers.api_port,cms_requester_config.repeat_check FROM cms_requester_config INNER JOIN cms_servers ON cms_servers.cluster=cms_requester_config.cluster AND cms_servers.ip=cms_requester_config.ip WHERE cms_requester_config.running='True';", logger)
        console_output = "we get config"
        print("UC-REQUESTER: " + console_output) #info
        logger.info(console_output)
        thread_index = 1
        for cluster_data in request_configuration_dict:
            process_information = {}  # словарь для сопоставления номера потока и IP ноды
            console_output = "start request for: " + cluster_data['ip']
            logger.info(console_output)
            process_information['Process'] = Process(target=getCallLegs, args=(cluster_data['login'],cluster_data['password'],cluster_data['ip'],cluster_data['api_port'],cluster_data['repeat_check']))
            process_information["cluster_data"] = cluster_data
            process_information['Process'].start()
            process_dict[thread_index] = process_information
            thread_index = thread_index + 1  # увеличиваем счетчик


        endOfCycle = False
        while not endOfCycle:
           for key in process_dict:
                if process_dict[key]['Process'].is_alive():
                    console_output = " Process for " + str(process_dict[key]['cluster_data']['ip']) + " PID " + str(process_dict[key]['Process'].ident) + " running status {}".format(process_dict[key]['Process'].is_alive())
                    logger.debug(console_output)
                else:
                    process_dict[key]['Process'] = Process(target=getCallLegs, args=(process_dict[key]['cluster_data']['login'],process_dict[key]['cluster_data']['password'],process_dict[key]['cluster_data']['ip'],process_dict[key]['cluster_data']['api_port'],process_dict[key]['cluster_data']['repeat_check']))
                    process_dict[key]['Process'].start()
                    console_output = "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Process restart for " + str(process_dict[key]['cluster_data']['ip']) + "  PID " + str(process_dict[key]['Process'].ident) + " running status {}".format(process_dict[key]['Process'].is_alive())
                    logger.error(console_output)
                time.sleep(process_dict[key]['cluster_data']['repeat_check'] + 3)


if __name__ == "__main__":
    if not sys.version_info.major == 3 and sys.version_info.minor >= 5:
        console_output =  ": Python 3.7 is needed!"
        print(console_output)
        console_output =   ": You are using Python {}.{}.".format(sys.version_info.majoar, sys.version_info.minor)
        print(console_output)
        sys.exit(1)

    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        console_output = "usage: ucrequester.py -s <CMS ip address>"
        print(console_output)