#die Datei Bestellungen.json muss im Ordner liegen
# mit /karte wird die Karte geschickt
#mit "Bestellung 12" wird eine Bestellung mit Namen eingetragen, wenn man nochmal eine Schickt, wird sie hinzugefügt

import urllib
import requests
import telebot
import json
url= 'http://www.capri-pizza-service.de/img/flyer_januar2020.pdf'

filedirectory= 'HIERMUSSEINEFILEDIRECTORY STEHEN'   #z.B. C:/Users/...
TOKEN= 'HIERMUSSEINTOKENSTEHEN'

bot= telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands= ['karte'])           #karte downloaden und schicken
def send_karte(message):
    global g_chatID
    g_chatID = message.chat.id
    myfile= requests.get(url, allow_redirects= True)    #TODO: hier link fest genutzt, nicht dynmaisch
    open(filedirectory,'wb').write(myfile.content)
    doc = open(filedirectory, 'rb')
    bot.send_document(g_chatID, doc )
    bot.send_message(g_chatID,'Danke man ')

@bot.message_handler(func=lambda msg: msg.text is not None and 'Bestellung' in msg.text)
def get_bestellung(message):
    bot.send_message(g_chatID,'Danke man ')
    texts = message.text.split(" ",2)               # Nachricht splitten um Bestellungsnummer finden
    name = message.from_user.first_name             #Vorname finden
    bestellung = texts[1]
    neueBestellung(name, bestellung)
    

def neueBestellung(name, bestellung):
    with open('Bestellungen.json', 'r') as f:       #bisherigre Datei öffnen
        try:                                        # wenn die Datei leer ist kann man sie nicht öffnen, dann springt man in except
            JSON_file = json.load(f)
        except:
            JSON_file= {}

    if name in JSON_file:                           # ist der Name schon in der Datei
        myname = JSON_file[name]
        myname.append(bestellung)
        JSON_file[name] = myname                    # wird zur Aktuellen beste´llung die neue Zahl hinzugefügt z.B. "Betti": ["12","13"]
        with open('Bestellungen.json', 'w') as outfile:#reinschreiben
            json.dump(JSON_file, outfile)
    else:                                              #gibt es den Namen nicht
        JSON_file= {name: [bestellung]}                 #wir hier die JSON Datei neu Beschrieben,TODO: in der Gruppe muss hier hinzugefügt werden, nicht überschrieben
        with open('Bestellungen.json', 'w') as outfile:
            json.dump(JSON_file, outfile)
   

while True:
    try:
        bot.infinity_polling(True)
    except Exception:
        time.sleep(3)