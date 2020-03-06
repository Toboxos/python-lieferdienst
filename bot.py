
import urllib
import requests
import telebot
url= 'http://www.capri-pizza-service.de/img/flyer_januar2020.pdf'

filedirectory= 'C:/Users/betki/Documents/Uni/webEngineering/Karte2.pdf'
TOKEN= '1009520225:AAFe0bRViAfP8CrHVlW7LwZHyTwpURBDGxA'

bot= telebot.TeleBot(token=TOKEN)
global g_chatID

@bot.message_handler(commands= ['karte'])
def send_karte(message):
    myfile= requests.get(url, allow_redirects= True)
    open(filedirectory,'wb').write(myfile.content)
    g_chatID = message.chat.id
    doc = open(filedirectory, 'rb')
    bot.send_document(g_chatID, doc )

while True:
    try:
        bot.infinity_polling(True)
    except Exception:
        time.sleep(3)