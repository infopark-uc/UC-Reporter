from flask import render_template, redirect
from application import app
from application.huntreport import huntreport
from application.usersreport import usersreport
from application.roomcontrol import codec,submit_order,get_value,set_value,send_order
from application.sqlrequests import cm_sqlselect,cm_sqlselectall,cm_sqlupdate
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

@app.route('/roomrequest', methods=['GET', 'POST'])
def roomrequest():
    codec()
    return "done"

@app.route('/SubmitOrder', methods=['GET', 'POST'])
def order():
    submit_order()
    return "done"

@app.route('/SendOrder', methods=['GET', 'POST'])
def SendOrder():
    send_order("0")
    return "done"

@app.route('/sql', methods=['GET', 'POST'])
def sql():
    systemindex = "0"

    phone_access_data_ip = cm_sqlselect("phone_ip", "cm_phones_table", "phone_index", systemindex)
    print("phone ip " + phone_access_data_ip)

    phone_access_data_login = cm_sqlselect("phone_user", "cm_phones_table", "phone_index", systemindex)
    print("phone login " + phone_access_data_login)

    phone_access_data_password = cm_sqlselect("phone_password", "cm_phones_table", "phone_index", systemindex)
    print("phone password " + phone_access_data_password)

    widget_data_CoffeeCount = cm_sqlselect("widget_data", "widget_table", "widget_name", "CoffeeCount")
    print("CoffeeCount " + str(widget_data_CoffeeCount))

    widget_data_TeaCount = cm_sqlselect("widget_data", "widget_table", "widget_name", "TeaCount")
    print("TeaCount " + str(widget_data_TeaCount))

    return "done"
