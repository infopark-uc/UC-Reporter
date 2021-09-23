from flask import render_template, redirect, url_for
import requests
import xmltodict
from pprint import pprint
from pprint import pformat
from application.sqlrequests import cm_sqlselect,cm_sqlselectall,cm_sqlupdate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectCMSClusterForCDR
from application.sqlrequests import sql_request_dict
import time
from flask_login import current_user
from application.ucreporter_logs import logger_init
import logging
import collections

# библиотеки для графиков
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.models import DatetimeTickFormatter, HoverTool, ColumnDataSource
from math import pi
from datetime import datetime


def is_digit(string):
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False

def cmsviewer():

    operationStartTime = datetime.now()

    SEARCH_FOR_ALL = "all"

    html_page_title = 'Cisco Meetings Server CDR Report'
    html_template = 'cisco_cmscdr.html'

    # Temporary values
    console_output = "Нет активного запроса"

    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        #print(console_output)
        return redirect(url_for(form_navigation.select_navigation.data))

    form_cmsselection = SelectCMSClusterForCDR(meta={'csrf': False})
    if form_cmsselection.validate_on_submit():
        if form_cmsselection.select_CMSCluster.data == SEARCH_FOR_ALL:
            if not form_cmsselection.confroom_filter.data:
                rows_list = sql_request_dict(
                    "SELECT meeting_id, name AS cospace_name , cospace AS cospace_id, id AS call_id, starttime, callLegsMaxActive, durationSeconds, EndTime, cms_ip FROM cms_cdr_calls ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
                #print("CMS VW: get dict")
            else:
                rows_list = sql_request_dict(
                    "SELECT meeting_id, name AS cospace_name , cospace AS cospace_id, id AS call_id, starttime, callLegsMaxActive, durationSeconds, EndTime, cms_ip FROM cms_cdr_calls WHERE (cms_cdr_calls.name LIKE  '%" + form_cmsselection.confroom_filter.data + "%') ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
                #print("CMS VW: get dict")
        else:
            if not form_cmsselection.confroom_filter.data:
                rows_list = sql_request_dict(
                    "SELECT meeting_id, cms_cdr_calls.name AS cospace_name,cms_cdr_calls.cospace AS cospace_id, cms_cdr_calls.id AS call_id, cms_cdr_calls.starttime, cms_cdr_calls.callLegsMaxActive, cms_cdr_calls.durationSeconds, cms_cdr_calls.EndTime, cms_cdr_calls.cms_ip FROM cms_cdr_calls INNER JOIN cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip WHERE cms_servers.cluster='" + form_cmsselection.select_CMSCluster.data + "' ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
                #print("CMS VW: get dict")
            else:
                rows_list = sql_request_dict(
                    "SELECT meeting_id, cms_cdr_calls.name AS cospace_name,cms_cdr_calls.cospace AS cospace_id, cms_cdr_calls.id AS call_id, cms_cdr_calls.starttime, cms_cdr_calls.callLegsMaxActive, cms_cdr_calls.durationSeconds, cms_cdr_calls.EndTime, cms_cdr_calls.cms_ip FROM cms_cdr_calls INNER JOIN cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip WHERE cms_servers.cluster='" + form_cmsselection.select_CMSCluster.data + "'AND (cms_cdr_calls.name LIKE  '%" + form_cmsselection.confroom_filter.data + "%') ORDER BY starttime DESC LIMIT " + form_cmsselection.limit_field.data)
                #print("CMS VW: get dict")

        operationEndTime = datetime.now()
        operationDuration = str( operationEndTime - operationStartTime)
        console_output = "Done in " + operationDuration + "\n 		Searching compleate for:" + str(len(rows_list)) + " elements"

        for row in rows_list:
            if row["durationSeconds"]:
                row["durationSeconds"] = time.strftime("%H:%M:%S", time.gmtime(int(row["durationSeconds"])))


        return render_template(html_template, html_page_title=html_page_title,
                               console_output=console_output,
                               rows_list=rows_list,
                               formNAV=form_navigation,
                               formCMS=form_cmsselection)

    operationEndTime = datetime.now()
    operationDuration = str( operationEndTime - operationStartTime)
    console_output = "Нет активного запроса (" + operationDuration + ")"
    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           formNAV=form_navigation,
                           formCMS=form_cmsselection)

def cmscallviewer(call_id):

    operationStartTime = datetime.now()

    html_page_title = 'CMS Call Report'
    html_template = 'cisco_cmsview.html'
    #print("CMS CALLVW: request for callID: " + call_id)

    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        #print(console_output)
        return redirect(url_for(form_navigation.select_navigation.data))


    sql_request_string_select_basic = "SELECT DISTINCT callleg_id,remoteaddress,displayName,durationseconds,startTime,cms_ip,alarm_type,alarm_value,reason"
    sql_request_string_audio_video_codecs = ",rxAudio_codec,txAudio_codec,rxVideo_codec,txVideo_codec,txVideo_maxHeight,txVideo_maxWidth"
    sql_request_string_audio_statistics = ",rxAudio_packetLossBurst_duration,rxAudio_packetLossBurst_density,rxAudio_packetGap_duration,rxAudio_packetGap_density"
    sql_request_string_video_statistics = ",rxVideo_packetLossBurst_duration,rxVideo_packetLossBurst_density,rxVideo_packetGap_duration,rxVideo_packetGap_density"
    sql_request_string_call_type = ",guestConnection,callLeg_subtype"
    sql_request_string_from = " FROM cms_cdr_records WHERE call_id='" + call_id + "';"
    sql_request_result_string = sql_request_string_select_basic\
                                + sql_request_string_audio_video_codecs\
                                + sql_request_string_audio_statistics\
                                + sql_request_string_video_statistics\
                                + sql_request_string_call_type\
                                + sql_request_string_from

    rows_list = sql_request_dict(sql_request_result_string)
        #"SELECT DISTINCT callleg_id,remoteaddress,durationseconds,rxAudio_codec,txAudio_codec,rxVideo_codec,txVideo_codec,txVideo_maxHeight,txVideo_maxWidth,cms_ip,alarm_type,alarm_value FROM cms_cdr_records WHERE call_id='" + call_id + "';")

    #print("CMS CALLVW: get dict for callID:  " + call_id)

    operationEndTime = datetime.now()
    operationDuration = str( operationEndTime - operationStartTime)
    console_output = "Done in " + operationDuration
    for row in rows_list:
        if row["durationseconds"]:
            if is_digit(row["durationseconds"]):
                row["durationseconds"] = time.strftime("%H:%M:%S", time.gmtime(int(row["durationseconds"])))

    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           rows_list=rows_list,
                           formNAV=form_navigation)

def cmsmeetingviewer(meeting_id):

    operationStartTime = datetime.now()

    html_page_title = 'CMS Call Report'
    html_template = 'cisco_cmsview.html'
    #print("CMS CALLVW: request for callID: " + call_id)

    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        #print(console_output)
        return redirect(url_for(form_navigation.select_navigation.data))

    sql_request_string_select_basic = "SELECT r.callleg_id,r.remoteaddress,r.displayName,r.durationseconds,r.startTime,r.cms_ip,r.alarm_type,r.alarm_value,r.reason"
    sql_request_string_audio_video_codecs = ",r.rxAudio_codec,r.txAudio_codec,r.rxVideo_codec,r.txVideo_codec,r.txVideo_maxHeight,r.txVideo_maxWidth"
    sql_request_string_audio_statistics = ",r.rxAudio_packetLossBurst_duration,r.rxAudio_packetLossBurst_density,r.rxAudio_packetGap_duration,r.rxAudio_packetGap_density"
    sql_request_string_video_statistics = ",r.rxVideo_packetLossBurst_duration,r.rxVideo_packetLossBurst_density,r.rxVideo_packetGap_duration,r.rxVideo_packetGap_density"
    sql_request_string_call_type = ",r.guestConnection,r.callLeg_subtype"
    sql_request_string_from = " FROM cms_cdr_calls c INNER JOIN cms_cdr_records r ON r.call_id=c.id WHERE meeting_id='" + meeting_id + "';"

    sql_request_result_string = sql_request_string_select_basic\
                                + sql_request_string_audio_video_codecs\
                                + sql_request_string_audio_statistics\
                                + sql_request_string_video_statistics\
                                + sql_request_string_call_type\
                                + sql_request_string_from

    rows_list = sql_request_dict(sql_request_result_string)
        #"SELECT DISTINCT callleg_id,remoteaddress,durationseconds,rxAudio_codec,txAudio_codec,rxVideo_codec,txVideo_codec,txVideo_maxHeight,txVideo_maxWidth,cms_ip,alarm_type,alarm_value FROM cms_cdr_records WHERE call_id='" + call_id + "';")

    #print("CMS CALLVW: get dict for callID:  " + call_id)

    operationEndTime = datetime.now()
    operationDuration = str( operationEndTime - operationStartTime)
    console_output = "Done in " + operationDuration
    for row in rows_list:
        if row["durationseconds"]:
            if is_digit(row["durationseconds"]):
                row["durationseconds"] = time.strftime("%H:%M:%S", time.gmtime(int(row["durationseconds"])))

    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           rows_list=rows_list,
                           formNAV=form_navigation)

def cmscalllegviewer(callleg_id):

    operationStartTime = datetime.now()

    html_page_title = 'CMS CallLeg Report'
    html_template = 'cisco_cmspacketloss.html'
    #print("CMS CALLLEGVW: request for calllegID: " + callleg_id)

    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        #print("CMS CALLLEGVW: " + console_output)
        return redirect(url_for(form_navigation.select_navigation.data))

    #sql_request_string = "SELECT cms_cdr_calllegs.callleg_id,cms_cdr_calllegs.date,cms_cdr_calllegs.AudioPacketLossPercentageRX,cms_cdr_calllegs.AudioPacketLossPercentageTX,cms_cdr_calllegs.VideoPacketLossPercentageRX,cms_cdr_calllegs.VideoPacketLossPercentageTX,cms_cdr_records.remoteaddress FROM cms_cdr_calllegs INNER JOIN cms_cdr_records ON  cms_cdr_calllegs.callleg_id=cms_cdr_records.callleg_id WHERE cms_cdr_calllegs.callleg_id='" + callleg_id + "';")
    sql_request_string = """SELECT cms_cdr_calllegs.callleg_id,
                                   cms_cdr_calllegs.date,
                                   cms_cdr_calllegs.AudioPacketLossPercentageRX,
                                   cms_cdr_calllegs.AudioPacketLossPercentageTX,
                                   cms_cdr_calllegs.VideoPacketLossPercentageRX,
                                   cms_cdr_calllegs.VideoPacketLossPercentageTX,
                                   cms_cdr_calllegs.AudioRoundTripTimeTX,
                                   cms_cdr_calllegs.VideoRoundTripTimeTX,
                                   cms_cdr_records.remoteaddress,
                                   cms_cdr_records.displayName
                                   FROM cms_cdr_calllegs INNER JOIN cms_cdr_records ON  cms_cdr_calllegs.callleg_id=cms_cdr_records.callleg_id WHERE cms_cdr_calllegs.callleg_id='""" + callleg_id + "';"

    console_output = "Делаем запрос в БД"
    #print("CMS CALLLEGVW: " + console_output)
    rows_list = sql_request_dict(sql_request_string)

    if isinstance(rows_list, list):
        console_output = "rows_list is list "
        #print("CMS CALLLEGVW:" + console_output)
    else:
        console_output = "rows_list is not list, it is: " + str(type(rows_list))
        #print("CMS CALLLEGVW: " + console_output)
        #pprint(rows_list)

        operationEndTime = datetime.now()
        operationDuration = str( operationEndTime - operationStartTime)
        console_output = "There is no data for the request in DB. Done in " + operationDuration
        #print(console_output)
        return render_template(html_template, html_page_title=html_page_title,
                               console_output=console_output,
                               formNAV=form_navigation)


    # создаем листы значений по осям x и y для построения графиков
    AudioPacketLossPercentageRX_list = []
    AudioPacketLossPercentageTX_list = []
    VideoPacketLossPercentageRX_list = []
    VideoPacketLossPercentageTX_list = []
    AudioRoundTripTimeTX_list = []
    VideoRoundTripTimeTX_list = []
    date_list = []

    # заполняем листы из словаря с данными из БД
    for row in rows_list:
        AudioPacketLossPercentageRX_list.append(float(row["AudioPacketLossPercentageRX"]))
        AudioPacketLossPercentageTX_list.append(float(row["AudioPacketLossPercentageTX"]))
        VideoPacketLossPercentageRX_list.append(float(row["VideoPacketLossPercentageRX"]))
        VideoPacketLossPercentageTX_list.append(float(row["VideoPacketLossPercentageTX"]))
        AudioRoundTripTimeTX_list.append(int(row["AudioRoundTripTimeTX"]))
        VideoRoundTripTimeTX_list.append(int(row["VideoRoundTripTimeTX"]))
        date_list.append(datetime.strptime(row["date"], '%Y-%m-%d %H:%M:%S.%f'))


    # формируем словарь с максимальными значениями потерь
    max_loss_values = {
        "AudioRX": max(AudioPacketLossPercentageRX_list if AudioPacketLossPercentageRX_list else 0),
        "AudioTX": max(AudioPacketLossPercentageTX_list),
        "VideoRX": max(VideoPacketLossPercentageRX_list),
        "VideoTX": max(VideoPacketLossPercentageTX_list)
    }

    # формируем словарь с максимальными значениями rtt
    max_loss_values_rtt = {
        "AudioRTT": max(AudioRoundTripTimeTX_list if AudioRoundTripTimeTX_list else 0),
        "VideoRTT": max(VideoRoundTripTimeTX_list)
    }

    # создаем объект класса ColumnDataSource содержащий все данные графика потерь
    plot_source = ColumnDataSource(data=dict(
        date=date_list,
        AudioRX=AudioPacketLossPercentageRX_list,
        AudioTX=AudioPacketLossPercentageTX_list,
        VideoRX=VideoPacketLossPercentageRX_list,
        VideoTX=VideoPacketLossPercentageTX_list)
    )

    # создаем объект класса ColumnDataSource содержащий все данные графика RTT
    plot_source_rtt = ColumnDataSource(data=dict(
        date=date_list,
        AudioRTT=AudioRoundTripTimeTX_list,
        VideoRTT=VideoRoundTripTimeTX_list)
    )

    # создаем объект класса HoverTool со значениями из ColumnDataSource для всплывающих подсказок графика потерь
    hover_tool = HoverTool(
        tooltips=[
            ("Audio RX", "@AudioRX{([0]0.0)}"),
            ("Audio TX", "@AudioTX{([0]0.0)}"),
            ("Video RX", "@VideoRX{([0]0.0)}"),
            ("Video TX", "@VideoTX{([0]0.0)}")
        ],

        # режим отображения подсказки при наведении мышкой на график
        mode='mouse'
    )

    # создаем объект класса HoverTool со значениями из ColumnDataSource для всплывающих подсказок графика RTT
    hover_tool_rtt = HoverTool(
        tooltips=[
            ("Audio RTT", "@AudioRTT{([0]0.0)}"),
            ("Video RTT", "@VideoRTT{([0]0.0)}")
        ],

        # режим отображения подсказки при наведении мышкой на график
        mode='mouse'
    )

    # создаем объект класса figure описывающий график потерь
    p = figure(plot_width=1800, plot_height=250, x_axis_type="datetime")
    p.sizing_mode = "scale_width"
    # добавляем к объекту графика инструмент - объект всплывающих подсказок
    p.add_tools(hover_tool)
    # добавляем линии на график
    p.line(x="date", y="AudioRX", source=plot_source, line_width=2, color='#A6CEE3', legend_label='Audio RX')
    p.line(x="date", y="AudioTX", source=plot_source, line_width=2, color='#B2DF8A', legend_label='Audio TX')
    p.line(x="date", y="VideoRX", source=plot_source, line_width=2, color='#33A02C', legend_label='Video RX')
    p.line(x="date", y="VideoTX", source=plot_source, line_width=2, color='#FB9A99', legend_label='Video TX')
    # задаем формат отображения даты и времени на оси x для масштабирования
    p.xaxis.formatter = DatetimeTickFormatter(
        milliseconds=["%H:%M:%S.%3Ns"],
        seconds=["%H:%M:%S"],
        minsec=["%H:%M:%S"],
        minutes=["%H:%M:%S"],
        hourmin=["%H:%M:%S"],
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    # задаем угол наклона подписей с датами на оси x
    p.xaxis.major_label_orientation = pi / 4
    # формируем объекты содержащие html-код с графиком для web-страницы
    script, div = components(p)
    # формируем обект содержащий html-код с ссылками на библиотеки javascript
    resources = CDN.render()
    # создаем объект класса figure описывающий график RTT
    p_rtt = figure(plot_width=1800, plot_height=250, x_axis_type="datetime")
    p_rtt.sizing_mode = "scale_width"
    # добавляем к объекту графика инструмент - объект всплывающих подсказок
    p_rtt.add_tools(hover_tool_rtt)
    # добавляем линии на график
    p_rtt.line(x="date", y="AudioRTT", source=plot_source_rtt, line_width=2, color='#A6CEE3', legend_label='Audio RTT')
    p_rtt.line(x="date", y="VideoRTT", source=plot_source_rtt, line_width=2, color='#33A02C', legend_label='Video RTT')
    # задаем формат отображения даты и времени на оси x для масштабирования
    p_rtt.xaxis.formatter = DatetimeTickFormatter(
        milliseconds=["%H:%M:%S.%3Ns"],
        seconds=["%H:%M:%S"],
        minsec=["%H:%M:%S"],
        minutes=["%H:%M:%S"],
        hourmin=["%H:%M:%S"],
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    # задаем угол наклона подписей с датами на оси x
    p_rtt.xaxis.major_label_orientation = pi / 4
    # формируем объекты содержащие html-код с графиком для web-страницы
    script_rtt, div_rtt = components(p_rtt)
    operationEndTime = datetime.now()
    operationDuration = str( operationEndTime - operationStartTime)
    console_output = "Information for: " + rows_list[0]["displayName"] + ". Done in " + operationDuration
    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           formNAV=form_navigation,
                           div=div,
                           script=script,
                           resources=resources,
                           max_loss_values=max_loss_values,
                           div_rtt=div_rtt,
                           script_rtt=script_rtt,
                           max_loss_values_rtt=max_loss_values_rtt)

def cmsallcalllegsviewer(meeting_id):

    # Настройка логирования
    logger = logger_init('CMS_VIEWER', logging.DEBUG)

    operationStartTime = datetime.now()

    html_page_title = 'CMS CallLeg Report'
    html_template ='cisco_cmspacketloss_for_meeting.html'
    console_output = "================================== Выполняется запрос для  meetingID: " + meeting_id
    logger.debug("CMS All CallLegs viewer: " + console_output)

    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        logger.debug("CMS All CallLegs viewer: " + console_output)
        return redirect(url_for(form_navigation.select_navigation.data))

    # Получаем список CallLeg_ID для Meeting_ID
    console_output = "Делаем запрос в БД об участниках совещании " + meeting_id
    logger.debug("CMS All CallLegs viewer: " + console_output)
    sql_request_string = "SELECT r.callleg_id, r.displayName, r.date FROM cms_cdr_calls c INNER JOIN cms_cdr_records r ON r.call_id=c.id WHERE meeting_id='" + meeting_id + "' ORDER BY r.displayName, r.date;"
    calleg_list = sql_request_dict(sql_request_string)
    console_output = "Запрос в БД об участниках совещании выполнен"
    logger.debug("CMS All CallLegs viewer: " + console_output)

    # Получаем время начала и окончания конференции для выравнивания графиков
    console_output = "Делаем запрос в БД о времени совещания " + meeting_id
    logger.debug("CMS All CallLegs viewer: " + console_output)
    sql_request_string = "SELECT MIN(r.date) AS startTime, MAX(IFNULL((ADDDATE(r.date, INTERVAL r.durationSeconds SECOND)), CURRENT_TIMESTAMP(6))) AS endTime FROM cms_cdr_calls as c INNER JOIN cms_cdr_records as r ON r.call_id=c.id WHERE meeting_id='" + meeting_id + "';"
    conference_time_list = sql_request_dict(sql_request_string)
    console_output = "Запрос в БД о времени совещании выполнен"
    logger.debug("CMS All CallLegs viewer: " + console_output)

    start_time = conference_time_list[0]["startTime"]
    end_time = conference_time_list[0]["endTime"]
    console_output = "Время начала: " + start_time + ", время окончания: " + end_time
    logger.debug("CMS All CallLegs viewer: " + console_output)

    # Делаем цикл для подготовки всех графиков
    resources = ""
    plot_list = []

    for callleg in calleg_list:

        console_output = "Начинаем строить график для " + callleg["displayName"]
        logger.debug("CMS All CallLegs viewer: " + console_output)

        sql_request_string = """SELECT cms_cdr_calllegs.date,
                                       cms_cdr_calllegs.AudioPacketLossPercentageRX,
                                       cms_cdr_calllegs.AudioPacketLossPercentageTX,
                                       cms_cdr_calllegs.VideoPacketLossPercentageRX,
                                       cms_cdr_calllegs.VideoPacketLossPercentageTX                                    
                                       FROM cms_cdr_calllegs WHERE cms_cdr_calllegs.callleg_id='""" + callleg["callleg_id"] + "';"

        console_output = "Делаем запрос в БД для calleg_ID " + callleg["callleg_id"]
        logger.debug("CMS All CallLegs viewer: " + console_output)
        try:
            rows_list = sql_request_dict(sql_request_string)
        except BaseException as e:
            console_output = "======= Что за дичь творится для " + callleg["callleg_id"] + "?!"
            logger.error("CMS All CallLegs viewer: " + console_output)
            console_output = ("CMS All CallLegs viewer: " + "{!r}; callleginfo get exception ".format(e))
            logger.error(console_output)
            console_output = "Завершаем график для " + callleg["displayName"]
            logger.debug("CMS All CallLegs viewer: " + console_output)
            continue

        if isinstance(rows_list, list):
            console_output = "Тип полученного объекта rows_list - list "
            logger.debug("CMS All CallLegs viewer: " + console_output)
        else:
            console_output = "Тип полученного объекта rows_list не list, это: " + str(type(rows_list))
            logger.debug("CMS All CallLegs viewer: " + console_output)
            logger.debug("\n" + pformat(rows_list))

            operationEndTime = datetime.now()
            operationDuration = str( operationEndTime - operationStartTime)
            console_output = "В БД нет данных для этого участника. Промежуточное время " + operationDuration
            logger.debug("CMS All CallLegs viewer: " + console_output)
            continue

        # создаем листы значений по осям x и y для построения графиков
        AudioPacketLossPercentageRX_list = []
        AudioPacketLossPercentageTX_list = []
        VideoPacketLossPercentageRX_list = []
        VideoPacketLossPercentageTX_list = []
        date_list = []

        # заполняем листы из словаря с данными из БД
        for row in rows_list:
            AudioPacketLossPercentageRX_list.append(float(row["AudioPacketLossPercentageRX"]))
            AudioPacketLossPercentageTX_list.append(float(row["AudioPacketLossPercentageTX"]))
            VideoPacketLossPercentageRX_list.append(float(row["VideoPacketLossPercentageRX"]))
            VideoPacketLossPercentageTX_list.append(float(row["VideoPacketLossPercentageTX"]))
            date_list.append(datetime.strptime(row["date"], '%Y-%m-%d %H:%M:%S.%f'))

        # создаем объект класса ColumnDataSource содержащий все данные графика потерь
        plot_source = ColumnDataSource(data=dict(
            date=date_list,
            AudioRX=AudioPacketLossPercentageRX_list,
            AudioTX=AudioPacketLossPercentageTX_list,
            VideoRX=VideoPacketLossPercentageRX_list,
            VideoTX=VideoPacketLossPercentageTX_list)
        )

        # создаем объект класса HoverTool со значениями из ColumnDataSource для всплывающих подсказок графика потерь
        hover_tool = HoverTool(
            tooltips=[
                ("Audio RX", "@AudioRX{([0]0.0)}"),
                ("Audio TX", "@AudioTX{([0]0.0)}"),
                ("Video RX", "@VideoRX{([0]0.0)}"),
                ("Video TX", "@VideoTX{([0]0.0)}")
            ],

            # режим отображения подсказки при наведении мышкой на график
            mode='mouse'
        )

        # создаем объект класса figure описывающий график потерь
        p = figure(title=callleg["displayName"], plot_width=1800, plot_height=250, x_axis_type="datetime",
                   x_range=(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f'), datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')))
        p.sizing_mode = "scale_width"
        # добавляем к объекту графика инструмент - объект всплывающих подсказок
        p.add_tools(hover_tool)
        # добавляем линии на график
        p.line(x="date", y="AudioRX", source=plot_source, line_width=2, color='#A6CEE3', legend_label='Audio RX')
        p.line(x="date", y="AudioTX", source=plot_source, line_width=2, color='#B2DF8A', legend_label='Audio TX')
        p.line(x="date", y="VideoRX", source=plot_source, line_width=2, color='#33A02C', legend_label='Video RX')
        p.line(x="date", y="VideoTX", source=plot_source, line_width=2, color='#FB9A99', legend_label='Video TX')
        # задаем формат отображения даты и времени на оси x для масштабирования
        p.xaxis.formatter = DatetimeTickFormatter(
            milliseconds=["%H:%M:%S.%3Ns"],
            seconds=["%H:%M:%S"],
            minsec=["%H:%M:%S"],
            minutes=["%H:%M:%S"],
            hourmin=["%H:%M:%S"],
            hours=["%d %B %Y"],
            days=["%d %B %Y"],
            months=["%d %B %Y"],
            years=["%d %B %Y"],
        )
        # задаем угол наклона подписей с датами на оси x
        p.xaxis.major_label_orientation = pi / 4
        # формируем объекты содержащие html-код с графиком для web-страницы
        script, div = components(p)

        plot_list.append([script, div])

        # формируем обект содержащий html-код с ссылками на библиотеки javascript
        if not resources:
            resources = CDN.render()

        operationEndTime = datetime.now()
        operationDuration = str( operationEndTime - operationStartTime)
        console_output = "График для " + callleg["displayName"] + " построен. Промежуточное время " + operationDuration
        logger.debug("CMS All CallLegs viewer: " + console_output)
    operationEndTime = datetime.now()
    operationDuration = str( operationEndTime - operationStartTime)
    console_output = "Done in " + operationDuration
    logger.debug("CMS All CallLegs viewer: " + console_output)
    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           formNAV=form_navigation,
                           plot_list=plot_list,
                           resources=resources)

def cmsrecordingsviewer():
    # вывод списка записей

    # Настройка логирования
    logger = logger_init('CMS_VIEWER', logging.DEBUG)

    NETPATH = "\\\\192.168.12.195\\record\\"
    RECORD_FILE_EXTENTION = ".mp4"
    operationStartTime = datetime.now()

    html_page_title = 'CMS CDR Recordings Report'
    html_template = 'cisco_cmsrecordings.html'
    console_output = "request for recordings"
    logger.debug("CMS Recording viewer: " + console_output)

    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        print(console_output)
        return redirect(url_for(form_navigation.select_navigation.data))

    sql_request_result_string = "SELECT cms_cdr_calls.name, cms_cdr_calls.callLegsMaxActive, cms_cdr_calls.StartTime, cms_cdr_calls.durationSeconds, cms_cdr_recordings.path, cms_cdr_recordings.recording_id FROM cms_cdr_calls INNER JOIN cms_cdr_recordings ON cms_cdr_recordings.call_id=cms_cdr_calls.id ORDER BY cms_cdr_calls.StartTime DESC;"
    rows_list = sql_request_dict(sql_request_result_string)

    console_output = "get dict for call recordings"
    logger.debug("CMS Recording viewer: " + console_output)

    for row in rows_list:
        row["original_path"] = row["path"]
        #переводим секунлы в нормальное время
        if row["durationSeconds"]:
            if is_digit(row["durationSeconds"]):
                row["durationSeconds"] = time.strftime("%H:%M:%S", time.gmtime(int(row["durationSeconds"])))

        #формируем путь к файлу
        row["path"] = NETPATH + row["path"].replace("_","\\") + RECORD_FILE_EXTENTION

    operationEndTime = datetime.now()
    operationDuration = str(operationEndTime - operationStartTime)
    console_output = "Done in " + operationDuration
    logger.debug("CMS Recording viewer: " + console_output)
    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           rows_list=rows_list,
                           formNAV=form_navigation)
