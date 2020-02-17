from flask_mysqldb import MySQL
from application import app


def cm_sqlselect(data_colum, table, filter_colum, filter_colum_data):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     cur.execute('SELECT ' + data_colum + ' FROM ' + table + '  WHERE  ' + filter_colum + ' LIKE "' + filter_colum_data + '";')
     result = cur.fetchall()
     mysql.connection.commit()
     cur.close()
     mysql.connection.close()
     return result

def cm_sqlselectall(table, filter_colum, filter_colum_data):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     cur.execute('SELECT * FROM ' + table + '  WHERE  ' + filter_colum + ' LIKE "' + filter_colum_data + '";')
     result = cur.fetchall()
     mysql.connection.commit()
     cur.close()
     mysql.connection.close()
     return result

def cm_sqlupdate(data, table, set_column, filter_colum, filter_colum_date):
     mysql = MySQL(app)
     cur = mysql.connection.cursor()
     cur.execute('UPDATE ' + table + ' SET ' + set_column + ' = "'+ data + '" WHERE ' + filter_colum + '="' + filter_colum_date + '";')
     result = cur.fetchall()
     mysql.connection.commit()
     cur.close()
     return result