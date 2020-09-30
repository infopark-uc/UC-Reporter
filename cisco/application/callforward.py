import requests
import xmltodict
import collections
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectSearchType, SelectForwardSearchType
from application.sqlrequests import sql_request_dict

def render():
    SEARCH_BY_DN = "DN"
    SEARCH_BY_TRANSFER = "Transfer"
    html_page_title = 'CUCM CallForward Report'
    # Temporary values
    console_output = "Нет активного запроса"
    form_navigation = SelectNavigation(csrf_enabled=False)
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        print(console_output)
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": form_navigation.select_navigation.data
        }
        return renderdata

    choise_data = sql_request_dict(
            "SELECT cluster,description FROM cm_servers_list")
    form_search = SelectForwardSearchType(csrf_enabled=False)
    form_search.select_region.choices = [(choise["cluster"], choise["description"]) for choise in choise_data]

    if form_search.validate_on_submit():
        console_output = form_search.select_region.data + " " + form_search.select_field.data + " " + form_search.string_field.data

        auth_data_list = sql_request_dict(
            "SELECT cm_ip,cm_username,cm_password FROM cm_servers_list WHERE cluster='" + form_search.select_region.data + "'")  # получаем лист словарей

        cucm_ip_address = str(auth_data_list[0]['cm_ip'])
        cucm_login = str(auth_data_list[0]['cm_username'])
        cucm_password = str(auth_data_list[0]['cm_password'])

        # CUCM URL's
        cucm_url = "https://" + cucm_ip_address + ":8443/axl/"
        console_output = cucm_url + "\n"
        #print(console_output)

        # V12 CUCM Headers
        headers11query = {'Content-Type': 'text/xml', 'SOAPAction': 'CUCM:DB ver=11.5 executeSQLQuery'}

        if form_search.select_field.data == SEARCH_BY_DN:
            msg_begin = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/11.5">
                <soapenv:Header/>
                <soapenv:Body>
                    <ns:executeSQLQuery>
                        <sql>
select n.dnorpattern, cfd.cfadestination, cfd.cfavoicemailenabled
from numplan n inner join callforwarddynamic as cfd on cfd.fknumplan=n.pkid
where n.dnorpattern like '"""
            msg_end = """%' order by n.dnorpattern
                        </sql>
                    </ns:executeSQLQuery>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            msg = msg_begin + form_search.string_field.data + msg_end
        elif form_search.select_field.data == SEARCH_BY_TRANSFER:
            msg_begin = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/11.5">
                <soapenv:Header/>
                <soapenv:Body>
                    <ns:executeSQLQuery>
                        <sql>select n.dnorpattern, cfd.cfadestination, cfd.cfavoicemailenabled
from numplan n inner join callforwarddynamic as cfd on cfd.fknumplan=n.pkid
where cfd.cfadestination like '"""
            msg_end = """%' order by n.dnorpattern
                        </sql>
                    </ns:executeSQLQuery>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            msg = msg_begin + form_search.string_field.data + msg_end
            console_output = msg + "\n"
            #print(console_output)

        # disable warning about untrusted certs
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Create the Requests Connection
        try:
            post = requests.post(cucm_url, data=msg.encode('utf-8'), headers=headers11query, verify=False,
                                 auth=(cucm_login, cucm_password))
        except requests.exceptions.ConnectionError:
            console_output = "Ошибка соединения с сервером " + cucm_ip_address
            #print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_callforward.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search
            }
            return renderdata

        except:
            console_output = "Что-то пошло не так при подключении пользователя " + cucm_login + " к серверу " + cucm_ip_address
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_callforward.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search
            }
            return renderdata

        # Check is answer is successful
        if post.status_code == 401:
            console_output = "Пользователь " + cucm_login + " не авторизован для подключения к серверу " + cucm_ip_address
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_callforward.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search
            }
            return renderdata

        if post.status_code != 200:
            console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_callforward.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search
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
                console_output = "Телефонов соответсвующих запросу не найдено"
                print(console_output)
                renderdata = {
                    "rendertype": "null",
                    "html_template": "cisco_callforward.html",
                    "html_page_title": html_page_title,
                    "console_output": console_output,
                    "form_navigation": form_navigation,
                    "form_search": form_search
                }
                return renderdata

        else:
            console_output = "Телефонов соответсвующих запросу не найдено"
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_callforward.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search
            }
            return renderdata

        console_output = "Найдено записей: " + str(len(rows_list))
        print(console_output)
        renderdata = {
            "rendertype": "success",
            "html_template": "cisco_callforward.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_search" : form_search,
            "rows_list": rows_list
        }
        print(rows_list)
        return renderdata

    else:
        if form_search.string_field.errors:
            console_output = " ".join(form_search.string_field.errors)
            print(console_output)

    renderdata = {
        "rendertype": "null",
        "html_template": "cisco_callforward.html",
        "html_page_title": html_page_title,
        "console_output": console_output,
        "form_navigation": form_navigation,
        "form_search": form_search
    }
    return renderdata
