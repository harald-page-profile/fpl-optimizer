import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

def get_play_data():
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    r = requests.get(url)
    json = r.json()
    players = pd.DataFrame(json['elements'])
    teams = pd.DataFrame(json['teams'])
    teams = teams[['id','name']]
    players.team = players.team.replace(teams['id'].values,teams['name'].values)
    return(players)


def scrape(cells):
    lizt = []
    for cell in cells:
        text = cell.text.strip()
        lizt.append(text)
    return(lizt)
    
def remove_char(string):
    import re
    string = string.replace("2X!","")
    string = re.sub("[A-Za-z]", "", string);
    return string

def get_cs_data():
    url = "https://playerdatabase247.com/include_premier_league_fixture_tracker_uusi.php?listtype=cs"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    cells = table.find_all("td")

    output = scrape(cells)

    output = np.array(output)
    output = output.reshape(21,7)
    output = pd.DataFrame(output)
    header_row = 0
    output.columns = output.iloc[header_row]
    output = output.drop(header_row)
    output = output.reset_index(drop = True)
    output.columns = ["team", "cs_gw2", "cs_gw3", "cs_gw4", "cs_gw5", "cs_gw6", "cs-total"]


    output.cs_gw2 = output.cs_gw2.apply(remove_char)
    output.cs_gw2 = output.cs_gw2.apply(float)
    output.cs_gw3 = output.cs_gw3.apply(remove_char)
    output.cs_gw3 = output.cs_gw3.apply(float)
    output.cs_gw4 = output.cs_gw4.apply(remove_char)
    output.cs_gw4 = output.cs_gw4.apply(float)
    output.cs_gw5 = output.cs_gw5.apply(remove_char)
    output.cs_gw5 = output.cs_gw5.apply(float)
    output.cs_gw6 = output.cs_gw6.apply(remove_char)
    output.cs_gw6 = output.cs_gw6.apply(float)
    ECS = output
    return ECS


def get_eg_data():
    url = "https://playerdatabase247.com/include_premier_league_fixture_tracker_uusi.php?listtype=expgoals"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    cells = table.find_all("td")
        
    output = scrape(cells)

    output = np.array(output)
    output = output.reshape(21,7)
    output = pd.DataFrame(output)
    header_row = 0
    output.columns = output.iloc[header_row]
    output = output.drop(header_row)
    output = output.reset_index(drop = True)
    output.columns = ["team", "gw2", "gw3", "gw4", "gw5", "gw6", "total"]

    output.gw2 = output.gw2.apply(remove_char)
    output.gw2 = output.gw2.apply(float)
    output.gw3 = output.gw3.apply(remove_char)
    output.gw3 = output.gw3.apply(float)
    output.gw4 = output.gw4.apply(remove_char)
    output.gw4 = output.gw4.apply(float)
    output.gw5 = output.gw5.apply(remove_char)
    output.gw5 = output.gw5.apply(float)
    output.gw6 = output.gw6.apply(remove_char)
    output.gw6 = output.gw6.apply(float)
    EG = output
    return EG

def get_game_history(ids):

    id = ids[0]
    url = 'https://fantasy.premierleague.com/api/element-summary/' + str(id) + "/"
    r = requests.get(url)
    json = r.json()
    df_temp = pd.DataFrame(json['history'])

    i=0
    for id in ids[1:]:
      url = 'https://fantasy.premierleague.com/api/element-summary/' + str(id) + "/"
      r = requests.get(url)
      json = r.json()
      df_temp = pd.concat([df_temp, pd.DataFrame(json['history'])])
      i+=1
      if(i%50==0):
        print("Done with: ", str(i))
    df_temp['good'] = np.where(df_temp['total_points']>=5, 1, 0);

    player_games = df_temp.groupby(['element']).agg(
        good_games = pd.NamedAgg(column='good', aggfunc=sum)
    )
    return player_games
