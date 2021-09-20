from application import db
import datetime

class CmsCdrRecordingsTableClass(db.Model):
	__tablename__ = 'cms_cdr_recordings'
	timestamp = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
	recording_id = db.Column(db.String(64), primary_key=True)
	path = db.Column(db.String(64))
	call_id = db.Column(db.String(64))
	callLeg_id = db.Column(db.String(64))

# Class table- table name in SQL
class CmsServerTableClass(db.Model):
	__tablename__ = 'cms_servers'
	id = db.Column(db.Integer, primary_key=True)
	login = db.Column(db.String(64), nullable=False)
	password = db.Column(db.String(64), nullable=False)
	ip = db.Column(db.String(64), nullable=False)
	api_port = db.Column(db.String(64), nullable=False)
	cluster = db.Column(db.String(64), nullable=False)
	requester_running = db.Column(db.String(64))
	def __repr__(self):
		return '<{}>'.format(self.ip)


class CmServerListTableClass(db.Model):
	__tablename__ = 'cm_servers_list'
	id = db.Column(db.Integer, primary_key=True)
	cm_ip = db.Column(db.String(64), unique=True)
	cm_username = db.Column(db.String(128), nullable=False)
	cm_password = db.Column(db.String(128), nullable=False)
	cluster = db.Column(db.String(128))
	phoneup_ip = db.Column(db.String(128), unique=True)
	phoneup_username = db.Column(db.String(128))
	phoneup_password = db.Column(db.String(128))
	phoneup_app_user = db.Column(db.String(128))
	description = db.Column(db.String(128))

	def __repr__(self):
		return '<{}>'.format(self.id)

