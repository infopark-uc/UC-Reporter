from flask import render_template, redirect, flash
from application import app
from application.huntreport import huntreport
from application.usersreport import usersreport
import application.callforward
import requests
import xmltodict
import collections
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectSearchType

@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def usersearchpage():
     module_result = usersreport() #получаем данные из модуля
     if module_result['rendertype'] == 'success': #проверка если данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                                   console_output=module_result['console_output'],
                                   rows_list=module_result['rows_list'],
                                   formNAV=module_result['form_navigation'],
                                   formSRCH=module_result['form_search'])

     if module_result['rendertype'] == 'redirect': #переход на другую страницу
        return redirect(module_result['redirect_to'])

     return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           formNAV=module_result['form_navigation'],
                           formSRCH=module_result['form_search'])

@app.route("/hunt", methods=['GET', 'POST'])
def huntpage():
     module_result = huntreport()
     if module_result['rendertype'] == 'redirect': #переход на другую страницу
        return redirect(module_result['redirect_to'])

     return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                            console_output=module_result['console_output'],
                            rows_list=module_result['rows_list'],
                            formNAV=module_result['form_navigation'])

@app.route("/cfa", methods=['GET', 'POST'])
def cfa():
     module_result = application.callforward.render()
     if module_result['rendertype'] == 'redirect': #переход на другую страницу
        return redirect(module_result['redirect_to'])

     if module_result['rendertype'] == 'success': # данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                                   console_output=module_result['console_output'],
                                   rows_list=module_result['rows_list'],
                                   formNAV=module_result['form_navigation'],
                                   formSRCH=module_result['form_search'])

     return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                            console_output=module_result['console_output'],
                            formNAV=module_result['form_navigation'],
                            formSRCH=module_result['form_search'])

