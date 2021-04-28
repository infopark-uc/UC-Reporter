import requests
import xmltodict
import collections
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectSearchType
from application.sqlrequests import sql_request_dict

def usersreport():
    SEARCH_BY_DN = "Number"
    SEARCH_BY_USER = "User"

    html_page_title = 'CUCM Users report'

    # Temporary values
    console_output = "Нет активного запроса"

    form_navigation = SelectNavigation(meta={'csrf': False})
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
    form_search = SelectSearchType(csrf_enabled=False)
    form_search.select_region.choices = [(choise["cluster"], choise["description"]) for choise in choise_data]
    #form_search = SelectSearchType(meta={'csrf': False})
    if form_search.validate_on_submit():
        console_output = form_search.select_region.data + " " + form_search.select_field.data + " " + form_search.string_field.data

        auth_data_list = sql_request_dict(
            "SELECT cm_ip,cm_username,cm_password FROM cm_servers_list WHERE cluster='"+ form_search.select_region.data + "'")  # получаем лист словарей

        cucm_ip_address = str(auth_data_list[0]['cm_ip'])
        cucm_login = str(auth_data_list[0]['cm_username'])
        cucm_password = str(auth_data_list[0]['cm_password'])



        # CUCM URL's
        cucm_url = "https://" + cucm_ip_address + ":8443/axl/"

        console_output = cucm_url + "\n"
        print(console_output)

        # V12 CUCM Headers
        headers11query = {'Content-Type': 'text/xml', 'SOAPAction': 'CUCM:DB ver=11.5 executeSQLQuery'}

        if form_search.select_field.data == SEARCH_BY_DN:
            msg_begin = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/11.5">
                <soapenv:Header/>
                <soapenv:Body>
                    <ns:executeSQLQuery>
                        <sql>select d.name,tm.name as devtype,d.description as description,n.dnorpattern as DN,rp.name as partition,c.name as css,display as display_line from device as d inner join devicenumplanmap as dnpm on dnpm.fkdevice = d.pkid inner join numplan as n on dnpm.fknumplan = n.pkid inner join routepartition as rp on n.fkroutepartition=rp.pkid and d.tkclass = 1 inner join typemodel as tm on d.tkmodel = tm.enum inner join callingsearchspace as c on n.fkcallingsearchspace_sharedlineappear = c.pkid where n.dnorpattern like '"""
            msg_end = """%'
                        </sql>
                    </ns:executeSQLQuery>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            msg = msg_begin + form_search.string_field.data + msg_end
        elif form_search.select_field.data == SEARCH_BY_USER:
            msg_begin = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/11.5">
                <soapenv:Header/>
                <soapenv:Body>
                    <ns:executeSQLQuery>
                        <sql>select d.name,tm.name as devtype,d.description as description,n.dnorpattern as DN,rp.name as partition,c.name as css,display as display_line from device as d inner join devicenumplanmap as dnpm on dnpm.fkdevice = d.pkid inner join numplan as n on dnpm.fknumplan = n.pkid inner join routepartition as rp on n.fkroutepartition=rp.pkid and d.tkclass = 1 inner join typemodel as tm on d.tkmodel = tm.enum inner join callingsearchspace as c on n.fkcallingsearchspace_sharedlineappear = c.pkid where lower(display) like lower('"""
            msg_end = """%')
                        </sql>
                    </ns:executeSQLQuery>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            msg = msg_begin + form_search.string_field.data + msg_end
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
                "html_template": "cisco_usersearch.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search,
            }
            return renderdata

        except:
            console_output = "Что-то пошло не так при подключении пользователя " + cucm_login + " к серверу " + cucm_ip_address
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_usersearch.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search,
            }
            return renderdata

        # Check is answer is successful
        if post.status_code == 401:
            console_output = "Пользователь " + cucm_login + " не авторизован для подключения к серверу " + cucm_ip_address
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_usersearch.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search,
            }
            return renderdata

        if post.status_code != 200:
            console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_usersearch.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search,
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
                    "html_template": "cisco_usersearch.html",
                    "html_page_title": html_page_title,
                    "console_output": console_output,
                    "form_navigation": form_navigation,
                    "form_search": form_search,
                }
                return renderdata
        else:
            console_output = "Телефонов соответсвующих запросу не найдено"
            print(console_output)
            renderdata = {
                "rendertype": "null",
                "html_template": "cisco_usersearch.html",
                "html_page_title": html_page_title,
                "console_output": console_output,
                "form_navigation": form_navigation,
                "form_search": form_search,
            }
            return renderdata

        console_output = "Найдено записей: " + str(len(rows_list))
        print(console_output)
        renderdata = {
            "rendertype": "success",
            "html_template": "cisco_usersearch.html",
            "html_page_title": html_page_title,
            "console_output": console_output,
            "form_navigation": form_navigation,
            "form_search": form_search,
            "rows_list" : rows_list
        }
        return renderdata

    else:
        if form_search.string_field.errors:
            console_output = " ".join(form_search.string_field.errors)
            print(console_output)

    renderdata={
        "rendertype": "Null",
        "html_template": "cisco_usersearch.html",
        "html_page_title": html_page_title,
        "console_output": console_output,
        "form_navigation": form_navigation,
        "form_search":form_search
    }
    return renderdata
