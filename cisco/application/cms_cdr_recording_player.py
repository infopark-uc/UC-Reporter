import os
import re
import sys
import time
import pprint
from datetime import datetime

import mimetypes
from flask import Response, render_template
from flask import Flask
from flask import send_file
from flask import request

from application.database import CmsCdrRecordingsTableClass
from application.forms import SelectNavigation, SelectSearchType



#рендрим страничку
def recording_page(recording_id):
    form_navigation = SelectNavigation(meta={'csrf': False})
    sql_request_path = CmsCdrRecordingsTableClass.query.get(recording_id)
    conference_id = str(sql_request_path.call_id)
    record_path = 'record/' + str(sql_request_path.path).replace("_","/") + '.mp4'
    print(record_path)
    response = render_template(
        'cisco_cms_recording_player.html',
        recording_id = record_path,
        formNAV = form_navigation,
        row = True,
        html_page_header = "Record play for " + conference_id,
    )
    return response
