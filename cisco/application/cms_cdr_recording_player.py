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
    response = render_template(
        'cisco_cms_recording_player.html',
        recording_id = recording_id,
        formNAV = form_navigation,
        row = True,
        html_page_header = "Record play",
    )
    return response

def get_range(request):
    range = request.headers.get('Range')
    #m = re.match("bytes=(?P<start>\d+)-(?P<end>\d+)?", range)
    m = False
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None

def partial_response(path, start, end=None):
    MB = 1 << 20
    BUFF_SIZE = 1 * MB

    file_size = os.path.getsize(path)

    # Determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # Read file
    with open(path, 'rb') as fd:
        fd.read(1024)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return response

def recording_play(recording_view_id):
    path = '../cms_videoarchive/'
    sql_request_path = CmsCdrRecordingsTableClass.query.get(recording_view_id)
    path = path + str(sql_request_path.path) + '.mp4'
    start, end = get_range(request)
    return partial_response(path, start, end)
