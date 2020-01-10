from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField
from wtforms.validators import Optional, Length, Regexp

class SelectNavigation(FlaskForm):
    select_navigation = SelectField('Navigation', choices=[('/index', 'Поиск пользователей'), ('/hunt', 'Отчет по пользователям Hunt Group'), ('/cfa', 'Отчет по переадресациям')])
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
