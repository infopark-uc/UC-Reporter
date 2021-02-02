from application import db
from flask_login import UserMixin


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


class UCReporterUsersTableClass(db.Model,UserMixin):
	__tablename__ = 'ucreporter_users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), nullable=False)
	password = db.Column(db.String(64), nullable=False)
	description = db.Column(db.String(64))
	password_hash = db.Column(db.String(100), nullable=False)

	def __repr__(self):
		return "<{}:{}>".format(self.id, self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

######### modul roomservice start ######
class RmcWidgetsTableClass(db.Model):
	__tablename__ = 'rmc_widgets'
	wg_id = db.Column(db.Integer, primary_key=True)
	wg_name = db.Column(db.String(50), nullable=False)
	wg_data = db.Column(db.Integer, nullable=False)
	panel_id = db.Column(db.Integer, db.ForeignKey('rmc_panels.panel_id'))

	def __init__(self, wg_name, wg_data):
		self.wg_name = wg_name
		self.wg_data = wg_data

	def __repr__(self):
		return '<{}>'.format(self.wg_id)

class RmcPanelTableClass(db.Model):
	__tablename__ = 'rmc_panels'
	panel_id = db.Column(db.Integer, primary_key=True)
	panel_name = db.Column(db.String(50), nullable=False)


	def __repr__(self):
		return '<{}>'.format(self.panel_name)



class RmcPhoneTableClass(db.Model):
	__tablename__ = 'rmc_phones'
	ph_id = db.Column(db.Integer, primary_key=True)
	ph_number = db.Column(db.String(10), nullable=False)
	ph_ip = db.Column(db.String(64), unique=True, nullable=False)
	ph_username = db.Column(db.String(64), nullable=False)
	ph_password = db.Column(db.String(64), nullable=False)

	def __repr__(self):
		return '<{}>'.format(self.ph_number)


class RmcCodecTableClass(db.Model):
	__tablename__ = 'rmc_codecs'
	cs_id = db.Column(db.Integer, primary_key=True)
	cs_ip = db.Column(db.String(50), unique=True, nullable=False)
	cs_username = db.Column(db.String(50), nullable=False)
	cs_password = db.Column(db.String(50), nullable=False)
	cs_description = db.Column(db.String(50))

	def __repr__(self):
		return '<{}>'.format(self.cs_ip)

class RmcSystemsTableClass(db.Model):
	__tablename__ = 'rmc_systems_index'
	system_id = db.Column(db.Integer, primary_key=True)
	cs_id = db.Column(db.Integer, db.ForeignKey('rmc_codec.cs_id'))
	ph_id = db.Column(db.Integer, db.ForeignKey('rmc_phones.ph_id'))
	panel_id = db.Column(db.Integer, db.ForeignKey('rmc_panels.panel_id'))
	system_name = db.Column(db.String(50), nullable=False)

	def __repr__(self):
		return '<{}>'.format(self.system_name)

######### modul roomservice end ######
