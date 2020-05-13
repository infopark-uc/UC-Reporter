from flask import Flask

app = Flask(__name__)

from application import routes

print("Flask start: __name__: " + __name__)
if __name__ == '__main__':
 print("Flask app.run")
 app.run(host='0.0.0.0', port=5000)
 app.run(debug=True)

