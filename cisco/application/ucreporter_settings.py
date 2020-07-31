from application.forms import SelectNavigation
from datetime import datetime

def ucreporter_settings_mainpage():
	operationStartTime = datetime.now()
	html_page_title = 'UC Reporter '
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

	content_type = "servers"
	renderdata = {
		"rendertype": "success",
		"content_type": "server_settings",
		"html_template": "ucreporter_settings_mainpage.html",
		"html_page_title": html_page_title,
		"html_page_header": html_page_header,
		"console_output": console_output,
		"form_navigation": form_navigation,
	}
	return renderdata