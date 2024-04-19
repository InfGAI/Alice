# импортируем библиотеки
import logging
import random

from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {
    'E8CE48D4050F69DC9457CAD77F0637CFF920653017BC98EA2ED0BA68978BE019':{
            'cities': [ {
                'title': 'Париж',
                'imgs': ['1540737/a85f7166d351e5e8ec92', '1030494/c58e1c4c948099d394c2'],
                'current_img': 0
            }
        ],
            'current_city':0
        }
}


@app.route('/', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info('Request: %r', request.json)

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    # Преобразовываем в JSON и возвращаем
    return jsonify(response)


def handle_dialog(req, res):
    global current
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'cities': [ {
                'title': 'Париж',
                'imgs': ['1540737/a85f7166d351e5e8ec92', '1030494/c58e1c4c948099d394c2'],
                'current_img': 0
            },
               {
                'title': 'Москва',
                'imgs': ['997614/b545bb607ed4ba6937c1', '1533899/12ede26b423a21640b82'],
                'current_img': 0
            }
        ],
            'current_city':0
        }

        # Заполняем текст ответа
        res['response']['text'] = 'Привет!'
        # Получим подсказки
        cities = sessionStorage[user_id]['cities']
        sessionStorage[user_id]['current_city']=random.choice(range(len(cities)))
        city = cities[sessionStorage[user_id]['current_city']]
        print(0,city)
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = ' Какой это город?'
        res['response']['card']['image_id'] = city['imgs'][city['current_img']]
        return

    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    user_text = req['request']['original_utterance'].lower()
    cities = sessionStorage[user_id]['cities']
    city = cities[sessionStorage[user_id]['current_city']]
    print(city)
    if city['title'].lower() in get_city(req):
            res['response']['text'] = f"Ты угадал - это {city['title']}!"
            cities[sessionStorage[user_id]['current_city']]['current_img'] = (city['current_img']+1)%2 #след картинку
            sessionStorage[user_id]['current_city']=random.choice(range(len(cities)))
            city = cities[sessionStorage[user_id]['current_city']]
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = ' Какой это город?'
            res['response']['card']['image_id'] = city['imgs'][city['current_img']]

    else:
            res['response']['text'] = f"Не угадал!"

    return



def get_city(req):
    cities=[]
    for item in req['request']['nlu']['entities']:
        if item['type']=='YANDEX.GEO':
            cities.append(item['value']['city'])
    return cities


if __name__ == '__main__':
    app.run()
