from flask import render_template, redirect
from application import app
from application.huntreport import huntreport
from application.usersreport import usersreport
from application.roomcontrol import codec,submit_order,get_value,set_value,send_order
import application.callforward




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

@server.route('/roomrequest', methods=['GET', 'POST'])
def roomrequest():
    codec()
    return "done"

@server.route('/SubmitOrder', methods=['GET', 'POST'])
def order():
    submit_order()
    return "done"



