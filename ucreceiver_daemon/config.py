import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Database config
    SQLALCHEMY_DATABASE_URI = 'mysql://sqladmin:Qwerty123@172.20.5.19/ucreporter?charset=utf8'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
