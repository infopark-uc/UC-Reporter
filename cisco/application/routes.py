
from flask import render_template, redirect, url_for
from application import app
from application.huntreport import huntreport
from application.usersreport import usersreport
from application.roomcontrol import codec,submit_order,get_value,set_value,send_order
from application.cms_cdr_reciver import cdr_receiver
from application.sendmail import ucsendmail
from application.cms_cdr_viewer import cmsviewer,cmscallviewer,cmscalllegviewer,cmsrecordingsviewer,cmsmeetingviewer,cmsallcalllegsviewer
from application.cms_cospace_viewer import cms_cospace_view
from application.ucreporter_login import ucreporter_login
from application.cms_cospace_usage import cms_cospace_usage, cms_cospace_usage_by_cluster
from flask_login import logout_user, current_user, login_required
from application.ucreporter_settings import ucreporter_settings_mainpage,ucreporter_settings_users
from application.ucreporter_settings import ucreporter_settings_CMSservers,ucreporter_settings_CUCMservers
import application.callforward
from application.aurus_consistency_checker import aurus_consistency_check
from application.cms_cdr_recording_player import recording_play,recording_page


@app.route("/", methods=['GET', 'POST'])
@app.route("/phones", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
@login_required
def usersearchpage():
     module_result = usersreport() #получаем данные из модуля
     if module_result['rendertype'] == 'success': #проверка если данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                                   console_output=module_result['console_output'],
                                   rows_list=module_result['rows_list'],
                                   formNAV=module_result['form_navigation'],
                                   formSRCH=module_result['form_search'])

     if module_result['rendertype'] == 'redirect': #переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

     return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           formNAV=module_result['form_navigation'],
                           formSRCH=module_result['form_search'])

@app.route("/hunt", methods=['GET', 'POST'])
@login_required
def huntpage():
     module_result = huntreport()
     if module_result['rendertype'] == 'redirect': #переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

     if module_result['rendertype'] == 'success':  # проверка если данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                            console_output=module_result['console_output'],
                            rows_list=module_result['rows_list'],
                            formNAV=module_result['form_navigation'],
                            form_hunt_group=module_result['form_hunt_group'])

     return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                            console_output=module_result['console_output'],
                            formNAV=module_result['form_navigation'],
                            form_hunt_group=module_result['form_hunt_group'])


@app.route("/cfa", methods=['GET', 'POST'])
@login_required
def cfa():
     module_result = application.callforward.render()
     if module_result['rendertype'] == 'redirect': #переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

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

@app.route('/roomrequest/<string:system_id>/', methods=['GET', 'POST'])
def roomrequest(system_id):
    return codec(system_id)

@app.route('/SubmitOrder/<string:system_id>/', methods=['GET', 'POST'])
def order(system_id):
    return submit_order(system_id)

@app.route('/cdr', methods=['POST'])
def cdr():
    return cdr_receiver()

@app.route('/cms', methods=['GET', 'POST'])
@app.route('/cms/', methods=['GET', 'POST'])
@login_required
def cmspage():

    module_result = cmsviewer()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

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
@login_required
def cmscall(callid):
    module_result = cmscallviewer(callid)

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           rows_list=module_result['rows_list'],
                           formNAV=module_result['form_navigation'])


@app.route('/cms/meeting/<string:meeting_id>/', methods=['GET', 'POST'])
@login_required
def cmsmeetingid(meeting_id):
    module_result = cmsmeetingviewer(meeting_id)

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           rows_list=module_result['rows_list'],
                           formNAV=module_result['form_navigation'])


@app.route('/cms/callleg/<string:callegid>/', methods=['GET', 'POST'])
@login_required
def cmscallleg(callegid):
    module_result = cmscalllegviewer(callegid)

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

    if module_result['rendertype'] == 'success':  # проверка если данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                               console_output=module_result['console_output'],
                               formNAV=module_result['form_navigation'],
                               div=module_result['div'],
                               script=module_result['script'],
                               resources=module_result['resources'],
                               max_loss_values=module_result['max_loss_values'],
                               div_rtt=module_result['div_rtt'],
                               script_rtt=module_result['script_rtt'],
                               max_loss_values_rtt=module_result['max_loss_values_rtt']
                               )

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
        console_output=module_result['console_output'],
        formNAV=module_result['form_navigation'])


@app.route('/cms/allcalllegsplot/<string:meeting_id>/', methods=['GET', 'POST'])
@login_required
def cmscallleg_for_meeting(meeting_id):
    module_result = cmsallcalllegsviewer(meeting_id)

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

    if module_result['rendertype'] == 'success':  # проверка если данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                               console_output=module_result['console_output'],
                               formNAV=module_result['form_navigation'],
                               plot_list=module_result['plot_list'],
                               resources=module_result['resources']
                               )

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
        console_output=module_result['console_output'],
        formNAV=module_result['form_navigation'])


@app.route('/cmscospace', methods=['GET', 'POST'])
@app.route('/cmscospace/', methods=['GET', 'POST'])
@login_required
def cms_cospace_page():

    module_result = cms_cospace_view()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

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


@app.route('/cmsusage', methods=['GET', 'POST'])
@app.route('/cmsusage/', methods=['GET', 'POST'])
@login_required
def cms_cospace_usage_page():

    module_result = cms_cospace_usage()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

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


@app.route('/cmsclusterusage', methods=['GET', 'POST'])
@app.route('/cmsclusterusage/', methods=['GET', 'POST'])
@login_required
def cms_cospace_usage_by_cluster_page():

    module_result = cms_cospace_usage_by_cluster()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

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

@app.route('/cmsrec', methods=['GET', 'POST'])
@app.route('/cmsrec/', methods=['GET', 'POST'])
@login_required
def cms_recordings_page():

    module_result = cmsrecordingsviewer()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

    if module_result['rendertype'] == 'success':  # данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                               console_output=module_result['console_output'],
                               rows_list=module_result['rows_list'],
                               formNAV=module_result['form_navigation'])

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           formNAV=module_result['form_navigation'])

@app.route('/cmsrec/playfile/<string:recording_id>/', methods=['GET', 'POST'])
@login_required
def cms_record_play_file(recording_id):
    return recording_play(recording_id)

@app.route('/cmsrec/playrecord/<string:recording_id>/', methods=['GET', 'POST'])
@login_required
def cms_record_play_page(recording_id):
    return recording_page(recording_id)

@app.route('/login', methods=['GET', 'POST'])
def login():

    module_result = ucreporter_login()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

    if module_result['rendertype'] == 'redirect_to_link':  # переход на другую страницу
        return redirect(module_result['redirect_to'])


    if module_result['rendertype'] == 'success':  # данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                               console_output=module_result['console_output'],
                               form_login=module_result['form_login'],
                               formNAV=module_result['form_navigation'])

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        print("User " + current_user.username + " is logging out")
    else:
        print("User is logging out")

    logout_user()
    print("User is logged out")
    return redirect(url_for('cmspage'))



#Модуль настроек платформы
@app.route('/platform', methods=['GET', 'POST'])
@app.route('/platform/', methods=['GET', 'POST'])
@app.route('/platform/servers/', methods=['GET', 'POST'])
@app.route('/platform/status/', methods=['GET', 'POST'])
@login_required
def platform():
    return ucreporter_settings_mainpage()

@app.route('/platform/users/', defaults={'userid': None}, methods=['GET', 'POST'])
@app.route('/platform/users/<string:userid>/', methods=['GET', 'POST'])
@login_required
def platform_users(userid):
    return ucreporter_settings_users(userid)

@app.route('/platform/servers/cucm/', defaults={'server_id': None }, methods=['GET', 'POST'])
@app.route('/platform/servers/cucm/<string:server_id>/', methods=['GET', 'POST'])
@login_required
def platform_CUCMservers(server_id):
    return ucreporter_settings_CUCMservers(server_id)

@app.route('/platform/servers/cms/', defaults={'server_id': None }, methods=['GET', 'POST'])
@app.route('/platform/servers/cms/<string:server_id>/', methods=['GET', 'POST'])
@login_required
def platform_CMSservers(server_id):
    return ucreporter_settings_CMSservers(server_id)

@app.route('/aurus', methods=['GET', 'POST'])
@app.route('/aurus/', methods=['GET', 'POST'])
@login_required
def aurus_consitency_check():

    module_result = aurus_consistency_check()

    if module_result['rendertype'] == 'redirect':  # переход на другую страницу
        return redirect(url_for(module_result['redirect_to']))

    if module_result['rendertype'] == 'success':  # данные получены
        return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                               console_output=module_result['console_output'],
                               rows_list=module_result['rows_list'],
                               formNAV=module_result['form_navigation'],
                               formCUCM=module_result['form_cluster_selection'])

    return render_template(module_result['html_template'], html_page_title=module_result['html_page_title'],
                           console_output=module_result['console_output'],
                           formNAV=module_result['form_navigation'],
                           formCUCM=module_result['form_cluster_selection'])


app.secret_key = "Super_secret_key"