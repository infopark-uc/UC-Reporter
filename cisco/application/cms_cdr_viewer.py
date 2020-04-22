import requests
import xmltodict
from pprint import pprint
from application.sqlrequests import cm_sqlselect,cm_sqlselectall,cm_sqlupdate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectSearchType
from application.sqlrequests import cms_sql_request_dict

# библиотеки для графиков
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN

def cmsviewer():

	html_page_title = 'CMS CDR Report'
	rows_list = cms_sql_request_dict(
		"SELECT name AS cospace_name , cospace AS cospace_id, id AS call_id, starttime AS time FROM cms_cdr_calls")
	print("CMS VW: get dict")
	#pprint (rows_list)


	form_navigation = SelectNavigation(csrf_enabled=False)
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		print(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	renderdata = {
		"rendertype": "success",
		"html_template": "cisco_cmscdr.html",
		"html_page_title": html_page_title,
		"console_output": "done",
		"form_navigation": form_navigation,
		"rows_list": rows_list
	}
	return renderdata

def cmscallviewer(call_id):

	html_page_title = 'CMS Call Report'
	print("CMS CALLVW: request for callID: " + call_id)
	rows_list = cms_sql_request_dict(
		"SELECT DISTINCT callleg_id,remoteaddress,durationseconds,cms_ip FROM cms_cdr_records WHERE call_id='" + call_id + "';")

	print("CMS CALLVW: get dict for callID:  " + call_id)
	#pprint (rows_list)


	form_navigation = SelectNavigation(csrf_enabled=False)
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		print(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	renderdata = {
		"rendertype": "success",
		"html_template": "cisco_cmsview.html",
		"html_page_title": html_page_title,
		"console_output": "done",
		"form_navigation": form_navigation,
		"rows_list": rows_list
	}
	return renderdata


def cmscalllegviewer(callleg_id):
	html_page_title = 'CMS CallLeg Report'
	print("CMS CALLLEGVW: request for calllegID: " + callleg_id)

	rows_list = cms_sql_request_dict(
		"SELECT DISTINCT callleg_id,AudioPacketLossPercentageRX,AudioPacketLossPercentageTX,VideoPacketLossPercentageRX,VideoPacketLossPercentageTX,cms_node  FROM cms_cdr_calllegs WHERE callleg_id='" + callleg_id + "';")

	print("CMS CALLLEGVW: get dict for callID:  " + callleg_id)
	#pprint(rows_list)



	form_navigation = SelectNavigation(csrf_enabled=False)
	if form_navigation.validate_on_submit():
		console_output = "Нет активного запроса"
		print(console_output)
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata

	#для графиков
	p = figure(plot_width=400, plot_height=400)
	p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)
	script, div = components(p)
	resources = CDN.render()
	print(resources)


	renderdata = {
		"rendertype": "success",
		"html_template": "cisco_cmspacketloss.html",
		"html_page_title": html_page_title,
		"console_output": "done",
		"form_navigation": form_navigation,
		"rows_list": rows_list,
		"script": script,
		"div": div,
		"resources": resources
	}
	return renderdata