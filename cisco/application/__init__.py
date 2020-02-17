from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = '172.20.31.50'
app.config['MYSQL_USER'] = 'sqladmin'
app.config['MYSQL_PASSWORD'] = 'Qwerty123'
app.config['MYSQL_DB'] = 'ucreporter'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

from application import routes

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=5000)
 app.run(debug=True)

