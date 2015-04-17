# pulling nba play-by-play via xml to json
#
#
import urllib2
import xml.etree.ElementTree as ET # parse xml
import json
#import xmltodict

def shotsJSON(gameID):        
    print gameID # debug
    date = gameID[:8]
    teams = gameID[8:]
    url = "http://www.nba.com/games/game_component/dynamic/" + date + "/" + teams + "/shotchart_all.xml"
    web = urllib2.urlopen(url)
    tree = ET.parse(web).getroot()
    # get game info
    # game info: tree[0].items()
    shotsjson = ''
    for event in tree[0]: # tree = "message" -> "game" -> "event"
        I = [('gameID', gameID)]        
        I.append(event.items())
        I.append(('play', event.text))
        shotsjson = shotsjson + json.dumps(I)
    return shotsjson

def playsJSON(gameID):        
    print gameID # debug
    date = gameID[:8]
    teams = gameID[8:]
    url = "http://www.nba.com/games/game_component/dynamic/" + date + "/" + teams + "/pbp_all.xml"
    web = urllib2.urlopen(url)
    tree = ET.parse(web).getroot()
    # get game info
    # game info: tree[0].items()
    playsjson = ''
    for event in tree[0]: # tree = "message" -> "game" -> "event"
        I = [('gameID', gameID)]        
        I.append(event.items())
        I.append(('play', event.text))
        playsjson = playsjson + json.dumps(I)
    return playsjson

#xml = xmltodict.parse(web)
#for event in xml['message']['game']:
#    print event['player_code']

def writePlays(gamelist, playlist):
  delim = "\t"
  fr = open(gamelist,"r") 
  fw = open(playlist,"w")
  fr.readline() # first line is data names
  for gameID in fr.readlines():
      gameID = gameID.replace(delim,'').replace('\n','')
      json.dump(playsJSON(gameID), fw) # write plays to text
      #json.dump(shotsJSON(gameID), fw) # write plays to text

def main():
    #gamelist = "gamelist_201415.txt"
    #playlist = "playbyplay_201415.json"
    #writePlays(gamelist, playlist)
    gamelist = "gamelist_json.txt"
    playlist = "shots_201415.json"
    writePlays(gamelist, playlist)

# boilerplate to run main on execution    
if __name__ == "__main__":
    main()