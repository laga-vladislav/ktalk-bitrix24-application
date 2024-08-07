import os
from src.logger.custom_logger import logger


def lifespan(_):
    logger.info("Запуск сервера FastAPI")

    # ВОЗМОЖНО ЭТО МОЖНО ПЕРЕНЕСТИ НА CREST ЧАСТЬ
    # НАПРИМЕР, CREST.CHECK_ENV() КОТОРЫЙ ВЕРНЕТ TRUE or FALSE
    # БЫЛО БЫ ЗАМЕЧАТЕЛЬНО, ВЕДЬ ТОГДА ИЗБАВИМСЯ ПОЛНОСТЬЮ ОТ ЗАВИСИМОСТИ
    # IMPORT OS И ПЕРЕМЕННЫХ .env НА СЕВРЕРЕ И С ЭТИМ РАБОТАЛ САМ CREST
    
    try:
        if os.getenv("CLIENT_ID") and os.getenv("CLIENT_SECRET"):
            logger.info("Активирован режим работы с приложениями")
        elif os.getenv("CLIENT_WEBHOOK"):
            logger.info("Активирован режим работы с вебхуками")
        else:
            raise Exception("Необходимо задать CLIENT_ID и CLIENT_SECRET или CLIENT_WEBHOOK") 
        yield
    except Exception as e:
        logger.exception(f"Возникла ошибка при запуске сервера FastAPI: {e}", exc_info=False)
        raise
    finally:
        logger.info("Завершение работы сервера FastAPI")