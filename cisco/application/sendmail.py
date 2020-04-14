from pprint import pprint
from flask import Flask, request
import requests
import json
import xmltodict
def ucsendmail():
    try:
        request_ip = str(request.environ['REMOTE_ADDR'])   #нужно добавить проверку на права отправки
        print("Received sendmail HTTP request: " + request.method + " from: " + request_ip)

        #разбираем XML от UCCX
        postdata = xmltodict.parse(request.data)
        postdata_dict = json.loads(json.dumps(postdata))

        #разбираем словарь на переменные
        to = str(postdata_dict['config']["SendToEmail"])   #mailto
        LastName = str(postdata_dict['config']["LastName"])  #Фамилия
        FirstName = str(postdata_dict['config']["FirstName"]) #Имя
        CalledNumber = str(postdata_dict['config']["CalledNumber"])  #набранный номер
        IncomingCallingNumber = str(postdata_dict['config']["IncomingCallingNumber"]) #АОН
        queuetype = str(postdata_dict['config']["queuetype"])  # Тип очереди


        # проверка после какой из очередей мы приняли запрос на отправку сообщения.
        if queuetype == 'None': #отправка для группы сервисных инженеров
            msg_body = str("ФИО: " + FirstName + " " + LastName + " \n"
					"Номер абонента: " + IncomingCallingNumber + " \n"
					"Номер сервиса: " + CalledNumber + " \n")
            subject = str("Сработала переадресация на мобильный номер")

        else:   #отправка для группы диспетчеров
            msg_body = str("ФИО: " + FirstName + " " + LastName + " \n"
					"Номер абонента: " + IncomingCallingNumber + " \n"
					"Номер сервиса: " + CalledNumber + " \n")
            subject = str("вызов пропущен группой")

        print(msg_body)




        return ('', 204)
    except:
        print('Parser failure!')
        pprint(postdata_dict)
        return ('', 204)