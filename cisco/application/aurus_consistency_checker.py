import requests
import xmltodict
import collections
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectCUCMCluster
from application.sqlrequests import sql_request_dict
from datetime import datetime
from pprint import pprint

def get_dict_from_cucm(cucm_url, headers11query, cucm_login, cucm_password, sql_query):

    msg_begin = """
           <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/11.5">
               <soapenv:Header/>
               <soapenv:Body>
                   <ns:executeSQLQuery>
                       <sql>"""
    msg_query = sql_query
    msg_end = """
                       </sql>
                   </ns:executeSQLQuery>
               </soapenv:Body>
           </soapenv:Envelope>"""

    msg = msg_begin + msg_query + msg_end
    console_output = msg + "\n"
    print(console_output)

    # disable warning about untrusted certs
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create the Requests Connection
    try:
        post = requests.post(cucm_url, data=msg.encode('utf-8'), headers=headers11query, verify=False,
                             auth=(cucm_login, cucm_password))
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + cucm_url
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    except:
        console_output = "Что-то пошло не так при подключении пользователя " + cucm_login + " к серверу " + cucm_url

        print(console_output)

        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    # Check is answer is successful
    if post.status_code == 401:
        console_output = "Пользователь " + cucm_login + " не авторизован для подключения к серверу " + cucm_ip_address
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    if post.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    # Convert output to Dict
    console_output = "Данные получены из CUCM " + cucm_url
    print(console_output)

    xml_dict = xmltodict.parse(post.text)

    # Get Dict with phones
    if type(xml_dict["soapenv:Envelope"]["soapenv:Body"]["ns:executeSQLQueryResponse"][
                "return"]) is collections.OrderedDict:
        if "row" in xml_dict["soapenv:Envelope"]["soapenv:Body"]["ns:executeSQLQueryResponse"]["return"]:
            if type(xml_dict["soapenv:Envelope"]["soapenv:Body"]["ns:executeSQLQueryResponse"]["return"][
                        "row"]) is list:
                rows_list = xml_dict["soapenv:Envelope"]["soapenv:Body"]["ns:executeSQLQueryResponse"]["return"][
                    "row"]
            elif type(xml_dict["soapenv:Envelope"]["soapenv:Body"]["ns:executeSQLQueryResponse"]["return"][
                          "row"]) is collections.OrderedDict:
                rows_list = [
                    xml_dict["soapenv:Envelope"]["soapenv:Body"]["ns:executeSQLQueryResponse"]["return"]["row"]]
        else:
            console_output = "DN с включеной записью не найдено"
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "console_output": console_output,
            }
            return renderdata
    else:
        console_output = "DN с включеной записью не найдено"
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    console_output = "Найдено записей: " + str(len(rows_list))
    print(console_output)

    renderdata = {
        "rendertype": "success",
        "console_output": console_output,
        "rows_list": rows_list
    }
    return renderdata

def get_dict_from_aurus(phoneup_url, phoneup_login, phoneup_password):

    # disable warning about untrusted certs
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create the Requests Connection
    try:
        get = requests.get(phoneup_url, verify=False, auth=(phoneup_login, phoneup_password))
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + phoneup_url
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    except:
        console_output = "Что-то пошло не так при подключении пользователя " + cucm_login + " к серверу " + phoneup_url

        print(console_output)

        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    # Check is answer is successful
    if get.status_code == 401:
        console_output = "Пользователь " + cucm_login + " не авторизован для подключения к серверу " + phoneup_url
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    if get.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    # Convert output to Dict
    console_output = "Данные получены из PhoneUP " + phoneup_url
    print(console_output)

    rows_list = json.loads(get.text)

    # Get Dict with phones
    if len(rows_list) == 0:
        console_output = "Устройств активированных для модуля запись в PhoneUP не найдено"
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "console_output": console_output,
        }
        return renderdata

    console_output = "Найдено записей: " + str(len(rows_list))
    print(console_output)

    renderdata = {
        "rendertype": "success",
        "console_output": console_output,
        "rows_list": rows_list
    }
    return renderdata

def aurus_consistency_check():

    operationStartTime = datetime.now()

    console_output = "Consistency check started"
    print(console_output)

    html_page_title = 'CUCM with Aurus consistency report'

    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": form_navigation.select_navigation.data
        }
        return renderdata

    console_output = "Creating cluster selection form"
    print(console_output)
    choice_data = sql_request_dict("SELECT cluster,description FROM cm_servers_list")
    form_cluster_selection = SelectCUCMCluster(meta={'csrf': False})
    form_cluster_selection.select_cluster.choices = [(choice["cluster"], choice["description"]) for choice in choice_data]
    if form_cluster_selection.validate_on_submit():

        auth_data_list = sql_request_dict(
            "SELECT cm_ip,cm_username,cm_password,phoneup_ip,phoneup_username,phoneup_password,phoneup_app_user FROM cm_servers_list WHERE cluster='" + form_cluster_selection.select_cluster.data + "'")  # получаем лист словарей

        cucm_ip_address = str(auth_data_list[0]['cm_ip'])
        cucm_login = str(auth_data_list[0]['cm_username'])
        cucm_password = str(auth_data_list[0]['cm_password'])
        phoneup_ip_address = str(auth_data_list[0]['phoneup_ip'])
        phoneup_login = str(auth_data_list[0]['phoneup_username'])
        phoneup_password = str(auth_data_list[0]['phoneup_password'])
        phoneup_app_user = str(auth_data_list[0]['phoneup_app_user'])

        # CUCM URL's
        cucm_url = "https://" + cucm_ip_address + ":8443/axl/"

        # V12 CUCM Headers
        headers11query = {'Content-Type': 'text/xml', 'SOAPAction': 'CUCM:DB ver=11.5 executeSQLQuery'}

        # ----------------------------------------------------------
        # Get information about lines with recorded option from CUCM
        # ----------------------------------------------------------
        sql_query = """select rec.name,tm.name as devicetype,d.name as devicename,n.dnorpattern,n.description,trec.name AS recflag from recordingdynamic AS rd 
                        INNER JOIN devicenumplanmap AS mdn ON mdn.pkid==rd.fkdevicenumplanmap
                        INNER JOIN numplan AS n ON n.pkid==mdn.fknumplan
                        INNER JOIN typerecordingflag AS trec ON trec.enum==rd.tkrecordingflag 
                        INNER JOIN device AS d ON d.pkid=mdn.fkdevice
                        INNER JOIN typemodel as tm on d.tkmodel = tm.enum
                        INNER JOIN recordingprofile as rec on mdn.fkrecordingprofile = rec.pkid"""

        renderdata = get_dict_from_cucm(cucm_url, headers11query, cucm_login, cucm_password, sql_query)

        if renderdata["rendertype"] == "success":
            devices_with_enabled_record_list = renderdata["rows_list"]
        else:
            devices_with_enabled_record_list = {}

        operationEndTime = datetime.now()
        operationDuration = str(operationEndTime - operationStartTime)
        console_output = " (Промежуточный результат " + operationDuration + ")"
        print(console_output)

        # -----------------------------------------------------------
        # Get information about devices in application user "phoneup"
        # -----------------------------------------------------------
        sql_query = """select n.dnorpattern,mdn.display,tm.name as devicetype,device.name as devicename from applicationuserdevicemap
                                INNER JOIN applicationuser ON applicationuser.pkid = applicationuserdevicemap.fkapplicationuser
                                INNER JOIN devicenumplanmap AS mdn ON mdn.fkdevice=applicationuserdevicemap.fkdevice
                                INNER JOIN numplan AS n ON n.pkid==mdn.fknumplan
                                INNER JOIN device ON device.pkid=applicationuserdevicemap.fkdevice
                                INNER JOIN typemodel as tm on device.tkmodel = tm.enum
                                where applicationuser.name = '""" + phoneup_app_user + "' AND tm.name NOT LIKE '%CTI%'"

        renderdata = get_dict_from_cucm(cucm_url, headers11query, cucm_login, cucm_password, sql_query)

        if renderdata["rendertype"] == "success":
            devices_in_application_user_list = renderdata["rows_list"]
        else:
            devices_in_application_user_list = {}

        operationEndTime = datetime.now()
        operationDuration = str(operationEndTime - operationStartTime)
        console_output = " (Промежуточный результат " + operationDuration + ")"
        print(console_output)

        # -------------------------------------------------------------
        # Get information about devices enabled for record from PhoneUP
        # -------------------------------------------------------------

        # phonUP URL's
        phoneup_url = "http://" + phoneup_ip_address + "/coreapi/api/Core/GetActivatedDevices?moduleName=record"

        console_output = phoneup_url + "\n"
        print(console_output)

        renderdata = get_dict_from_aurus(phoneup_url, phoneup_login, phoneup_password)

        if renderdata["rendertype"] == "success":
            phoneup_activated_devices_list = renderdata["rows_list"]
        else:
            phoneup_activated_devices_list = {}

        operationEndTime = datetime.now()
        operationDuration = str(operationEndTime - operationStartTime)
        console_output = " (Промежуточный результат " + operationDuration + ")"
        print(console_output)

        # -------------------------------------------------------------
        # Get information about lines enabled for record from PhoneUP
        # -------------------------------------------------------------

        # phonUP URL's
        phoneup_url = "http://" + phoneup_ip_address + "/coreapi/api/Record/GetRecordedLines"

        renderdata = get_dict_from_aurus(phoneup_url, phoneup_login, phoneup_password)

        if renderdata["rendertype"] == "success":
            phoneup_activated_lines_list = renderdata["rows_list"]
        else:
            phoneup_activated_lines_list = {}

        operationEndTime = datetime.now()
        operationDuration = str(operationEndTime - operationStartTime)
        console_output = " (Промежуточный результат " + operationDuration + ")"
        print(console_output)

        result_dict = {}

        console_output = "Начинаем формировать итоговый словарь"
        print(console_output)

        # Add enabled devices to result dict
        for enabled_device in devices_with_enabled_record_list:
            result_dict[enabled_device["devicename"]] = {
                "devicetype": enabled_device["devicetype"],
                "devicename": enabled_device["devicename"],
                "username": enabled_device["description"],
                "dnorpattern": enabled_device["dnorpattern"],
                "cucmline_dnorpattern": enabled_device["dnorpattern"]
            }

        console_output = "Информация о линиях с включенной записью в CUCM добавлена в итоговый словарь"
        print(console_output)

        # Add devices from application user to result dict
        for device_in_app in devices_in_application_user_list:
            if device_in_app["devicename"] in result_dict:
                result_dict[device_in_app["devicename"]]["app_devicename"] = device_in_app["devicename"]
                result_dict[device_in_app["devicename"]]["app_username"] = device_in_app["display"]
                result_dict[device_in_app["devicename"]]["app_dnorpattern"] = device_in_app["dnorpattern"]
                result_dict[device_in_app["devicename"]]["app_devicetype"] = device_in_app["devicetype"]
            else:
                result_dict[device_in_app["devicename"]] = {
                    "devicetype": device_in_app["devicetype"],
                    "devicename": device_in_app["devicename"],
                    "username": device_in_app["display"],
                    "dnorpattern": device_in_app["dnorpattern"],
                    "app_devicename": device_in_app["devicename"],
                    "app_username": device_in_app["display"],
                    "app_dnorpattern": device_in_app["dnorpattern"],
                    "app_devicetype": device_in_app["devicetype"]
                }

        console_output = "Информация об устройствах из Application User в CUCM добавлена в итоговый словарь"
        print(console_output)

        # Add activated devices from PhoneUP to result dict
        for phoneup_activated_device in phoneup_activated_devices_list:
            if phoneup_activated_device["Name"] in result_dict:
                result_dict[phoneup_activated_device["Name"]]["phoneup_devicename"] = phoneup_activated_device["Name"]
                result_dict[phoneup_activated_device["Name"]]["phoneup_devicetype"] = phoneup_activated_device["Type"]
            else:
                if len(phoneup_activated_device["PhoneLines"]) > 0:
                    phoneup_activated_device_line = phoneup_activated_device["PhoneLines"][0]
                else:
                    phoneup_activated_device_line = ""
                result_dict[phoneup_activated_device["Name"]] = {
                    "devicetype": phoneup_activated_device["Type"],
                    "devicename": phoneup_activated_device["Name"],
                    "dnorpattern": phoneup_activated_device_line,
                    "phoneup_devicename": phoneup_activated_device["Name"],
                    "phoneup_devicetype": phoneup_activated_device["Type"]
                }

        console_output = "Информация об активированных устройствах в PhoneUP добавлена в итоговый словарь"
        print(console_output)

        # Add recorded lines from PhoneUP to result dict
        # Перебираем в цикле все полученниые линии включенные на запись в Фонапе
        for phoneup_activated_lines in phoneup_activated_lines_list:
            # Перебираем в цикле все существующие записи итогового словоря чтобы найти нет ли такой линии
            line_was_found = False
            for record in result_dict.values():
                # Проверяем есть ли записываемая линия в записи итогового словаря
                if record["dnorpattern"] == phoneup_activated_lines["PhoneLine"]:
                    # Записываемая линия уже есть в записи итогового словаря, тогда
                    # Дописываем значения в существующую запись
                    record["line_dnorpattern"] = phoneup_activated_lines["PhoneLine"]
                    # Проверяем есть ли информация об устройстве записываемой линии
                    if len(phoneup_activated_lines["DeviceNames"]) > 0:
                        phoneup_activated_line_device = phoneup_activated_lines["DeviceNames"][0]
                    else:
                        phoneup_activated_line_device = ""
                    record["line_devicename"] = phoneup_activated_line_device
                    # Проверяем есть ли информация о контактах записываемой линии
                    if len(phoneup_activated_lines["Contacts"]) > 0:
                        phoneup_activated_line_contact = phoneup_activated_lines["Contacts"][0]
                    else:
                        phoneup_activated_line_contact = ""
                    record["line_username"] = phoneup_activated_line_contact
                    line_was_found = True
                    break
            if not line_was_found:
                # Записываемой линии нет в итоговом словаре, тогда
                # Создаем запись
                # Проверяем есть ли информация об устройстве записываемой линии
                if len(phoneup_activated_lines["DeviceNames"]) > 0:
                    if phoneup_activated_lines["DeviceNames"][0] != "Unknown":
                        phoneup_activated_line_device = phoneup_activated_lines["DeviceNames"][0]
                    else:
                        phoneup_activated_line_device = ""
                else:
                    phoneup_activated_line_device = ""
                # Проверяем есть ли информация о контактах записываемой линии
                if len(phoneup_activated_lines["Contacts"]) > 0:
                    if phoneup_activated_lines["Contacts"][0] != "Unknown":
                        phoneup_activated_line_contact = phoneup_activated_lines["Contacts"][0]
                    else:
                        phoneup_activated_line_contact = ""
                else:
                    phoneup_activated_line_contact = ""
                result_dict[phoneup_activated_lines["PhoneLine"]] = {
                    "devicename": phoneup_activated_line_device,
                    "username": phoneup_activated_line_contact,
                    "dnorpattern": phoneup_activated_lines["PhoneLine"],
                    "line_devicename": phoneup_activated_line_device,
                    "line_dnorpattern": phoneup_activated_lines["PhoneLine"],
                    "line_username": phoneup_activated_line_contact
                }

        console_output = "Информация о включенных на запись линиях в PhoneUP добавлена в итоговый словарь"
        print(console_output)

        # console_output = "result_dict: "
        # print(console_output)
        # pprint(result_dict)


        operationEndTime = datetime.now()
        operationDuration = str(operationEndTime - operationStartTime)
        console_output = "Найдено записей: " + str(len(result_dict)) + " (Done in " + operationDuration + ")"

        renderdata = {
            "rendertype": "success",
            "html_template": "ucreporter_aurus.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_cluster_selection": form_cluster_selection,
            "rows_list": result_dict
        }

        return renderdata

    console_output = "Нет активного запроса"

    renderdata = {
        "rendertype": "null",
        "html_template": "ucreporter_aurus.html",
        "html_page_title": html_page_title,
        "console_output": console_output,
        "form_navigation": form_navigation,
        "form_cluster_selection": form_cluster_selection
    }
    return renderdata


