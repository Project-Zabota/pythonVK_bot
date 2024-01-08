import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_bot import VkBot
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json


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


def CreateStart_ChatData(id, name):
    ChatData[id] = {'userData': {'name': name,
                                 'type_person': TYPE_PERSON_DEFAULT},

                    'requestData': {'type_request': TYPE_REQUEST_DEFAULT,
                                    'subtype_request': SUBTYPE_REQUEST_DEFAULT,
                                    'request_text': None}}


def createBotton(id, botMessage, bottons):
    keyboard = VkKeyboard(inline=False)
    count = len(bottons)
    for i in range(count):
        keyboard.add_button(bottons[i])
        # keyboard.add_line()
        if (i+1) % 2 == 0 and i != 0 and count-i > 1:
            keyboard.add_line()
    write_msg(id, botMessage, keyboard=keyboard.get_keyboard())


def q1_definitionPerson(id):
    createBotton(id, "Здравствуйте, укажите кто вы", ['клиент', 'сотрудник Жизньмарт'])


def define_type(chat_id):
    createBotton(chat_id, 'Чем могу помочь?', ['есть проблема', 'задать вопрос', 'оставить отзыв'])


def person_identif_type(chat_id, type_person):
    global ChatData
    ChatData[chat_id]['userData']['type_person'] = type_person
    if type_person == 'сотрудник Жизньмарт':
        createBotton(id, "Уточните место работы", ['магазин', 'бэк офис'])
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
        createBotton(chat_id, 'С чем возникла проблема?', buttonsForType)

    # elif type_request == 'задать вопрос':
    #     mesg = bot.send_message(chat_id, f'Напишите ваш вопрос', parse_mode='HTML')
    #     bot.register_next_step_handler(mesg, get_text_art) #TODO как дожидаться сообщения пользователя?
    # elif type_request == 'оставить отзыв':
    #     mesg = bot.send_message(chat_id, f'Пожалуйста, оставьте ваш отзыв ниже)', parse_mode='HTML')
    #     bot.register_next_step_handler(mesg, get_text_art)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            message = event.text
            print('New message:')
            print(f'For me by: {event.user_id}')

            # bot = VkBot(event.user_id)
            # write_msg(event.user_id, bot.new_message(event.text))
            id = event.user_id

            user_get = session_api.users.get(user_ids=(id))
            user_get = user_get[0]
            CreateStart_ChatData(id, user_get['first_name'] + ' ' + user_get['last_name'])
            print(ChatData[id])

            # if message == "Hi":
            #     write_msg(id, "Фух работает")
            print('Text: ', message)

            keyboard = VkKeyboard(inline=False)
            keyboard.add_button("начать")

            if message == 'начать':
                q1_definitionPerson(id)

            if message in ['сотрудник Жизньмарт', 'клиент', 'магазин', 'бэк офис']:
                person_identif_type(id, message)
            elif message in ['есть проблема', 'задать вопрос', 'оставить отзыв']:  # кнопки типа запроса
                request_identif_type(id, message)