import json
import os
from datetime import datetime
from urllib.parse import urlencode

import requests
from environs import Env

# Инициализация Env
env = Env()
env.read_env(override=True)


class CRest:
    VERSION = "1.36"  # версия
    BATCH_COUNT = 50  # количество запросов в одном батче
    TYPE_TRANSPORT = "json"  # тип данных для передачи (json или xml)

    @staticmethod
    def install_app(request):
        """
        Устанавливает приложение на основе запроса.

        ### Описание:
        Определяет, как установить приложение в зависимости от информации в запросе.
        Обрабатываются два случая: установка при событии `ONAPPINSTALL` и установка по умолчанию.

        #### Аргументы:
        - `request` (dict): Словарь с данными запроса.

        #### Возвращаемое значение:
        - `dict`: Результат установки приложения, содержащий:
            - `rest_only` (bool): Флаг, указывающий, что приложение должно работать только через REST API. По умолчанию True.
            - `install` (bool): Флаг, указывающий, успешно ли выполнена установка приложения. По умолчанию False.
        """
        # Инициализация результата по умолчанию
        result = {"rest_only": True, "install": False}

        # Получение значений из запроса
        event = request.get("event")
        auth = request.get("auth")
        placement = request.get("PLACEMENT")

        # Установка приложения при событии ONAPPINSTALL
        if event == "ONAPPINSTALL" and auth:
            result["install"] = CRest.set_app_settings(auth, isInstall=True)

        # Установка приложения по умолчанию
        elif placement == "DEFAULT":
            result["rest_only"] = False
            app_settings = {
                "access_token": request.get("AUTH_ID"),
                "expires_in": request.get("AUTH_EXPIRES"),
                "application_token": request.get("APP_SID"),
                "refresh_token": request.get("REFRESH_ID"),
                "domain": request.get("DOMAIN"),
                "client_endpoint": f"https://{request.get('DOMAIN')}/rest/",
            }
            result["install"] = CRest.set_app_settings(app_settings, isInstall=True)

        # Логируем запрос и результат
        CRest.set_log({"request": request, "result": result}, "installApp")

        return result

    @staticmethod
    def set_app_settings(arSettings, isInstall=False):
        """
        ### Описание:
        Устанавливает настройки приложения.

        #### Аргументы:

        - `arSettings` (dict): Словарь с новыми настройками приложения.
        - `isInstall` (bool, по умолчанию False): Логическое значение, указывающее, является ли это установкой приложения. Если True, то `arSettings` будут использоваться для первоначальной установки.

        #### Возвращаемое значение:

        - `bool`: Результат установки настроек. Возвращает результат работы `CRest.set_setting_data`, либо `False` в случае ошибки.
        """
        if not isinstance(arSettings, dict):
            return False  # Если настройки не в виде словаря, возвращаем False

        # Если это не установка и уже есть старые настройки, объединяем их с новыми
        if not isInstall:
            oldData = CRest.get_app_settings() or {}
            arSettings.update(oldData)

        # Сохраняем обновленные настройки и возвращаем результат
        return CRest.set_setting_data(arSettings)

    @staticmethod
    def set_setting_data(arSettings):
        """
        Записывает данные настроек в файл `settings.json`.

        ### Описание:
        Метод записывает данные настроек в JSON-файл. Если при записи данных возникает ошибка,
        метод возвращает `False`. В противном случае возвращает `True`.

        #### Аргументы:
        - `arSettings` (dict): Словарь с данными настроек, которые необходимо записать в файл.

        #### Возвращаемое значение:
        - `bool`: `True`, если данные успешно записаны в файл, `False` в случае ошибки.
        """
        # Определяем путь к файлу настроек
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")

        try:
            # Открываем файл для записи и записываем данные
            with open(settings_path, "w") as file:
                file.write(CRest.wrap_data(arSettings))
            return True
        except (IOError, TypeError) as e:
            # Логируем ошибку, если запись не удалась
            CRest.set_log({"error": str(e)}, "setSettingData")
            return False

    @staticmethod
    def get_app_settings():
        """
        Получает настройки приложения из доступных источников.

        ### Описание:
        Метод сначала проверяет наличие URL веб-хука в переменных окружения. Если он найден,
        возвращаются настройки, используя этот URL. Если URL отсутствует, метод попытается
        получить настройки из другой конфигурации.

        #### Возвращаемое значение:
        - `dict` или `bool`: Возвращает словарь с настройками приложения, если все необходимые данные найдены.
        Возвращает `False`, если не удалось найти или получить текущие данные.
        """
        try:
            # Проверка наличия URL веб-хука в переменных окружения
            webhook_url = env.str("C_REST_WEB_HOOK_URL", None)
            if webhook_url:
                return {"client_endpoint": webhook_url, "is_web_hook": "Y"}

            # Получение данных из другого источника
            arData = CRest.get_setting_data()
            required_keys = {
                "access_token",
                "domain",
                "refresh_token",
                "application_token",
                "client_endpoint",
            }

            # Проверка наличия всех необходимых ключей
            if all(key in arData for key in required_keys):
                return arData

            return False

        except Exception as e:
            # Логирование ошибки для диагностики
            CRest.set_log({"error": str(e)}, "getAppSettings")
            return False

    @staticmethod
    def get_setting_data():
        """
        Получает данные настроек из файла `settings.json` и добавляет переменные окружения.

        ### Описание:
        Метод проверяет наличие файла `settings.json` в текущей директории. Если файл существует,
        данные читаются и добавляются переменные окружения `C_REST_CLIENT_ID` и `C_REST_CLIENT_SECRET`, если они определены и не пустые.

        #### Возвращаемое значение:
        - `dict`: Словарь с данными настроек, объединёнными из файла и переменных окружения.
        """

        return_data = {}
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")

        if os.path.exists(settings_path):
            try:
                # Открываем файл и читаем данные
                with open(settings_path, "r") as file:
                    raw_data = file.read()
                    # Обработка данных, аналогичная expandData
                    return_data = CRest.expand_data(raw_data)
            except (IOError, TypeError) as e:
                # Логируем ошибку чтения или декодирования JSON
                CRest.set_log({"error": str(e)}, "getSettingData")
                return {}

        # Получаем переменные окружения с использованием environs
        client_id = env.str("C_REST_CLIENT_ID", None)
        client_secret = env.str("C_REST_CLIENT_SECRET", None)

        if client_id:
            return_data["C_REST_CLIENT_ID"] = client_id
        if client_secret:
            return_data["C_REST_CLIENT_SECRET"] = client_secret

        return return_data

    @staticmethod
    def change_encoding(data, encoding=True):
        """
        Изменяет кодировку данных.

        ### Описание:
        Преобразует строки из одной кодировки в другую, в зависимости от параметра `encoding`.

        #### Аргументы:
        - data (str | dict): Данные, которые нужно преобразовать.
        - encoding (bool): Если True, преобразует данные в UTF-8. Если False, декодирует из UTF-8 в исходную кодировку.

        #### Возвращаемое значение:
        - str | dict: Данные с измененной кодировкой.
        """
        current_encoding = env.str("C_REST_CURRENT_ENCODING", default="utf-8")

        if isinstance(data, dict):
            return {
                CRest.change_encoding(k, encoding): CRest.change_encoding(v, encoding)
                for k, v in data.items()
            }
        elif isinstance(data, str):
            if encoding:
                return data.encode(current_encoding, errors="ignore").decode("utf-8")
            else:
                return data.encode("utf-8", errors="ignore").decode(current_encoding)
        else:
            # Если data не строка, список или словарь, возвращаем его без изменений
            return data

    @staticmethod
    def expand_data(data):
        """
        Расширяет данные, декодируя JSON и изменяя кодировку.

        ### Описание:
        Декодирует строку JSON и изменяет её кодировку, если переменная `C_REST_CURRENT_ENCODING` определена.

        #### Аргументы:
        - data (str): Строка JSON для декодирования.

        #### Возвращаемое значение:
        - dict: Расширенные данные в виде словаря.
        """
        # Декодирование строки JSON
        return_data = json.loads(data)
        # Изменение кодировки данных, если переменная окружения установлена
        if env.str("C_REST_CURRENT_ENCODING", default=None):
            return_data = CRest.change_encoding(return_data, encoding=False)
        return return_data

    @staticmethod
    def wrap_data(data, debug=False):
        """
        Кодирует данные в формате JSON с учетом кодировки и опциональной отладки.

        ### Описание:
        Метод преобразует данные в JSON-формат, учитывая текущую кодировку, если это необходимо.
        При активной отладке метод проверяет наличие ошибок кодирования и возвращает сообщение об ошибке, если таковая имеется.

        #### Аргументы:
        - `data`: Данные, которые необходимо закодировать в JSON.
        - `debug` (bool, по умолчанию False): Если True, включает режим отладки, который проверяет наличие ошибок кодирования.

        #### Возвращаемое значение:
        - `str`: Закодированные данные в формате JSON или сообщение об ошибке.
        """
        # Преобразование кодировки, если указана переменная окружения
        if env.str("C_REST_CURRENT_ENCODING", None):
            data = CRest.change_encoding(data, encoding=True)

        try:
            # Кодирование данных в формат JSON с экранированием специальных символов
            result = json.dumps(data, ensure_ascii=False, indent=4)
        except (TypeError, ValueError) as e:
            if debug:
                error_message = f"Failed encoding! Error: {str(e)}"
                return error_message

        return result

    @staticmethod
    def call(method, params=None):
        """
        Выполняет вызов метода Bitrix24 с указанными параметрами.

        ### Описание:
        Метод формирует запрос для указанного метода Bitrix24 и отправляет его,
        используя функцию `call_curl`. При необходимости параметры запроса могут быть
        преобразованы в соответствии с кодировкой, указанной в переменной окружения.

        #### Аргументы:
        - `method` (str): Название вызываемого метода Bitrix24.
        - `params` (dict, по умолчанию None): Параметры, передаваемые в метод.

        #### Возвращаемое значение:
        - dict: Результат выполнения запроса, возвращаемый функцией `call_curl`.
        """
        # Если параметры не переданы, используем пустой словарь
        if params is None:
            params = {}

        # Формируем данные запроса
        arPost = {"method": method, "params": params}

        # Преобразование кодировки, если указано в переменной окружения
        if env.str("C_REST_CURRENT_ENCODING", None):
            arPost["params"] = CRest.change_encoding(arPost["params"])

        # Выполнение запроса и возврат результата
        result = CRest.call_curl(arPost)

        return result

    @staticmethod
    def call_batch(arData, halt=0):
        """
        Выполняет пакетный вызов методов Bitrix24 API.

        ### Описание:
        Метод отправляет несколько запросов к API Bitrix24 в одном пакетном запросе.
        Если возникают ошибки, можно остановить выполнение пакета на первой ошибке
        с помощью параметра `halt`.

        #### Аргументы:
        - `arData` (dict): Словарь с данными запросов, где ключи - это имена запросов,
                        а значения - словари с методами и параметрами.
        - `halt` (int, по умолчанию 0): Флаг, указывающий, следует ли остановить выполнение
                                        пакета при первой ошибке (0 - продолжить, 1 - остановить).

        #### Возвращаемое значение:
        - `dict`: Результат выполнения пакетного запроса.

        #### Пример arData:
        arData = {
            'find_contact': {
                'method': 'crm.duplicate.findbycomm',
                'params': {"entity_type": "CONTACT", "type": "EMAIL", "values": ["info@bitrix24.com"]}
            },
            'find_contact_another_func': {
                'method': 'crm.duplicate.findbycomm',
                'params': {"entity_type": "CONTACT", "type": "EMAIL", "values": ["info@bitrix24.com"]}
            }
        }

        """
        # Результат выполнения
        arResult = {}

        # Проверяем, что входные данные являются словарем
        if isinstance(arData, dict):
            # Преобразуем кодировку данных, если указано в переменной окружения
            if env.str("C_REST_CURRENT_ENCODING", None):
                arData = CRest.change_encoding(arData)

            # Словарь для хранения команд и параметров для пакетного вызова
            arDataRest = {"cmd": {}}
            i = 0

            # Проходим по каждому запросу в входных данных
            for key, data in arData.items():
                if "method" in data:
                    i += 1
                    # Проверяем, не превышает ли количество запросов в пакете лимит
                    if i <= CRest.BATCH_COUNT:
                        # Формируем строку запроса
                        method = data["method"]
                        params = data.get("params", {})
                        if params:
                            # Кодируем параметры для включения в URL
                            method += "?" + urlencode(params)
                        arDataRest["cmd"][key] = method

            # Если есть команды для выполнения
            if arDataRest["cmd"]:
                # Добавляем флаг для остановки при ошибке
                arDataRest["halt"] = halt
                # Формируем пакетный запрос
                arPost = {"method": "batch", "params": arDataRest}
                # Выполняем запрос и сохраняем результат
                arResult = CRest.call_curl(arPost)

        return arResult

    @staticmethod
    def call_curl(params):
        """
        Выполняет HTTP-запрос с использованием библиотеки requests.

        Аргументы:
        - params (dict): Параметры запроса, включая метод и параметры для метода.

        Возвращаемое значение:
        - dict: Результат выполнения запроса или информация об ошибке.
        """

        # Получение настроек приложения
        arSettings = CRest.get_app_settings()
        if arSettings is not False:
            # Определение URL в зависимости от параметров
            if params.get("this_auth") == "Y":
                url = "https://oauth.bitrix.info/oauth/token/"
            else:
                url = f"{arSettings['client_endpoint']}{params['method']}.{CRest.TYPE_TRANSPORT}"
                if arSettings.get("is_web_hook") != "Y":
                    params["params"]["auth"] = arSettings["access_token"]

            # Получение значения IGNORE_SSL из переменных окружения
            ignore_ssl = env.bool(
                "IGNORE_SSL", False
            )  # По умолчанию False, если переменная не задана

            # Использование значения ignore_ssl в настройках SSL
            verify = not ignore_ssl

            # Выполнение POST-запроса
            try:
                response = requests.post(
                    url,
                    data=params["params"],
                    headers={"User-Agent": f"Bitrix24 CRest Python {CRest.VERSION}"},
                    verify=verify,
                )

                if CRest.TYPE_TRANSPORT == "xml" and params.get("this_auth") != "Y":
                    result = response.text
                else:
                    result = CRest.expand_data(response.text)

                # Обработка ошибок в ответе
                if "error" in result:
                    if result["error"] == "expired_token" and not params.get(
                        "this_auth"
                    ):
                        result = CRest.get_new_auth(params)
                    else:
                        error_inform = {
                            "expired_token": "Expired token, can’t get new auth? Check access OAuth server.",
                            "invalid_token": "Invalid token, need to reinstall application",
                            "invalid_grant": "Invalid grant, check C_REST_CLIENT_SECRET or C_REST_CLIENT_ID",
                            "invalid_client": "Invalid client, check C_REST_CLIENT_SECRET or C_REST_CLIENT_ID",
                            "QUERY_LIMIT_EXCEEDED": "Too many requests, maximum 2 queries per second",
                            "ERROR_METHOD_NOT_FOUND": "Method not found! Check application permissions",
                            "NO_AUTH_FOUND": 'Setup error, check event "OnRestCheckAuth"',
                            "INTERNAL_SERVER_ERROR": "Server down, try again later",
                        }
                        result["error_information"] = error_inform.get(
                            result["error"], "Unknown error"
                        )

                # Логирование результата
                CRest.set_log(
                    {
                        "url": url,
                        "info": response.headers,
                        "params": params,
                        "result": result,
                    },
                    "callCurl",
                )

                return result
            except Exception as e:
                # Логирование ошибки исключения
                CRest.set_log(
                    {
                        "message": str(e),
                        "code": e.__class__.__name__,
                        "trace": e.__traceback__,
                        "params": params,
                    },
                    "exceptionCurl",
                )

                return {
                    "error": "exception",
                    "error_exception_code": e.__class__.__name__,
                    "error_information": str(e),
                }
        else:
            # Логирование отсутствия настроек
            CRest.set_log({"params": params}, "emptySetting")

        return {
            "error": "no_install_app",
            "error_information": "Error installing app, please install the local application",
        }

    @staticmethod
    def get_new_auth(arParams):
        """
        Получает новый токен авторизации и повторно выполняет запрос, если возникла ошибка авторизации.

        Аргументы:
        - arParams (dict): Параметры первоначального запроса, при котором произошла ошибка авторизации.

        Возвращает:
        - dict: Результат выполнения повторного запроса с новым токеном.
        """
        # Инициализация результата
        result = {}

        # Получение текущих настроек приложения
        arSettings = CRest.get_app_settings()

        # Проверка, успешно ли получены настройки
        if arSettings is not False:
            # Формирование параметров для запроса на обновление токена
            arParamsAuth = {
                "this_auth": "Y",  # Указание, что это запрос для обновления токена
                "params": {
                    "client_id": arSettings["C_REST_CLIENT_ID"],
                    "grant_type": "refresh_token",  # Используем grant_type для обновления токена
                    "client_secret": arSettings["C_REST_CLIENT_SECRET"],
                    "refresh_token": arSettings["refresh_token"],
                },
            }

            # Выполнение запроса для получения нового токена
            newData = CRest.call_curl(arParamsAuth)

            # Удаление конфиденциальных данных из ответа
            newData.pop("C_REST_CLIENT_ID", None)
            newData.pop("C_REST_CLIENT_SECRET", None)
            newData.pop("error", None)

            # Сохранение нового токена в настройках приложения
            if CRest.set_app_settings(newData):
                # Обновление параметров для повторного запроса
                arParams["this_auth"] = "N"
                # Повторный запрос с новыми параметрами
                result = CRest.call_curl(arParams)

        # Возврат результата
        return result

    @staticmethod
    def check_server():
        """
        Проверяет наличие необходимых настроек для работы CRest.

        Аргументы:
        - print_result (bool): Флаг для вывода результата проверки.

        Возвращаемое значение:
        - dict: Словарь с результатом проверки.
        """
        # Инициализация библиотеки environs для работы с переменными окружения
        env = Env()
        env.read_env()

        # Получаем настройки из переменных окружения
        client_id = env.str("C_REST_CLIENT_ID", None)
        client_secret = env.str("C_REST_CLIENT_SECRET", None)
        web_hook_url = env.str("C_REST_WEB_HOOK_URL", None)

        # Проверяем наличие необходимых параметров
        if (client_id and client_secret) or web_hook_url:
            result = {"success": "ok"}
        else:
            result = {
                "error": "Required settings are missing. Either C_REST_CLIENT_ID and C_REST_CLIENT_SECRET or C_REST_WEB_HOOK_URL must be set."
            }

        return result

    @staticmethod
    def set_log(data, log_type=""):
        """
        Записывает данные в лог-файл.

        Аргументы:
        - data (dict): Данные для логирования.
        - log_type (str): Тип лога, используемый в названии файла.
        """
        try:
            # Добавление текущей даты и времени к данным
            if isinstance(data, dict):
                data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Определение пути к директории логов
            logs_dir = os.path.join(os.path.dirname(__file__), "logs")
            # Создание директории, если она не существует
            os.makedirs(logs_dir, exist_ok=True)

            # Определение имени файла лога
            log_filename = os.path.join(logs_dir, f"{log_type}_log.log")
            # Открытие файла в режиме добавления и запись данных
            with open(log_filename, "a", encoding="utf-8") as file:
                file.write(CRest.wrap_data(data) + "\n")

        except Exception as e:
            print(f"Ошибка при логировании: {e}")
