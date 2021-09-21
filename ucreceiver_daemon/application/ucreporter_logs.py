import logging.handlers
from sys import platform


def logger_init(logger_name, logging_level):
    # Настройка логирования для логирования в файл
    LOG_FILE_NAME = "../logs/" + logger_name + ".log"
    LOG_FILE_SIZE = 2048000
    LOG_FILE_COUNT = 5

    # Создаем диспетчер логов
    logger = logging.getLogger(logger_name)
    # Устанавливаем уровень логирования для диспетчера логов
    logger.setLevel(logging_level)

    # Проверяем наличие обработчика логов в диспетчере логов
    if logger.hasHandlers():
        console_output = "Handlers are already exists in Logger " + logger_name + str([(type(handler)) for handler in logger.handlers])
        logger.debug(console_output)
        console_output = logger_name + ": logging level: " + logging.getLevelName(logging_level)
        logger.debug(console_output)
        return logger
    else:
        console_output = "No any handlers in Logger " + logger_name + " - create new one"
        # Проверяем платформу
        if platform == "linux":
            # Создаем обработчик логов отправляющий их на SocketServer логов для Linux
            socketHandler = logging.handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
            logger.addHandler(socketHandler)

        elif platform == "win32":
            # Создаем обработчик логов отправляющий файл логов для Windows
            auth_rotate_file_handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME,
                                                                            maxBytes=LOG_FILE_SIZE,
                                                                            backupCount=LOG_FILE_COUNT)

            auth_rotate_file_handler.setLevel(logging_level)
            formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
            auth_rotate_file_handler.setFormatter(formatter)
            logger.addHandler(auth_rotate_file_handler)

        logger.info(console_output)
        console_output = "New handler was created in Logger " + logger_name + " logging level: " + logging.getLevelName(
            logging_level)
        logger.info(console_output)
        return logger
