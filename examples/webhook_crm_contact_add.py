import json
import requests

# URL вебхука
WEBHOOK_URL = "https://WEBHOOK_URL/crm.contact.add"

# Данные для отправки
payload = {
    "fields":
		{ 
			"NAME": "Глеб", 
			"SECOND_NAME": "Егорович", 
			"LAST_NAME": "Титов", 
			"OPENED": "Y", 
			"ASSIGNED_BY_ID": 1, 
			"TYPE_ID": "CLIENT",
			"SOURCE_ID": "SELF",
			"PHONE": [ { "VALUE": "555888", "VALUE_TYPE": "WORK" } ] 	
		},
	"params": { "REGISTER_SONET_EVENT": "Y" }	
}

# Отправляем POST-запрос
response = requests.post(WEBHOOK_URL, json=payload)

# Выводим результат
print(response.status_code)
# 200
print(json.dumps(response.json(), indent=4, ensure_ascii=False))
# {
#     "result": 644,
#     "time": {
#         "start": 1722992489.557107,
#         "finish": 1722992489.850241,
#         "duration": 0.2931339740753174,
#         "processing": 0.2653169631958008,
#         "date_start": "2024-08-07T04:01:29+03:00",
#         "date_finish": "2024-08-07T04:01:29+03:00",
#         "operating_reset_at": 1722993089,
#         "operating": 0.26529693603515625
#     }
# }