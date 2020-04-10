from pprint import pprint
import xmltodict
def ucsendmail():
    try:
        sendmail_request = xmltodict.parse(request.data)



        return ('', 204)
    except:
        print('Parser failure!')
        pprint(sendmail_request)
        return ('', 204)