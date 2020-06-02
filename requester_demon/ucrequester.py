import xmltodict
import pymysql
from pprint import pprint
import time
import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict
import getopt
import sys
from multiprocessing import Process
import logging.handlers


def sqlselect_dict(sqlrequest):
    try:
         con = pymysql.connect('172.20.31.50', 'sqladmin', 'Qwerty123', 'ucreporter', cursorclass=pymysql.cursors.DictCursor)
    except:
        console_output = "MySQL DB access error"
        print(console_output) #info
        logger.info(console_output)
        return None
    with con:
        cur = con.cursor()
        cur.execute(sqlrequest)
        result = cur.fetchall()
        cur.close()  # закрываем курсор
    con.close() # закрываем соединение
    return result

def sqlrequest(sqlrequest):
    try:
        con = pymysql.connect('172.20.31.50', 'sqladmin', 'Qwerty123', 'ucreporter')
    except:
        console_output = "MySQL DB access error"
        print(console_output) #info
        logger.info(console_output)
        return None
    with con:
        cur = con.cursor()
        cur.execute(sqlrequest)
        cur.close()  # закрываем курсор
    con.close() # закрываем соединение
    return "Request to database done"


def callleginfo(callleg_id,cms_ip,cms_login,cms_password,cms_port):

    # Настройка логирования
    UC_REQUESTER_LOG_FILE_NAME = "/opt/UC-Reporter/logs/UC-REQUESTER.log"
    UC_REQUESTER_LOG_FILE_SIZE = 2048000
    UC_REQUESTER_LOG_FILE_COUNT = 5

    # Диспетчер логов
    logger = logging.getLogger('UC-REQUESTER_CALLLEGINFO')
    #
    logger.setLevel(logging.DEBUG)

    # Обработчик логов - запись в файлы с перезаписью
    if not logger.handlers:
        console_output = ": no any handlers in Logger - create new one"
        print("UC-REQUESTER_CALLLEGINFO " + console_output)

        rotate_file_handler = logging.handlers.RotatingFileHandler(UC_REQUESTER_LOG_FILE_NAME, maxBytes=UC_REQUESTER_LOG_FILE_SIZE, backupCount=UC_REQUESTER_LOG_FILE_COUNT)
        rotate_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
        rotate_file_handler.setFormatter(formatter)
        logger.addHandler(rotate_file_handler)
    else:
        console_output = ": handlers are already exists in Logger"
        print("UC-REQUESTER_CALLLEGINFO " + console_output)


    # URL
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/callLegs/" + callleg_id
    console_output =  cms_ip + ": URL: "+ http_url
    print(console_output) #debug
    logger.debug(console_output)

    http_headers = {'Content-Type': 'text/xml'}

    timenow = str(datetime.datetime.now())
    try:
       get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
    except requests.exceptions.ConnectionError:
        console_output =  cms_ip + ":  Server connection error " + cms_ip
        print(console_output) #info
        logger.info(console_output)
        get.close()
        return
    except requests.exceptions.RequestException as err:
        console_output = cms_ip + ":Error Something Else" + err
        print(console_output) #info
        logger.info(console_output)
        get.close()
        return

    if get.status_code == 401:
        console_output = cms_ip + ": User " + cms_login + " deny by " + cms_ip
        print(console_output) #info
        logger.info(console_output)
        get.close()
        return

    if get.status_code != 200:
        console_output = cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
        print(console_output) #info
        logger.info(console_output)
        get.close()
        return

    console_output = cms_ip + ": we got dict with callLegs"
    print(console_output) #debug
    logger.debug(console_output)
    xml_dict = xmltodict.parse(get.text)
    get.close()  # закрываем web сессию
    callLeg = xml_dict['callLeg']

    # забираем call ID
    if "call" in callLeg:
        call_id = callLeg['call']
    else:
        call_id="none"

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

    console_output = cms_ip +  " CallID:"+callleg_id + " insert to database"
    print(console_output) #debug
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
                    + "',AudioRoundTripTimeTX='" + AudioRoundTripTimeTX + "';")

def getCallLegs(cms_login,cms_password,cms_ip,cms_port,repeat_check):

    CALLLEG_CHECK_REPEATTIME = 1 #пауза между запусками функции callleginfo

    # Настройка логирования
    UC_REQUESTER_LOG_FILE_NAME = "/opt/UC-Reporter/logs/UC-REQUESTER.log"
    UC_REQUESTER_LOG_FILE_SIZE = 2048000
    UC_REQUESTER_LOG_FILE_COUNT = 5

    # Диспетчер логов
    logger = logging.getLogger('UC-REQUESTER_GET_CALLLEGS')
    #
    logger.setLevel(logging.DEBUG)

    # Обработчик логов - запись в файлы с перезаписью
    if not logger.handlers:
        console_output = ": no any handlers in Logger - create new one"
        print("UC-REQUESTER_GET_CALLLEGS " + console_output)

        rotate_file_handler = logging.handlers.RotatingFileHandler(UC_REQUESTER_LOG_FILE_NAME, maxBytes=UC_REQUESTER_LOG_FILE_SIZE, backupCount=UC_REQUESTER_LOG_FILE_COUNT)
        rotate_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
        rotate_file_handler.setFormatter(formatter)
        logger.addHandler(rotate_file_handler)
    else:
        console_output = ": handlers are already exists in Logger"
        print("UC-REQUESTER_GET_CALLLEGS " + console_output)



    if (cms_login is None) or (cms_password is None) or (cms_port is None):
        console_output = cms_ip + ": Login, password and port not received"
        print(console_output) #info
        logger.info(console_output)
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

        endOfCycle = False
        while not endOfCycle:
            http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/callLegs?limit=" + str(page_limit) + "&offset=" + str(page_offset)
            console_output =  cms_ip + ": URL: " + http_url
            print(console_output) #debug
            logger.debug(console_output)

            try:
                get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
            except requests.exceptions.ConnectionError:
                console_output = cms_ip + ":  Server connection error " + cms_ip
                print(console_output) #info
                logger.info(console_output)
                get.close()
                break
            except requests.exceptions.RequestException as err:
                console_output = cms_ip + ": Error Something Else" + str(err)
                print(console_output) #info
                logger.info(console_output)
                get.close()
                return #закрываем функцию т.к. мы не знаем что это такое, если бы мы знали, что это такое, мы не знаем, что это такое.

            if get.status_code == 401:
                console_output = cms_ip + ": User " + cms_login + " deny by " + cms_ip
                print(console_output) #info
                logger.info(console_output)
                get.close()
                return #закрываем функцию, т.к. можно заблочить пользователя на длительный срок.

            if get.status_code != 200:
                console_output =cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
                print(console_output) #info
                logger.info(console_output)
                get.close()
                break
            console_output = cms_ip + ": we got dict with calls"
            print(console_output) #debug
            logger.debug(console_output)
            xml_dict = xmltodict.parse(get.text)
            get.close() #закрываем web сессию
            totalCallLegs = xml_dict["callLegs"]["@total"]
            console_output =  cms_ip + ": Total number of CallLegs: " + totalCallLegs
            print(console_output) #debug
            logger.debug(console_output)

            # проверям что есть активные CallLeg
            if "callLeg" in xml_dict["callLegs"]:
                # Проверяем тип list или OrderedDict для выбора корректного способа добавления в общий список
                if type(xml_dict["callLegs"]["callLeg"]) is OrderedDict:
                    callLeg_list.append(xml_dict["callLegs"]["callLeg"])
                    console_output =  cms_ip + ": Number of CallLegs from current request: 1"
                    print(console_output) #debug
                    logger.debug(console_output)
                elif type(xml_dict["callLegs"]["callLeg"]) is list:
                    callLeg_list.extend(xml_dict["callLegs"]["callLeg"])
                    console_output =  cms_ip + ": Number of CallLegs from current request: " + str(len(xml_dict["callLegs"]["callLeg"]))
                    print(console_output) #debug
                    logger.debug(console_output)
            console_output =  cms_ip + ": Number of collected CallLegs: " + str(len(callLeg_list))
            print(console_output) #debug
            logger.debug(console_output)

            if int(totalCallLegs) > len(callLeg_list):
                page_offset = len(callLeg_list)
                endOfCycle = False
            else:
                endOfCycle = True

        # перебираем все активные callLeg
        for callLeg in callLeg_list:

            # забираем callLeg ID
            if "@id" in callLeg:
                callLeg_id = callLeg["@id"]
                callleginfo(callLeg_id,cms_ip,cms_login,cms_password,cms_port)
                time.sleep(CALLLEG_CHECK_REPEATTIME) #уменьшаем переодичность запросов callLeg
            else:
                callLeg_id = "none"

        time.sleep(repeat_check)

def main(argv):

    # Настройка логирования
    UC_REQUESTER_LOG_FILE_NAME = "/opt/UC-Reporter/logs/UC-REQUESTER.log"
    UC_REQUESTER_LOG_FILE_SIZE = 2048000
    UC_REQUESTER_LOG_FILE_COUNT = 5

    # Диспетчер логов
    logger = logging.getLogger('UC-REQUESTER')
    #
    logger.setLevel(logging.DEBUG)

    # Обработчик логов - запись в файлы с перезаписью
    if not logger.handlers:
        console_output = ": no any handlers in Logger - create new one"
        print("UC-REQUESTER " + console_output)

        rotate_file_handler = logging.handlers.RotatingFileHandler(UC_REQUESTER_LOG_FILE_NAME, maxBytes=UC_REQUESTER_LOG_FILE_SIZE, backupCount=UC_REQUESTER_LOG_FILE_COUNT)
        rotate_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
        rotate_file_handler.setFormatter(formatter)
        logger.addHandler(rotate_file_handler)
    else:
        console_output = ": handlers are already exists in Logger"
        print("UC-REQUESTER " + console_output)

    cms_ip_address = ""
    try:
        opts, args = getopt.getopt(argv, 's:d')
        for opt,val in opts:
            if opt=='-s':
                cms_ip_address = val
            elif opt=='-d':
                console_output = "start database mode"
                print(console_output)  # info
                logger.info(console_output)

    except:
        console_output = "usage: ucrequester.py -s <CMS ip address>"
        print(console_output) #info
        logger.info(console_output)
        sys.exit(2)

    if cms_ip_address:  #если указан IP

        request_configuration_dict = sqlselect_dict(
            "SELECT cms_servers.ip,cms_servers.login,cms_servers.password,cms_servers.api_port, cms_requester_config.repeat_check FROM cms_requester_config INNER JOIN cms_servers ON cms_servers.cluster=cms_requester_config.cluster WHERE cms_servers.ip='" + cms_ip_address + "'")  # получаем лист словарей
        cluster_data = request_configuration_dict[0]  # делаем из листа словарь
        console_output = "we get config for: " + cms_ip_address
        print(console_output)  # info
        getCallLegs(cluster_data['login'],cluster_data['password'],cluster_data['ip'],cluster_data['api_port'],cluster_data['repeat_check'])

    else:
        request_configuration_dict = sqlselect_dict("SELECT cms_servers.ip,cms_servers.login,cms_servers.password,cms_servers.api_port,cms_requester_config.repeat_check FROM cms_requester_config INNER JOIN cms_servers ON cms_servers.cluster=cms_requester_config.cluster WHERE cms_requester_config.running='True'")
        console_output = "we get config"
        print(console_output) #info
        logger.info(console_output)
        #pprint(request_configuration_dict)
        for cluster_data in request_configuration_dict:
            console_output = "start request for: " + cluster_data['ip']
            print(console_output) #info
            logger.info(console_output)
            #pprint(cluster_data)
            p = threading.Thread(target=getCallLegs, args=(cluster_data['login'],cluster_data['password'],cluster_data['ip'],cluster_data['api_port'],cluster_data['repeat_check'],))
            p.start() # запуск процедуры в отдельном потоке
            console_output = str(p.name) + " PID " + str(p.ident) + " started for: " + cluster_data['ip']
            print(console_output) #info
            logger.info(console_output)
            #p.join() - ждать пока выполниться процедура.


if __name__ == "__main__":
    if not sys.version_info.major == 3 and sys.version_info.minor >= 5:
        console_output =  cms_ip + ": Python 3.7 is needed!"
        print(console_output)
        console_output =  cms_ip + ": You are using Python {}.{}.".format(sys.version_info.majoar, sys.version_info.minor)
        print(console_output)
        sys.exit(1)

    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        console_output = "usage: ucrequester.py -s <CMS ip address>"
        print(console_output)