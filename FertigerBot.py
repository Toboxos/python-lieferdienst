from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from io import StringIO
from bs4 import BeautifulSoup 
import requests
import re
import urllib
import json

TOKEN = '1059740952:AAHHEfgqgGkdhxUntCiF2lmGt8TqnakZ8ss'
_capriUrl= 'http://www.capri-pizza-service.de/'
_menueName = "MenuCapri.pdf"
_menuPlace = "./MenuCapri.pdf"
_jsonFileName = "data.json"

_bestellungAmLaufen = False

    #speichern der chatId in globaer Variable

def sendMessage(update,text):
    update.message.reply_text(text)

#______________________________________________________________________________________________________
def startOrder(update,context):
    if (_bestellungAmLaufen == True):
        sendMessage(update, 'Es ist schon eine Bestellung am Laufen.')
    else:

        file = open(_jsonFileName, 'w+')
        sendMenue(update, context)

def sendMenue(update,context):
    _bestellungAmLaufen = True
    loadMenue(update,context)
    print("das Menü senden")
    context.bot.send_document(chat_id=update.effective_chat.id, document=open(_menuPlace, 'rb'))

def loadMenue(update,context):
    print("Lade Speisekarte von Capriwebseite")
    url = getUrl()
    if (url == None ):
        sendMessage("Bitte kontaktieren Sie die Entwickler. Es hat sich entwas grundlegend geändert.")
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

#_________________________________________________________________________________________________________
def bestellung(update,context):
    print("bestellung")
    if (returnBestellungAmLaufen):
        print("bestellung if")
        get_bestellung(update, context)
    else:
        Print("Jemand hat Nr geschrieben obwohl eine Bestellung läuft.")
def returnBestellungAmLaufen():
    return _bestellungAmLaufen
def get_bestellung(update,context):
    print("get_bestellung")
    texts = update.message.text.split(" ", 2)               # Nachricht splitten um Bestellungsnummer finden
    name = update.message.from_user.first_name              #Vorname finden
    orderNumber = texts[1]
    neueBestellung(name, orderNumber)

#Generierung der Json-Datei mit NAmen und Bestellnummer
def neueBestellung(name, orderNumber):
    print(name + 'hat nr ' + orderNumber + 'bestellt')

    with open(_jsonFileName, 'r') as file:  # bisherigre Datei öffnen
        try:  # wenn die Datei leer ist kann man sie nicht öffnen, dann springt man in except
            jsonData = json.load(file)
        except:
            jsonData = {}

    if name in jsonData:    #prüfen ob Name bereits in der Json-Datei vorhanden ist
        nameElement = jsonData[name]
        nameElement.append(orderNumber) #Datensatz für Namen mit Bestellnummer erweitern
        jsonData[name] = nameElement
        with open(_jsonFileName, 'w') as outfile:
            json.dump(jsonData, outfile)
    else:
        newNameElement = {name: [orderNumber]} #Neues Element mit neuem Namen  und Bestellnummer erstellen
        jsonData.update(newNameElement)
        with open(_jsonFileName, 'w') as outfile:
            json.dump(jsonData, outfile)


def wasLoeschen(update,context):
    texts = update.message.text.split(" ", 2)               # Nachricht splitten
    name = update.message.from_user.first_name
    wasSollGeloeschtWerden = texts[1]
    if (wasSollGeloeschtWerden == 'alles'):
        loescheGesamtenEintrag(name)
    else:
        print('lösche nur die Nummer')
        loescheNurEineNummer(name, wasSollGeloeschtWerden)

def loescheGesamtenEintrag(name):
    print("alles loeschen")    
    with open(_jsonFileName) as data_file:
        data = json.load(data_file)

    if name in data:
        del data[name]

    with open(_jsonFileName, 'w') as data_file:
        data = json.dump(data, data_file)

def loescheNurEineNummer(name, nr):
    print("Das funktioniert noch nicht")
#____________________________________________________________________________________________________________________

def end(update,context):
    message = finalOrderCalc()
    print(message)
    sendMessage(update,message)
    _bestellungAmLaufen = False

def finalOrderCalc():
    dict = {}
    with open(_jsonFileName, 'r') as file:  # bisherigre Datei öffnen
        try:  # wenn die Datei leer ist kann man sie nicht öffnen, dann springt man in except
            jsonData = json.load(file)
        except:
            jsonData = {}

        for name in jsonData:
            print(jsonData[name])
            personOrder = jsonData[name]
            for orderNum in personOrder:
                if orderNum in dict.keys():
                    dict[orderNum] = dict[orderNum] + 1
                else:
                    dict[orderNum] = 1
        message = ""
        for key in dict:
            message += str(dict[key]) + " mal Gericht " + str(key) + "\n"
        return message

def endWerWas(update,context):
    dict = {}
    with open('data.json', 'r') as file:  # bisherigre Datei öffnen
        try:  # wenn die Datei leer ist kann man sie nicht öffnen, dann springt man in except
            jsonData = json.load(file)
        except:
            jsonData = {}
    message = ""
    for name in jsonData:
        personOrder = jsonData[name]
        message += name + " hat  " + str(jsonData[name]) + " bestellt\n"

    sendMessage(update,message)

updater = Updater(TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('capricapri', startOrder))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'Nr'), bestellung))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'lösche'), wasLoeschen))
updater.dispatcher.add_handler(CommandHandler('Ende', end))
updater.dispatcher.add_handler(CommandHandler('WerWas', endWerWas))
updater.start_polling()
updater.idle()
