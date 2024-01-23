import telebot
from telebot.types import ReplyKeyboardMarkup
from PIL import Image
import json
API_TOKEN = '6721240922:AAHJpMaIMw_pfYsKLsqRNx5j9tH12GnVEfs'
start_image = Image.open('images/start.png')
bot = telebot.TeleBot(API_TOKEN)
quest_info = ("В далёкой и загадочной стране, где магия и мифические существа — не вымысел, "
              "а реальность, живёт молодой искатель приключений по имени Эмиль.\n"
              "Он всегда мечтал стать великим воином и защитником своего народа, но судьба распорядилась иначе.\n"
              "Однажды, путешествуя по лесу, Эмиль случайно наткнулся на таинственный артефакт, "
              "который оказался картой к забытому городу древних магов.\n"
              "Легенда гласила, что в этом городе спрятаны сокровища, "
              "способные изменить жизнь любого, кто их найдёт.\n"
              "Решив, что это его шанс стать настоящим героем, Эмиль отправился в опасное путешествие.")
data_file = open('users_data.json', 'r', encoding='utf8')
try:  # попытка загрузки файла
    users_data = {}
    temp_file = json.load(data_file)
    for i in temp_file:  # преобразование формата
        temp_id = int(i)
        users_data[temp_id] = {}
        for e in temp_file[i]:
            users_data[temp_id][e] = temp_file[i][e]
except:
    users_data = {}
data_file.close()

with open('locations.json', 'r', encoding='utf8') as locs:
    locations = json.load(locs)
    locs.close()


@bot.message_handler(commands=['start'])  # команда запуска игры
def start(message):
    user_id = message.from_user.id
    if user_id not in users_data:  # регистрация пользователя
        register(message)
    else:
        users_data[user_id]['location'] = "location1"  # локация
        bot.send_message(message.chat.id, f"\n"
                                          f"Игра началась!\n\n\n"
                                          f"{quest_info}",
                         reply_markup=keyboard_assemble(users_data[user_id]['location']))
        bot.send_photo(message.chat.id, start_image)
        data_save()
        loc_info(message)


@bot.message_handler(commands=['help'])  # выводит список доступных команд и пояснения к использованию бота
def help_command(message):
    bot.send_message(message.chat.id, "Помощь!\n"
                                      "\nЧтобы начать проходить квест, напиши /start.\n"
                                      "Также ты можешь написать эту команду, чтобы перезапустить игру.\n"
                                      "В процессе игры ты будешь перемещаться по локациям, на каждой из которых "
                                      "тебе будут предложены варианты действий.\n"
                                      "Выбирай наиболее понравившееся из них.\n"
                                      "В зависимости от твоих ответов ты можешь победить или проиграть.\n"
                                      "\nСписок команд:\n"
                                      "/start - начать опрос\n"
                                      "/info - информация о текущей локации")


@bot.message_handler(commands=['info'])
def info(message):
    loc_info(message)


def register(message):  # регистрация
    user_id = message.from_user.id
    users_data[user_id] = {}
    users_data[user_id]['name'] = message.from_user.first_name
    users_data[user_id]['user_name'] = message.from_user.username
    users_data[user_id]['location'] = 'zero'
    bot.send_message(message.chat.id, f"Здравствуй, {users_data[message.from_user.id]['name']}!\n"
                                      'Перед тобой бот-квест.\n'
                                      'Чтобы начать квест, напиши команду /start\n'
                                      'Чтобы получить список доступных команд, напиши /help')
    data_save()


@bot.message_handler(content_types=['text'])
def text_handler(message):
    user_id = message.from_user.id
    msg_text = message.text
    loc = users_data[user_id]['location']
    if answer_check(loc, msg_text, user_id):
        loc_info(message)
    else:
        bot.send_message(message.chat.id, "Выбери один из предложенных вариантов ответа",
                         reply_markup = keyboard_assemble(users_data[user_id]['location']))


def data_save():
    with open('users_data.json', 'w', encoding='utf8') as data:
        json.dump(users_data, data, indent=2, ensure_ascii=False)
        data.close()
        return


def loc_info(message):
    user_id = message.from_user.id
    loc = locations[users_data[user_id]['location']]
    bot.send_message(message.chat.id, f"{loc['description']}",
                     reply_markup = keyboard_assemble(users_data[user_id]['location']))
    if loc['loc_image'] != "":
        bot.send_photo(message.chat.id, Image.open(f"images/{loc['loc_image']}"))
        return


def keyboard_assemble(loc):  # сборка клавиатуры ответа
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in locations[loc]['options']:
        if option != '':
            keyboard.add(option)
    return keyboard


def answer_check(loc, message_text, user_id):  # проверка ответа на соответствие одному из вариантов
    loc = locations[loc]
    if message_text in loc['options']:
        users_data[user_id]['location'] = loc['options'][message_text]
        data_save()
        return True
    else:
        return False


bot.polling(none_stop=True)
