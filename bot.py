#die Datei Bestellungen.json muss im Ordner liegen
# mit /karte wird die Karte geschickt
#mit "Bestellung 12" wird eine Bestellung mit Namen eingetragen, wenn man nochmal eine Schickt, wird sie hinzugefügt
#bei mir 

import urllib
import requests
import telebot
import json
url= 'http://www.capri-pizza-service.de/img/flyer_januar2020.pdf'

filedirectory= 'hierdiespeicheradresseaufdemPC'
TOKEN= 'hiermussdastokenstehen'

bot= telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands= ['karte'])
def send_karte(message):
    global g_chatID
    g_chatID = message.chat.id
    myfile= requests.get(url, allow_redirects= True)
    open(filedirectory,'wb').write(myfile.content)
    doc = open(filedirectory, 'rb')
    bot.send_document(g_chatID, doc )
    bot.send_message(g_chatID,'Danke man ')

@bot.message_handler(func=lambda msg: msg.text is not None and 'Bestellung' in msg.text)
def get_bestellung(message):
    bot.send_message(g_chatID,'Danke man ')
    texts = message.text.split(" ",2)
    name = message.from_user.first_name
    bestellung = texts[1]
    neueBestellung(name, bestellung)
    

def neueBestellung(name, bestellung):
    with open('Bestellungen.json', 'r') as f:
        try:
            JSON_file = json.load(f)
        except:
            JSON_file= {}

    if name in JSON_file:
        myname = JSON_file[name]
        myname.append(bestellung)
        JSON_file[name] = myname
        with open('Bestellungen.json', 'w') as outfile:
            json.dump(JSON_file, outfile)
    else:
        JSON_file= {name: [bestellung]}	#in der Gruppe muss hier was anderes stehen.
        with open('Bestellungen.json', 'w') as outfile:
            json.dump(JSON_file, outfile)
   

while True:
    try:
        bot.infinity_polling(True)
    except Exception:
        time.sleep(3)