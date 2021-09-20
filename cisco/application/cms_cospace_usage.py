import xmltodict
from pprint import pprint
from datetime import datetime, timedelta
import time
import logging.handlers
from flask import render_template, redirect, url_for
from application.sqlrequests import sql_request_dict
from application.forms import SelectNavigation, SelectCMSClusterForCospace, SelectCMSClusterForReport


def time_format(input_time):
    minutes, seconds = divmod(int(input_time),60)
    hours, minutes = divmod(minutes, 60)
    hms_time = (str(hours) + ":" + str(minutes) + ":" + str(seconds))
    result = hms_time
    return result

def time_format_with_days(input_time):
    #result = time.strftime("%d %H:%M:%S", time.gmtime(int(input_time)))
    result = str(timedelta(seconds=input_time))
    return result

def cms_cospace_usage():

    # Настройка логирования
    CMS_RECEIVER_LOG_FILE_NAME = "../logs/CMS_COSPACE_USAGE.log"
    CMS_RECEIVER_LOG_FILE_SIZE = 2048000
    CMS_RECEIVER_LOG_FILE_COUNT = 5

    # Диспетчер логов
    logger = logging.getLogger('CMS_COSPACE_USAGE')
    logger.setLevel(logging.DEBUG)

    # Обработчик логов - запись в файлы с перезаписью
    if not logger.handlers:
        console_output = ": no any handlers in Logger - create new one"
        print("CMS_COSPACE_USAGE " + console_output)



        rotate_file_handler = logging.handlers.RotatingFileHandler(CMS_RECEIVER_LOG_FILE_NAME,
                                                                   maxBytes=CMS_RECEIVER_LOG_FILE_SIZE,
                                                                   backupCount=CMS_RECEIVER_LOG_FILE_COUNT)
        rotate_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
        rotate_file_handler.setFormatter(formatter)
        logger.addHandler(rotate_file_handler)

    operation_start_time = datetime.now()
    html_page_title = 'CMS CoSpace Usage Report'
    html_template = 'cisco_cms_cospace_usage.html'
    form_cmsselection = SelectCMSClusterForCospace(csrf_enabled=False)
    form_navigation = SelectNavigation(csrf_enabled=False)
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        logger.debug(console_output)
        return redirect(url_for(form_navigation.select_navigation.data))

    if form_cmsselection.validate_on_submit():
            sql_request_result_string_mounth = """SELECT cms_cdr_calls.Name,COUNT(cms_cdr_calls.Name) AS count_mounth,
              SUM(cms_cdr_calls.durationSeconds) AS duration_mounth FROM cms_cdr_calls
              INNER JOIN  cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip 
              WHERE cms_cdr_calls.StartTime >= DATE(NOW()) - INTERVAL 30 DAY AND cms_servers.cluster 
              LIKE '"""+ form_cmsselection.select_CMSCluster.data +"""' AND NAME NOT LIKE 'Сове%' GROUP BY NAME ORDER BY NAME"""

            sql_request_result_string_last_week = """SELECT cms_cdr_calls.Name,COUNT(cms_cdr_calls.Name) AS count_last_week,
                SUM(cms_cdr_calls.durationSeconds) AS duration_last_week FROM cms_cdr_calls
                INNER JOIN  cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip 
                WHERE cms_cdr_calls.StartTime >= DATE(NOW()) - INTERVAL 7 DAY AND cms_servers.cluster 
                LIKE '""" + form_cmsselection.select_CMSCluster.data + """' AND NAME NOT LIKE 'Сове%' AND NAME NOT LIKE 'none' GROUP BY NAME ORDER BY NAME"""


            #Словарь с данными за месяц
            rows_list_mounth = sql_request_dict(sql_request_result_string_mounth)
            #перевести секунды в часы

            for row in rows_list_mounth:
                if row["duration_mounth"]:
                    row["duration_mounth"] = time_format(row["duration_mounth"])

            # Словарь с данными за неделю
            rows_list_last_week = sql_request_dict(sql_request_result_string_last_week)
            # перевести секунды в часы
            for row in rows_list_last_week:
                if row["duration_last_week"]:
                    row["duration_last_week"] = time_format(row["duration_last_week"])


            rows_list = rows_list_mounth
            for row in rows_list:
                for key in rows_list_last_week:
                    if row["Name"] == key["Name"]:
                        if key["count_last_week"]:
                            row["duration_last_week"] = key["duration_last_week"]
                            row["count_last_week"] = key["count_last_week"]

            operation_end_time = datetime.now()
            operation_duration = str( operation_end_time - operation_start_time)
            console_output = "Done in " + operation_duration
            logger.debug(console_output)
            return render_template(html_template, html_page_title=html_page_title,
                                   console_output=console_output,
                                   rows_list=rows_list,
                                   formNAV=form_navigation,
                                   formCMS=form_cmsselection)

    operation_end_time = datetime.now()
    operation_duration = str( operation_end_time - operation_start_time)
    console_output = "Нет активного запроса (" + operation_duration + ")"
    logger.debug(console_output)
    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           formNAV=form_navigation,
                           formCMS=form_cmsselection)

def add_new_value_to_average(count, current_avarege, new_value):
    result = (count - 1) / count * current_avarege + (new_value / count)
    return result

def cms_cospace_usage_by_cluster():

    # Настройка логирования
    CMS_RECEIVER_LOG_FILE_NAME = "../logs/CMS_COSPACE_CLUSTER_USAGE.log"
    CMS_RECEIVER_LOG_FILE_SIZE = 2048000
    CMS_RECEIVER_LOG_FILE_COUNT = 5

    # Диспетчер логов
    logger = logging.getLogger('CMS_COSPACE_CLUSTER_USAGE')
    logger.setLevel(logging.DEBUG)

    # Обработчик логов - запись в файлы с перезаписью
    if not logger.handlers:
        console_output = ": no any handlers in Logger - create new one"
        print("CMS_COSPACE_CLUSTER_USAGE " + console_output)



        rotate_file_handler = logging.handlers.RotatingFileHandler(CMS_RECEIVER_LOG_FILE_NAME,
                                                                   maxBytes=CMS_RECEIVER_LOG_FILE_SIZE,
                                                                   backupCount=CMS_RECEIVER_LOG_FILE_COUNT)
        rotate_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
        rotate_file_handler.setFormatter(formatter)
        logger.addHandler(rotate_file_handler)

    operation_start_time = datetime.now()
    html_page_title = 'CMS CoSpace Usage by cluster Report'
    html_template = 'cisco_cms_cospace_by_cluster_usage.html'
    form_cmsselection = SelectCMSClusterForReport(meta={'csrf': False})
    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        logger.debug(console_output)
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": form_navigation.select_navigation.data
        }
        return renderdata

    if form_cmsselection.validate_on_submit():
        sql_request_result_string = """SELECT cms_cdr_calls.Name,COUNT(cms_cdr_calls.Name) AS count_servers,cms_cdr_calls.meeting_id AS id,
          MAX(cms_cdr_calls.durationSeconds) AS duration,
          SUM(cms_cdr_calls.callLegsMaxActive) AS callLegs FROM cms_cdr_calls
          INNER JOIN cms_servers ON cms_cdr_calls.cms_ip=cms_servers.ip
          WHERE cms_cdr_calls.StartTime >= DATE(NOW()) - INTERVAL """ + str(form_cmsselection.integer_field.data) + """ DAY AND cms_servers.cluster
          LIKE '""" + form_cmsselection.select_CMSCluster.data + """' AND NAME NOT LIKE 'Сове%' AND cms_cdr_calls.meeting_id IS NOT NULL GROUP BY id ORDER BY NAME"""

        rows_list_period = sql_request_dict(sql_request_result_string)

        rows_list = {}
        for row in rows_list_period:

            if row["Name"]:
                row_name = (row["Name"])
            else:
                row_name = ""
            if row["duration"]:
                row_duration = int(row["duration"])
            else:
                row_duration = 0
            if row["count_servers"]:
                row_count_servers = int(row["count_servers"])
            else:
                row_count_servers = 0
            if row["callLegs"]:
                row_calllegs = int(row["callLegs"])
            else:
                row_calllegs = 0

            if row_name in rows_list:

                rows_list[row_name]["number_of_confs"] += 1
                rows_list[row_name]["avg_servers"] = add_new_value_to_average(rows_list[row_name]["number_of_confs"],
                                                                                          rows_list[row_name]["avg_servers"],
                                                                                          row_count_servers)

                rows_list[row_name]["avg_duration"] = add_new_value_to_average(rows_list[row_name]["number_of_confs"],
                                                                                          rows_list[row_name]["avg_duration"],
                                                                                          row_duration)
                if row_duration > rows_list[row["Name"]]["max_duration"]:
                    rows_list[row_name]["max_duration"] = row_duration
                rows_list[row_name]["sum_duration"] += row_duration

                rows_list[row_name]["avg_calllegs"] = add_new_value_to_average(rows_list[row_name]["number_of_confs"],
                                                                                          rows_list[row_name]["avg_calllegs"],
                                                                                          row_calllegs)
                if row_calllegs > rows_list[row["Name"]]["max_calllegs"]:
                    rows_list[row_name]["max_calllegs"] = row_calllegs

                rows_list[row_name]["sum_calllegs"] += row_calllegs

            else:
                rows_list[row_name] = row
                rows_list[row_name]["number_of_confs"] = 1
                rows_list[row_name]["avg_servers"] = row_count_servers
                rows_list[row_name]["avg_duration"] = row_duration
                rows_list[row_name]["max_duration"] = row_duration
                rows_list[row_name]["sum_duration"] = row_duration
                rows_list[row_name]["avg_calllegs"] = row_calllegs
                rows_list[row_name]["max_calllegs"] = row_calllegs
                rows_list[row_name]["sum_calllegs"] = row_calllegs

        #перевести секунды в часы
        for row in rows_list.values():
            if row["avg_duration"]:
                print(f'avg_duration before: {row["avg_duration"]}')
                row["avg_duration"] = time_format_with_days(round(row["avg_duration"]))
                print(f'avg_duration after: {row["avg_duration"]}')
            if row["max_duration"]:
                print(f'max_duration before: {row["max_duration"]}')
                row["max_duration"] = time_format_with_days(row["max_duration"])
                print(f'max_duration after: {row["max_duration"]}')
            if row["sum_duration"]:
                print(f'sum_duration before: {row["sum_duration"]}')
                row["sum_duration"] = time_format_with_days(row["sum_duration"])
                print(f'sum_duration after: {row["sum_duration"]}')
            if row["avg_servers"]:
                row["avg_servers"] = round(row["avg_servers"], 1)
            if row["avg_calllegs"]:
                row["avg_calllegs"] = round(row["avg_calllegs"], 1)


        operation_end_time = datetime.now()
        operation_duration = str( operation_end_time - operation_start_time)
        console_output = "Done in " + operation_duration
        logger.debug(console_output)
        return render_template(html_template, html_page_title=html_page_title,
                               console_output=console_output,
                               rows_list=rows_list.values(),
                               formNAV=form_navigation,
                               formCMS=form_cmsselection)
    else:
        if form_cmsselection.integer_field.errors:
            console_output = " ".join(form_cmsselection.integer_field.errors)
            operation_end_time = datetime.now()
            operation_duration = str(operation_end_time - operation_start_time)
            logger.debug(console_output)
            return render_template(html_template, html_page_title=html_page_title,
                                   console_output=console_output,
                                   formNAV=form_navigation,
                                   formCMS=form_cmsselection)

    operation_end_time = datetime.now()
    operation_duration = str( operation_end_time - operation_start_time)
    console_output = "Нет активного запроса (" + operation_duration + ")"
    logger.debug(console_output)
    return render_template(html_template, html_page_title=html_page_title,
                           console_output=console_output,
                           formNAV=form_navigation,
                           formCMS=form_cmsselection)