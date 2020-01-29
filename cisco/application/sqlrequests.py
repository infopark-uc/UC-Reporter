from flask_mysqldb import MySQL
from application import app

def cm_sqlselect(data,table,column,like):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     cur.execute('SELECT ' + data + ' FROM ' + table  + '  WHERE  ' + column + ' LIKE "' + like + '";')
     result = cur.fetchall()
     return result

def cm_sqlupdate(data,table,column,like):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     cur.execute('SELECT  ' + data + ' FROM ' + table  + '  WHERE  ' + column + ' LIKE "' + like + '";')
     result = cur.fetchall()
     return result