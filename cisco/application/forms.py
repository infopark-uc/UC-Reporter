from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, PasswordField,Label, IntegerField
from wtforms.validators import Optional, Length, Regexp, DataRequired, NumberRange, InputRequired

class SelectNavigation(FlaskForm):
    select_navigation = SelectField('Navigation', choices=[('usersearchpage', 'UC Reporter'), ('platform', 'Platform Administrator')])
    submit = SubmitField('Go')

class SelectSearchType(FlaskForm):
    select_region = SelectField('Navigation', default="NF", choices=[('MSK', 'Московский филиал'),
                                                                     ('KF', 'Красноярский филиал'),
                                                                     ('NF', 'Нефтеюганский филиал'),
                                                                     ('TF', 'Томский филиал'),
                                                                     ('NU', 'Ямальский филиал (Новый Уренгой)'),
                                                                     ('Infocell', 'Инфосэл')])
    select_field = SelectField('Navigation', choices=[('User', 'имя пользователя'), ('Number', 'внутренний номер')])
    string_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                            Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    submit = SubmitField('Найти')

class SelectCUCMCluster(FlaskForm):
    select_cluster = SelectField('Navigation', default="NF", choices=[])
    submit = SubmitField('Найти')

class SelectForwardSearchType(FlaskForm):
    select_region = SelectField('Navigation', default="NF", choices=[])
    select_field = SelectField('Navigation', choices=[('DN', 'номер абонента'), ('Transfer', 'номер переадресации')])
    string_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    submit = SubmitField('Найти')

class SelectCMSClusterForCDR(FlaskForm):
    select_CMSCluster = SelectField('Navigation', default="all", choices=[('all', 'Все кластеры'), ('ssk', 'ССК'), ('Infocell', 'Инфосэл'), ('infopark', 'Инфопарк')])
    confroom_filter = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    limit_field = SelectField('',default="50", choices=[("50", '50'), ("100", '100'), ("200", '200'),("300", '300'),("999999999999", 'ALL')])
    submit = SubmitField('Найти')

class SelectCMSClusterForCospace(FlaskForm):
    select_CMSCluster = SelectField('Navigation', choices=[('ssk', 'ССК'), ('Infocell', 'Инфосэл'), ('infopark', 'Инфопарк')])
    submit = SubmitField('Найти')

class SelectCMSClusterForReport(FlaskForm):
    class Meta:
        locales = ['es_ES', 'es']
    select_CMSCluster = SelectField('Navigation', choices=[('ssk', 'ССК'), ('Infocell', 'Инфосэл'), ('infopark', 'Инфопарк')])
    integer_field = IntegerField(7, validators=[DataRequired(message=" Укажите количество дней в интервале от 1 до 365"),
                                              NumberRange(min=1, max=365, message=" Количество дней должно быть в интервале от 1 до 365")])
    submit = SubmitField('Найти')

class UCRepoterLogin(FlaskForm):
    login_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    password_field = PasswordField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."), Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    submit = SubmitField('Login')

class UserInformation(FlaskForm):
    UserName_field = StringField('UserName')
    id_field = Label('id',text='')
    Descriotion_field = StringField('Description',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    Password_field = StringField('Password',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    SaveSubmit = SubmitField('Save')

class CUCMServerInformation(FlaskForm):
    id_field = Label('id', text='')
    Cluster_field = StringField('',validators=[DataRequired()])
    username_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    ip_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    password_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$',message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    SaveSubmit = SubmitField('Save')

class CMSServerInformation(FlaskForm):
    API_Port_field = StringField('')
    id_field = Label('id', text='')
    Requester_field = SelectField('', default="True", choices=[('True', 'Enable'), ('False', 'Disable')])
    cluster_field = StringField('',validators=[Optional(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    ip_field = StringField('',validators=[DataRequired(), Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$', message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    username_field = StringField('', validators=[DataRequired(),Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$',message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    password_field = StringField('', validators=[DataRequired(),Length(max=32, message=" Длина запроса не более 32 символов."),
                                        Regexp('^\w+$',message=" Допустимые символы в запросе: буквы, цифры и подчеркивания.")])
    SaveSubmit = SubmitField('Save')

class SelectHuntGroup(FlaskForm):
    select_hunt_group = SelectField('Navigation', default="", choices=[])
    submit = SubmitField('Найти')





