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
        mailtype = str(postdata_dict['config']["mailtype"])  # Тип очереди







        return ('', 204)
    except:
        print('Parser failure!')
        pprint(postdata_dict)
        return ('', 204)