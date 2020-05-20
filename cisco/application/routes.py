from flask import render_template, redirect
from application import app
from application.huntreport import huntreport
from application.usersreport import usersreport
from application.roomcontrol import codec,submit_order,get_value,set_value,send_order
from application.cms_cdr_reciver import cdr_receiver
from application.sendmail import ucsendmail
from application.cms_cdr_viewer import cmsviewer,cmscallviewer,cmscalllegviewer

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
    codec("0") # "0" - index roomsystem from database
    return "roomrequest done"

@app.route('/SubmitOrder', methods=['GET', 'POST'])
def order():
    return submit_order("0") # "0" - index roomsystem from database

@app.route('/ucsendmail', methods=['POST'])
def ucmail():
    return ucsendmail()

@app.route('/cdr', methods=['POST'])
def cdr():
    return cdr_receiver()

@app.route('/cms', methods=['GET', 'POST'])
@app.route('/cms/', methods=['GET', 'POST'])
def cmspage():

    module_result = cmsviewer()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(module_result['redirect_to'])

    if module_result['rendertype'] == 'success':  # данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                               console_output=module_result['console_output'],
                               rows_list=module_result['rows_list'],
                               formNAV=module_result['form_navigation'],
                               formCMS=module_result['form_cmsselection'])

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           formNAV=module_result['form_navigation'],
                           formCMS=module_result['form_cmsselection'])



@app.route('/cms/call/<string:callid>/', methods=['GET', 'POST'])
def cmscall(callid):
    module_result = cmscallviewer(callid)

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(module_result['redirect_to'])

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           rows_list=module_result['rows_list'],
                           formNAV=module_result['form_navigation'])


@app.route('/cms/callleg/<string:callegid>/', methods=['GET', 'POST'])
def cmscallleg(callegid):
    module_result = cmscalllegviewer(callegid)

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(module_result['redirect_to'])

    if module_result['rendertype'] == 'success':  # проверка если данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                               console_output=module_result['console_output'],
                               formNAV=module_result['form_navigation'],
                               div=module_result['div'],
                               script=module_result['script'],
                               resources=module_result['resources'],
                               max_loss_values=module_result['max_loss_values'])

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
        console_output=module_result['console_output'],
        formNAV=module_result['form_navigation'])


