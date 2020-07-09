from application.forms import UCRepoterLogin, SelectNavigation
from flask_login import current_user, login_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import login
from pprint import pprint
from application.sqlrequests import cms_sql_request_dict
from flask import request
from werkzeug.urls import url_parse
import logging.handlers
from pprint import pformat

class User(UserMixin):

    id = ""
    username = ""
    password = ""
    password_hash = ""
    DB_search_result = False

    def __init__(self, id):

        logger = logger_init_auth()

        self.id = id

        console_output = "Инициализации нового пользовательского объекта id: " + str(self.username) + ". Выполняется запрос в базу данных."
        print(console_output)
        logger.debug(console_output)

        sql_request_result_string = "SELECT username, password, password_hash FROM ucreporter_users WHERE id='" + str(id) + "';"
        rows_list = cms_sql_request_dict(sql_request_result_string)

        console_output = "Инициализации нового пользовательского объекта. Из базы данных получены данные о пользователе:"
        print(console_output)
        logger.debug(console_output)
        pprint(rows_list)
        logger.debug(pformat(rows_list))

        if isinstance(rows_list, list):
            self.username = rows_list[0]["username"]
            self.password = rows_list[0]["password"]
            self.password_hash = rows_list[0]["password_hash"]
            self.DB_search_result = True
            console_output = "Инициализации нового пользовательского объекта выполнена username: " + str(self.username)
            print(console_output)
            logger.debug(console_output)
        else:
            console_output = "Ошибка инициализации нового пользовательского объекта - в БД нет пользователя c id: " + str(id)
            print(console_output)
            logger.debug(console_output)
            self.DB_search_result = False


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

    logger = logger_init_auth()

    console_output = "Flask-Login иницировал проверку текущего пользователя"
    print(console_output)
    logger.debug(console_output)

    console_output = ("Flask-Login извлек UserID текущего пользователя из сеанса:" + str(id))
    print(console_output)
    logger.debug(console_output)

    u = User(id)
    if u.DB_search_result:
        console_output = "Flask-Login создал объект текушего пользователя c id: " + str(id)
        print(console_output)
        logger.debug(console_output)
        return u
    else:
        console_output = "Flask-Login не смог получить информацию о текущем пользователе: " + str(id) + ". Производится удаление текущего пользователя из сеанса."
        print(console_output)
        logger.debug(console_output)
        return None

def ucreporter_login():

    DEFAULT_PAGE_FOR_REDIRECT = 'cmspage'

    logger = logger_init_auth()

    # Проверяем аутентифицирован ли пользователь
    if current_user.is_authenticated:
        console_output = "Пользователь " + current_user.username + " аутентифицирован"
        print(console_output)
        logger.debug(console_output)
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": "cms_recordings_page"
        }
        return renderdata

    # Пользователь не аутентифицирован
    console_output = "Пользователь не аутентифицирован"
    print(console_output)
    logger.debug(console_output)

    # Генерируем форму навигации
    console_output = "Генерируем форму навигации"
    print(console_output)
    logger.debug(console_output)
    form_navigation = SelectNavigation(meta={'csrf': False})
    if form_navigation.validate_on_submit():
        console_output = "Нет активного запроса"
        print(console_output)
        logger.debug(console_output)
        renderdata = {
            "rendertype": "redirect",
            "redirect_to": form_navigation.select_navigation.data
        }
        return renderdata

    # Генерируем форму для входа
    console_output = "Генерируем форму для входа"
    print(console_output)
    logger.debug(console_output)
    form_login = UCRepoterLogin(meta={'csrf': False})
    if form_login.validate_on_submit():

        console_output = "Нажата кнопка Login"
        print(console_output)
        logger.debug(console_output)
        # Запрашиваем данные о пользователе по его логину
        sql_request_result_string = "SELECT id, password FROM ucreporter_users WHERE username='" + str(form_login.login_field.data) + "';"
        rows_list = cms_sql_request_dict(sql_request_result_string)
        console_output = "Запрашиваем данные пользователя " + str(form_login.login_field.data) + " из БД"
        print(console_output)
        logger.debug(console_output)
        pprint(rows_list)
        logger.debug(pformat(rows_list))

        # Проверяем получены ли данные о пользователе
        if not isinstance(rows_list, list):
            console_output = "В БД нет пользователя: " + form_login.login_field.data
            print(console_output)
            logger.debug(console_output)
            # Пользователя с такими логином и паролем нет в БД - переадресуем заново на страницу в логином
            renderdata = {
                "rendertype": "redirect",
                "redirect_to": "login"
            }
            return renderdata


        console_output = "Данные пользователя получены"
        print(console_output)
        logger.debug(console_output)

        # проверяем введенный пароль
        if rows_list[0]["password"] != form_login.password_field.data:
            console_output = "Пароль в БД не совпадает"
            print(console_output)
            logger.debug(console_output)
            # Пользователя с такими логином и паролем нет в БД - переадресуем заново на страницу в логином
            renderdata = {
                "rendertype": "redirect",
                "redirect_to": "login"
            }
            return renderdata

        console_output = "Пароли совпали"
        print(console_output)
        logger.debug(console_output)
        console_output = "Получен id пользователя: " + rows_list[0]["id"]
        print(console_output)
        logger.debug(console_output)
        # создаем объект нового пользователя
        u = User(rows_list[0]["id"])
        console_output = "Создан новый объект пользователя: " + u.username
        print(console_output)
        logger.debug(console_output)

        # Пользователь есть - логиним его
        login_user(u, remember=True)
        console_output = "New user logged in"
        print(console_output)
        logger.debug(console_output)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            console_output = "Next page empty"
            print(console_output)
            logger.debug(console_output)
            next_page = DEFAULT_PAGE_FOR_REDIRECT
            renderdata = {
                "rendertype": "redirect",
                "redirect_to": next_page
            }
            return renderdata
        console_output = "Next page: " + next_page
        print(console_output)
        logger.debug(console_output)
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

def logger_init_auth():

    # Настройка логирования
    UCREPORTER_AUTH_LOG_FILE_NAME = "../logs/UCREPORTER_AUTH.log"
    UCREPORTER_AUTH_LOG_FILE_SIZE = 2048000
    UCREPORTER_AUTH_LOG_FILE_COUNT = 5

    # Диспетчер логов
    logger = logging.getLogger('UC-REPORTER_AUTH')
    #
    logger.setLevel(logging.DEBUG)

    # Обработчик логов - запись в файлы с перезаписью
    if logger.hasHandlers():

        console_output = "handlers are already exists in Logger UC-REPORTER_AUTH"
        print("UC-REPORTER_AUTH: " + console_output)
        logger.debug(console_output)

        return logger

    else:
        console_output = "no any handlers in Logger UC-REPORTER_AUTH - create new one"
        print("UC-REPORTER_AUTH: " + console_output)

        auth_rotate_file_handler = logging.handlers.RotatingFileHandler(UCREPORTER_AUTH_LOG_FILE_NAME,
                                                                        maxBytes=UCREPORTER_AUTH_LOG_FILE_SIZE,
                                                                        backupCount=UCREPORTER_AUTH_LOG_FILE_COUNT)
        auth_rotate_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
        auth_rotate_file_handler.setFormatter(formatter)
        logger.addHandler(auth_rotate_file_handler)

        logger.info(console_output)
        console_output = "New handler was created in Logger UC-REPORTER_AUTH"
        print("UC-REPORTER_AUTH: " + console_output)
        logger.info(console_output)
        return logger

