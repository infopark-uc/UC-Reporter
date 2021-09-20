from flask import Flask
from flask_login import LoginManager
import logging, logging.handlers
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
#SQLAlchemy
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from application import routes

print("Flask for CMS-Reciver start: __name__: " + __name__)
if __name__ == '__main__':
 print("Flask app.run")
 app.run(host='0.0.0.0', port=5000)
 app.run(debug=True)

