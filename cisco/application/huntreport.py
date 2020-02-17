import requests
import xmltodict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.forms import SelectNavigation, SelectSearchType
from application.sqlrequests import cm_sqlselect,cm_sqlselectall,cm_sqlupdate


def huntreport():

    cucm_ip_address = cm_sqlselect("cm_ip", "cm_servers_list", "cm_name", "INFOCELL")
    print(cucm_ip_address)
    cucm_ip_address = cucm_ip_address["cm_ip"]
    print (cucm_ip_address)

    cucm_login = cm_sqlselect("cm_username", "cm_servers_list", "cm_name", "INFOCELL")
    print(cucm_login)
    cucm_login=cucm_login["cm_username"]
    print(cucm_login)

    cucm_password = cm_sqlselect("cm_password", "cm_servers_list", "cm_name", "INFOCELL")
    cucm_password = cucm_password["cm_password"]
    print(cucm_password)

    html_page_title = 'CUCM Hunt Report'

    # CUCM URL's
    cucm_url = "https://" + cucm_ip_address + ":8443/axl/"

    # V12 CUCM Headers
    headers11query = {'Content-Type': 'text/xml', 'SOAPAction': 'CUCM:DB ver=12.5 executeSQLQuery'}

    msg = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/12.5">
        <soapenv:Header/>
        <soapenv:Body>
            <ns:executeSQLQuery>
                <sql>select lg.name as LineGroup,n.dnorpattern, display, tm.name as devtype, dhd.hlog from linegroup as lg inner join linegroupnumplanmap as lgmap on lgmap.fklinegroup=lg.pkid inner join numplan as n on lgmap.fknumplan = n.pkid inner join devicenumplanmap as dmap on dmap.fknumplan = n.pkid inner 
                join device as d on dmap.fkdevice=d.pkid inner join typemodel as tm on d.tkmodel = tm.enum inner join devicehlogdynamic as dhd on dhd.fkdevice=d.pkid order by lg.name
                </sql>
            </ns:executeSQLQuery>
        </soapenv:Body>
    </soapenv:Envelope>
    """

    # disable warning about untrusted certs
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create the Requests Connection
    try:
        post = requests.post(cucm_url, data=msg, headers=headers11query, verify=False, auth=(cucm_login, cucm_password))
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + cucm_ip_address
        print(console_output)
    except:
        console_output = "Что-то пошло не так при подключении пользователя " + cucm_login + " к серверу " + cucm_ip_address
        print(console_output)

    # Check is answer is successful
    if post.status_code == 401:
        console_output = "Пользователь " + cucm_login + " не авторизован для подключения к серверу " + cucm_ip_address
        print(console_output)

    if post.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)

    # Convert output to Dict
    console_output = "Данные получены из CUCM " + cucm_ip_address
    print(console_output)

    xml_dict = xmltodict.parse(post.text)

    # Get Dict with users
    rows_list = xml_dict["soapenv:Envelope"]["soapenv:Body"]["ns:executeSQLQueryResponse"]["return"]["row"]

    # Temporary values
    console_output = "Hunt group Start page"
    # rows_list = [{"linegroup":"linegroup"},{"dnorpattern":"dnorpattern"},{"display":"display"},{"devtype":"devtype"},{"hlog":"hlog"}]

    form_navigation = SelectNavigation(csrf_enabled=False)
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        print(console_output)
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": form_navigation.select_navigation.data
        }
        return renderdata

    renderdata = {
        "rendertype": "success",
        "html_template": "cisco_huntgroup.html",
        "html_page_title": html_page_title,
        "console_output": console_output,
        "form_navigation": form_navigation,
        "rows_list": rows_list
    }
    return renderdata


