import telebot
from datetime import datetime
from time import sleep
from telebot import types
import requests
import sqlite3 as sql
from bs4 import BeautifulSoup as bs

teamsfromt20 = []
def tablecreating():
    connt = sql.connect('users.db')
    curt = connt.cursor()
    curt.execute("""CREATE TABLE IF NOT EXISTS users(
       userid INT PRIMARY KEY,
       fteam TEXT);
    """)
    connt.commit()
    connt.close()

tablecreating()

actual_rating = ""
month = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]



def adding_new_users(id):
    tempo_id = (id,)
    conn = sql.connect('users.db', timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT userid FROM users;")

    joinedusers = set(cur.fetchall())
    if tempo_id not in joinedusers:
        id_tuple = (id, "Without team")
        cur.execute("INSERT INTO users VALUES(?, ?);", id_tuple)
    conn.commit()
    conn.close()
    return 0


def get_actualrank():
    rankurl = "https://www.hltv.org/ranking/teams/"
    current_time = datetime.now()
    current_year = current_time.timetuple()[0]
    current_month = current_time.timetuple()[1]
    current_day = current_time.timetuple()[2]
    if current_time.weekday() >= 1:
        rankurl += str(current_year) + "/" + month[current_month - 1] + "/" + str(int(current_day) - current_time.weekday())

    r = requests.get(rankurl)
    soup = bs(r.text, 'lxml')
    quotes = soup.find_all('span', class_='name')

    actual_rating = ""
    for i in range(20):
        tempo = str(quotes[i])[19::]
        tempo = tempo[:tempo.find("<")]
        actual_rating += str(i + 1) + ". " + tempo + "\n"
        teamsfromt20.append(tempo)
    return actual_rating

useless = get_actualrank()

def get_actualmembers(nameOfTeam):
    rankurl = "https://www.hltv.org/ranking/teams/"
    current_time = datetime.now()
    current_year = current_time.timetuple()[0]
    current_month = current_time.timetuple()[1]
    current_day = current_time.timetuple()[2]
    if current_time.weekday() >= 1:
        rankurl += str(current_year) + "/" + month[current_month - 1] + "/" + str(
            int(current_day) - current_time.weekday())
    r = requests.get(rankurl)
    soup = bs(r.text, 'html.parser')
    find_teammate = soup.find_all('div', {'class': 'rankingNicknames'})
    team =""
    numberOfTeam = teamsfromt20.index(nameOfTeam)
    for i in range(numberOfTeam*5, (numberOfTeam+1)*5):
        team += str(find_teammate[i].get_text()) + "\n"
    return team


def get_actualmatches():
    links2matches = []
    matchurl = "https://www.hltv.org/matches"
    r = requests.get(matchurl)
    soup = bs(r.text, 'lxml')
    divs4links_upcoming = soup.find_all('div', {'class': 'upcomingMatch'})
    divs4links_ongoing = soup.find_all('div', {'class': 'liveMatch'})
    tournaments = []
    teams = []
    links = []
    for div in divs4links_ongoing:
        links2matches.append("https://www.hltv.org"+div.find('a')['href'])
    for div in divs4links_upcoming:
        links2matches.append("https://www.hltv.org"+div.find('a')['href'])
    for link in links2matches:
        req = requests.get(link)
        soupt = bs(req.text, 'lxml')
        temp = soupt.find('title')
        tempo = temp.text
        if tempo.find(' vs. ') != -1:
            links.append(link)
            tournaments.append(tempo[tempo.find(' at')+4:tempo.find(' | '):])
            teams.append(tempo[:tempo.find(' at'):])
        sleep(0.2)
    timeOfMatch = soup.find_all('div', {'class': 'matchTime'})
    timeOfMatch_str = []
    for elem in timeOfMatch:
        t = str(elem)
        t = t[t.find('>')+1::]
        t = t[:t.find('<')]
        timeOfMatch_str.append(t[t.find('>')+1::])
    typesOfMatches = soup.find_all('div', {'class': 'matchMeta'})
    typesOfMatches_str = []
    for elem in typesOfMatches:
        t = str(elem)
        t = t[t.find('>')+1::]
        t = t[:t.find('<')]
        typesOfMatches_str.append(t)
    return tournaments, teams, timeOfMatch_str, typesOfMatches_str, links



bot = telebot.TeleBot("5697822865:AAFlny2ecdUqyw0yzOAPoMPnnirEOtcCGTg")


@bot.message_handler(commands=["start"])
def start(message):
    conn = sql.connect('users.db', timeout=10)
    cur = conn.cursor()
    req = cur.execute("SELECT userid FROM users WHERE userid=?;", (message.from_user.id, ))
    if req.fetchone() is not None:
        bot.send_message(message.chat.id, 'И снова здравствуй!)')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Что ты хочешь посмотреть?', reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)
    else:
        adding_new_users(message.from_user.id)
        bot.send_message(message.chat.id, 'Хай! Тебя приветствует HLTVbot. Мы рады, что вы решили пользоваться нашим ботом. Надеюсь он хоть чуточку улучшит ваш досуг;)')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Что ты хочешь посмотреть?', reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)


def first_menu(message):
    if message.text == "Рейтинг":
        actual_rating = get_actualrank()
        bot.send_message(message.chat.id, actual_rating)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Посмотреть составы команд", "На главную")
        mesg = bot.send_message(message.chat.id, 'Что ты хочешь посмотреть?',
                         reply_markup=markup)

        bot.register_next_step_handler(mesg, team_members)

    if message.text == "Любимая команда":
        conn = sql.connect('users.db', timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT fteam FROM users WHERE userid=?;", (message.from_user.id,))
        fteam = cur.fetchone()
        conn.close()
        if fteam == ('Without team',):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Да")
            markup.add("Нет")
            mesg = bot.send_message(message.chat.id, 'У тебя пока не выбрана любимая команда. Хочешь выбрать?',
                                    reply_markup=markup)
            bot.register_next_step_handler(mesg, favourite_teams_choosing)
        else:
            markup = types.ReplyKeyboardMarkup(row_width=1)
            markup.add("Изменить любимую команду", "Ближайшие матчи команды", "На главную")
            mesg = bot.send_message(message.chat.id, 'Чего желаешь?',
                             reply_markup=markup)
            bot.register_next_step_handler(mesg, favourite_teams_menu_second)



    if message.text == "Матчи":
        markup = types.ReplyKeyboardMarkup(row_width=1)
        markup.add("Матчи команд из топ 20", "Все известные матчи", "На главную")
        mesg = bot.send_message(message.chat.id, 'Какие матчи ты хочешь посмотреть?',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, matches_menu)


def matches_menu(message):
    if message.text == "Все известные матчи":
        bot.send_message(message.chat.id, 'Подожди немного, я ищу мачти. Осталось совсем чуть-чуть)')
        tournaments, matches, timeOfMatch_str, typesOfMatches_str, links = get_actualmatches()
        for i in range(len(matches)):
            mesg = "Турнир: " + tournaments[i] + "\n" + "Команды: " + matches[i] + "\n" + "Время: " + timeOfMatch_str[i] + "\n" + "Формат матча: " + typesOfMatches_str[i] + "\n"
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Страница матча", url=links[i])
            keyboard.add(url_button)
            bot.send_message(message.chat.id, mesg, reply_markup=keyboard)
            sleep(0.1)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Не хочешь посмотреть что-нибудь еще?',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)
    if message.text == "Матчи команд из топ 20":
        bot.send_message(message.chat.id, 'Подожди немного, я ищу мачти. Осталось совсем чуть-чуть)')

        tournaments, matches, timeOfMatch_str, typesOfMatches_str, links = get_actualmatches()
        for i in range(len(matches)):
            t = matches[i].split(' vs. ')
            if t[0] in teamsfromt20 or t[1] in teamsfromt20:
                mesg = "Турнир: " + tournaments[i] + "\n" + "Команды: " + matches[i] + "\n" + "Время: " + timeOfMatch_str[i] + "\n" + "Формат матча: " + typesOfMatches_str[i] + "\n"
                keyboard = types.InlineKeyboardMarkup()
                url_button = types.InlineKeyboardButton(text="Страница матча", url=links[i])
                keyboard.add(url_button)
                bot.send_message(message.chat.id, mesg, reply_markup=keyboard)
                sleep(0.1)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Не хочешь посмотреть что-нибудь еще?',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)
    if message.text == "На главную":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Не хочешь посмотреть что-нибудь еще?',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)


def team_members(message):
    if message.text == "На главную":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Что ты хочешь посмотреть?',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)
    elif message.text == "Посмотреть составы команд":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(20):
            markup.add(teamsfromt20[i])
        mesg = bot.send_message(message.chat.id, 'Выбери команду, состав которой хочешь посмотреть.', reply_markup=markup)
        bot.register_next_step_handler(mesg, team_members)
    else:
        tempo = get_actualmembers(message.text)
        if tempo != "":
            bot.send_message(message.chat.id, "Актуальный состав " + message.text + ":")
            bot.send_message(message.chat.id, tempo)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Матчи", "Рейтинг", "Любимая команда")
            mesg = bot.send_message(message.chat.id, 'Хочешь посмотреть что-то ещё?',
                             reply_markup=markup)
            bot.register_next_step_handler(mesg, first_menu)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Матчи", "Рейтинг", "Любимая команда")
            mesg = bot.send_message(message.chat.id, 'Что-то я не знаю такой команды( Хочешь посмотреть что-то ещё?',
                             reply_markup=markup)
            bot.register_next_step_handler(mesg, first_menu)


def favourite_teams_menu_second(message):
    if message.text == "Изменить любимую команду":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Да", "Нет")
        mesg = bot.send_message(message.chat.id, 'Вы точно хотите изменить любимую команду? Старая может расстроиться...', reply_markup=markup)
        bot.register_next_step_handler(mesg, favourite_teams_choosing)

    if message.text == "Ближайшие матчи команды":
        flag = False
        conn = sql.connect('users.db', timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT fteam FROM users WHERE userid=?;", (message.from_user.id,))
        fteam = cur.fetchone()
        conn.close()
        print(*fteam)
        bot.send_message(message.chat.id, 'Подожди немного, я ищу мачти. Осталось совсем чуть-чуть)')
        tournaments, matches, timeOfMatch_str, typesOfMatches_str, links = get_actualmatches()
        for i in range(len(matches)):
            t = matches[i].split(' vs. ')
            if t[0] == fteam[0] or t[1] == fteam[0]:
                flag = True
                mesg = "Турнир: " + tournaments[i] + "\n" + "Команды: " + matches[i] + "\n" + "Время: " + timeOfMatch_str[i] + "\n" + "Формат матча: " + typesOfMatches_str[i] + "\n"
                keyboard = types.InlineKeyboardMarkup()
                url_button = types.InlineKeyboardButton(text="Страница матча", url=links[i])
                keyboard.add(url_button)
                bot.send_message(message.chat.id, mesg, reply_markup=keyboard)
                sleep(0.1)
        if not flag:
            bot.send_message(message.chat.id, 'Прости, видимо твоя любимая команда не играет в ближайшее время. Но ты не расстраивайся!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Не хочешь посмотреть что-нибудь еще?',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)

    if message.text == "На главную":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        rep = bot.send_message(message.chat.id, 'Что ты хочешь посмотреть?', reply_markup=markup)
        bot.register_next_step_handler(rep, first_menu)


def favourite_teams_choosing(message):
    if message.text == "Да":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Natus Vincere")
        markup.add("Outsiders")
        markup.add("Cloud9")
        markup.add("FaZe")
        markup.add("G2")
        markup.add("Heroic")
        markup.add("Vitality")
        markup.add("Liquid")
        markup.add("MOUZ")
        markup.add("fnatic")
        markup.add("Spirit")
        markup.add("Astralis")
        markup.add("OG")
        markup.add("Ninjas in Pyjamas")
        mesg = bot.send_message(message.chat.id, 'Выбери свою любимую команду',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, favourite_teams_adding)
    if message.text == "Нет":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Матчи", "Рейтинг", "Любимая команда")
        mesg = bot.send_message(message.chat.id, 'Не желаешь ли ты посмотреть ещё что-нибудь?',
                                reply_markup=markup)
        bot.register_next_step_handler(mesg, first_menu)


def favourite_teams_adding(message):
    data = (message.text, message.from_user.id)
    conn = sql.connect('users.db', timeout=10)
    cur = conn.cursor()
    cur.execute("UPDATE users SET fteam=? WHERE userid=?;", data)
    conn.commit()
    conn.close()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Матчи", "Рейтинг", "Любимая команда")
    mesg = bot.send_message(message.chat.id, 'Ты выбрал команду ' + message.text + ' своей любимой. Хочешь посмотреть еще что-нибудь?',
                     reply_markup=markup)
    bot.register_next_step_handler(mesg, first_menu)


bot.infinity_polling()
