from telebot import types
import telebot
import pickle
from random_word import RandomWords
from googletrans import Translator


class LanguageBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.translator = Translator()
        self.users_points = {}
        self.states = {}  # 0: menu; 1: ru -> en; 2: en -> ru
        self.last_word = {}
        self.random_word = RandomWords()

        self.load_data()
        self.setup_message_handlers()

    def ru_to_en_train(self, message):
        res = 'banana'

        while self.translator.detect(res).lang != 'ru':
            res = self.translator.translate(
                self.random_word.get_random_word(), dest='ru', src='en').text

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("End training 🏁")
        btn2 = types.KeyboardButton("Give me another word 🔄")
        markup.add(btn1, btn2)
        self.bot.send_message(message.chat.id,
                              text=f"Translate the following word to English: *{res}*",
                              reply_markup=markup,
                              parse_mode="Markdown")

        self.last_word[message.from_user.username] = res

    def en_to_ru_train(self, message):
        res = self.random_word.get_random_word()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("End training 🏁")
        btn2 = types.KeyboardButton("Give me another word 🔄")
        markup.add(btn1, btn2)
        self.bot.send_message(message.chat.id,
                              text=f"Translate the following word to Russian: *{res}*",
                              reply_markup=markup,
                              parse_mode="Markdown")

        self.last_word[message.from_user.username] = res

    def save_data(self):
        with open('users_data.pickle', 'wb') as f:
            pickle.dump(self.users_points, f)

    def load_data(self):
        try:
            with open('users_data.pickle', 'rb') as f:
                self.users_points = pickle.load(f)
        except BaseException:
            self.users_points = {}

    def main_menu(self, message):
        self.states[message.from_user.username] = 0

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Russian -> English 🇷🇺➡️🇬🇧")
        btn2 = types.KeyboardButton("English -> Russian 🇬🇧➡️🇷🇺")
        btn3 = types.KeyboardButton("About the bot... ℹ️")
        btn4 = types.KeyboardButton("My stats/Menu 📊")
        markup.add(btn1, btn2, btn3, btn4)
        self.bot.send_message(
            message.chat.id,
            text=f"Hello, {message.from_user.username}! Let's learn English! 🌍",
            reply_markup=markup)

    def setup_message_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.load_data()

            if message.from_user.username not in self.users_points:
                self.users_points[message.from_user.username] = 0

            self.main_menu(message)

        @self.bot.message_handler(content_types=['text'])
        def func(message):
            if (message.text == "Russian -> English 🇷🇺➡️🇬🇧"):
                markup_remove = types.ReplyKeyboardRemove()
                self.bot.send_message(
                    message.chat.id,
                    text="Let's translate words from Russian to English! 🌍",
                    reply_markup=markup_remove)
                self.states[message.from_user.username] = 1
                self.ru_to_en_train(message)

            elif (message.text == "English -> Russian 🇬🇧➡️🇷🇺"):
                markup_remove = types.ReplyKeyboardRemove()
                self.bot.send_message(
                    message.chat.id,
                    text="Let's translate words from English to Russian! 🌍",
                    reply_markup=markup_remove)
                self.states[message.from_user.username] = 2
                self.en_to_ru_train(message)

            elif (message.text == "About the bot... ℹ️"):
                self.bot.send_message(
                    message.chat.id,
                    text="Bot developed by _Sokol Daria_ ([tg](https://t.me/gitrkh))",
                    parse_mode="Markdown")
                self.bot.send_message(message.chat.id, text="You have returned to the main menu 🏠")
                self.main_menu(message)

            elif (message.text == "My stats/Menu 📊" or message.text == "End training 🏁"):
                self.bot.send_message(
                    message.chat.id,
                    text=f"User {message.from_user.username}! \nTotal points: {self.users_points[message.from_user.username]}.")
                self.bot.send_message(message.chat.id, text="You have returned to the main menu 🏠")
                self.main_menu(message)

                self.save_data()  # Save data only when the user sees :)

            elif self.states[message.from_user.username] == 1:  # ru -> en

                if message.text == "Give me another word 🔄":
                    self.ru_to_en_train(message)
                    return

                true_result = self.translator.translate(self.last_word[message.from_user.username],
                                                        dest='en',
                                                        src='ru').text.lower()

                if message.text.lower() == true_result:
                    self.users_points[message.from_user.username] += 1

                    self.bot.send_message(message.chat.id, text="Great job, keep it up! 🎉")

                else:
                    self.bot.send_message(
                        message.chat.id,
                        text=f"Not quite right, try again! The correct answer was {true_result}")

                self.ru_to_en_train(message)
            elif self.states[message.from_user.username] == 2:  # en -> ru

                if message.text == "Give me another word 🔄":
                    self.en_to_ru_train(message)
                    return

                true_result = self.translator.translate(self.last_word[message.from_user.username],
                                                        dest='ru',
                                                        src='en').text.lower()

                if message.text.lower() == true_result:
                    self.users_points[message.from_user.username] += 1

                    self.bot.send_message(message.chat.id, text="Great job, keep it up! 🎉")

                else:
                    self.bot.send_message(
                        message.chat.id,
                        text=f"Not quite right, try again! The correct answer was {true_result}")

                self.en_to_ru_train(message)

    def start_polling(self):
        self.bot.polling(none_stop=True, interval=0)


if __name__ == "__main__":
    TOKEN = '6237721491:AAF3wzJfZPbpH5X7ctH2MNxg0ehmqnP7zME'
    language_bot = LanguageBot(TOKEN)
    language_bot.start_polling()