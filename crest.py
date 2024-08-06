import json
import os
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
            # Преобразуем данные в формат JSON
            json_data = json.dumps(arSettings, ensure_ascii=False, indent=4)

            # Открываем файл для записи и записываем данные
            with open(settings_path, "w") as file:
                file.write(json_data)
            return True
        except (IOError, TypeError, ValueError) as e:
            # Можно добавить логирование ошибки или сообщение для отладки
            print(f"Ошибка при записи данных в файл: {e}")
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

        except Exception:
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
                # Открываем файл и читаем данные напрямую как JSON
                with open(settings_path, "r") as file:
                    return_data = json.load(file)
            except (IOError, TypeError, json.JSONDecodeError) as e:
                # Логирование ошибки или вывод сообщения для отладки
                print(f"Ошибка при чтении или разборе файла настроек: {e}")
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

            # flat_dict = CRest.flatten_dict(params["params"])
            # sPostFields = urlencode(flat_dict, doseq=True)

            # Выполнение POST-запроса
            try:
                response = requests.post(
                    url,
                    json=params["params"],
                    # data=sPostFields,  # строчный запрос заменен блочным выше
                    headers={"User-Agent": f"Bitrix24 CRest Python {CRest.VERSION}"},
                )
                result = response.text
                if CRest.TYPE_TRANSPORT == "xml" and params.get("this_auth") != "Y":
                    result = result
                else:
                    result = json.loads(response.text)

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

                return result
            except Exception as e:
                return {
                    "error": "exception",
                    "error_exception_code": e.__class__.__name__,
                    "error_information": str(e),
                }
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

    # Претендент на удаление
    @staticmethod
    def flatten_dict(d, parent_key="", sep=""):
        """
        Преобразует многомерный словарь в одномерный.

        ### Описание:
        Эта функция принимает вложенный словарь и преобразует его в одномерный,
        где ключи формируются путем конкатенации всех уровней иерархии.
        Полезно для преобразования сложных структур данных в формат,
        подходящий для HTTP-запросов.

        #### Аргументы:
        - d (dict): Входной словарь, который может содержать вложенные словари и списки.
        - parent_key (str): Ключ верхнего уровня для текущего уровня рекурсии.
        Используется для построения ключей в результирующем словаре.
        - sep (str): Разделитель, используемый между уровнями вложенности.

        #### Возвращаемое значение:
        - dict: Одномерный словарь, в котором все ключи представляют полные пути к значениям.
        """

        # Инициализируем список для хранения результирующих пар ключ-значение
        items = []

        # Перебираем все элементы словаря
        for k, v in d.items():
            # Формируем новый ключ, добавляя текущий к родительскому ключу
            # Если это верхний уровень, используем только текущий ключ
            new_key = f"{parent_key}{sep}[{k}]" if parent_key else k

            # Если значение - это словарь, вызываем рекурсивно flatten_dict
            if isinstance(v, dict):
                items.extend(CRest.flatten_dict(v, new_key, sep=sep).items())

            # Если значение - это список, обрабатываем каждый элемент
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    # Если элемент списка - словарь, вызываем рекурсивно flatten_dict
                    if isinstance(item, dict):
                        items.extend(
                            CRest.flatten_dict(item, f"{new_key}[{i}]", sep=sep).items()
                        )
                    else:
                        # Если элемент не словарь, добавляем его в список как есть
                        items.append((f"{new_key}[{i}]", item))
            else:
                # Если значение - ни словарь, ни список, просто добавляем его в список
                items.append((new_key, v))

        # Преобразуем список пар ключ-значение в словарь и возвращаем
        return dict(items)
