import os

from fastapi import FastAPI
from crest.crest import CRestBitrix24
from src.logger.custom_logger import logger


def lifespan(app: FastAPI):
    logger.info("Запуск сервера FastAPI")

    # Создаем экземпляр CREST при инициализации приложения
    CRest = None

    try:
        if os.getenv("CLIENT_ID") and os.getenv("CLIENT_SECRET"):
            logger.info("Активирован режим работы с приложениями")
            CRest = CRestBitrix24(
                client_id=os.getenv("CLIENT_ID"),
                client_secret=os.getenv("CLIENT_SECRET"),
            )

        elif os.getenv("CLIENT_WEBHOOK"):
            logger.info("Активирован режим работы с вебхуками")
            CRest = CRestBitrix24(client_webhook=os.getenv("CLIENT_WEBHOOK"))

        else:
            raise Exception(
                "Необходимо задать CLIENT_ID и CLIENT_SECRET или CLIENT_WEBHOOK"
            )

        app.state.CRest = CRest

        yield
    except Exception as e:
        logger.exception(
            f"Возникла ошибка при запуске сервера FastAPI: {e}", exc_info=False
        )
        raise
    finally:
        logger.info("Завершение работы сервера FastAPI")
