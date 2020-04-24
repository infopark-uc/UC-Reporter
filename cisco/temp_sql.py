#import pymysql
from pprint import pprint
from application.sqlrequests import cms_sql_request_dict


#con = pymysql.connect('172.20.31.50', 'sqladmin', 'Qwerty123', 'ucreporter', cursorclass=pymysql.cursors.DictCursor)

#with con:
#    cur = con.cursor()
#    cur.execute('SELECT * FROM cm_servers_list ;')
#    result = cur.fetchall()
#    #pprint(result)
#    ip = result[0]["cm_ip"]
#    pprint(ip)

rows_list = cms_sql_request_dict(
    "SELECT DISTINCT callleg_id,AudioPacketLossPercentageRX,AudioPacketLossPercentageTX,VideoPacketLossPercentageRX,VideoPacketLossPercentageTX,cms_node  FROM cms_cdr_calllegs WHERE callleg_id='ac4bb7ec-bfad-493c-b6d9-d5acc393659d';")
pprint(rows_list)