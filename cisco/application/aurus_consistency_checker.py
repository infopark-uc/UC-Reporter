import requests
import xmltodict
import collections
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectCUCMCluster
from application.sqlrequests import sql_request_dict
from datetime import datetime
from pprint import pprint


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

    form_cluster_selection = SelectCUCMCluster(meta={'csrf': False})
    if form_cluster_selection.validate_on_submit():

        auth_data_list = sql_request_dict(
            "SELECT cm_ip,cm_username,cm_password FROM cm_servers_list WHERE cluster='" + form_cluster_selection.select_cluster.data + "'")  # получаем лист словарей

        cucm_ip_address = str(auth_data_list[0]['cm_ip'])
        cucm_login = str(auth_data_list[0]['cm_username'])
        cucm_password = str(auth_data_list[0]['cm_password'])

        # CUCM URL's
        cucm_url = "https://" + cucm_ip_address + ":8443/axl/"

        console_output = cucm_url + "\n"
        print(console_output)

        # V12 CUCM Headers
        headers11query = {'Content-Type': 'text/xml', 'SOAPAction': 'CUCM:DB ver=11.5 executeSQLQuery'}

        # ----------------------------------------------------------
        # Get information about lines with recorded option from CUCM
        # ----------------------------------------------------------

        msg_begin = """
               <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/11.5">
                   <soapenv:Header/>
                   <soapenv:Body>
                       <ns:executeSQLQuery>
                           <sql>"""
        msg_query = """select rec.name,tm.name as devicetype,d.name as devicename,n.dnorpattern,n.description,trec.name AS recflag from recordingdynamic AS rd 
                        INNER JOIN devicenumplanmap AS mdn ON mdn.pkid==rd.fkdevicenumplanmap
                        INNER JOIN numplan AS n ON n.pkid==mdn.fknumplan
                        INNER JOIN typerecordingflag AS trec ON trec.enum==rd.tkrecordingflag 
                        INNER JOIN device AS d ON d.pkid=mdn.fkdevice
                        INNER JOIN typemodel as tm on d.tkmodel = tm.enum
                        INNER JOIN recordingprofile as rec on mdn.fkrecordingprofile = rec.pkid"""
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
            console_output = "Ошибка соединения с сервером " + cucm_ip_address
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "ucreporter_aurus.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_cluster_selection": form_cluster_selection
            }
            return renderdata

        except:
            console_output = "Что-то пошло не так при подключении пользователя " + cucm_login + " к серверу " + cucm_ip_address
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "ucreporter_aurus.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_cluster_selection": form_cluster_selection
            }
            return renderdata

        # Check is answer is successful
        if post.status_code == 401:
            console_output = "Пользователь " + cucm_login + " не авторизован для подключения к серверу " + cucm_ip_address
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "ucreporter_aurus.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_cluster_selection": form_cluster_selection
            }
            return renderdata

        if post.status_code != 200:
            console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "ucreporter_aurus.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_cluster_selection": form_cluster_selection
            }
            return renderdata

        # Convert output to Dict
        console_output = "Данные получены из CUCM " + cucm_ip_address
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
                    "html_template": "ucreporter_aurus.html",
                    "html_page_title": html_page_title,
                    "console_output": console_output,
                    "form_navigation": form_navigation,
                    "form_cluster_selection": form_cluster_selection
                }
                return renderdata
        else:
            console_output = "DN с включеной записью не найдено"
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "ucreporter_aurus.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_cluster_selection": form_cluster_selection
            }
            return renderdata

        console_output = "Найдено записей: " + str(len(rows_list))
        print(console_output)

        pprint(rows_list)



        operationEndTime = datetime.now()
        operationDuration = str(operationEndTime - operationStartTime)
        console_output = "Done in " + operationDuration


        renderdata = {
            "rendertype": "success",
            "html_template": "ucreporter_aurus.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_cluster_selection": form_cluster_selection,
            "rows_list": rows_list
        }
        return renderdata

    renderdata = {
        "rendertype": "null",
        "html_template": "ucreporter_aurus.html",
        "html_page_title": html_page_title,
        "console_output": console_output,
        "form_navigation": form_navigation,
        "form_cluster_selection": form_cluster_selection
    }
    return renderdata


def get_dict_from_cucm(cucm_url, headers11query, cucm_login, cucm_password, sql_query):
    # ----------------------------------------------------------
    # Get information about lines with recorded option from CUCM
    # ----------------------------------------------------------

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
        console_output = "Ошибка соединения с сервером " + cucm_ip_address
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "html_template": "ucreporter_aurus.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_cluster_selection": form_cluster_selection
        }
        return renderdata

    except:
        console_output = "Что-то пошло не так при подключении пользователя " + cucm_login + " к серверу " + cucm_ip_address
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "html_template": "ucreporter_aurus.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_cluster_selection": form_cluster_selection
        }
        return renderdata

    # Check is answer is successful
    if post.status_code == 401:
        console_output = "Пользователь " + cucm_login + " не авторизован для подключения к серверу " + cucm_ip_address
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "html_template": "ucreporter_aurus.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_cluster_selection": form_cluster_selection
        }
        return renderdata

    if post.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "html_template": "ucreporter_aurus.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_cluster_selection": form_cluster_selection
        }
        return renderdata

    # Convert output to Dict
    console_output = "Данные получены из CUCM " + cucm_ip_address
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
                "html_template": "ucreporter_aurus.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_cluster_selection": form_cluster_selection
            }
            return renderdata
    else:
        console_output = "DN с включеной записью не найдено"
        print(console_output)
        renderdata = {
            "rendertype": "null",
            "html_template": "ucreporter_aurus.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_cluster_selection": form_cluster_selection
        }
        return renderdata

    console_output = "Найдено записей: " + str(len(rows_list))
    print(console_output)

    pprint(rows_list)