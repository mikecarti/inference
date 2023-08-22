from datetime import datetime
from time import sleep

import requests

URL = "http://0.0.0.0:8000/add_message"
payload = {
    "text": "сколько стоит доставка",
    "date": datetime.now().isoformat(),
    "from_user": {
        "id": 228,
        "username": "anonymous"
    }
}
response = requests.post(URL, json=payload)
if response.status_code == 200:  # Assuming a successful response has a status code of 200
    response_data = response.json()  # Convert the response JSON string to a Python dictionary
    print(response_data)
else:
    print("Request failed with status code:", response.status_code)
    print("Response content:", response.text)

sleep(1)

URL = "http://0.0.0.0:8000/answer_message"
payload = {
    "user_id": 228,
    "misspelling_level": 2,
    "anger_level": 3
}
response = requests.post(URL, json=payload)


if response.status_code == 200:  # Assuming a successful response has a status code of 200
    response_data = response.json()  # Convert the response JSON string to a Python dictionary
    print(response_data)
else:
    print("Request failed with status code:", response.status_code)
    print("Response content:", response.text)
