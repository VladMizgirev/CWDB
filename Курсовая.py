import telebot
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import random
import requests
import sqlalchemy
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
import json
from models import create_tables, Word, New_word, Client, Client_list_word
from random import randint
from random import shuffle

login = str(input('Введите логин:'))
password = str(input('Введите пароль:'))
name_bd = str(input('Введите название базы данных:'))
DSN = f'postgresql+psycopg2://{login}:{password}@localhost:5432/{name_bd}'
engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()

create_tables(engine)

def load_db():
    with open ('База_данных_json.json', encoding='utf-8') as f:
        data = json.load(f)

    for record in data:
        model = {
            'word': Word,
            'new_word': New_word,
        }[record.get('model')]
        session.add(model(id=record.get('pk'), rus=record.get('rus'), en=record.get('en'), w_en_1=record.get('w_en_1'), w_en_2=record.get('w_en_2'), w_en_3=record.get('w_en_3')))
    session.commit()

load_db()

state_storage = StateMemoryStorage()
token_bot = input('Введите токен')
bot = telebot.TeleBot(token_bot)
bot = TeleBot(token_bot, state_storage=state_storage)

def show_hint(*lines):
    return '\n'.join(lines)

def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"

class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()
            
@bot.message_handler(commands=['start', 'cards'])
def cards_bot(message):
    user_id = message.chat.id
    data_client = session.query(Client).filter(Client.id == user_id).all()
    if data_client == []:
        session.add(Client(id=user_id))
        session.add(Client_list_word(id_client=user_id, id_word=[1, 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10 , 11 , 12 , 13 , 14 , 15]))
        session.commit()
        bot.send_message(user_id, 'Привет 👋 Давай попрактикуемся в английском языке.'
                         'Тренировки можешь проходить в удобном для себя темпе.'
                          'У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения.'
                          'Для этого воспрользуйся инструментами:'
                          'добавить слово ➕' 
                          'удалить слово 🔙'
                          'Ну что, начнём ⬇️')
    else:
        marcup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        data_speshial = session.query(Client_list_word.id_word, Client_list_word.id_new_word).filter(Client_list_word.id_client == user_id)
        data = session.query(
            Word.rus, Word.en, Word.w_en_1, Word.w_en_2, Word.w_en_3
                ).select_from(Word)
        global id_target
        id_target = 0
        while id_target == 0:
            random = randint(1, 30)
            global nobber
            nobber = random
            for id_word, id_new_word in data_speshial:
                id_word = id_word.strip('{}').split(',')
                if 1 <= random <= 15:
                    for id in id_word:
                        id = int(id)
                        if id == random:
                            id_target = random
                if 16 <= random <= 30:
                    if id_new_word is None:
                        continue
                    else:
                        id_new_word = id_new_word.strip('{}').split(',')
                        for id in id_new_word:
                            id = int(id)
                            if id == random:
                                id_target = random
        if 1 <= id_target <= 15:
            pub = data.filter(Word.id == id_target).all()
        elif 16 <= id_target <= 30:
            pub = data.filter(New_word.id == id_target).all()
        for rus, en, w_en_1, w_en_2, w_en_3 in pub:
            rus_word = rus
            target_word = en        
            other_word = [w_en_1, w_en_2, w_en_3]
        global buttons
        buttons = []
        target_word_btn = types.KeyboardButton(target_word)
        buttons.append(target_word_btn)
        other_words_btns = [types.KeyboardButton(word) for word in other_word]
        buttons.extend(other_words_btns)
        shuffle(buttons)
        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
        buttons.extend([next_btn, add_word_btn, delete_word_btn])
        
        marcup.add(*buttons)
        
        greeting = f"Выбери перевод слова:\n🇷🇺 {rus_word}"
        bot.send_message(message.chat.id, greeting, reply_markup=marcup)
        bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['target_word'] = target_word
            data['translate_word'] = rus_word
            data['other_words'] = other_word

@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    cards_bot(message)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    user_id = message.chat.id
    data_speshial = session.query(Client_list_word.id_word, Client_list_word.id_new_word).filter(Client_list_word.id_client == user_id).all()
    for id_word, id_new_word in data_speshial:
        if 1 <= id_target <= 15:
            prod = []
            id_word = id_word.strip('{}').split(',')
            for id in id_word:
                id = int(id)
                prod.append(id)
            prod.remove(id_target)
            prod_second = []
            id_new_word = id_new_word.strip('{}').split(',')
            for id in id_new_word:
                id = int(id)
                prod_second.append(id)
            session.query(Client_list_word).filter(Client_list_word.id_client == user_id).delete()
            session.commit()
            session.add(Client_list_word(id_client=user_id, id_word= prod, id_new_word = prod_second))
            session.commit()
            triper = session.query(Client_list_word.id_word)
            for i in triper:
                print(i)
        if 16 <= id_target <= 30:
            prod = []
            id_new_word = id_new_word.strip('{}').split(',')
            for id in id_new_word:
                id = int(id)
                prod.append(id)
            prod.remove(id_target)
            prod_first_list = []
            id_word = id_word.strip('{}').split(',')
            for id in id_word:
                id = int(id)
                prod_first_list.append(id)
            session.query(Client_list_word).filter(Client_list_word.id_client == user_id).delete()
            session.commit()
            session.add(Client_list_word(id_client=user_id, id_word = prod_first_list, id_new_word = prod))
            session.commit()
    cards_bot(message)

@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    user_id = message.chat.id
    data_speshial = session.query(Client_list_word.id_word, Client_list_word.id_new_word).filter(Client_list_word.id_client == user_id).all()
    try:
        for id_word, id_new_word in data_speshial:
            prod = []
            id_new_word = id_new_word.strip('{}').split(',')
            for id in id_new_word:
                id = int(id)
                prod.append(id)
            prod_first_list = []
            id_word = id_word.strip('{}').split(',')
            for id in id_word:
                id = int(id)
                prod_first_list.append(id)
        max_id = prod[-1]
        new_id = max_id + 1
        prod.append(new_id)
        session.query(Client_list_word).filter(Client_list_word.id_client == user_id).delete()
        session.commit()
        session.add(Client_list_word(id_client=user_id, id_word= prod_first_list, id_new_word = prod))
        session.commit()
    except:
        for id_word, id_new_word in data_speshial:
            id_word = id_word.strip('{}').split(',')
            prod_first_list = []
            for id in id_word:
                id = int(id)
                prod_first_list.append(id)
        session.query(Client_list_word).filter(Client_list_word.id_client == user_id).delete()
        session.commit()
        session.add(Client_list_word(id_client=user_id, id_word= prod_first_list, id_new_word = [1]))
        session.commit()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")

    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    print('Работаем')
    bot.polling()




