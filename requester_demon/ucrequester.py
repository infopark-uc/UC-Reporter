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
import threading
import logging.handlers
from multiprocessing import Process


def sqlselect_dict(sqlrequest):

    logger = logger_init_auth()

    try:
         con = pymysql.connect('172.20.5.19', 'sqladmin', 'Qwerty123', 'ucreporter', cursorclass=pymysql.cursors.DictCursor)
    except:
        console_output = "sqlselect_dict: MySQL DB access error"
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

    logger = logger_init_auth()

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


def callleginfo(callleg_id,cms_ip,cms_login,cms_password,cms_port):

    logger = logger_init_auth()

    # URL
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/callLegs/" + callleg_id
    console_output =  cms_ip + ": URL: "+ http_url
    #print(console_output) #debug
    logger.debug(console_output)

    http_headers = {'Content-Type': 'text/xml'}

    timenow = str(datetime.datetime.now())
    try:
       get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
    except requests.exceptions.ConnectionError:
        console_output =  cms_ip + ":  Server connection error " + cms_ip
        #print(console_output) #info
        logger.error(console_output)
        get.close()
        return
    except requests.exceptions.RequestException as err:
        console_output = cms_ip + ":Error Something Else" + err
        #print(console_output) #info
        logger.error(console_output)
        get.close()
        return
    except BaseException as e:
        console_output = ('{!r}; callleginfo get exception '.format(e) + ' ' + cms_ip)
        #print(console_output)
        logger.error(console_output)
        #get.close() #закоменчен т.к. нечего закрывать.
        return


    if get.status_code == 401:
        console_output = cms_ip + ": User " + cms_login + " deny by " + cms_ip
        #print(console_output) #info
        logger.error(console_output)
        get.close()
        return

    if get.status_code != 200:
        console_output = cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
        #print(console_output) #info
        logger.error(console_output)
        get.close()
        return

    console_output = cms_ip + ": we got dict with callLeg Information"
    #print(console_output) #debug
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

    # забираем Имя
    if "name" in callLeg:
        call_id_name = str(callLeg['name'])
    else:
        call_id_name = "None"

    # забираем Remote Party
    if "remoteParty" in callLeg:
        call_id_remote_party = str(callLeg['remoteParty'])
    else:
        call_id_remote_party = "None"

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

    console_output = cms_ip + " CallLeg for user " + current_user + " ID:" + callleg_id + " is inserted to database"
    #print(console_output) #debug
    logger.info(console_output)
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

    logger = logger_init_auth()

    if (cms_login is None) or (cms_password is None) or (cms_port is None):
        console_output = cms_ip + ": Login, password and port not received"
        #print(console_output) #info
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
            console_output =  cms_ip + ": URL: " + http_url
            #print(console_output) #debug
            logger.debug(console_output)

            try:
                get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
            except requests.exceptions.ConnectionError:
                console_output = cms_ip + ":  Server connection error " + cms_ip
                #print(console_output) #info
                logger.error(console_output)
                get.close()
                break
            except requests.exceptions.RequestException as err:
                console_output = cms_ip + ": Error Something Else" + str(err)
                #print(console_output) #info
                logger.error(console_output)
                get.close()
                return #закрываем функцию т.к. мы не знаем что это такое, если бы мы знали, что это такое, мы не знаем, что это такое.
            except BaseException as e:
                console_output = ('{!r}; getCallLegs get exception '.format(e)  + ' ' + cms_ip)
                #print(console_output)
                logger.error(console_output)
                #get.close() #нечего закрывать.
                return

            if get.status_code == 401:
                console_output = cms_ip + ": User " + cms_login + " deny by " + cms_ip
                #print(console_output) #info
                logger.error(console_output)
                get.close()
                return #закрываем функцию, т.к. можно заблочить пользователя на длительный срок.

            if get.status_code != 200:
                console_output =cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
                #print(console_output) #info
                logger.error(console_output)
                get.close()
                break

            console_output = cms_ip + ": we got dict with calls"
            #print(console_output) #debug
            logger.debug(console_output)
            xml_dict = xmltodict.parse(get.text)
            get.close() #закрываем web сессию
            totalCallLegs = xml_dict["callLegs"]["@total"]
            console_output =  cms_ip + ": Total number of CallLegs: " + totalCallLegs
            #print(console_output) #debug
            logger.debug(console_output)

            # проверям что есть активные CallLeg
            if "callLeg" in xml_dict["callLegs"]:
                # Проверяем тип list или OrderedDict для выбора корректного способа добавления в общий список
                if type(xml_dict["callLegs"]["callLeg"]) is OrderedDict:
                    callLeg_list.append(xml_dict["callLegs"]["callLeg"])
                    console_output =  cms_ip + ": Number of CallLegs from current request: 1"
                    #print(console_output) #debug
                    logger.debug(console_output)
                elif type(xml_dict["callLegs"]["callLeg"]) is list:
                    callLeg_list.extend(xml_dict["callLegs"]["callLeg"])
                    console_output =  cms_ip + ": Number of CallLegs from current request: " + str(len(xml_dict["callLegs"]["callLeg"]))
                    #print(console_output) #debug
                    logger.debug(console_output)
            console_output =  cms_ip + ": Number of collected CallLegs: " + str(len(callLeg_list))
            #print(console_output) #debug
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
                tasks[callLeg_id] = threading.Thread(target=callleginfo, args=(callLeg_id,cms_ip,cms_login,cms_password,cms_port))
                tasks[callLeg_id].start()

            while threading.active_count() > 1: #засыпаем пока работают потоки
                time.sleep(repeat_check) #уменьшаем переодичность запросов callLeg
                #pprint(tasks)


def main(argv):

    logger = logger_init_auth()

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
            "SELECT cms_servers.ip,cms_servers.login,cms_servers.password,cms_servers.api_port,cms_requester_config.repeat_check FROM cms_requester_config INNER JOIN cms_servers ON cms_servers.cluster=cms_requester_config.cluster AND cms_servers.ip=cms_requester_config.ip WHERE cms_requester_config.running='True';")
        console_output = "we get config"
        print("UC-REQUESTER: " + console_output) #info
        logger.info(console_output)
        #pprint(request_configuration_dict)
        thread_index = 1
        for cluster_data in request_configuration_dict:
            process_information = {}  # словарь для сопоставления номера потока и IP ноды
            console_output = "start request for: " + cluster_data['ip']
            logger.info(console_output)
            process_information['Process'] = Process(target=getCallLegs, args=(cluster_data['login'],cluster_data['password'],cluster_data['ip'],cluster_data['api_port'],cluster_data['repeat_check'],))
            process_information["cluster_data"] = cluster_data
            process_information['Process'].start()
            process_dict[thread_index] =  process_information
            thread_index = thread_index + 1  # увеличиваем счетчик


        endOfCycle = False
        while not endOfCycle:
           for key in process_dict:
                if process_dict[key]['Process'].is_alive():
                    console_output = " Process for " + str(process_dict[key]['cluster_data']['ip']) + " PID " + str(process_dict[key]['Process'].ident) + " running status {}".format(process_dict[key]['Process'].is_alive())
                    #print(console_output)
                    logger.debug(console_output)
                else:
                    #process_dict[key]['Process'].terminate()
                    process_dict[key]['Process'] = Process(target=getCallLegs, args=(process_dict[key]['cluster_data']['login'],process_dict[key]['cluster_data']['password'],process_dict[key]['cluster_data']['ip'],process_dict[key]['cluster_data']['api_port'],process_dict[key]['cluster_data']['repeat_check'],))
                    process_dict[key]['Process'].start()
                    console_output = "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Process restart for " + str(process_dict[key]['cluster_data']['ip']) + "  PID " + str(process_dict[key]['Process'].ident) + " running status {}".format(process_dict[key]['Process'].is_alive())
                    logger.error(console_output)
                time.sleep(process_dict[key]['cluster_data']['repeat_check'] + 3)

def logger_init_auth():

    # Настройка логирования
    UC_REQUESTER_LOG_FILE_NAME = "../logs/UC-REQUESTER.log"
    UC_REQUESTER_LOG_FILE_SIZE = 2048000
    UC_REQUESTER_LOG_FILE_COUNT = 5

    # Диспетчер логов
    logger = logging.getLogger('UC-REQUESTER')
    # Уровень логирования, сообщения которого записываются в файл
    logger.setLevel(logging.INFO)

    # Обработчик логов - запись в файлы с перезаписью
    if logger.hasHandlers():

        console_output = "handlers are already exists in Logger UC-REQUESTER"
        #print("UC-REQUESTER: " + console_output)
        logger.debug(console_output)

        return logger

    else:
        console_output = "no any handlers in Logger UC-REQUESTER - create new one"
        #print("UC-REPORTER_AUTH: " + console_output)

        rotate_file_handler = logging.handlers.RotatingFileHandler(UC_REQUESTER_LOG_FILE_NAME,
                                                                   maxBytes=UC_REQUESTER_LOG_FILE_SIZE,
                                                                   backupCount=UC_REQUESTER_LOG_FILE_COUNT)
        rotate_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
        rotate_file_handler.setFormatter(formatter)
        logger.addHandler(rotate_file_handler)

        logger.info(console_output)
        console_output = "New handler was created in Logger UC-REQUESTER"
        #print("UC-REQUESTER: " + console_output)
        logger.info(console_output)
        return logger


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