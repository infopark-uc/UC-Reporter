from flask import Flask, abort, request
import xmltodict
from pprint import pprint
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
#from application.sqlrequests import cm_sqlselect, cm_sqlselectall, cm_sqlupdate
from sqlrequests import cm_sqlselect

def callleginfo(calllegid,cms_ip):
	# URL
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

	# auth data
	cms_password = cm_sqlselect("password", "cms_servers", "ip", cms_ip)
	cms_login = cm_sqlselect("login", "cms_servers", "ip", cms_ip)
	cms_port = cm_sqlselect("api_port", "cms_servers", "ip", cms_ip)
	http_url = "http://" + cms_ip + ":" + cms_port + "/api/v1/callLegs/" + calllegid
	http_headers = {'Content-Type': 'text/xml'}
	print("We use IP: " + cms_ip + " login: " + cms_login + " Password: " + cms_password)

	try:
		get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
	except requests.exceptions.ConnectionError:
		console_output = "CMS Rq:  Server connection error " + cms_ip
		print(console_output)
		return "CMS RQ: connection error"
	except:
		console_output = "CMS Rq: Auth by " + roomkit_access_data_login + " to server " + roomkit_access_data_ip + " error"
		print(console_output)
		return "CMS RQ: login fail"

	xml_dict = xmltodict.parse(get.text)
	pprint(xml_dict)

	return "data inserted"



callleginfo("17d8e887-4465-4d6e-b1eb-bbd42e872140","10.250.62.18")