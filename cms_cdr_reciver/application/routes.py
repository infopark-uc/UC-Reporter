
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



@app.route('/cdr', methods=['POST'])
def cdr():
    return cdr_receiver()

app.secret_key = "Super_secret_key"