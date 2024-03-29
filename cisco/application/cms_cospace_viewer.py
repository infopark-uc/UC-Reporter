from flask import Flask, request, render_template, redirect, url_for
import xmltodict
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
from collections import OrderedDict
from datetime import datetime
from pprint import pprint
from pprint import pformat
import logging.handlers
from application.sqlrequests import cms_sql_request,cm_sqlselect_dict,cm_sqlupdate,cms_sql_request_dict
from application.forms import SelectNavigation, SelectCMSClusterForCospace
from flask_login import current_user


def cms_webrequest(http_url,cms_ip,cms_login,cms_password):
	http_headers = {'Content-Type': 'text/xml'}
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # отключаем алерты на сертификаты
	try:
		get = requests.get(http_url, headers=http_headers, verify=False, auth=(cms_login, cms_password))
	except requests.exceptions.ConnectionError:
		console_output = cms_ip + ":  Server connection error " + cms_ip
		print(console_output)  # info
		get.close()
		return
	except requests.exceptions.RequestException as err:
		console_output = cms_ip + ": Error Something Else" + str(err)
		print(console_output)  # info
		get.close()
		return  # закрываем функцию т.к. мы не знаем что это такое, если бы мы знали, что это такое, мы не знаем, что это такое.

	if get.status_code == 401:
		console_output = cms_ip + ": User " + cms_login + " deny by " + cms_ip
		print(console_output)  # info

		get.close()
		return  # закрываем функцию, т.к. можно заблочить пользователя на длительный срок.

	if get.status_code != 200:
		console_output = cms_ip + ": Connect error: " + str(get.status_code) + ": " + get.reason
		print(console_output)  # info

		get.close()
		return

	result = get.text
	get.close()  # закрываем web сессию
	return result

def cms_cospace_detail(cospace_id,cms_login,cms_password,cms_ip,cms_port):
	http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/coSpaces/" + cospace_id
	console_output = cms_ip + ": URL: " + http_url
	#print(console_output)  # debug
	xml_dict = xmltodict.parse(cms_webrequest(http_url,cms_ip,cms_login,cms_password))
	result = xml_dict['coSpace']
	#pprint(result)
	return result

def cms_cospace_view():
	page_offset = 0
	page_limit = 10
	CoSpace_list = []
	rows_list = []

	# Настройка логирования
	CMS_RECEIVER_LOG_FILE_NAME = "../logs/CMS_COSPACE_VIEWER.log"
	CMS_RECEIVER_LOG_FILE_SIZE = 2048000
	CMS_RECEIVER_LOG_FILE_COUNT = 5

	# Диспетчер логов
	logger = logging.getLogger('CMS_COSPACE_VIEWER')
	#
	logger.setLevel(logging.DEBUG)

	# Обработчик логов - запись в файлы с перезаписью
	if not logger.handlers:
		console_output = ": no any handlers in Logger - create new one"
		print("CMS_COSPACE_VIEWER " + console_output)



		rotate_file_handler = logging.handlers.RotatingFileHandler(CMS_RECEIVER_LOG_FILE_NAME,
																   maxBytes=CMS_RECEIVER_LOG_FILE_SIZE,
																   backupCount=CMS_RECEIVER_LOG_FILE_COUNT)
		rotate_file_handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
		rotate_file_handler.setFormatter(formatter)
		logger.addHandler(rotate_file_handler)

	operationStartTime = datetime.now()
	html_page_title = 'CMS CoSpace Report'
	html_template = 'cisco_cms_cospaceview.html'

	form_navigation = SelectNavigation(csrf_enabled=False)
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		#print(console_output)
		logger.debug(console_output)
		return redirect(url_for(form_navigation.select_navigation.data))

	form_cmsselection = SelectCMSClusterForCospace(csrf_enabled=False)
	if form_cmsselection.validate_on_submit():
			cluster_config = cms_sql_request_dict(
				"SELECT DISTINCT login,password,ip,api_port FROM cms_servers WHERE cluster='" + form_cmsselection.select_CMSCluster.data + "' LIMIT 1;")
			console_output = "get config from SQL"
			print(console_output)
			logger.debug(console_output)

			cms_ip=cluster_config[0]['ip']
			cms_port=cluster_config[0]['api_port']
			cms_login=cluster_config[0]['login']
			cms_password=cluster_config[0]['password']
			endOfCycle = False
			while not endOfCycle:   #запускаем цикл получения списка спейсов
				#формируем сслыку на опрос
				http_url = "https://" + cms_ip + ":" + cms_port + "/api/v1/coSpaces?limit=" + str(
					page_limit) + "&offset=" + str(page_offset)
				console_output = cms_ip + ": URL: " + http_url
				print(console_output)  # debug
				logger.debug(console_output)
				xml_dict = xmltodict.parse(cms_webrequest(http_url,cms_ip,cms_login,cms_password))
				total_coSpaces = xml_dict["coSpaces"]["@total"]
				console_output = cms_ip + ": Total number of CallLegs: " + total_coSpaces
				#print(console_output)  # debug
				logger.debug(console_output)


				# проверям что есть coSpace
				if "coSpace" in xml_dict["coSpaces"]:
					# Проверяем тип list или OrderedDict для выбора корректного способа добавления в общий список
					if type(xml_dict["coSpaces"]["coSpace"]) is OrderedDict:
						CoSpace_list.append(xml_dict["coSpaces"]["coSpace"])
						console_output = cms_ip + ": Number of CoSpace from current request: 1"
						#print(console_output)  # debug
						logger.debug(console_output)

					elif type(xml_dict["coSpaces"]["coSpace"]) is list:
						CoSpace_list.extend(xml_dict["coSpaces"]["coSpace"])
						console_output = cms_ip + ": Number of CoSpace from current request: " + str(
							len(xml_dict["coSpaces"]["coSpace"]))
						#print(console_output)  # debug
						logger.debug(console_output)

				console_output = cms_ip + ": Number of collected CoSpace: " + str(len(CoSpace_list))
				#print(console_output)  # debug
				logger.debug(console_output)

				#закрываем цикл
				if int(total_coSpaces) > len(CoSpace_list):
					page_offset = len(CoSpace_list)
					endOfCycle = False
				else:
					endOfCycle = True
					#pprint(CoSpace_list)
			# перебираем все активные callLeg
			for CoSpace in CoSpace_list:
				# забираем CoSpace ID, собираем rows_list
				if "@id" in CoSpace:
					CoSpace_id = CoSpace["@id"]
					rows_list.append(cms_cospace_detail(CoSpace_id,cms_login,cms_password,cms_ip,cms_port))

			operationEndTime = datetime.now()
			operationDuration = str( operationEndTime - operationStartTime)
			console_output = "Done in " + operationDuration
			logger.debug(console_output)
			return render_template(html_template, html_page_title=html_page_title,
			                       console_output=console_output,
			                       rows_list=rows_list,
			                       formNAV=form_navigation,
			                       formCMS=form_cmsselection)

	operationEndTime = datetime.now()
	operationDuration = str( operationEndTime - operationStartTime)
	console_output = "Нет активного запроса (" + operationDuration + ")"
	logger.debug(console_output)

	return render_template(html_template, html_page_title=html_page_title,
	                       console_output=console_output,
	                       formNAV=form_navigation,
	                       formCMS=form_cmsselection)