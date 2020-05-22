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


def sqlselect_dict(sqlrequest):
    con = pymysql.connect('172.20.31.50', 'sqladmin', 'Qwerty123', 'ucreporter', cursorclass=pymysql.cursors.DictCursor)
    with con:
        cur = con.cursor()
        cur.execute(sqlrequest)
        result = cur.fetchall()
        cur.close()  # закрываем курсор
    con.close() # закрываем соединение
    return result

def sqlrequest_dict(sqlrequest):
    try:
        con = pymysql.connect('172.20.31.50', 'sqladmin', 'Qwerty123', 'ucreporter')
    except:
        print("CMS Rq MySQL: DB access error")
        return None
    with con:
        cur = con.cursor()
        cur.execute(sqlrequest)
        cur.close()  # закрываем курсор
    con.close() # закрываем соединение
    return "Request to database done"


def callleginfo(callleg_id,cms_ip,cms_login,cms_password,cms_port):
    # auth data
    #cms_login = sqlselect("login", "cms_servers", "ip", cms_ip)
    #cms_password = sqlselect("password", "cms_servers", "ip", cms_ip)
    #cms_port = sqlselect("api_port", "cms_servers", "ip", cms_ip)

    # URL
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/callLegs/" + callleg_id
    print("CMS Rq " + cms_ip + ": URL: "+ http_url)

    http_headers = {'Content-Type': 'text/xml'}

    timenow = str(datetime.datetime.now())
    try:
       get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
    except requests.exceptions.ConnectionError:
        print("CMS Rq " + cms_ip + ":  Server connection error " + cms_ip)
        return
    except:
        print("CMS Rq: Auth by " + cms_login + " to server " + cms_ip + " error")
        return

    if get.status_code == 401:
        console_output = "CMS Rq " + cms_ip + ": User " + cms_login + " deny by " + cms_ip
        print(console_output)
        return

    if get.status_code != 200:
        console_output = "CMS Rq " + cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
        print(console_output)
        return

    print("CMS Rq: we got dict with callLegs")
    xml_dict = xmltodict.parse(get.text)
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

    print("CMS Rq: CallID:"+callleg_id + " insert to database")
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


def getCallLegs(cms_ip):
    # auth data
    #cms_login = sqlselect("login", "cms_servers", "ip", cms_ip)
    #cms_password = sqlselect("password", "cms_servers", "ip", cms_ip)
    #cms_port = sqlselect("api_port", "cms_servers", "ip", cms_ip)

    auth_data_dict = sqlselect_dict("SELECT login,password,api_port FROM cms_servers WHERE ip='" + cms_ip + "'") #получаем лист словарей
    auth_data = auth_data_dict[0] # делаем из листа словарь

    cms_login = str(auth_data['login'])
    cms_password = str(auth_data['password'])
    cms_port = str(auth_data['api_port'])

    if (cms_login is None) or (cms_password is None) or (cms_port is None):
        print("CMS Rq " + cms_ip + ": Login, password and port not received")
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
            #http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/coSpaces?limit=" + str(page_limit) + "&offset=" + str(page_offset)
            print("CMS Rq " + cms_ip + ": URL: " + http_url)

            try:
                get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
            except requests.exceptions.ConnectionError:
                print("CMS Rq " + cms_ip + ":  Server connection error " + cms_ip)
                break
            except:
                print("CMS Rq " + cms_ip + ": Auth by " + cms_login + " to server " + cms_ip + " error")
                break

            if get.status_code == 401:
                console_output = "CMS Rq " + cms_ip + ": User " + cms_login + " deny by " + cms_ip
                print(console_output)
                break

            if get.status_code != 200:
                console_output = "CMS Rq " + cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
                print(console_output)
                break
            print("CMS Rq " + cms_ip + ": we got dict with calls")
            xml_dict = xmltodict.parse(get.text)
            totalCallLegs = xml_dict["callLegs"]["@total"]
            #totalCallLegs = xml_dict["coSpaces"]["@total"]
            print("CMS Rq " + cms_ip + ": Total number of CallLegs: " + totalCallLegs)


#            if "coSpace" in xml_dict["coSpaces"]:
#                if type(xml_dict["coSpaces"]["coSpace"]) is OrderedDict:
#                    callLeg_list.append(xml_dict["coSpaces"]["coSpace"])
#                    print("CMS Rq: Number of CallLegs from current request: 1")
#                elif type(xml_dict["coSpaces"]["coSpace"]) is list:
#                    callLeg_list.extend(xml_dict["coSpaces"]["coSpace"])
#                    print("CMS Rq: Number of CallLegs from current request: " + str(len(xml_dict["coSpaces"]["coSpace"])))

            # проверям что есть активные CallLeg
            if "callLeg" in xml_dict["callLegs"]:
                # Проверяем тип list или OrderedDict для выбора корректного способа добавления в общий список
                if type(xml_dict["callLegs"]["callLeg"]) is OrderedDict:
                    callLeg_list.append(xml_dict["callLegs"]["callLeg"])
                    print("CMS Rq " + cms_ip + ": Number of CallLegs from current request: 1")
                elif type(xml_dict["callLegs"]["callLeg"]) is list:
                    callLeg_list.extend(xml_dict["callLegs"]["callLeg"])
                    print("CMS Rq " + cms_ip + ": Number of CallLegs from current request: " + str(len(xml_dict["callLegs"]["callLeg"])))

            print("CMS Rq " + cms_ip + ": Number of collected CallLegs: " + str(len(callLeg_list)))

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
            else:
                callLeg_id = "none"

        time.sleep(2)

def main(argv):

    try:
        opts, args = getopt.getopt(argv, 's:')
        for opt,val in opts:
            if opt=='-s':
                cms_ip_address = val

    except:
        print ('usage: ucrequester.py -s <CMS ip address>')
        sys.exit(2)

    getCallLegs(cms_ip_address)


if __name__ == "__main__":
    if not sys.version_info.major == 3 and sys.version_info.minor >= 5:
        print("CMS Rq " + cms_ip + ": Python 3.5 is needed!")
        print("CMS Rq " + cms_ip + ": You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
        sys.exit(1)

    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        print('usage: ucrequester.py -s <CMS ip address>')