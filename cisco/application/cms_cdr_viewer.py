import requests
import xmltodict
from pprint import pprint
from application.sqlrequests import cm_sqlselect,cm_sqlselectall,cm_sqlupdate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectCMSClusterForCDR
from application.sqlrequests import cms_sql_request_dict
import time
from flask_login import current_user
import collections

# библиотеки для графиков
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.models import DatetimeTickFormatter, HoverTool, ColumnDataSource
from math import pi
from datetime import datetime

def cmsviewer():

	operationStartTime = datetime.now()

	SEARCH_FOR_ALL = "all"

	html_page_title = 'Cisco Meetings Server CDR Report'

	# Temporary values
	console_output = "Нет активного запроса"

	form_navigation = SelectNavigation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		#print(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	form_cmsselection = SelectCMSClusterForCDR(meta={'csrf': False})
	if form_cmsselection.validate_on_submit():
		if form_cmsselection.select_CMSCluster.data == SEARCH_FOR_ALL:
			if not form_cmsselection.confroom_filter.data:
				rows_list = cms_sql_request_dict(
					"SELECT name AS cospace_name , cospace AS cospace_id, id AS call_id, starttime, callLegsMaxActive, durationSeconds, EndTime, cms_ip FROM cms_cdr_calls ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
				#print("CMS VW: get dict")
			else:
				rows_list = cms_sql_request_dict(
					"SELECT name AS cospace_name , cospace AS cospace_id, id AS call_id, starttime, callLegsMaxActive, durationSeconds, EndTime, cms_ip FROM cms_cdr_calls WHERE (cms_cdr_calls.name LIKE  '%" + form_cmsselection.confroom_filter.data + "%') ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
				#print("CMS VW: get dict")
		else:
			if not form_cmsselection.confroom_filter.data:
				rows_list = cms_sql_request_dict(
					"SELECT cms_cdr_calls.name AS cospace_name,cms_cdr_calls.cospace AS cospace_id, cms_cdr_calls.id AS call_id, cms_cdr_calls.starttime, cms_cdr_calls.callLegsMaxActive, cms_cdr_calls.durationSeconds, cms_cdr_calls.EndTime, cms_cdr_calls.cms_ip FROM cms_cdr_calls INNER JOIN cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip WHERE cms_servers.cluster='" + form_cmsselection.select_CMSCluster.data + "' ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
				#print("CMS VW: get dict")
			else:
				rows_list = cms_sql_request_dict(
					"SELECT cms_cdr_calls.name AS cospace_name,cms_cdr_calls.cospace AS cospace_id, cms_cdr_calls.id AS call_id, cms_cdr_calls.starttime, cms_cdr_calls.callLegsMaxActive, cms_cdr_calls.durationSeconds, cms_cdr_calls.EndTime, cms_cdr_calls.cms_ip FROM cms_cdr_calls INNER JOIN cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip WHERE cms_servers.cluster='" + form_cmsselection.select_CMSCluster.data + "'AND (cms_cdr_calls.name LIKE  '%" + form_cmsselection.confroom_filter.data + "%') ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
				#print("CMS VW: get dict")

		operationEndTime = datetime.now()
		operationDuration = str( operationEndTime - operationStartTime)
		console_output = "Done in " + operationDuration + "\n 		Searching compleate for:" + str(len(rows_list)) + " elements"

		for row in rows_list:
			if row["durationSeconds"]:
				row["durationSeconds"] = time.strftime("%H:%M:%S", time.gmtime(int(row["durationSeconds"])))

		renderdata = {
			"rendertype": "success",
			"html_template": "cisco_cmscdr.html",
			"html_page_title": html_page_title,
			"console_output": console_output,
			"form_navigation": form_navigation,
			"form_cmsselection": form_cmsselection,
			"rows_list": rows_list
		}
		return renderdata

	operationEndTime = datetime.now()
	operationDuration = str( operationEndTime - operationStartTime)
	console_output = "Нет активного запроса (" + operationDuration + ")"

	renderdata = {
		"rendertype": "Null",
		"html_template": "cisco_cmscdr.html",
		"html_page_title": html_page_title,
		"console_output": console_output,
		"form_navigation": form_navigation,
		"form_cmsselection": form_cmsselection
	}
	return renderdata

def cmscallviewer(call_id):

	operationStartTime = datetime.now()

	html_page_title = 'CMS Call Report'
	#print("CMS CALLVW: request for callID: " + call_id)

	form_navigation = SelectNavigation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		#print(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata


	sql_request_string_select_basic = "SELECT DISTINCT callleg_id,remoteaddress,displayName,durationseconds,startTime,cms_ip,alarm_type,alarm_value,reason"
	sql_request_string_audio_video_codecs = ",rxAudio_codec,txAudio_codec,rxVideo_codec,txVideo_codec,txVideo_maxHeight,txVideo_maxWidth"
	sql_request_string_audio_statistics = ",rxAudio_packetLossBurst_duration,rxAudio_packetLossBurst_density,rxAudio_packetGap_duration,rxAudio_packetGap_density"
	sql_request_string_video_statistics = ",rxVideo_packetLossBurst_duration,rxVideo_packetLossBurst_density,rxVideo_packetGap_duration,rxVideo_packetGap_density"
	sql_request_string_call_type = ",guestConnection,callLeg_subtype"
	sql_request_string_from = " FROM cms_cdr_records WHERE call_id='" + call_id + "';"
	sql_request_result_string = sql_request_string_select_basic\
								+ sql_request_string_audio_video_codecs\
								+ sql_request_string_audio_statistics\
								+ sql_request_string_video_statistics\
								+ sql_request_string_call_type\
								+ sql_request_string_from

	rows_list = cms_sql_request_dict(sql_request_result_string)
		#"SELECT DISTINCT callleg_id,remoteaddress,durationseconds,rxAudio_codec,txAudio_codec,rxVideo_codec,txVideo_codec,txVideo_maxHeight,txVideo_maxWidth,cms_ip,alarm_type,alarm_value FROM cms_cdr_records WHERE call_id='" + call_id + "';")

	#print("CMS CALLVW: get dict for callID:  " + call_id)

	operationEndTime = datetime.now()
	operationDuration = str( operationEndTime - operationStartTime)
	console_output = "Done in " + operationDuration
	for row in rows_list:
		if row["durationseconds"]:
			if type(row["durationseconds"]) is int:
				row["durationseconds"] = time.strftime("%H:%M:%S", time.gmtime(int(row["durationseconds"])))

	renderdata = {
		"rendertype": "success",
		"html_template": "cisco_cmsview.html",
		"html_page_title": html_page_title,
		"console_output": console_output,
		"form_navigation": form_navigation,
		"rows_list": rows_list
	}
	return renderdata


def cmscalllegviewer(callleg_id):

	operationStartTime = datetime.now()

	html_page_title = 'CMS CallLeg Report'
	#print("CMS CALLLEGVW: request for calllegID: " + callleg_id)

	form_navigation = SelectNavigation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		print(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	rows_list = cms_sql_request_dict(
#		"SELECT callleg_id,date,AudioPacketLossPercentageRX,AudioPacketLossPercentageTX,VideoPacketLossPercentageRX,VideoPacketLossPercentageTX FROM cms_cdr_calllegs WHERE callleg_id='" + callleg_id + "' ;")
		"SELECT cms_cdr_calllegs.callleg_id,cms_cdr_calllegs.date,cms_cdr_calllegs.AudioPacketLossPercentageRX,cms_cdr_calllegs.AudioPacketLossPercentageTX,cms_cdr_calllegs.VideoPacketLossPercentageRX,cms_cdr_calllegs.VideoPacketLossPercentageTX,cms_cdr_records.remoteaddress FROM cms_cdr_calllegs INNER JOIN cms_cdr_records ON  cms_cdr_calllegs.callleg_id=cms_cdr_records.callleg_id WHERE cms_cdr_calllegs.callleg_id='" + callleg_id + "';")

	#print("CMS CALLLEGVW: get dict for callID:  " + callleg_id)
	#print("CMS CALLLEGVW: rows_list type:	" + str(type(rows_list)))

	if isinstance(rows_list, list):
		print("CMS CALLLEGVW: rows_list is list ")
	else:
		#print("CMS CALLLEGVW: rows_list is not list, it is: " + str(type(rows_list)))

		operationEndTime = datetime.now()
		operationDuration = str( operationEndTime - operationStartTime)
		console_output = "There is no data for the request in DB. Done in " + operationDuration
		#print(console_output)
		renderdata = {
			"rendertype": "null",
			"html_template": "cisco_cmspacketloss.html",
			"html_page_title": html_page_title,
			"console_output": console_output,
			"form_navigation": form_navigation
		}
		return renderdata

	# создаем листы значений по осям x и y для построения графиков
	AudioPacketLossPercentageRX_list = []
	AudioPacketLossPercentageTX_list = []
	VideoPacketLossPercentageRX_list = []
	VideoPacketLossPercentageTX_list = []
	date_list = []

	# заполняем листы из словаря с данными из БД
	for row in rows_list:
		AudioPacketLossPercentageRX_list.append(float(row["AudioPacketLossPercentageRX"]))
		AudioPacketLossPercentageTX_list.append(float(row["AudioPacketLossPercentageTX"]))
		VideoPacketLossPercentageRX_list.append(float(row["VideoPacketLossPercentageRX"]))
		VideoPacketLossPercentageTX_list.append(float(row["VideoPacketLossPercentageTX"]))
		date_list.append(datetime.strptime(row["date"], '%Y-%m-%d %H:%M:%S.%f'))


	# формируем словарь с максимальными значениями потерь
	max_loss_values = {
		"AudioRX": max(AudioPacketLossPercentageRX_list if AudioPacketLossPercentageRX_list else 0),
		"AudioTX": max(AudioPacketLossPercentageTX_list),
		"VideoRX": max(VideoPacketLossPercentageRX_list),
		"VideoTX": max(VideoPacketLossPercentageTX_list)
	}

	# создаем объект класса ColumnDataSource содержащий все данные графика
	plot_source = ColumnDataSource(data=dict(
		date=date_list,
		AudioRX=AudioPacketLossPercentageRX_list,
		AudioTX=AudioPacketLossPercentageTX_list,
		VideoRX=VideoPacketLossPercentageRX_list,
		VideoTX=VideoPacketLossPercentageTX_list)
	)

	# создаем объект класса HoverTool со значениями из ColumnDataSource для всплывающих подсказок
	hover_tool = HoverTool(
		tooltips=[
			("Audio RX", "@AudioRX{([0]0.0)}"),
			("Audio TX", "@AudioTX{([0]0.0)}"),
			("Video RX", "@VideoRX{([0]0.0)}"),
			("Video TX", "@VideoTX{([0]0.0)}")
		],

		# режим отображения подсказки при наведении мышкой на график
		mode='mouse'
	)

	# создаем объект класса figure описывающий график
	p = figure(plot_width=1800, plot_height=400, x_axis_type="datetime")
	p.sizing_mode = "scale_width"
	# добавляем к объекту графика инструмент - объект всплывающих подсказок
	p.add_tools(hover_tool)
	# добавляем линии на график
	p.line(x="date", y="AudioRX", source=plot_source, line_width=2, color='#A6CEE3', legend_label='Audio RX')
	p.line(x="date", y="AudioTX", source=plot_source, line_width=2, color='#B2DF8A', legend_label='Audio TX')
	p.line(x="date", y="VideoRX", source=plot_source, line_width=2, color='#33A02C', legend_label='Video RX')
	p.line(x="date", y="VideoTX", source=plot_source, line_width=2, color='#FB9A99', legend_label='Video TX')
	# задаем формат отображения даты и времени на оси x для масштабирования
	p.xaxis.formatter = DatetimeTickFormatter(
		milliseconds=["%H:%M:%S.%3Ns"],
		seconds=["%H:%M:%S"],
		minsec=["%H:%M:%S"],
		minutes=["%H:%M:%S"],
		hourmin=["%H:%M:%S"],
		hours=["%d %B %Y"],
		days=["%d %B %Y"],
		months=["%d %B %Y"],
		years=["%d %B %Y"],
	)
	# задаем угол наклона подписей с датами на оси x
	p.xaxis.major_label_orientation = pi / 4
	# формируем объекты содержащие html-код с графиком для web-страницы
	script, div = components(p)
	# формируем обект содержащий html-код с ссылками на библиотеки javascript
	resources = CDN.render()

	operationEndTime = datetime.now()
	operationDuration = str( operationEndTime - operationStartTime)
	console_output = "Information for: " + rows_list[0]["remoteaddress"] + ". Done in " + operationDuration


	renderdata = {
		"rendertype": "success",
		"html_template": "cisco_cmspacketloss.html",
		"html_page_title": html_page_title,
		"console_output": console_output,
		"form_navigation": form_navigation,
		"script": script,
		"div": div,
		"resources": resources,
		"max_loss_values": max_loss_values
	}
	return renderdata

def cmsrecordingsviewer():
	# вывод списка записей

	NETPATH = "\\\\192.168.12.195\\record\\"
	RECORD_FILE_EXTENTION = ".mp4"

	operationStartTime = datetime.now()

	html_page_title = 'CMS CDR Recordings Report'
	print("CMS CALLVW: request for recordings")

	form_navigation = SelectNavigation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		print(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	sql_request_result_string = "SELECT cms_cdr_calls.name, cms_cdr_calls.callLegsMaxActive, cms_cdr_calls.StartTime, cms_cdr_calls.durationSeconds, cms_cdr_recordings.path, cms_cdr_recordings.recording_id FROM cms_cdr_calls INNER JOIN cms_cdr_recordings ON cms_cdr_recordings.call_id=cms_cdr_calls.id ORDER BY cms_cdr_calls.StartTime DESC;"
	rows_list = cms_sql_request_dict(sql_request_result_string)

	print("CMS CALLVW: get dict for call recordings")

	for row in rows_list:
		row["original_path"] = row["path"]
		#переводим секунлы в нормальное время
		if row["durationSeconds"]:
			row["durationSeconds"] = time.strftime("%H:%M:%S", time.gmtime(int(row["durationSeconds"])))
		#формируем путь к файлу
		row["path"] = NETPATH + row["path"].replace("/","\\") + RECORD_FILE_EXTENTION

	operationEndTime = datetime.now()
	operationDuration = str(operationEndTime - operationStartTime)
	console_output = "Done in " + operationDuration

	renderdata = {
		"rendertype": "success",
		"html_template": "cisco_cmsrecordings.html",
		"html_page_title": html_page_title,
		"console_output": console_output,
		"form_navigation": form_navigation,
		"rows_list": rows_list
	}
	return renderdata