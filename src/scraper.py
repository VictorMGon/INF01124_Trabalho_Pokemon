from bs4 import BeautifulSoup
import requests
import re
import csv

def processNumber(str):
    numbers = re.findall('[0-9]+',str)
    if len(numbers)>0:
        return int(numbers[0])
    else:
        return -1

def processGen(str):
    result = re.search('Generation ([A-Z]+)',str)

    if len(result.groups()) == 0:
        return -1

    s = result.group(1)

    if len(s)>0:
        roman = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000,'IV':4,'IX':9,'XL':40,'XC':90,'CD':400,'CM':900}
        i = 0
        num = 0
        while i < len(s):
         if i+1<len(s) and s[i:i+2] in roman:
            num+=roman[s[i:i+2]]
            i+=2
         else:
            #print(i)
            num+=roman[s[i]]
            i+=1
        return num
    else:
        return -1

def csvString(str):
    return str
    #return '\"'+str+'\"'

class PokemonMovesScraper:
    url = 'https://bulbapedia.bulbagarden.net'
    magic_filter1 = '#mw-content-text > div > table:nth-child(4) > tbody > tr > td > table > tbody'
    magic_filter2 = '#mw-content-text > div  table[style*="float:right"] > tbody'
    magic_filter3 = '#By_leveling_up'
    moves_url = []
    moves = []
    moves_pkmn_list = []
    moves_count = 0

    def __init__(self):
        pass
    def extractMovesURL(self):
        moves_html_request = requests.get(self.url+'/wiki/List_of_moves')
        moves_html = moves_html_request.text
        soup = BeautifulSoup(moves_html, 'html.parser')

        table_addr = soup.select_one(self.magic_filter1).findAll('tr')
        for entry in table_addr[1:]:
            self.moves_url.append(self.url+entry.findAll('td')[1].a['href'])
    def processMoveURL(self,url):
        move_html_request = requests.get(url)
        move_html = move_html_request.text
        soup = BeautifulSoup(move_html, 'html.parser')

        info_box_addr = soup.select_one(self.magic_filter2)
        info_box_addr2 = info_box_addr.select_one('tr:nth-of-type(4)').findAll('tr')

        move_name = csvString(info_box_addr.select_one('b').text)
        move_type = csvString(info_box_addr2[0].select_one('th + td span > b').text)
        move_category = csvString(info_box_addr2[1].select_one('th + td span').text)
        move_PP = processNumber(info_box_addr2[2].select_one('td').text)
        move_power = processNumber(info_box_addr2[3].select_one('td').text)
        move_accuracy = processNumber(info_box_addr2[4].select_one('td').text)
        move_gen = processGen(info_box_addr.select_one('tr:nth-of-type(6) th + td a').text)
        move_id = self.moves_count + 1

        move_pkmn_list = []

        if soup.select_one(self.magic_filter3) != None:
            pkmn_table = soup.select_one(self.magic_filter3).parent.findNext('table').findAll('tr')[2:-1]
            for pkmn in pkmn_table:
                move_pkmn_list.append(int(processNumber(pkmn.select_one('td').text)))

        self.moves_pkmn_list.append([move_id,move_pkmn_list])
        self.moves.append([move_id, move_name, move_type, move_category, move_PP, move_power, move_accuracy, move_gen])
        self.moves_count += 1
    def processMovesURL(self):
        for url in self.moves_url:
            print(url)
            self.processMoveURL(url)
    def dumpMoves(self):
        with open('moves.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['move_id','move_name','move_type','move_category','move_PP','move_power','move_accuracy','move_gen'])
            for move in self.moves:
                writer.writerow(move)
    def dumpMovesPKMN(self):
        with open('movespkmn.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['entry_id','move_id','pkmn_id',])
            entry_id = 1
            for move_pkmn_list in self.moves_pkmn_list:
                for pkmn_id in move_pkmn_list[1]:
                    writer.writerow([entry_id, move_pkmn_list[0], pkmn_id])
                    entry_id += 1

#scraper = PokemonMovesScraper()

#scraper.extractMovesURL()
#scraper.processMovesURL()

#scraper.dumpMoves()
#scraper.dumpMovesPKMN()
