import xmltodict
from pprint import pprint
from datetime import datetime
import time
import logging.handlers
from application.sqlrequests import sql_request_dict
from application.forms import SelectNavigation, SelectCMSClusterForCospace

def cms_cospace_usage():
	rows_list = []
	# Настройка логирования
	CMS_RECEIVER_LOG_FILE_NAME = "../logs/CMS_COSPACE_USAGE.log"
	CMS_RECEIVER_LOG_FILE_SIZE = 2048000
	CMS_RECEIVER_LOG_FILE_COUNT = 5

	# Диспетчер логов
	logger = logging.getLogger('CMS_COSPACE_USAGE')
	logger.setLevel(logging.DEBUG)

	# Обработчик логов - запись в файлы с перезаписью
	if not logger.handlers:
		console_output = ": no any handlers in Logger - create new one"
		print("CMS_COSPACE_USAGE " + console_output)



		rotate_file_handler = logging.handlers.RotatingFileHandler(CMS_RECEIVER_LOG_FILE_NAME,
																   maxBytes=CMS_RECEIVER_LOG_FILE_SIZE,
																   backupCount=CMS_RECEIVER_LOG_FILE_COUNT)
		rotate_file_handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
		rotate_file_handler.setFormatter(formatter)
		logger.addHandler(rotate_file_handler)

	operation_start_time = datetime.now()
	html_page_title = 'CMS CoSpace Usage Report'
	form_cmsselection = SelectCMSClusterForCospace(csrf_enabled=False)
	form_navigation = SelectNavigation(csrf_enabled=False)
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		logger.debug(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	if form_cmsselection.validate_on_submit():
			sql_request_result_string_mounth = """SELECT cms_cdr_calls.Name,COUNT(cms_cdr_calls.Name) AS count_mounth,
			  SUM(cms_cdr_calls.durationSeconds) AS duration_mounth FROM cms_cdr_calls
			  INNER JOIN  cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip 
			  WHERE cms_cdr_calls.StartTime >= DATE(NOW()) - INTERVAL 30 DAY AND cms_servers.cluster 
			  LIKE '"""+ form_cmsselection.select_CMSCluster.data +"""' AND NAME NOT LIKE 'Сове%' GROUP BY NAME ORDER BY NAME"""

			sql_request_result_string_last_week = """SELECT cms_cdr_calls.Name,COUNT(cms_cdr_calls.Name) AS count_last_week,
				SUM(cms_cdr_calls.durationSeconds) AS duration_last_week FROM cms_cdr_calls
				INNER JOIN  cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip 
				WHERE cms_cdr_calls.StartTime >= DATE(NOW()) - INTERVAL 7 DAY AND cms_servers.cluster 
				LIKE '""" + form_cmsselection.select_CMSCluster.data + """' AND NAME NOT LIKE 'Сове%' AND NAME NOT LIKE 'none' GROUP BY NAME ORDER BY NAME"""


			#Словарь с данными за месяц
			rows_list_mounth = sql_request_dict(sql_request_result_string_mounth)
			#перевести секунды в часы

			for row in rows_list_mounth:
				if row["duration_mounth"]:
						row["duration_mounth"] = round((int(row["duration_mounth"]) / 3600),1)

			# Словарь с данными за неделю
			rows_list_last_week = sql_request_dict(sql_request_result_string_last_week)
			# перевести секунды в часы
			for row in rows_list_last_week:
				if row["duration_last_week"]:
					row["duration_last_week"] = round((int(row["duration_last_week"]) /3600),1)


			rows_list = rows_list_mounth
			for row in rows_list:
				for key in rows_list_last_week:
					if row["Name"] == key["Name"]:
						if key["count_last_week"]:
							row["duration_last_week"] = key["duration_last_week"]
							row["count_last_week"] = key["count_last_week"]

			operation_end_time = datetime.now()
			operation_duration = str( operation_end_time - operation_start_time)
			console_output = "Done in " + operation_duration
			logger.debug(console_output)
			renderdata = {
				"rendertype": "success",
				"html_template": "cisco_cms_cospace_usage.html",
				"html_page_title": html_page_title,
				"console_output": console_output,
				"form_navigation": form_navigation,
				"form_cmsselection": form_cmsselection,
				"rows_list": rows_list
			}
			return renderdata

	operation_end_time = datetime.now()
	operation_duration = str( operation_end_time - operation_start_time)
	console_output = "Нет активного запроса (" + operation_duration + ")"
	logger.debug(console_output)

	renderdata = {
		"rendertype": "Null",
		"html_template": "cisco_cms_cospace_usage.html",
		"html_page_title": html_page_title,
		"console_output": console_output,
		"form_navigation": form_navigation,
		"form_cmsselection": form_cmsselection
	}
	return renderdata