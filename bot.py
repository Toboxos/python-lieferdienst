#die Datei Bestellungen.json muss im Ordner liegen
# mit /karte wird die Karte geschickt
#mit "Bestellung 12" wird eine Bestellung mit Namen eingetragen, wenn man nochmal eine Schickt, wird sie hinzugefügt

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from io import StringIO
import urllib
import requests
import json

<<<<<<< Updated upstream
=======

filedirectory= 'hierdiespeicheradresseaufdemPC'
TOKEN= '1059740952:AAHHEfgqgGkdhxUntCiF2lmGt8TqnakZ8ss'

>>>>>>> Stashed changes


url= 'http://www.capri-pizza-service.de/img/flyer_januar2020.pdf'

filedirectory= 'C:/Users/betki/Documents/Uni/webEngineering/Karte2.pdf'
TOKEN= '1009520225:AAFe0bRViAfP8CrHVlW7LwZHyTwpURBDGxA'


 #karte downloaden und schicken
def send_karte(update,context):
    myfile= requests.get(url, allow_redirects= True)    #TODO: hier link fest genutzt, nicht dynmaisch
    open(filedirectory,'wb').write(myfile.content)
    doc = open(filedirectory, 'rb')
<<<<<<< Updated upstream
    context.bot.send_document( chat_id=update.effective_chat.id, document=doc )

def get_bestellung(update,context):
    update.message.reply_text('danke')
    texts = update.message.text.split(" ", 2)               # Nachricht splitten um Bestellungsnummer finden
    name = update.message.from_user.first_name              #Vorname finden
=======
    bot.send_document(g_chatID, doc )
    bot.send_message(g_chatID,'Such dir was aus!')



@bot.message_handler(func=lambda msg: msg.text is not None and 'Bestellung' in msg.text)
def get_bestellung(message):
    bot.send_message(g_chatID,'Danke man ')
    texts = message.text.split(" ",2)               # Nachricht splitten um Bestellungsnummer finden
    name = message.from_user.first_name             #Vorname finden

>>>>>>> Stashed changes
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
        JSON_file= {name: [bestellung]}                 #wir hier die JSON Datei neu Beschrieben,TODO: in der Gruppe muss hier hinzugefügt werden
        with open('Bestellungen.json', 'w') as outfile:
            json.dump(JSON_file, outfile)
   

updater = Updater(TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('karte', send_karte))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'Bestellung'), get_bestellung))  #ruft get_bestellung auf wenn Bestellung in der Nachricht enthalten ist

updater.start_polling()
updater.idle()