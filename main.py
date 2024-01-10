import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_bot import VkBot
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import requests
import datetime
from threading import Thread
from flask import Flask, request


def write_msg(user_id, text, keyboard=None, template=None):
    vk.method("messages.send", {"user_id": user_id, "message": text,
                                "random_id": get_random_id(),
                                "keyboard": keyboard, "template": template})


# API-ключ созданный ранее
token = "vk1.a.3xbXIeYBGghiCZwF1L2UzYJMsS5AvIuyVOgvmXLS9AVSg3Cq5_AidDm7jjo46r8ZVYRmHx7WrtqFpgjLM3KJkiYpSofOd-RLiyn0dXn-hFJd87xB7nEcywl8FavvNnuZi5-Vc57xMPskCW4WKk6xRg5BcuD49QxaGn6y8pyOjKpxqxnmh8dNJ3Rx5GqROhADyqWKWzW-IW0rP5VeCWclMQ"

# # Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

session_api = vk.get_api()
longpoll = VkLongPoll(vk)



TYPE_PERSON_DEFAULT = 'клиент'
TYPE_REQUEST_DEFAULT = 'есть проблема'
SUBTYPE_REQUEST_DEFAULT = 'другое'
TYPES_PERSON = ['клиент', 'магазин', 'бэк офис', 'сотрудник Жизньмарт']
ALLNAMEBUTTON_PROBLEMS = [
                ('с обслуживанием', [TYPES_PERSON[0]]),
                ('с приложением', TYPES_PERSON[0:3]),
                ('с сайтом', TYPES_PERSON[0:3]),
                ('с оплатой', TYPES_PERSON[0:2]),
                ('с доставкой', [TYPES_PERSON[0]]),
                ('с сервером', [TYPES_PERSON[2]]),
                ('с оборудованием', TYPES_PERSON[1:3]),
                ('с кассой', [TYPES_PERSON[1]]),
                ('другое', TYPES_PERSON[0:3])
            ]

# def get_name(id):
# 	info = getting_api.users.get(user_ids = id)[0]
# 	full_name = info.get('first_name') + ' ' + info['last_name']
# 	return full_name

print("Server started")
ChatData = {}


def CreateStart_ChatData_name(id, name):
    ChatData[id] = {'userData': {'name': name,
                                 'type_person': TYPE_PERSON_DEFAULT},

                    'requestData': {'type_request': TYPE_REQUEST_DEFAULT,
                                    'subtype_request': SUBTYPE_REQUEST_DEFAULT,
                                    'request_text': None}}


def createBotton(id, botMessage, bottons, oneTime):
    keyboard = VkKeyboard(inline=False, one_time=oneTime)
    count = len(bottons)
    if count != 0:
        for i in range(count):
            keyboard.add_button(bottons[i])
            # keyboard.add_line()
            if (i+1) % 2 == 0 and i != 0 and count-i > 1:
                keyboard.add_line()
        if bottons[0] != "начать":
            keyboard.add_line()
            keyboard.add_button("вернуться в начало")
        write_msg(id, botMessage, keyboard=keyboard.get_keyboard())
    else:
        write_msg(id, botMessage)
        # vk.method("messages.send", {"user_id": id, "message": botMessage,
        #                             "random_id": get_random_id(),
        #                             "buttons": []})


def q1_definitionPerson(id):
    createBotton(id, "Здравствуйте, укажите кто вы", ['клиент', 'сотрудник Жизньмарт'], False)


def define_type(chat_id):
    createBotton(chat_id, 'Чем могу помочь?', ['есть проблема', 'задать вопрос', 'оставить отзыв'], True)


def person_identif_type(chat_id, type_person):
    global ChatData
    ChatData[chat_id]['userData']['type_person'] = type_person
    if type_person == 'сотрудник Жизньмарт':
        createBotton(id, "Уточните место работы", ['магазин', 'бэк офис'], False)
    # elif type_person == 'магазин':  #TODO как дожидаться сообщения пользователя?
    #     mesg = bot.send_message(chat_id, 'В каком магазине вы работаете?')
    #     bot.register_next_step_handler(mesg, get_text_shop)
    else:
        define_type(chat_id)


def getListButtonsForType(allNameButton, person):
    buttons = []
    for button in allNameButton:
        if person in button[1]:
            buttons.append(button[0])
    return buttons


def request_identif_type(chat_id, type_request):
    global ChatData
    ChatData[chat_id]['requestData']['type_request'] = type_request
    if type_request == 'есть проблема':
        person = ChatData[chat_id]['userData']['type_person']
        buttonsForType = getListButtonsForType(ALLNAMEBUTTON_PROBLEMS, person)
        createBotton(chat_id, 'С чем возникла проблема?', buttonsForType, True)
    elif type_request == 'задать вопрос':
        write_msg(chat_id, 'Напишите ваш вопрос')
        # createBotton(id, "Напишите ваш вопрос", [], True)
    elif type_request == 'оставить отзыв':
        write_msg(chat_id, 'Пожалуйста, оставьте ваш отзыв ниже)')
        # createBotton(id, "Пожалуйста, оставьте ваш отзыв ниже)", [], True)


def CreateStart_ChatData(id):
    user_get = session_api.users.get(user_ids=(id))
    user_get = user_get[0]
    CreateStart_ChatData_name(id, user_get['first_name'] + ' ' + user_get['last_name'])


# -------------------------
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            message = event.text

            id = event.user_id
            if id not in ChatData:
                CreateStart_ChatData(id)
                # createBotton(id, "Чтобы начать нажмите на кнопку)", ["начать"], False)


            # keyboard = VkKeyboard(inline=False)
            # keyboard.add_button("начать")
            # print([subtipe for subtipe in [problem[1] for problem in ALLNAMEBUTTON_PROBLEMS]])
            if message == 'начать':
                q1_definitionPerson(id)
                # CreateStart_ChatData(id)
            elif message in ['сотрудник Жизньмарт', 'клиент', 'магазин', 'бэк офис']:
                CreateStart_ChatData(id)
                person_identif_type(id, message)
            elif message in ['есть проблема', 'задать вопрос', 'оставить отзыв']:  # кнопки типа запроса
                request_identif_type(id, message)
                # ChatData[id]['requestData']['request_text'] = None
                ChatData[id]['requestData']['request_text'] = "в ожидании"
            elif message in [problem[0] for problem in ALLNAMEBUTTON_PROBLEMS]:
                ChatData[id]['requestData']['subtype_request'] = message
                write_msg(id, "Опишите, что случилось")
            else:
                # ChatData[id]['requestData']['type_request'] == 'есть проблема' and \
                if ChatData[id]['requestData']['request_text'] == "в ожидании":
                    write_msg(id, "Ваш запрос принят в работу")
                    createBotton(id, "Если у вас есть ещё один запрос, нажмите на кнопку", ["начать"], False)
                elif ChatData[id]['requestData']['request_text'] is None:
                    createBotton(id, "Чтобы начать нажмите на кнопку)", ["начать"], False)

                ChatData[id]['requestData']['request_text'] = message
                print(ChatData[id])
                # send_to_server(id)





def send_to_server(chat_id):
    global ChatData

    departamentMapper = {
        'client': 2,
        'shop': 1,
        'back_office': 0
    }

    user = ChatData[chat_id]
    createTicket = {
        "name": user['requestData']['request_text'],
        "webhook": "http://localhost:5000/update",
        "type": 0, #user['requestData']['type_request'].upper(),
        "departament": departamentMapper[user['userData']['type_person']],
        "sender": {
            "name": user['userData']['name'],
            "type": 0
        },
        "priority": 1 #TODO автоматизировать (1 - высокий 0 - низкий)
    }

    # data_json = json.dumps(data)
    # payload = {'json_payload': data_json}
    r = requests.post("http://localhost:5179/api/ticket", json=createTicket) # создается тикет
    addMessage = {
        "ticketId": r.text,
        "text": user['requestData']['request_text'],
        "sender": {
            "name": user['userData']['name'],
            "type": 0
        },
        "timestamp": datetime.datetime.now().strftime("%d.%m.%Y")
    }
    user_by_ticket[int(r.text)] = chat_id
    r = requests.post("http://localhost:5179/api/message/add", json=addMessage)# добавляю сообщение в тикет


# ------ zabota_client ---------
# host_name = "localhost"
# server_port = 8080

user_by_ticket = {} # пишу свой словарь
server = Flask(__name__)


@server.route("/update/", methods=['POST'])
def processUpdate(): #  TODO dict localhost:5000
    body = json.loads(request.json)
    print(body)
    action = body['action']
    ticket = body['ticket']
    data = body['data']
    if action == "NEW_MESSAGE":
        write_msg(user_by_ticket[ticket], data['text'])
    return ""

# {
#   "action": "NEW_MESSAGE",
#   "ticket": 1,
#   "data": {
#     "text": "нереальный текст"
#   }
# }


def bot_polling():
    longpoll.listen()


Thread(target=bot_polling).start()

server.run()





