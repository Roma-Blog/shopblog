from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

@csrf_exempt
def webhook_tg(request):
    if request.method == 'POST':
        update = json.loads(request.body)
        chat_id = update['message']['chat']['id']
        text = update['message']['text']

        # Пример ответа на сообщение
        if text == '/start':
            send_message(chat_id, 'Привет! Я ваш бот.')

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'not a POST request'})

def send_message(chat_id, text):
    TOKEN = 'YOUR_API_TOKEN'
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=payload)

