import requests


def refresh_token(client_id, client_secret, refresh_token):
    """
    Метод обновляет токен авторизации.

    :param client_id: код приложения, получаемый в партнерском кабинете при регистрации приложения 
                      либо на портале в случае локального приложения.
    :param client_secret: секретный ключ приложения, получаемый в партнерском кабинете при регистрации 
                          приложения либо на портале в случае локального приложения.
    :param refresh_token: значение сохраненного токена продления авторизации.
    :return: ответ от сервера в формате JSON.
    """
    # URL для запроса обновления токена
    url = "https://oauth.bitrix.info/oauth/token/"
    payload = {
        "grant_type": "refresh_token",  # тип авторизационных данных
        "client_id": client_id,  # код приложения
        "client_secret": client_secret,  # секретный ключ приложения
        "refresh_token": refresh_token  # значение сохраненного токена продления авторизации
    }
    response = requests.post(url, data=payload)
    return response.json()

