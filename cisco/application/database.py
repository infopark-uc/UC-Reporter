from application import db

#Class table- table name in SQL
class CMS_SERVER_TABLE_CLASS(db.Model):
    __tablename__ = 'cms_servers'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    ip = db.Column(db.String(128), unique=True)
    api_port = db.Column(db.String(128))
    cluster = db.Column(db.String(128))
    requester_running = db.Column(db.String(128))

    def __repr__(self):
        return '<{}>'.format(self.username)


class CM_SERVER_LIST_TABLE_CLASS(db.Model):
    __tablename__ = 'cm_servers_list'
    id = db.Column(db.Integer, primary_key=True)
    cm_ip = db.Column(db.String(64), unique=True)
    cm_username = db.Column(db.String(128))
    cm_password = db.Column(db.String(128))
    cluster = db.Column(db.String(128))
    phoneup_ip = db.Column(db.String(128), unique=True)
    phoneup_username = db.Column(db.String(128))
    phoneup_password = db.Column(db.String(128))
    phoneup_app_user = db.Column(db.String(128))
    description = db.Column(db.String(128))

    def __repr__(self):
        return '<{}>'.format(self.username)

class CM_PHONES_TABLE_CLASS(db.Model):
    __tablename__ = 'cm_phones_table'
    phone_index = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(64), unique=True)
    phone_ip = db.Column(db.String(128))
    phone_user = db.Column(db.String(128), unique=True)
    phone_password = db.Column(db.String(128))

    def __repr__(self):
        return '<{}>'.format(self.username)

class UCREPORTER_USERS_TABLE_CLASS(db.Model):
    __tablename__ = 'ucreporter_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),nullable=False)
    password = db.Column(db.String(64),nullable=False)
    password_hash = db.Column(db.String(64))
    description = db.Column(db.String(64))

    def __repr__(self):
        return '<{}>'.format(self.username)

