#
#
#
import glob
import datetime
import re
import bb_tools as bb

def main():
  season_id = '00216'

  print 'Finding date of last update...'
  try:
    last_boxscore_file = sorted(glob.glob('%s/json/pbp_%s*.json' % (bb.DATAHOME,season_id)))[-1]
    last_boxscore_gameid = re.findall('pbp_(.+).json', last_boxscore_file)[0]
    last_game_info = bb.get_info(last_boxscore_gameid)
    last_update = bb.dateify(last_game_info['GAME_DATE_EST'].split('T')[0])
    start_day = last_update + datetime.timedelta(days=1)
  except: # if no data exists, use first day of season
    start_day = datetime.date(2016,10,25)
  end_day = datetime.date.today() - datetime.timedelta(days=1)
  
  print 'Getting list of games since last update...'
  bb.write_gamelist_by_date('%s/csv/gamelist_update.csv' % bb.DATAHOME, season_id, start_day, end_day)

  print 'Getting stats for each game...'
  bb.write_gamelist_json('%s/csv/gamelist_update.csv' % bb.DATAHOME)

if __name__ == '__main__': 
  main()
