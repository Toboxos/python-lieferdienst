# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from io import StringIO
from bs4 import BeautifulSoup 
import requests
import re
import urllib
import json
import os

TOKEN = '1059740952:AAHHEfgqgGkdhxUntCiF2lmGt8TqnakZ8ss'
_capriUrl= 'http://www.capri-pizza-service.de/'
_menueName = "MenuCapri.pdf"                        # Name  of menu pdf file
_menuPlace = "./MenuCapri.pdf"                      # Path to menu pdf file
_jsonFileName = "data.json"


class BestellungsManager:

    def __init__(self):

        # JSON-Datei exisitiert
        if os.path.exists(_jsonFileName):

            # Öffne gespeicherte Bestellungen
            with open(_jsonFileName, 'r') as file:
                try:
                    self.bestellungen = json.load(file)
                except:
                    self.bestellungen = {}

        # JSON-Datei exisitiert nicht
        else:
            self.bestellungen = {}

    # Speichere Bestellungen in JSON-Datei
    def save(self):
        with open(_jsonFileName, "w") as file:
            json.dump(self.bestellungen, file)

    # Gibt zurück ob eine Bestellung bereits im Gange ist
    def istBestellungAmLaufen(self, id):
        print( self.bestellungen )
        
        # Es gibt noch keine Bestellung
        if not id in self.bestellungen:
            self.bestellungen[id] = { "amLaufen": False, "users": {} }   # Erstelle Bestellung

        return self.bestellungen[id]["amLaufen"]

    # Beginnt eine neue Bestellung und löscht die alte
    def beginneBestellung(self, id):
        self.bestellungen[id] = { "amLaufen": True, "users": {} }   # Lösche alte Bestellung und beginne neue

    # Beendet eine Bestellung
    def beendeBestellung(self, id):
        self.bestellungen[id]["amLaufen"] = False

    # Fügt die Bestellung eines Benutzers hinzu
    def neueBestellung(self, id, name, nummer):
        
        # Name existiert noch nicht
        if not name in self.bestellungen[id]['users']:
            print( "Neuer user", name )
            self.bestellungen[id]['users'][name] = []  # Füge BestellListe für Name hinzu

        print( self.bestellungen )
        self.bestellungen[id]['users'][name].append(nummer)

    # Lösche die eine Bestellnummer eine einzelenen Nuters
    def loscheUserNummer(self, id, name, nummer):

        # Name existiert nicht
        if not name in self.bestellungen[id]['users']:
            return

        # Nummer existiert nicht
        if not nummer in self.bestellungen[id]['users'][name]:
            return

        # Lösche nummer
        self.bestellungen[id]['users'][name].remove(nummer)

    # Löscht die Bestellung eines einzelnen Nutzers
    def loescheUserGesamteBestellung(self, id, name):

        # Name existiert nicht
        if not name in self.bestellungen[id]['users']:
            return

        # Lösche Bestellung
        self.bestellungen[id]['users'].pop(name)

    # Gibt als Text zurück, wie of eine Bestell-Nummer bestellt wurde
    def finalOrderCalc(self, id):
        counter = {}

        for name in self.bestellungen[id]['users']:
            personOrder = self.bestellungen[id]['users'][name]
            for orderNum in personOrder:
                if orderNum in counter.keys():
                    counter[orderNum] += 1
                else:
                    counter[orderNum] = 1

        message = ""
        for nummer in counter:
            message += str(counter[nummer]) + " mal Gericht " + str(nummer) + "\n"
        return message

    # Gibt als Text zurück wer was bestellt hat
    def werWas(self, id):
        message = ""
        for name, nummern in self.bestellungen[id]['users'].items():
            message += name + " hat  " + ",".join([str(nummer) for nummer in nummern]) + " bestellt\n"

        return message
        
    



_manager = BestellungsManager()

def sendMessage(update,text):
    update.message.reply_text(text)

# Liefert die Chat Id zu einem Update
def getChatId(update):
    return str(update.message.chat.id)

# Start a order 
def startOrder(update,context):
    id = getChatId(update)

    # Es läuft schon eine Bestellung
    if _manager.istBestellungAmLaufen(id):
        sendMessage(update, 'Es ist schon eine Bestellung am Laufen.')
    
    # Es läuft noch keine Bestellung
    else:
        _manager.beginneBestellung(id)  # Starte neue Bestellung
        _manager.save()                 # Speichern
        sendMenue(update, context)


def sendMenue(update,context):
    loadMenue(update,context)                   # Load pdf from live website
    print("das Menü senden")
    context.bot.send_document(chat_id=update.effective_chat.id, document=open(_menuPlace, 'rb'))

def loadMenue(update,context):
    print("Lade Speisekarte von Capriwebseite")
    url = getUrl()
    if (url == None ):
        sendMessage(update, "Bitte kontaktieren Sie die Entwickler. Es hat sich entwas grundlegend geändert.")
    else:
        print(url +" in load Menue")
        urllib.request.urlretrieve(url, _menueName)

def getUrl():
    r = requests.get(_capriUrl+'lieferservice.html')
    soup = BeautifulSoup(r.text, 'html.parser') 

    for link in soup.findAll('a', attrs={'href': re.compile("img/")}):
        pdf= _capriUrl + link.get('href')
        print(pdf + "in for schleife")
        return pdf
    return None

# User writes a number in Chat
def bestellung(update,context):
    id = getChatId(update)
    print("Neue Nummer", id)

    if _manager.istBestellungAmLaufen(id):
        print("Füge Nummer Bestellung hinzu")
        get_bestellung(update, context)
    else:
        print("Jemand hat Nr geschrieben obwohl eine Bestellung läuft.")

def get_bestellung(update,context):
    id = getChatId(update)
    print("get_bestellung")

    texts = update.message.text.split(" ", 2)               # Nachricht splitten um Bestellungsnummer finden
    name = update.message.from_user.first_name              #Vorname finden
    orderNumber = texts[1]
    neueBestellung(id, name, orderNumber)

#Generierung der Json-Datei mit NAmen und Bestellnummer
def neueBestellung(id, name, orderNumber):
    print(name + 'hat nr ' + orderNumber + 'bestellt')
    _manager.neueBestellung(id, name, orderNumber)
    _manager.save()


def wasLoeschen(update,context):
    id = getChatId(update)

    # Wenn keine Bestellung am laufen ist
    if not _manager.istBestellungAmLaufen(id):
        return

    texts = update.message.text.split(" ", 2)               # Nachricht splitten
    name = update.message.from_user.first_name
    wasSollGeloeschtWerden = texts[1]

    if (wasSollGeloeschtWerden == 'alles'):
        _manager.loescheUserGesamteBestellung(id, name)
    else:
        print('lösche nur die Nummer')
        _manager.loscheUserNummer(id, name, wasSollGeloeschtWerden)

    _manager.save()
#____________________________________________________________________________________________________________________

def end(update,context):
    print("ENDE")
    id = getChatId(update)

    _manager.beendeBestellung(id)
    _manager.save()

    message = _manager.finalOrderCalc(id)
    print(message)
    sendMessage(update,message)

def endWerWas(update,context):
    id = getChatId(update)
    message = _manager.werWas(id)
    sendMessage(update, message)


def extra(update, context):
    sendMessage(update, 'Judt ist so ein sehr toller Dozent der sehr toll ist. Er ist so toll, das alle Gruppen-Mitglieder eine 1 bekomme und nie wieder Anwesenheitspflicht haben. Wenn das nicht passiert, dann ist Judt gar nicht toll. Sehr uncool')

updater = Updater(TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('capricapri', startOrder))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'Nr'), bestellung))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'lösche'), wasLoeschen))
updater.dispatcher.add_handler(CommandHandler('Ende', end))
updater.dispatcher.add_handler(CommandHandler('WerWas', endWerWas))
updater.dispatcher.add_handler(CommandHandler('Judt', extra))
updater.start_polling()
updater.idle()
