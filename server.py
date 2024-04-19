# импортируем библиотеки
import logging
import random

from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}


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
            }
        ],
            'current_city':0
        }

        # Заполняем текст ответа
        res['response']['text'] = 'Привет!'
        # Получим подсказки
        print(sessionStorage[user_id]['cities'])
        city=random.choice(sessionStorage[user_id]['cities'])
        print(city)
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = ' Какой это город?'
        res['response']['card']['image_id'] = city['imgs'][city['current_img']]
        return

    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    user_text = req['request']['original_utterance'].lower()
    cities = sessionStorage[user_id]['cities']
    city = cities[sessionStorage[user_id]['current_city']]
    if city['title'].lower() in user_text:
            res['response']['text'] = f"Ты угадал - это {city['title']}!"
            city['current_img'] = (city['current_img']+1)%2 #след картинку
            sessionStorage[user_id]['current_city']=random.choice(cities)
            res['response']['end_session']=True
    else:
            res['response']['text'] = f"Не угадал!"

    return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = f'Все говорят "%s", а ты купи {animal}!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
