import pymysql
from pprint import pprint

def cm_sqlupdate(data, table, set_column, filter_colum, filter_colum_data):
     con = pymysql.connect('172.20.5.19', 'sqladmin','Qwerty123', 'ucreporter')
     with con:
          cur = con.cursor()
          cur.execute('UPDATE ' + table + ' SET ' + set_column + ' = "' + data + '" WHERE ' + filter_colum + '="' + filter_colum_data + '";')

     return "update database done"

def cm_sqlselect(data_colum, table, filter_colum, filter_colum_data):
     con = pymysql.connect('172.20.5.19', 'sqladmin','Qwerty123', 'ucreporter')
     with con:
          cur = con.cursor()
          cur.execute('SELECT ' + data_colum + ' FROM ' + table + '  WHERE  ' + filter_colum + ' LIKE "' + filter_colum_data + '";')
          result = cur.fetchone()
          result = result[0]
     return result

def cm_sqlselectall(table, filter_colum, filter_colum_data):
     con = pymysql.connect('172.20.5.19', 'sqladmin','Qwerty123', 'ucreporter')
     with con:
          cur = con.cursor()
          cur.execute('SELECT * FROM ' + table + '  WHERE  ' + filter_colum + ' LIKE "' + filter_colum_data + '";')
          result = cur.fetchone()
     return result


############ SQL Requests ###################################

def sql_request_dict(sqlrequest):   #запрос листа словорей

     try:
          con = pymysql.connect('172.20.5.19', 'sqladmin', 'Qwerty123', 'ucreporter',
                                cursorclass=pymysql.cursors.DictCursor)
     except:
          console_output = "sqlselect_dict: MySQL DB access error"
          print(console_output)  # info
          #logger.info(console_output)
          return None

     with con:
          cur = con.cursor()
          cur.execute(sqlrequest)
          result = cur.fetchall()
          cur.close()  # закрываем курсор
     con.close()  # закрываем соединение
     return result

def sql_execute(sqlrequest):
     con = pymysql.connect('172.20.5.19', 'sqladmin','Qwerty123', 'ucreporter')
     with con:
          cur = con.cursor()
          cur.execute(sqlrequest)
          cur.close()  # закрываем курсор
     con.commit() #подтверждает изменения
     con.close() #закрываем соединение
     return "Request to database done"



############# CMS Requests #############


def cms_sql_request(sqlrequest):
     con = pymysql.connect('172.20.5.19', 'sqladmin','Qwerty123', 'ucreporter')
     with con:
          cur = con.cursor()
          cur.execute(sqlrequest)

     return "Request to database done"

def cm_sqlselect_dict(data_colum, table, filter_colum, filter_colum_data):
     con = pymysql.connect('172.20.5.19', 'sqladmin','Qwerty123', 'ucreporter',cursorclass=pymysql.cursors.DictCursor)
     with con:
          cur = con.cursor()
          cur.execute('SELECT ' + data_colum + ' FROM ' + table + '  WHERE  ' + filter_colum + ' LIKE "' + filter_colum_data + '";')
          result = cur.fetchall()
          cur.close() # закрываем курсор
     con.close() # закрываем соединение
     return result

def cms_sql_request_dict(sqlrequest):
     con = pymysql.connect('172.20.5.19', 'sqladmin','Qwerty123', 'ucreporter',cursorclass=pymysql.cursors.DictCursor)
     with con:
          cur = con.cursor()
          cur.execute(sqlrequest)
          result = cur.fetchall() #забираем все значения
          cur.close() #закрываем курсор
     con.close()
     return result