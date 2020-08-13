from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, PasswordField,TextAreaField,Label
from wtforms.validators import Optional, Length, Regexp, DataRequired

class SelectNavigation(FlaskForm):
    select_navigation = SelectField('Navigation', choices=[('usersearchpage', 'Поиск пользователей'), ('huntpage', 'Отчет по пользователям Hunt Group'), ('cfa', 'Отчет по переадресациям'), ('cmspage', 'Отчет по конференциям CMS'),('cms_cospace_page', 'Отчет по пин-кодам CMS'),('cms_recordings_page', 'Отчет по записанным конференциям')])
    submit = SubmitField('Go')

class SelectSearchType(FlaskForm):
    select_region = SelectField('Navigation', default="NF", choices=[('MSK', 'Московский филиал'), ('KF', 'Красноярский филиал'), ('NF', 'Нефтеюганский филиал'), ('TF', 'Томский филиал'), ('NU', 'Ямальский филиал (Новый Уренгой)'), ('Infocell', 'Инфосэл')])
    select_field = SelectField('Navigation', choices=[('User', 'имя пользователя'), ('Number', 'внутренний номер')])
    string_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    submit = SubmitField('Найти')

class SelectForwardSearchType(FlaskForm):
    select_region = SelectField('Navigation', default="NF", choices=[('MSK', 'Московский филиал'), ('KF', 'Красноярский филиал'), ('NF', 'Нефтеюганский филиал'), ('TF', 'Томский филиал'), ('NU', 'Ямальский филиал (Новый Уренгой)'), ('Infocell', 'Инфосэл')])
    select_field = SelectField('Navigation', choices=[('DN', 'номер абонента'), ('Transfer', 'номер переадресации')])
    string_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    submit = SubmitField('Найти')

class SelectCMSClusterForCDR(FlaskForm):
    select_CMSCluster = SelectField('Navigation', default="all", choices=[('all', 'Все кластеры'), ('ssk', 'ССК'), ('Infocell', 'Инфосэл'), ('infopark', 'Инфопарк')])
    submit = SubmitField('Найти')

class SelectCMSClusterForCospace(FlaskForm):
    select_CMSCluster = SelectField('Navigation', choices=[('ssk', 'ССК'), ('Infocell', 'Инфосэл'), ('infopark', 'Инфопарк')])
    submit = SubmitField('Найти')

class UCRepoterLogin(FlaskForm):
    login_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    password_field = PasswordField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    submit = SubmitField('Login')

class UserInformation(FlaskForm):
    UserName_field = StringField('UserName')
    id_field = Label('id',text='')
    Descriotion_field = StringField('Description',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    Password_field = StringField('Password',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    SaveSubmit = SubmitField('Save')

class CUCMServerInformation(FlaskForm):
    id_field = Label('id', text='')
    Cluster_field = StringField('',validators=[DataRequired()])
    username_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    ip_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    password_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."),Regexp('^\w+$',message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    SaveSubmit = SubmitField('Save')

class CMSServerInformation(FlaskForm):
    API_Port_field = StringField('')
    Requester_field = SelectField('', default="True", choices=[('True', 'Enable'), ('False', 'Disable')])
    cluster_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    ip_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    username_field = StringField('', validators=[DataRequired(),Length(max=32, message=" Длина запроса не более 32 символов."),Regexp('^\w+$',message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    password_field = StringField('', validators=[DataRequired(),Length(max=32, message=" Длина запроса не более 32 символов."),Regexp('^\w+$',message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    SaveSubmit = SubmitField('Save')


class UcrequesterInformation(FlaskForm):
    ServerName_field = StringField('')
    Descriotion_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    ip_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    SaveSubmit = SubmitField('Save')
    DeleteSubmit = SubmitField('Delete')
    AddSubmit = SubmitField('Add New')

class AddNewForm(FlaskForm):
    AddSubmit = SubmitField('Add New')

class DeleteForm(FlaskForm):
    DeleteSubmit = SubmitField('Delete')

