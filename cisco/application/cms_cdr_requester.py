import xmltodict
from pprint import pprint
import time
import datetime
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.sqlrequests import cm_sqlselect,cms_sql_request

def callleginfo(callleg_id,cms_ip):
    # auth data
    cms_login = cm_sqlselect("login", "cms_servers", "ip", cms_ip)
    cms_password = cm_sqlselect("password", "cms_servers", "ip", cms_ip)
    cms_port = cm_sqlselect("api_port", "cms_servers", "ip", cms_ip)

    # URL
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/callLegs/" + callleg_id
    print("CMS Rq: URL: "+ http_url)
    http_headers = {'Content-Type': 'text/xml'}
    #print("We use IP: " + cms_ip + " login: " + cms_login + " Password: " + cms_password)
	#запускаем цикл
    while True:
     timenow = str(datetime.datetime.now())
     try:
        get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
     except requests.exceptions.ConnectionError:
        print("CMS Rq:  Server connection error " + cms_ip)
        break
     except:
        print("CMS Rq: Auth by " + cms_login + " to server " + cms_ip + " error")
        break

     if get.status_code == 401:
        console_output = "CMS Rq: User " + cms_login + " deny by " + cms_ip
        print(console_output)
        break

     if get.status_code != 200:
        console_output = "CMS Rq: Connect error: " + str(get.status_code) + ": " + get.reason
        print(console_output)
        break
     print("CMS Rq: we parse dict")
     xml_dict = xmltodict.parse(get.text)
     cdr_dict = json.loads(json.dumps(xml_dict))  # trasfrorm OrderedDict to Dict
     callleg_id = str(cdr_dict['callLeg']['@id'])  # забираем callleg ID
     print("CMS Rq: we get " + callleg_id)

     # забираем callleg ID
     if "call" in cdr_dict['callLeg']:
        call_id = str(cdr_dict['callLeg']['call'])
     else:
        call_id="none"

     # забираем информацию по Аудио
     if "rxAudio" in cdr_dict['callLeg']['status']:

       if "packetLossPercentage" in cdr_dict['callLeg']['status']['rxAudio']:
            AudioPacketLossPercentageRX = str(cdr_dict['callLeg']['status']['rxAudio']['packetLossPercentage'])
       else:
            AudioPacketLossPercentageRX = "0.0"
     else:
        AudioPacketLossPercentageRX = "0.0"
     if "txAudio" in cdr_dict['callLeg']['status']:
       if "packetLossPercentage" in cdr_dict['callLeg']['status']['txAudio']:
            AudioPacketLossPercentageTX = str(cdr_dict['callLeg']['status']['txAudio']['packetLossPercentage'])
       else:
            AudioPacketLossPercentageTX = "0.0"
       if "roundTripTime" in cdr_dict['callLeg']['status']['txAudio']:
            AudioRoundTripTimeTX = str(cdr_dict['callLeg']['status']['txAudio']['roundTripTime'])
       else:
            AudioRoundTripTimeTX = "0"
     else:
       AudioPacketLossPercentageTX = "0.0"
       AudioRoundTripTimeTX = "0"



     # забираем информацию по Видео
     if "rxVideo" in cdr_dict['callLeg']['status']:
       if "packetLossPercentage" in cdr_dict['callLeg']['status']['rxVideo']:
            VideoPacketLossPercentageRX = str(cdr_dict['callLeg']['status']['rxVideo']['packetLossPercentage'])
       else:
            VideoPacketLossPercentageRX = "0.0"
     else:
         VideoPacketLossPercentageRX = "0.0"

     if "txVideo" in cdr_dict['callLeg']['status']:
       if "packetLossPercentage" in cdr_dict['callLeg']['status']['txVideo']:
            VideoPacketLossPercentageTX = str(cdr_dict['callLeg']['status']['txVideo']['packetLossPercentage'])
       else:
            VideoPacketLossPercentageTX = "0.0"
       if "roundTripTime" in cdr_dict['callLeg']['status']['txVideo']:
            VideoRoundTripTimeTX = str(cdr_dict['callLeg']['status']['txVideo']['roundTripTime'])
       else:
            VideoRoundTripTimeTX = "0"
     else:
       VideoPacketLossPercentageTX = "0.0"
       VideoRoundTripTimeTX = "0"


     print("CMS Rq: CallID:"+callleg_id + " insert to database")
     cms_sql_request(
		"INSERT INTO cms_cdr_calllegs SET callleg_id='" + callleg_id + "',cms_node='" + cms_ip + "',date='" + timenow + "',call_id='" + call_id + "',VideoRoundTripTimeTX='" + VideoRoundTripTimeTX + "',VideoPacketLossPercentageTX='" + VideoPacketLossPercentageTX + "',VideoPacketLossPercentageRX='" + VideoPacketLossPercentageRX + "',AudioPacketLossPercentageRX='" + AudioPacketLossPercentageRX + "',AudioPacketLossPercentageTX='" + AudioPacketLossPercentageTX + "',AudioRoundTripTimeTX='" + AudioRoundTripTimeTX + "';")
     #pprint(cdr_dict)
     #print("CMS RQ: data inserted")

     #ждем повторения цикла
     time.sleep(10)
     # удаляем данные из базы старше 30 дней.
     cms_sql_request(
	 "DELETE FROM cms_cdr_calllegs WHERE date < (NOW() - INTERVAL 30 DAY)")

    return "end of call"