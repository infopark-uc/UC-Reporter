from application.forms import UCRepoterLogin, SelectNavigation
from flask_login import current_user, login_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import login
from pprint import pprint
from application.sqlrequests import cms_sql_request_dict
from flask import request
from werkzeug.urls import url_parse

class User(UserMixin):

    id = ""
    username = ""
    password = ""
    password_hash = ""

    def __init__(self, id):
        self.id = id

        sql_request_result_string = "SELECT username, password, password_hash FROM ucreporter_users WHERE id='" + str(id) + "';"
        rows_list = cms_sql_request_dict(sql_request_result_string)

        pprint(rows_list)

        if not isinstance(rows_list, list):
            console_output = "В БД нет пользователя: " + form_login.login_field.data
            print(console_output)
            self.id = "99"
            self.username = "tempuser"
            self.password = "12345"
            self.password_hash = "12345"


        self.username = rows_list[0]["username"]
        self.password = rows_list[0]["password"]
        self.password_hash = rows_list[0]["password_hash"]


    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def set_hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_hash_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    print("UserID from user_loader:" + str(id))
    u = User(id)
    return u

def ucreporter_login():

    DEFAULT_PAGE_FOR_REDIRECT = 'cmspage'

    # Проверяем аутентифицирован ли пользователь
    if current_user.is_authenticated:
        console_output = "User " + current_user.username + " is athenticated"
        print(console_output)
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": "cms_recordings_page"
        }
        return renderdata

    # Пользователь не аутентифицирован
    console_output = "User NOT is athenticated"
    print(console_output)

    # Генерируем форму навигации
    console_output = "Генерируем форму навигации"
    print(console_output)
    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        print(console_output)
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": form_navigation.select_navigation.data
        }
        return renderdata

    # Генерируем форму для входа
    console_output = "Генерируем форму для входа"
    print(console_output)
    form_login = UCRepoterLogin(meta={'csrf': False})
    if form_login.validate_on_submit():

        console_output = "Нажата кнопка Login"
        print(console_output)
        # Запрашиваем данные о пользователе по его логину
        sql_request_result_string = "SELECT id, password FROM ucreporter_users WHERE username='" + str(form_login.login_field.data) + "';"
        rows_list = cms_sql_request_dict(sql_request_result_string)
        console_output = "Запрашиваем данные пользователя " + str(form_login.login_field.data) + " из БД"
        print(console_output)
        pprint(rows_list)

        # Проверяем получены ли данные о пользователе
        if not isinstance(rows_list, list):
            console_output = "В БД нет пользователя: " + form_login.login_field.data
            print(console_output)
            # Пользователя с такими логином и паролем нет в БД - переадресуем заново на страницу в логином
            renderdata = {
                "rendertype": "redirect",
                "redirect_to": "login"
            }
            return renderdata


        console_output = "Данные пользователя получены"
        print(console_output)

        # проверяем введенный пароль
        if rows_list[0]["password"] != form_login.password_field.data:
            console_output = "Пароль в БД не совпадает"
            print(console_output)
            # Пользователя с такими логином и паролем нет в БД - переадресуем заново на страницу в логином
            renderdata = {
                "rendertype": "redirect",
                "redirect_to": "login"
            }
            return renderdata

        console_output = "Пароли совпали"
        print(console_output)
        console_output = "Получен id пользователя: " + rows_list[0]["id"]
        print(console_output)
        # создаем объект нового пользователя
        u = User(rows_list[0]["id"])
        console_output = "Создан новый объект пользователя: " + u.username
        print(console_output)

        # Пользователь есть - логиним его
        login_user(u, remember=True)
        console_output = "New user logged in"
        print(console_output)
        next_page = request.args.get('next')
        console_output = "Next page: " + next_page
        print(console_output)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = DEFAULT_PAGE_FOR_REDIRECT
            renderdata = {
                "rendertype": "redirect",
                "redirect_to": next_page
            }
            return renderdata
        renderdata = {
            "rendertype": "redirect_to_link",
            "redirect_to": next_page
        }
        return renderdata


    console_output = ""
    renderdata = {
        "rendertype": "success",
        "html_template": "ucreporter_login.html",
        "html_page_title": "UC Reporter login",
        "console_output": console_output,
        "form_navigation": form_navigation,
        "form_login": form_login
    }
    return renderdata
