from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

login = LoginManager(app)
login.login_view = 'login'

from application import routes

print("Flask start: __name__: " + __name__)
if __name__ == '__main__':
 print("Flask app.run")
 app.run(host='0.0.0.0', port=5000)
 app.run(debug=True)

