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
    """Diese Klasse verwaltet die Bestellungen von verschiedenen Gruppen.
    
    Die Bestellungen werden in der Variable bestellungen als Dictionary gespeichert. Folgende Struktur:
    {
        chatId:
            "amLaufen": True|False,
            "users": {
                "user1": [1, 2, 3],
                "user2": [2, 3],
                ...
            }
        },
        ...
    }
    """

    def __init__(self):
        """
        Initialisierung eines BestellungsManagers:
        - wenn JSON-Datei schon existiert, werden gespeicherte Bestellungen in Variable übernommen
        - ansonsten leere Variable bestellungen
        """
    
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

    def save(self):
        """
        Speichere den Inhalt der Variable bestellung in JSON-Datei
        """

        with open(_jsonFileName, "w") as file:
            json.dump(self.bestellungen, file)


    def istBestellungAmLaufen(self, id):
        """     
        - Ermittelt, ob schon eine Bestellung für einen Chat mit ID läuft
        - legt ggf. eine neue Bestellung für diese ChatID an: Variable amLaufen jedoch False
        :param id: zu überprüfende ChatID
        :return: ChatID mit entweder True/False je nach amLaufen
        """

        print( self.bestellungen )
        
        # Es gibt noch keine Bestellung
        if not id in self.bestellungen:
            self.bestellungen[id] = { "amLaufen": False, "users": {} }   # Erstelle Bestellung

        return self.bestellungen[id]["amLaufen"]

    def beginneBestellung(self, id):
        """
        Beginnt eine Chat-Bestellung:
         - amLaufen wird für die id auf True gesetzt
         - Etwaige vorhandene Bestellung werden gelöscht: zur Bestellung gespeicherte Daten werden geleert
        :param id: ChatID, deren Bestellung neu gestartet wird
        """

        self.bestellungen[id] = { "amLaufen": True, "users": {} }

    def beendeBestellung(self, id):
        """
        Beenden einer Chat-Bestellung:
         - setzt amLaufen für Bestellung der übergebenen ChatID zu False
        :param id: ChatID der zu beendenden Bestellung
        """
        self.bestellungen[id]["amLaufen"] = False

    def neueBestellung(self, id, name, nummer):
        """
        Hinzufügen einer User-Bestellung
         - ggf. Anlegen des Users falls nicht schon in Bestellung dieses Chats
         - Nummer wird an die Nummerliste des Users angefügt
        :param id: ChatID des Users
        :param name: Name des Users
        :param nummer: einzugetragende Bestellnummer
        """

        # Name existiert noch nicht
        if not name in self.bestellungen[id]['users']:
            print( "Neuer user", name )
            self.bestellungen[id]['users'][name] = []  # Füge Bestellliste für Name hinzu

        print( self.bestellungen )
        self.bestellungen[id]['users'][name].append(nummer)

    def loescheUserNummer(self, id, name, nummer):
        """
        Löscht eine bestimmte Bestellnummer eines Users:
         - falls User nicht angelegt oder die Nummer nicht in seiner Liste: Funktionsabbruch
         - Nummer wird aus der Liste des Users in dem angegebenen Chat entfernt
        :param id: ChatID des Users
        :param name: Name des Users
        :param nummer: zu löschende Bestellnummer       
        """

        # Name existiert nicht
        if not name in self.bestellungen[id]['users']:
            return

        # Nummer existiert nicht
        if not nummer in self.bestellungen[id]['users'][name]:
            return

        # Lösche nummer
        self.bestellungen[id]['users'][name].remove(nummer)

    def loescheUserGesamteBestellung(self, id, name):
        """
        Löscht die gesamte Bestellung eines Users:
         - falls User nicht angelegt Funktionsabbruch
         - entfernt User aus der Bestellung für die angegebene ChatID
        :param id: ChatID des Users
        :param name: Name des Users
        """

        # Name existiert nicht
        if not name in self.bestellungen[id]['users']:
            return

        # Lösche Bestellung
        self.bestellungen[id]['users'].pop(name)

    def finalOrderCalc(self, id):
        """
        Stellt eine Nachricht zusammen, wie oft insgesamt eine Bestellnummer bestellt wurde:
         - legt dictionary counter an
         - geht jede User-Bestellung durch und inkrementiert die Anzahl der Bestellungen für die jeweiligen Nummern in counter
         - erstellt message string mit allen Bestellnummern und korrespondieren Anzahlen
        :param id: ChatID der zusammenzufassenden Bestellung
        :return: message string
        """

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

    def werWas(self, id):
        """
    	Stellt eine Nachricht zusammen, welcher User was bestellt hat:
         - legt message string an
         - für alle User wird der Name und sämtliche bestellte Nummern in den string eingetragen
        :param id: ChatID der zusammenzufassenden Bestellung
        :return: message string
        """

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
        sendMessage(update, "Bitte kontaktieren Sie die Entwickler. Es hat sich etwas grundlegend geändert.")
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
        _manager.loescheUserNummer(id, name, wasSollGeloeschtWerden)

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




if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('capricapri', startOrder))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'Nr'), bestellung))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'lösche'), wasLoeschen))
    updater.dispatcher.add_handler(CommandHandler('Ende', end))
    updater.dispatcher.add_handler(CommandHandler('WerWas', endWerWas))
    updater.start_polling()
    updater.idle()
