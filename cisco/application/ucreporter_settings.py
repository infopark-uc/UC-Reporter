from application.forms import SelectNavigation, UserInformation, CUCMServerInformation, \
	CMSServerInformation
from datetime import datetime
from flask import render_template, redirect, url_for
from application.sqlrequests import sql_request_dict, sql_execute
from application.database import UCReporterUsersTableClass,CmsServerTableClass,CmServerListTableClass
from pprint import pprint
from application import db

def ucreporter_settings_mainpage():
	"""отрировка главной странички

	:return:
	"""
	operation_start_time = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'UC Reporter administration'
	form_navigation = SelectNavigation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		return redirect(url_for(form_navigation.select_navigation.data))

	operation_end_time = datetime.now()
	operation_duration = str(operation_end_time - operation_start_time)
	console_output = "Done in " + operation_duration
	content_type = "main_page"

	return render_template('ucreporter_settings_mainpage.html',
	                       html_page_title=html_page_title,
	                       html_page_header=html_page_header,
	                       content_type= content_type,
	                       console_output = console_output,
	                       formNAV = form_navigation)

def ucreporter_settings_users(user_id):
	"""страница настроек пользователей

	:param user_id: ID пользователя
	:return:
	"""
	operation_start_time = datetime.now()
	html_page_title = 'UC Reporter administration '
	html_page_header = 'User administration'
	form_navigation = SelectNavigation(meta={'csrf': False})
	form_edit_user = UserInformation(meta={'csrf': False})

	# нажака нопка перехода на другую страницу
	if form_navigation.validate_on_submit():
		return redirect(url_for(form_navigation.select_navigation.data))

	# нажака нопка SAVE
	if form_edit_user.validate_on_submit():
		# запрашиваем ID в базе
		try:
			save_data = UCReporterUsersTableClass.query.get(form_edit_user.id_field.text)
		except:
			save_data = False

		# если запрос пустой, создаем запись.
		if not save_data:

			insert_data = UCReporterUsersTableClass(
				id = form_edit_user.id_field.text,
				username = form_edit_user.UserName_field.data,
				password = form_edit_user.Password_field.data,
				password_hash = form_edit_user.Password_field.data,
				description = form_edit_user.Description_field.data
			)
			try:
				db.session.add(insert_data)
				db.session.commit()
			except:
				console_output = "error insert User to SQL"



		else:
			#забираем пользователя по ID для обнновления
			#обновляем данные
			save_data.username = form_edit_user.UserName_field.data
			save_data.description = form_edit_user.Description_field.data
			save_data.password = form_edit_user.Password_field.data
			save_data.password_hash = form_edit_user.Password_field.data
			#вносим изменения в базу
			try:
				db.session.add(save_data)
				db.session.commit()
				console_output = "update done"
			except:
				console_output = "error update"


		# переходим на список
		return redirect(url_for('platform_users'))

	if user_id:
		if user_id == "AddNew":
			# Новый пользователь, считаем номер нового ID

			#sql_request_result_string = "SELECT MAX(id) FROM ucreporter_users;"  # забираем максимальный
			#rows_list = sql_request_dict(sql_request_result_string)
			# index_data = int(rows_list[0]['MAX(id)']) + 1

			# заполняем форму
			rows_list = db.session.query(db.func.max(UCReporterUsersTableClass.id)).scalar()
			index_data =  int(rows_list) + 1

			form_edit_user.id_field.text = index_data
			form_edit_user.UserName_field.data = str("username")
			form_edit_user.Password_field.data = str("password")
			form_edit_user.Description_field.data = str("description")
		else:
			# заполняем форму
			rows_list = UCReporterUsersTableClass.query.get(user_id)
			form_edit_user.id_field.text = rows_list.id
			form_edit_user.UserName_field.data = rows_list.username
			form_edit_user.Password_field.data = rows_list.password
			form_edit_user.Description_field.data =  rows_list.description

		#Проверяем наличие данных для отрисовки страницы.
		if rows_list:
			content_type = "user_edit"
			operation_end_time = datetime.now()
			operation_duration = str(operation_end_time - operation_start_time)
			console_output = "Done in " + operation_duration
			return render_template('ucreporter_settings_mainpage.html', html_page_title=html_page_title,
		                       html_page_header=html_page_header,
		                       content_type=content_type,
		                       console_output=console_output,
		                       form_edit_user=form_edit_user,
		                       rows_list=rows_list,
		                       formNAV=form_navigation)

	else:
		#забираем все записи из базы
		rows_list = UCReporterUsersTableClass.query.all()

		content_type = "user_list"
		operation_end_time = datetime.now()
		operation_duration = str(operation_end_time - operation_start_time)
		console_output = "Done in " + operation_duration

		return render_template('ucreporter_settings_mainpage.html', html_page_title=html_page_title,
	                       html_page_header=html_page_header,
	                       content_type=content_type,
	                       console_output=console_output,
	                           form_edit_user=form_edit_user,
	                        rows_list=rows_list,
	                       formNAV=form_navigation)

	operation_end_time = datetime.now()
	operation_duration = str(operation_end_time - operation_start_time)
	console_output = "Done in " + operation_duration
	content_type = "main_page"
	return render_template('ucreporter_settings_mainpage.html', html_page_title=html_page_title,
	                       html_page_header=html_page_header,
	                       content_type=content_type,
	                       console_output=console_output,
	                       formNAV=form_navigation)

def ucreporter_settings_CMSservers(server_id):
	"""Отображение страницы настроек CMS

	:param server_id:
	:return:
	"""
	operation_start_time = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'CMS administration'

	form_navigation = SelectNavigation(meta={'csrf': False})
	form_cms_server = CMSServerInformation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		return redirect(url_for(form_navigation.select_navigation.data))

	if form_cms_server.validate_on_submit():
		# проверяем наличие ID в базе
		sql_request_result_string = "SELECT * FROM cms_servers WHERE id=" + str(form_cms_server.id_field.text) + ";"
		save_data = sql_request_dict(sql_request_result_string)
		# если ID отсутствует, создаем запись, если есть обновляем
		if not save_data:

			insert_data = CmsServerTableClass(
				login = form_cms_server.username_field.data,
				password = form_cms_server.password_field.data,
				ip = form_cms_server.ip_field.data,
				api_port = form_cms_server.API_Port_field.data,
				cluster = form_cms_server.cluster_field.data
			)
			print(insert_data)
			db.session.add(insert_data)
			db.session.commit
			print("Insert done")

		else:
			sql_execute(
				"UPDATE cms_servers SET cluster='" + form_cms_server.cluster_field.data
				+ "',api_port='" + form_cms_server.API_Port_field.data
				+ "',login='" + form_cms_server.username_field.data
				+ "',password='" + form_cms_server.password_field.data
				+ "',ip='" + form_cms_server.ip_field.data
				+ "' WHERE id=" + str(form_cms_server.id_field.text)
				+ ";")
		# переходим на список
		return redirect(url_for('platform_CMSservers'))

	if server_id:
		if server_id == "AddNew":
			# Новый пользователь, считаем номер нового ID
			sql_request_result_string = "SELECT MAX(id) FROM cms_servers;"  # забираем максимальный
			rows_list = sql_request_dict(sql_request_result_string)
			# заполняем форму
			index_data = int(rows_list[0]['MAX(id)']) + 1
			form_cms_server.id_field.text = index_data
			form_cms_server.API_Port_field.data = str('api_port')
			form_cms_server.ip_field.data = str('ip')
			form_cms_server.cluster_field.data = str('cluster')
			form_cms_server.password_field.data = str('password')
			form_cms_server.username_field.data = str('login')

		else:
			#sql_request_result_string = "SELECT * FROM cms_servers WHERE id=" + server_id + ";"
			#rows_list = sql_request_dict(sql_request_result_string)
			rows_list = CmsServerTableClass.query.get(server_id)
			# заполняем форму
			form_cms_server.id_field.text = rows_list.id
			form_cms_server.API_Port_field.data = rows_list.api_port
			form_cms_server.ip_field.data = rows_list.ip
			form_cms_server.cluster_field.data = rows_list.cluster
			form_cms_server.password_field.data = rows_list.password
			form_cms_server.username_field.data = rows_list.login

		if rows_list:
			content_type = "cms_server_edit"
			operation_end_time = datetime.now()
			operation_duration = str(operation_end_time - operation_start_time)
			console_output = "Done in " + operation_duration
			return render_template('ucreporter_settings_mainpage.html', html_page_title=html_page_title,
		                       html_page_header=html_page_header,
		                       content_type=content_type,
		                       console_output=console_output,
		                       form_CMS_server=form_cms_server,
		                       rows_list=rows_list,
		                       formNAV=form_navigation)
	# отрисовка данных списка серверов в случае, если не пришел ID сервера.
	else:

		rows_list = CmsServerTableClass.query.all()
		content_type = "cms_server_list"
		operation_end_time = datetime.now()
		operation_duration = str(operation_end_time - operation_start_time)
		console_output = "Done in " + operation_duration

		return render_template('ucreporter_settings_mainpage.html', html_page_title=html_page_title,
		                       html_page_header=html_page_header,
		                       content_type=content_type,
		                       console_output=console_output,
		                       form_CMS_server=form_cms_server,
		                       rows_list=rows_list,
		                       formNAV=form_navigation)

def ucreporter_settings_CUCMservers(server_id):
	"""страница настроек CUCM

	:param server_id:
	:return:
	"""
	operation_start_time = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'CUCM Server administration'

	form_navigation = SelectNavigation(meta={'csrf': False})
	form_cucm_server = CUCMServerInformation(meta={'csrf': False})

	if form_navigation.validate_on_submit():
		return redirect(url_for(form_navigation.select_navigation.data))

	if form_cucm_server.validate_on_submit():
		# проверяем наличие ID в базе
		sql_request_result_string = "SELECT * FROM cm_servers_list WHERE id=" + str(form_cucm_server.id_field.text) + ";"
		save_data = sql_request_dict(sql_request_result_string)
		# если ID отсутствует, создаем запись, если есть обновляем
		if not save_data:
			print("INSERT")
			sql_execute(
				"INSERT INTO cm_servers_list SET id=" + str(form_cucm_server.id_field.text)
				+ ",cluster='" + form_cucm_server.Cluster_field.data
				+ "',cm_username='" + form_cucm_server.username_field.data
				+ "',cm_password='" + form_cucm_server.password_field.data
				+ "',cm_ip='" + form_cucm_server.ip_field.data + "';")
		else:
			print("UPDATE")
			sql_execute(
				"UPDATE cm_servers_list SET cluster='" + form_cucm_server.Cluster_field.data
				+ "',cm_username='" + form_cucm_server.username_field.data
				+ "',cm_password='" + form_cucm_server.password_field.data
				+ "',cm_ip='" + form_cucm_server.ip_field.data
				+ "' WHERE id='" + str(form_cucm_server.id_field.text) + "'")
		# переходим на список
		return redirect(url_for('platform_CUCMservers'))

	# отрисовка страницы изменения серверов.
	if server_id:
		if server_id == "AddNew":
			# Новый пользователь, считаем номер нового ID
			sql_request_result_string = "SELECT MAX(id) FROM cm_servers_list;"  # забираем максимальный
			rows_list = sql_request_dict(sql_request_result_string)
			# заполняем форму
			index_data = int(rows_list[0]['MAX(id)']) + 1
			form_cucm_server.id_field.text = index_data
			form_cucm_server.Cluster_field.data = str('cluster')
			form_cucm_server.username_field.data = str('cm_username')
			form_cucm_server.ip_field.data = str('cm_ip')
			form_cucm_server.password_field.data = str('cm_password')
		else:
			sql_request_result_string = "SELECT * FROM cm_servers_list WHERE id=" + server_id + ";"
			rows_list = sql_request_dict(sql_request_result_string)
			# заполняем форму
			form_cucm_server.id_field.text = str(rows_list[0]['id'])
			form_cucm_server.Cluster_field.data = str(rows_list[0]['cluster'])
			form_cucm_server.username_field.data = str(rows_list[0]['cm_username'])
			form_cucm_server.ip_field.data = str(rows_list[0]['cm_ip'])
			form_cucm_server.password_field.data = str(rows_list[0]['cm_password'])

		if rows_list:
			content_type = "cucm_server_edit"
			operation_end_time = datetime.now()
			operation_duration = str(operation_end_time - operation_start_time)
			console_output = "Done in " + operation_duration
			return render_template("ucreporter_settings_mainpage.html", html_page_title=html_page_title,
		                       html_page_header=html_page_header,
		                       content_type=content_type,
		                       console_output=console_output,
		                       rows_list=rows_list,
		                       form_CUCM_server=form_cucm_server,
		                       formNAV=form_navigation)

	# отрисовка данных списка серверов в случае, если не пришел ID сервера.
	else:

		rows_list = CmServerListTableClass.query.all()
		content_type = "cucm_server_list"
		operation_end_time = datetime.now()
		operation_duration = str(operation_end_time - operation_start_time)
		console_output = "Done in " + operation_duration

		return render_template("ucreporter_settings_mainpage.html", html_page_title=html_page_title,
	                       html_page_header=html_page_header,
	                       content_type=content_type,
	                       console_output=console_output,
	                       rows_list=rows_list,
	                       form_CUCM_server=form_cucm_server,
	                       formNAV=form_navigation)

def ucreporter_settings_roomcontroll(system_id):
	"""страница настроек Terminal

	"""
	operation_start_time = datetime.now()
	html_page_title = 'UC Reporter administration'
	html_page_header = 'RoomControl administration'

	form_navigation = SelectNavigation(meta={'csrf': False})
	form_roomcontroll = roomcontroll_information(meta={'csrf': False})

	if form_navigation.validate_on_submit():
		renderdata = {
			"content_type": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	if form_roomcontroll.validate_on_submit():
		# проверяем наличие ID в базе
		sql_request_result_string = "SELECT * FROM cm_roomsystems_table WHERE room_index=" + str(
			form_roomcontroll.id_field.text) + ";"
		save_data = sql_request_dict(sql_request_result_string)
		# если ID отсутствует, создаем запись, если есть обновляем
		if not save_data:
			print("INSERT")
			sql_execute(
				"INSERT INTO cm_roomsystems_table SET cm_roomsystems_table=" + str(form_cucm_server.id_field.text)
				+ ",cluster='" + form_cucm_server.Cluster_field.data
				+ "',cm_username='" + form_cucm_server.username_field.data
				+ "',cm_password='" + form_cucm_server.password_field.data
				+ "',cm_ip='" + form_cucm_server.ip_field.data + "';")
		else:
			print("UPDATE")
			sql_execute(
				"UPDATE cm_roomsystems_table SET cluster='" + form_cucm_server.Cluster_field.data
				+ "',cm_username='" + form_cucm_server.username_field.data
				+ "',cm_password='" + form_cucm_server.password_field.data
				+ "',cm_ip='" + form_cucm_server.ip_field.data
				+ "' WHERE id='" + str(form_cucm_server.id_field.text) + "'")
		# переходим на список
		print("REDIRECT")
		renderdata = {
			"content_type": "redirect",
			"redirect_to": "platform_CUCMservers"
		}
		return renderdata

	# отрисовка страницы изменения серверов.
	if system_id:
		if system_id == "AddNew":
			# Новый пользователь, считаем номер нового ID
			sql_request_result_string = "SELECT MAX(id) FROM cm_roomsystems_table;"  # забираем максимальный
			rows_list = sql_request_dict(sql_request_result_string)
			# заполняем форму
			index_data = int(rows_list[0]['MAX(id)']) + 1
			form_cucm_server.id_field.text = index_data
			form_cucm_server.Cluster_field.data = str('cluster')
			form_cucm_server.username_field.data = str('cm_username')
			form_cucm_server.ip_field.data = str('cm_ip')
			form_cucm_server.password_field.data = str('cm_password')
		else:
			sql_request_result_string = "SELECT * FROM cm_roomsystems_table WHERE id=" + server_id + ";"
			rows_list = sql_request_dict(sql_request_result_string)
			# заполняем форму
			form_cucm_server.id_field.text = str(rows_list[0]['id'])
			form_cucm_server.Cluster_field.data = str(rows_list[0]['cluster'])
			form_cucm_server.username_field.data = str(rows_list[0]['cm_username'])
			form_cucm_server.ip_field.data = str(rows_list[0]['cm_ip'])
			form_cucm_server.password_field.data = str(rows_list[0]['cm_password'])

		if rows_list:
			content_type = "cucm_server_edit"
			operation_end_time = datetime.now()
			operation_duration = str(operation_end_time - operation_start_time)
			console_output = "Done in " + operation_duration
			renderdata = {
				"content_type": content_type,
				"html_template": "ucreporter_settings_mainpage.html",
				"html_page_title": html_page_title,
				"html_page_header": html_page_header,
				"console_output": console_output,
				"form_cucm_server": form_cucm_server,
				"rows_list": rows_list,
				"form_navigation": form_navigation,
			}
			return renderdata

	# отрисовка данных списка серверов в случае, если не пришел ID сервера.
	else:
		sql_request_result_string = "SELECT * FROM cm_roomsystems_table;"
		rows_list = sql_request_dict(sql_request_result_string)
		content_type = "cucm_server_list"
		operation_end_time = datetime.now()
		operation_duration = str(operation_end_time - operation_start_time)
		console_output = "Done in " + operation_duration
		renderdata = {
			"content_type": content_type,
			"html_template": "ucreporter_settings_mainpage.html",
			"html_page_title": html_page_title,
			"html_page_header": html_page_header,
			"form_cucm_server": form_cucm_server,
			"console_output": console_output,
			"rows_list": rows_list,
			"form_navigation": form_navigation,
		}
		return renderdata
