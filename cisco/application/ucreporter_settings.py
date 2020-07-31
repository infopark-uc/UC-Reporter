from application.forms import SelectNavigation

def ucreporter_settings_mainpage():
	html_page_title = 'UC Reporter '
	html_page_header = 'UC Reporter administration'
	console_output = "Нет активного запроса"

	form_navigation = SelectNavigation(meta={'csrf': False})
	if form_navigation.validate_on_submit():
		renderdata = {
			"rendertype": "redirect",
			"redirect_to": form_navigation.select_navigation.data
		}
		return renderdata


	renderdata = {
		"rendertype": "success",
		"html_template": "ucreporter_settings_mainpage.html",
		"html_page_title": html_page_title,
		"html_page_header": html_page_header,
		"console_output": console_output,
		"form_navigation": form_navigation,
	}
	return renderdata