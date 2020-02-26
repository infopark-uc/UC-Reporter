from flask import Flask, abort, request
import xmltodict
from pprint import pprint
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from application.sqlrequests import cm_sqlselect, cm_sqlselectall, cm_sqlupdate

def codec(systemindex):

    print("Получен HTTP запрос " + request.method)

    if not request.json:
        print("Нет JSON внутри HTTP запроса")
        return "OK"

    json_data = request.json

    event = []

    try:
        event = (json_data['Event']['UserInterface']['Extensions']['Panel']['Clicked']['PanelId']['Value']).split(":")
        print('Приехало событие от панельки')
    except KeyError:
        print('Сработало исключение для панельки')

    #try:
    #    event = (json_data['Event']['UserInterface']['Extensions']['Event']['Pressed']['Signal']['Value']).split(":")
    #    print('Приехало событие от виджета - Pressed')
    #except KeyError:
    #    print('Сработало исключение для виджета - Pressed')

    try:
        event = (json_data['Event']['UserInterface']['Extensions']['Event']['Clicked']['Signal']['Value']).split(":")
        print('Приехало событие от виджета Clicked')
    except KeyError:
        print('Сработало исключение для виджета Clicked')

    if event:
        if event[0] == "CoffeService":
            # Обработка для открытия панельки
            print ("Обрабатываем событие открытия панельки Кофе")

            get_value(systemindex) #забираем данные с панельки и обновляем базу, обновляем данные с базы данных по виджетам при открытии панельки

        elif event[0] == "CoffeeCount":
            widget_data_CoffeeCount = cm_sqlselect("widget_data", "widget_table", "widget_name", str(event[0]))
            # Обработка для изменения количества кофе
            if event[1] == "increment":
                widget_data_CoffeeCount = cm_sqlselect("widget_data", "widget_table", "widget_name", str(event[0]))
                widget_data_CoffeeCount = str(int(widget_data_CoffeeCount) + 1)
                set_value(systemindex, event[0], widget_data_CoffeeCount)
                print("Обрабатываем событие увелечения кофе")
            elif (event[1] == "decrement") and (int(widget_data_CoffeeCount) >= 1):
                widget_data_CoffeeCount = cm_sqlselect("widget_data", "widget_table", "widget_name", str(event[0]))
                widget_data_CoffeeCount = str(int(widget_data_CoffeeCount) - 1)
                set_value(systemindex, event[0], widget_data_CoffeeCount)
                print("Обрабатываем событие уменьшения кофе")

        elif event[0] == "TeaCount":
            widget_data_TeaCount = cm_sqlselect("widget_data", "widget_table", "widget_name", str(event[0]))
            #Обработка для изменения количества  чая
            print(event[0])
            if event[1] == "increment":
                widget_data_TeaCount = cm_sqlselect("widget_data", "widget_table", "widget_name", str(event[0]))
                widget_data_TeaCount = str(int(widget_data_TeaCount) + 1)
                set_value(systemindex, event[0], widget_data_TeaCount)
                print("Обрабатываем событие увелечения чая")
            elif (event[1] == "decrement") and (int(widget_data_TeaCount) >= 1):
                widget_data_TeaCount = cm_sqlselect("widget_data", "widget_table", "widget_name", str(event[0]))
                widget_data_TeaCount = str(int(widget_data_TeaCount) - 1)
                set_value(systemindex, event[0], widget_data_TeaCount)
                print("Обрабатываем событие уменьшения чая")

        elif event[0] == "SendButton":
            # Обработка отправки заказа
            print("Обрабатываем событие отправки заказа")
            send_order(systemindex)

        else:
            #что-то непонятное, неизвестный виджет - ничего не делаем
            print("Какое-то непонятное событие - ничего не делаем")

    else:
        print("В HTTP запросе пусто - выросла капуста")

    return 'OK'


def submit_order(systemindex):
    roomkit_access_data_ip = cm_sqlselect("room_ip", "cm_roomsystems_table", "room_index", systemindex)
    roomkit_access_data_login = cm_sqlselect("room_user", "cm_roomsystems_table", "room_index", systemindex)
    roomkit_access_data_password = cm_sqlselect("room_password", "cm_roomsystems_table", "room_index", systemindex)
    print("Получен HTTP запрос - подтверждение заказа: " + request.method)
    set_value(systemindex, "CoffeeCount", "0")
    set_value(systemindex, "TeaCount", "0")


    # URL
    http_url = "http://" + roomkit_access_data_ip + "/putxml"

    # HTTP Headers
    http_headers = {'Content-Type': 'text/xml'}

    http_data = """
<Command>
	<UserInterface>
		<Message>
			<Alert>
				<Display>
					<Duration>15</Duration>
                    <Text>Заказ принят</Text>
                </Display>
            </Alert>
        </Message>
    </UserInterface>
</Command>"""

    # disable warning about untrusted certs
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create the Requests Connection
    try:
        post = requests.post(http_url, data=http_data.encode('utf-8'), headers=http_headers, verify=False, auth=(roomkit_access_data_login,roomkit_access_data_password))
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + roomkit_access_data_ip
        print(console_output)
        return "OK"
    except:
        console_output = "Что-то пошло не так при подключении пользователя " + roomkit_access_data_login + " к серверу " + roomkit_access_data_ip
        print(console_output)
        return "OK"

    # Check is answer is successful
    if post.status_code == 401:
        console_output = "Пользователь " + roomkit_access_data_login + " не авторизован для подключения к серверу " + roomkit_access_data_ip
        print(console_output)
        return "OK"

    if post.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)
        return "OK"

    # Convert output to Dict
    console_output = "Данные получены от " + roomkit_access_data_ip
    print(console_output)

    print("Send submit to phone")
    return '<CiscoIPPhoneText><Title>Заказ</Title><Text>Заказ подтвержден</Text><SoftKeyItem><Name>Выход</Name><URL>SoftKey:Exit</URL><Position>1</Position></SoftKeyItem></CiscoIPPhoneText>'.encode('utf-8')

def set_value(systemindex, widget_name, widget_value):
    # credentials from database
    roomkit_access_data_ip = cm_sqlselect("room_ip", "cm_roomsystems_table", "room_index", systemindex)
    roomkit_access_data_login = cm_sqlselect("room_user", "cm_roomsystems_table", "room_index", systemindex)
    roomkit_access_data_password = cm_sqlselect("room_password", "cm_roomsystems_table", "room_index", systemindex)


    print ("Выполняется функция установки значений виджетов set_value")
    # URL
    http_url = "http://" + roomkit_access_data_ip + "/putxml"

    # HTTP Headers
    http_headers = {'Content-Type': 'text/xml'}

    http_data = """
<Command>
  <UserInterface>
    <Extensions>
	  <Widget>
	    <SetValue> 
		  <WidgetId>""" + widget_name + """</WidgetId>
		  <Value>""" + widget_value + """</Value> 
		</SetValue>
	  </Widget>
	</Extensions>
  </UserInterface>
</Command>
    """

    # disable warning about untrusted certs
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create the Requests Connection
    try:
        post = requests.post(http_url, data=http_data, headers=http_headers, verify=False, auth=(roomkit_access_data_login, roomkit_access_data_password))
        cm_sqlupdate(widget_value, "widget_table", "widget_data", "widget_name", widget_name)
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + roomkit_access_data_ip
        print(console_output)
        return
    except:
        console_output = "Что-то пошло не так при подключении пользователя " + roomkit_access_data_login + " к серверу " + roomkit_access_data_ip
        print(console_output)
        return

    # Check is answer is successful
    if post.status_code == 401:
        console_output = "Пользователь " + roomkit_access_data_login + " не авторизован для подключения к серверу " + roomkit_access_data_ip
        print(console_output)
        return


    if post.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)
        return

    # Convert output to Dict
    console_output = "Данные получены от " + roomkit_access_data_ip
    print(console_output)

def get_value(systemindex):
	# credentials from database
    roomkit_access_data_ip = cm_sqlselect("room_ip", "cm_roomsystems_table", "room_index", systemindex)
    roomkit_access_data_login = cm_sqlselect("room_user", "cm_roomsystems_table", "room_index", systemindex)
    roomkit_access_data_password = cm_sqlselect("room_password", "cm_roomsystems_table", "room_index", systemindex)
    widget_data = {}

    print("Выполняется функция считывания значений виджетов get_value")
    
    # URL
    http_url = "http://" + roomkit_access_data_ip + "/getxml"

    # HTTP Headers
    http_headers = {'Content-Type': 'text/xml'}

    http_params = {"location": "/Status/UserInterface/Extensions"}

    # disable warning about untrusted certs
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create the Requests Connection
    try:
        get = requests.get(http_url, params=http_params, headers=http_headers, verify=False, auth=(roomkit_access_data_login, roomkit_access_data_password))
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + roomkit_access_data_ip
        print(console_output)
        return
    except:
        console_output = "Что-то пошло не так при подключении пользователя " + roomkit_access_data_login + " к серверу " + roomkit_access_data_ip
        print(console_output)
        return

    # Check is answer is successful
    if get.status_code == 401:
        console_output = "Пользователь " + roomkit_access_data_login + " не авторизован для подключения к серверу " + roomkit_access_data_ip
        print(console_output)
        return

    if get.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(get.status_code) + ": " + get.reason
        print(console_output)
        return

    # Convert output to Dict
    console_output = "Данные получены от " + roomkit_access_data_ip
    print(console_output)

    xml_dict = xmltodict.parse(get.text)

    # Get Dict with phones
    widget_list = xml_dict["Status"]["UserInterface"]["Extensions"]["Widget"]
    print (xml_dict)
    if type(widget_list) is list:
        for widget in widget_list:
            widget_data[widget["WidgetId"]] = widget["Value"]

    if "CoffeeCount" in widget_data:
        if widget_data["CoffeeCount"] is None:
            set_value(systemindex, "CoffeeCount", "0")

    if "TeaCount" in widget_data:
        if widget_data["TeaCount"] is None:
            set_value(systemindex, "TeaCount", "0")

    print("Установлены исходные значения для виджетов:")
    pprint(widget_data)

def send_order(systemindex):
	#credentials from database
    submit_server = cm_sqlselect("server_ip", "server_config_table", "server_index", "0")
    submit_server_port = cm_sqlselect("server_port", "server_config_table", "server_index", "0")
    phone_access_data_ip = cm_sqlselect("phone_ip", "cm_phones_table", "phone_index", systemindex)
    phone_access_data_login = cm_sqlselect("phone_user", "cm_phones_table", "phone_index", systemindex)
    phone_access_data_password = cm_sqlselect("phone_password", "cm_phones_table", "phone_index", systemindex)
    widget_data_CoffeeCount = cm_sqlselect("widget_data", "widget_table", "widget_name", "CoffeeCount")
    widget_data_TeaCount = cm_sqlselect("widget_data", "widget_table", "widget_name", "TeaCount")

    print("Отправляем заказ")
    # URL
    http_url = "http://" + phone_access_data_ip + "/CGI/Execute"

    # HTTP Headers
    http_headers = {'Content-Type': 'text/xml; charset=utf-8'}

    message = "Прошу подать следующие напитки \nКофе: " + str(widget_data_CoffeeCount) + "\n" + "Чай: " + str(widget_data_TeaCount)
    http_data = 'XML=<?xml version="1.0" encoding="utf-8" ?><CiscoIPPhoneText><Title>Конференц-зал</Title><Text>' + message  + '</Text><SoftKeyItem><Name>Подтвердить</Name><URL method="post">http://' + submit_server + ':' + submit_server_port + '/SubmitOrder</URL><Position>4</Position></SoftKeyItem></CiscoIPPhoneText>'

    # disable warning about untrusted certs
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create the Requests Connection
    try:
        post = requests.post(http_url, data=http_data.encode('utf-8'), headers=http_headers, verify=False, auth=(phone_access_data_login, phone_access_data_password))
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + phone_access_data_ip
        print(console_output)
        return
    except:
        console_output = "Что-то пошло не так при подключении пользователя " + phone_access_data_login + " к серверу " + phone_access_data_ip
        print(console_output)
        return

    # Check is answer is successful
    if post.status_code == 401:
        console_output = "Пользователь " + phone_access_data_login + " не авторизован для подключения к серверу " + phone_access_data_ip
        print(console_output)
        return

    if post.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)
        return

    # Convert output to Dict
    console_output = "Данные получены от " + phone_access_data_ip
    print(console_output)

    http_data = 'XML= <CiscoIPPhoneExecute><ExecuteItem URL="Play:Chime.raw" /></CiscoIPPhoneExecute>'

    # Create the Requests Connection
    try:
        post = requests.post(http_url, data=http_data, headers=http_headers, verify=False, auth=(phone_access_data_login, phone_access_data_password))
    except requests.exceptions.ConnectionError:
        console_output = "Ошибка соединения с сервером " + phone_access_data_ip
        print(console_output)
        return
    except:
        console_output = "Что-то пошло не так при подключении пользователя " + phone_access_data_login + " к серверу " + phone_access_data_ip
        print(console_output)
        return

    # Check is answer is successful
    if post.status_code == 401:
        console_output = "Пользователь " + phone_access_data_login + " не авторизован для подключения к серверу " + phone_access_data_ip
        print(console_output)
        return

    if post.status_code != 200:
        console_output = "Ошибка при подключении к серверу: " + str(post.status_code) + ": " + post.reason
        print(console_output)
        return

    # Convert output to Dict
    console_output = "Данные получены от " + phone_access_data_ip
    print(console_output)
