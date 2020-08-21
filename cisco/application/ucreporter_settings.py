from application.forms import SelectNavigation,UserInformation,CUCMServerInformation,CMSServerInformation
from datetime import datetime
from application.sqlrequests import sql_request_dict,sql_execute
from pprint import pprint
import subprocess

def run_linux_command(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

#отрировка главной странички
def ucreporter_settings_mainpage():
	operationStartTime = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'UC Reporter administration'

	form_navigation = SelectNavigation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	operationEndTime = datetime.now()
	operationDuration = str(operationEndTime - operationStartTime)
	console_output = "Done in " + operationDuration

	content_type = "main_page"
	renderdata = {
		"rendertype": "success",
		"content_type": content_type,
		"html_template": "ucreporter_settings_mainpage.html",
		"html_page_title": html_page_title,
		"html_page_header": html_page_header,
		"console_output": console_output,
		"form_navigation": form_navigation,
	}
	return renderdata

#страница настроек пользователей
def ucreporter_settings_users(user_id):
	operationStartTime = datetime.now()
	html_page_title = 'UC Reporter administration '
	html_page_header = 'User administration'
	form_navigation = SelectNavigation(meta={'csrf': False})
	form_edit_user = UserInformation(meta={'csrf': False})


	#нажака нопка перехода на другую страницу
	if form_navigation.validate_on_submit():
		renderdata = {
			"content_type": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	#нажака нопка SAVE
	if form_edit_user.validate_on_submit():
		# запрашиваем ID в базе
		sql_request_result_string = "SELECT * FROM ucreporter_users WHERE id=" + str(form_edit_user.id_field.text) + ";"
		save_data = sql_request_dict(sql_request_result_string)
		pprint(save_data)
		# если запрос пустой, создаем запись.
		if not save_data:
			sql_execute(
				"INSERT INTO ucreporter_users SET id=" + str(form_edit_user.id_field.text)
				+ ",password='" + form_edit_user.Password_field.data
				+ "',password_hash='" + form_edit_user.Password_field.data
				+ "',description='" + form_edit_user.Descriotion_field.data
				+ "',username='" + form_edit_user.UserName_field.data
				+ "';")
		else:
			sql_execute(
				"UPDATE ucreporter_users SET password='" + form_edit_user.Password_field.data
				+ "',password_hash='" + form_edit_user.Password_field.data
				+ "',description='" + form_edit_user.Descriotion_field.data
				+ "',username='" + form_edit_user.UserName_field.data
				+ "' WHERE id=" + str(form_edit_user.id_field.text)
				+ ";")
		# переходим на список
		renderdata = {
			"content_type": "redirect",
			"redirect_to": "platform_users"
		}
		return renderdata




	if user_id:
		if user_id == "AddNew":
			#Новый пользователь, считаем номер нового ID
			sql_request_result_string = "SELECT MAX(id) FROM ucreporter_users;" #забираем максимальный
			rows_list = sql_request_dict(sql_request_result_string)
			#заполняем форму
			index_data = int(rows_list[0]['MAX(id)']) + 1
			form_edit_user.id_field.text = index_data
			form_edit_user.UserName_field.data = str("username")
			form_edit_user.Password_field.data = str("password")
			form_edit_user.Descriotion_field.data = str("description")
		else:
			sql_request_result_string = "SELECT * FROM ucreporter_users WHERE id="+user_id+";"
			rows_list = sql_request_dict(sql_request_result_string)
			#заполняем форму
			form_edit_user.id_field.text = (rows_list[0]['id'])
			form_edit_user.UserName_field.data = str(rows_list[0]['username'])
			form_edit_user.Password_field.data = str(rows_list[0]['password'])
			form_edit_user.Descriotion_field.data = str(rows_list[0]['description'])

		if rows_list:
			content_type = "user_edit"
			operationEndTime = datetime.now()
			operationDuration = str(operationEndTime - operationStartTime)
			console_output = "Done in " + operationDuration
			renderdata = {
				"content_type": content_type,
				"html_template": "ucreporter_settings_mainpage.html",
				"html_page_title": html_page_title,
				"html_page_header": html_page_header,
				"console_output": console_output,
                "form_edit_user":form_edit_user,
				"rows_list": rows_list,
				"form_navigation": form_navigation,
			}
			return renderdata

	else:
		sql_request_result_string = "SELECT * FROM ucreporter_users;"
		rows_list = sql_request_dict(sql_request_result_string)


		content_type = "user_list"
		operationEndTime = datetime.now()
		operationDuration = str(operationEndTime - operationStartTime)
		console_output = "Done in " + operationDuration
		renderdata = {
			"content_type": content_type,
			"html_template": "ucreporter_settings_mainpage.html",
			"html_page_title": html_page_title,
			"html_page_header": html_page_header,
			"console_output": console_output,
			"form_edit_user": form_edit_user,
			"rows_list": rows_list,
			"form_navigation": form_navigation,
		}
		return renderdata


	operationEndTime = datetime.now()
	operationDuration = str(operationEndTime - operationStartTime)
	console_output = "Done in " + operationDuration
	content_type = "main_page"
	renderdata = {
		"content_type": content_type,
		"html_template": "ucreporter_settings_mainpage.html",
		"html_page_title": html_page_title,
		"html_page_header": html_page_header,
		"console_output": console_output,
		"form_navigation": form_navigation,
	}
	return renderdata

#страница настроек CMS
def ucreporter_settings_CMSservers(server_id):
	operationStartTime = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'CMS administration'

	form_navigation = SelectNavigation(meta={'csrf': False})
	form_CMS_server = CMSServerInformation(meta={'csrf': False})
	form_addnew = DeleteForm(meta={'csrf': False})
	form_delete = AddNewForm(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		renderdata = {
			"content_type": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata


	if server_id:
		sql_request_result_string = "SELECT * FROM cms_servers WHERE id=" + server_id + ";"
		rows_list = sql_request_dict(sql_request_result_string)
		if rows_list:
			#заполняем форму
			form_CMS_server.API_Port_field.data = str(rows_list[0]['api_port'])
			form_CMS_server.ip_field.data = str(rows_list[0]['ip'])
			form_CMS_server.cluster_field.data = str(rows_list[0]['cluster'])
			form_CMS_server.password_field.data = str(rows_list[0]['password'])
			form_CMS_server.username_field.data = str(rows_list[0]['login'])

			content_type = "cms_server_edit"
			operationEndTime = datetime.now()
			operationDuration = str(operationEndTime - operationStartTime)
			console_output = "Done in " + operationDuration
			renderdata = {
				"content_type": content_type,
				"html_template": "ucreporter_settings_mainpage.html",
				"html_page_title": html_page_title,
				"html_page_header": html_page_header,
				"console_output": console_output,
				"form_CMS_server": form_CMS_server,
				"form_addnew": form_addnew,
				"form_delete": form_delete,
				"rows_list": rows_list,
				"form_navigation": form_navigation,
			}
			return renderdata
#отрисовка данных списка серверов в случае, если не пришел ID сервера.
	else:
		sql_request_result_string = "SELECT * FROM cms_servers;"
		rows_list = sql_request_dict(sql_request_result_string)
		content_type = "cms_server_list"
		operationEndTime = datetime.now()
		operationDuration = str(operationEndTime - operationStartTime)
		console_output = "Done in " + operationDuration
		renderdata = {
			"content_type": content_type,
			"html_template": "ucreporter_settings_mainpage.html",
			"html_page_title": html_page_title,
			"html_page_header": html_page_header,
			"console_output": console_output,
			"form_CMS_server": form_CMS_server,
			"form_addnew": form_addnew,
			"form_delete": form_delete,
			"rows_list": rows_list,
			"form_navigation": form_navigation,
		}
		return renderdata

#страница настроек CUCM
def ucreporter_settings_CUCMservers(server_id):
	operationStartTime = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'CUCM Server administration'

	form_navigation = SelectNavigation(meta={'csrf': False})
	form_CUCM_server = CUCMServerInformation(meta={'csrf': False})

	if form_navigation.validate_on_submit():
		renderdata = {
			"content_type": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	#отрисовка страницы изменения серверов.
	if server_id:
		if server_id == "AddNew":
			#Новый пользователь, считаем номер нового ID
			sql_request_result_string = "SELECT MAX(id) FROM ucreporter_users;" #забираем максимальный
			rows_list = sql_request_dict(sql_request_result_string)
			#заполняем форму
			index_data = int(rows_list[0]['MAX(id)']) + 1
			form_CUCM_server.id_field.text = index_data
			form_CUCM_server.Cluster_field.data = str(rows_list[0]['cluster'])
			form_CUCM_server.username_field.data = str(rows_list[0]['cm_username'])
			form_CUCM_server.ip_field.data = str(rows_list[0]['cm_ip'])
			form_CUCM_server.password_field.data = str(rows_list[0]['cm_password'])
		else:
			sql_request_result_string = "SELECT * FROM cm_servers_list WHERE id=" + server_id + ";"
			rows_list = sql_request_dict(sql_request_result_string)
			# заполняем форму
			form_CUCM_server.id_field.text = str(rows_list[0]['id'])
			form_CUCM_server.Cluster_field.data = str(rows_list[0]['cluster'])
			form_CUCM_server.username_field.data = str(rows_list[0]['cm_username'])
			form_CUCM_server.ip_field.data = str(rows_list[0]['cm_ip'])
			form_CUCM_server.password_field.data = str(rows_list[0]['cm_password'])

		if rows_list:
			content_type = "cucm_server_edit"
			operationEndTime = datetime.now()
			operationDuration = str(operationEndTime - operationStartTime)
			console_output = "Done in " + operationDuration
			renderdata = {
				"content_type": content_type,
				"html_template": "ucreporter_settings_mainpage.html",
				"html_page_title": html_page_title,
				"html_page_header": html_page_header,
				"console_output": console_output,
				"form_CUCM_server": form_CUCM_server,
				"rows_list": rows_list,
				"form_navigation": form_navigation,
			}
			return renderdata


		# отрисовка данных списка серверов в случае, если не пришел ID сервера.
	else:
		sql_request_result_string = "SELECT * FROM cm_servers_list;"
		rows_list = sql_request_dict(sql_request_result_string)
		content_type = "cucm_server_list"
		operationEndTime = datetime.now()
		operationDuration = str(operationEndTime - operationStartTime)
		console_output = "Done in " + operationDuration
		renderdata = {
			"content_type": content_type,
			"html_template": "ucreporter_settings_mainpage.html",
			"html_page_title": html_page_title,
			"html_page_header": html_page_header,
			"form_CUCM_server": form_CUCM_server,
			"console_output": console_output,
			"rows_list": rows_list,
			"form_navigation": form_navigation,
		}
		return renderdata

def ucreporter_settings_ucrequester(server_id):
	operationStartTime = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'UC Requester administration'

	form_navigation = SelectNavigation(meta={'csrf': False})
	form_edit_server = CUCMServerInformation(meta={'csrf': False})

	if form_navigation.validate_on_submit():
		renderdata = {
			"content_type": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	#отрисовка страницы изменения серверов.
	if server_id:
		sql_request_result_string = "SELECT * FROM cms_requester_config WHERE id=" + server_id + ";"
		rows_list = sql_request_dict(sql_request_result_string)
		# заполняем форму
		pprint(rows_list)
		form_edit_server.Cluster_field.data = str(rows_list[0]['cluster'])
		form_edit_server.username_field.data = str(rows_list[0]['cm_username'])
		form_edit_server.ip_field.data = str(rows_list[0]['cm_ip'])
		form_edit_server.password_field.data = str(rows_list[0]['cm_password'])

		if rows_list:
			content_type = "cucm_server_edit"
			operationEndTime = datetime.now()
			operationDuration = str(operationEndTime - operationStartTime)
			console_output = "Done in " + operationDuration
			renderdata = {
				"content_type": content_type,
				"html_template": "ucreporter_settings_mainpage.html",
				"html_page_title": html_page_title,
				"html_page_header": html_page_header,
				"console_output": console_output,
				"form_edit_server": form_edit_server,
				"rows_list": rows_list,
				"form_navigation": form_navigation,
			}
			return renderdata


		# отрисовка данных списка серверов в случае, если не пришел ID сервера.
	else:
		sql_request_result_string = "SELECT * FROM cms_requester_config;"
		rows_list = sql_request_dict(sql_request_result_string)
		content_type = "requester_server_list"
		operationEndTime = datetime.now()
		operationDuration = str(operationEndTime - operationStartTime)
		console_output = "Done in " + operationDuration
		renderdata = {
			"content_type": content_type,
			"html_template": "ucreporter_settings_mainpage.html",
			"html_page_title": html_page_title,
			"html_page_header": html_page_header,
			"console_output": console_output,
			"rows_list": rows_list,
			"form_navigation": form_navigation,
		}
		return renderdata

