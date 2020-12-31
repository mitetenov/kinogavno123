from threading import Thread

import requests
from bs4 import BeautifulSoup
import telebot
import bot_config
import schedule
import time
from datetime import datetime

ID = bot_config.ID
URL = 'https://www.crowdgames.ru/collection/shop'
URL2 = 'https://www.crowdgames.ru/collection/accessoriesandpromo'
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/87.0.4280.88 Safari/537.36', 'accept': '*/*'}
HOST = 'https://www.crowdgames.ru'


def get_html(url, params=None):
    request = requests.get(url, headers=HEADERS, params=params)
    return request


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='a-prod')

    games = []
    for item in items:
        games.append({
            'Name': item.find('div', class_='titile-prod').get_text(strip=True),
            'Link': HOST + item.find('a').get('href')
        })
    return games


def find_eclipse(items):
    global saved_links
    answer = []
    for item in items:
        if ('eclipse' in item['Name'].lower() or 'эклипс' in item['Name'].lower()) and item['Link'] not in saved_links:
            answer.append(item['Link'])
    return answer


def parse(url):
    html = get_html(url)
    if html.status_code == 200:
        items = get_content(html.text)
        answer = find_eclipse(items)
        if len(answer) > 0:
            bot.send_message(chat_id=ID, text='\n'.join(answer))
            for item in answer:
                saved_links.append(item)
            file = open('saved_links.txt', 'w')
            file.writelines(answer)
            file.close()
    else:
        print(f'Error: status code = {html.status_code}')


def do_bots_stuff():
    global last_request_time
    parse(URL)
    parse(URL2)
    last_request_time = datetime.now()


f = open('saved_links.txt', 'r')
saved_links = f.readlines()
f.close()

bot = telebot.TeleBot(bot_config.TOKEN)
bot.send_message(chat_id=ID, text='bot started')
schedule.every(2).minutes.do(do_bots_stuff)

last_request_time = 0


@bot.message_handler(commands=['info'])
def handle_info(message):
    links = '\n'.join(saved_links)
    bot.send_message(chat_id=ID, text=f'last request: {last_request_time}\n\ncurrent links: {links}')


def schedule_run():
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print('Error: ', e)
        time.sleep(1)


def bot_run():
    bot.polling(none_stop=True)


Thread(target=schedule_run).start()
Thread(target=bot_run).start()
