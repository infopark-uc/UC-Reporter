from flask_mysqldb import MySQL
from application import app


def cm_sqlselect(data_colum, table, filter_colum, filter_colum_date):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     cur.execute('SELECT ' + data_colum + ' FROM ' + table  + '  WHERE  ' + filter_colum + ' LIKE "' + filter_colum_date + '";')
     result = cur.fetchall()
     mysql.connection.commit()
     cur.close()
     mysql.connection.close()
     return result

def cm_sqlselectall(table, filter_colum, filter_colum_date):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     print('cursor is open')
     try:
         cur.execute('SELECT * FROM ' + table + '  WHERE  ' + filter_colum + ' LIKE "' + filter_colum_date + '";')
         print('sql request')
         result = cur.fetchall()
         mysql.connection.commit()
         print('sql commit')
         cur.close()
         print('cur close')
         #mysql.connection.close()

         return result
     except MySQLdb.ProgrammingError:
         print ('cursor is closed;')
         return "error"
     if mysql.connection.open:
         print('connection is open')
         return "open"
     else:
         print('connection is closed')
         return "close"



def cm_sqlupdate(data, table, set_column, filter_colum, filter_colum_date):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     cur.execute('UPDATE ' + table + ' SET ' + set_column + ' = "'+ data + '" WHERE ' + filter_colum + '="' + filter_colum_date + '";')
     result = cur.fetchall()
     mysql.connection.commit()
     cur.close()
     return result