import urllib
from pydantic import BaseModel
from typing import Dict


class CallRequest(BaseModel):
    method: str
    params: Dict = {}

    def form_data(self, convention="%s"):
        """
        Возвращает преобразованные параметры (qs) в виде строки
        Пример: FIELDS[NAME]=test&FIELDS[LAST_NAME]=test
        """
        return self._format_params_recursion(self.params, convention)

    def _format_params_recursion(self, params, convention="%s"):
        if not params:
            return ""

        output = []
        for key, value in params.items():
            if isinstance(value, dict):
                output.append(
                    self._format_params_recursion(value, convention % key + "[%s]")
                )
            elif isinstance(value, list):
                new_params = {str(i): element for i, element in enumerate(value)}
                output.append(
                    self._format_params_recursion(new_params, convention % key + "[%s]")
                )
            else:
                key = urllib.parse.quote(key)
                val = urllib.parse.quote(str(value))
                output.append(convention % key + "=" + val)

        return "&".join(output)

    # crm.contact.add?FIELDS[NAME]=test&FIELDS[LAST_NAME]=test
    def get_path(self):
        """
        Возвращает путь, сформированный из метода и обработанных параметров (qs)
        Пример: FIELDS[NAME]=test&FIELDS[LAST_NAME]=test
        """
        url = f"{self.method}?{self.form_data()}"
        return url
